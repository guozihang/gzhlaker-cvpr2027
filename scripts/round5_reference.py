#!/usr/bin/env python3
"""Deterministic reference semantics for the round-5 manuscript, not the prototype.

This module implements only the definitions that the paper uses to make the
decision layer reproducible:

* strongest-competitor margin over executed comparison pools;
* grouped, round-robin, selection-only anchor ordering;
* first-version fusion-edge geometry;
* a bounded connection-path check on a synthetic grid;
* zero-error binomial risk bound and evidence-count accounting.

It is deliberately small and standard-library-only. Running it does not execute
the FastVCL prototype, a dataset pair, a model or a GPU kernel.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Margin and selector
# ---------------------------------------------------------------------------
def strongest_competitor_margin(anchor, by_a, by_b):
    """Return the bidirectional margin of ``anchor`` under the round-5 rule.

    ``by_a[i]`` maps a compared B coordinate to its cosine for A coordinate i;
    ``by_b[j]`` maps a compared A coordinate to its cosine for B coordinate j.
    The union across plans is expected to be merged before the call. A side is
    missing when it has no competitor after removing the current match.
    """
    i, j = int(anchor[0]), int(anchor[1])
    own = float(by_a[i][j])
    competitors_b = {j2: float(s) for j2, s in by_a.get(i, {}).items() if j2 != j}
    competitors_a = {i2: float(s) for i2, s in by_b.get(j, {}).items() if i2 != i}
    mu_b = own - max(competitors_b.values()) if competitors_b else None
    mu_a = own - max(competitors_a.values()) if competitors_a else None
    missing = []
    if mu_a is None:
        missing.append("A")
    if mu_b is None:
        missing.append("B")
    mu = min(mu_a, mu_b) if not missing else None
    return {
        "anchor": [i, j],
        "score": own,
        "margin_a": mu_a,
        "margin_b": mu_b,
        "margin": mu,
        "missing": missing,
    }


def _normalized_ranks(values):
    """Ranks in [0, 1], larger value -> larger rank, ties get the mean rank."""
    n = len(values)
    if n == 0:
        return {}
    order = sorted(range(n), key=lambda k: (values[k], k))
    ranks = [0.0] * n
    pos = 0
    while pos < n:
        end = pos + 1
        while end < n and values[order[end]] == values[order[pos]]:
            end += 1
        mean = (pos + end - 1) / 2.0
        for q in range(pos, end):
            ranks[order[q]] = mean / (n - 1) if n > 1 else 0.5
        pos = end
    return {k: ranks[k] for k in range(n)}


def selector_order(anchors, margins, residuals, s_min, budget):
    """Group by two-axis time cell, round-robin groups, rank inside each group.

    ``anchors`` is a list of ``(i, j)``; ``margins`` and ``residuals`` map an
    anchor to a float or ``None`` (missing). The neutral rank for missing
    signals is 0.5. Returns the selected prefix and per-group visit counts.
    """
    width = 2 * int(s_min)
    groups = {}
    for a in anchors:
        groups.setdefault((a[0] // width, a[1] // width), []).append(a)
    keys = sorted(groups)
    rank_mu = _normalized_ranks([
        -(margins.get(a) if margins.get(a) is not None else 0.0) for a in anchors
    ])
    rank_rho = _normalized_ranks([
        (residuals.get(a) if residuals.get(a) is not None else 0.0) for a in anchors
    ])
    index = {a: k for k, a in enumerate(anchors)}

    def priority(a):
        m = margins.get(a)
        r = residuals.get(a)
        rm = rank_mu[index[a]] if m is not None else 0.5
        rr = rank_rho[index[a]] if r is not None else 0.5
        return (-(0.5 * rm + 0.5 * rr), a[0], a[1])

    ordered = {k: sorted(v, key=priority) for k, v in groups.items()}
    selected = []
    visits = {k: 0 for k in keys}
    cursor = {k: 0 for k in keys}
    active = list(keys)
    while len(selected) < int(budget) and active:
        next_active = []
        for k in active:
            if len(selected) >= int(budget):
                break
            pos = cursor[k]
            if pos >= len(ordered[k]):
                continue
            selected.append(ordered[k][pos])
            cursor[k] = pos + 1
            visits[k] += 1
            if cursor[k] < len(ordered[k]):
                next_active.append(k)
        active = next_active
    return selected, visits


# ---------------------------------------------------------------------------
# Fusion geometry
# ---------------------------------------------------------------------------
def _fragment_ok(c):
    return all(k in c for k in ("id", "a_s", "a_e", "b_s", "b_e", "alpha", "beta"))


def fusion_edge(u, v, config):
    """Return ``(legal, reasons, measures)`` for the first-version edge rule."""
    reasons = []
    if not (_fragment_ok(u) and _fragment_ok(v)):
        return False, ["missing map"], {}
    if u["a_e"] > v["a_s"] or u["b_e"] > v["b_s"]:
        reasons.append("order/overlap")
    gap_a = v["a_s"] - u["a_e"]
    gap_b = v["b_s"] - u["b_e"]
    if gap_a < 0 or gap_b < 0:
        reasons.append("negative gap")
    if gap_a > config["G_A"] or gap_b > config["G_B"]:
        reasons.append("gap cap")
    # Boundary maps: A->B for u, B->A for v.
    map_errors = []
    for a in (v["a_s"], v["a_e"]):
        map_errors.append(abs((u["alpha"] * a + u["beta"]) - (v["b_s"] if a == v["a_s"] else v["b_e"])))
    for b in (u["b_s"], u["b_e"]):
        inv = (b - v["beta"]) / v["alpha"]
        map_errors.append(abs(inv - (u["a_s"] if b == u["b_s"] else u["a_e"])))
    if max(map_errors) > max(config["kappa_A"], config["kappa_B"]):
        reasons.append("boundary map")
    if gap_a > 0:
        slope = gap_b / gap_a
        if not (config["alpha_min"] <= slope <= config["alpha_max"]):
            reasons.append("connector slope")
    # Same A interval at a different B position is a separate copy.
    iou_a = _iou(u["a_s"], u["a_e"], v["a_s"], v["a_e"])
    iou_b = _iou(u["b_s"], u["b_e"], v["b_s"], v["b_e"])
    if iou_a >= config["theta_dedup"] and iou_b < config["theta_dedup"]:
        reasons.append("same-A different-B")
    return (not reasons), reasons, {
        "gap_a": gap_a, "gap_b": gap_b, "iou_a": iou_a, "iou_b": iou_b,
        "max_map_error": max(map_errors),
    }


def _iou(a0, a1, b0, b1):
    inter = max(0, min(a1, b1) - max(a0, b0))
    union = max(a1, b1) - min(a0, b0)
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Bounded connection path
# ---------------------------------------------------------------------------
def connection_path(sim, valid, starts, ends, tau, max_low_run, min_coverage):
    """Bounded one-step-path check used to make ``Conn`` testable.

    ``sim``/``valid`` are 2-D grids; ``starts``/``ends`` are coordinate sets.
    The DP uses steps (1,1),(1,2),(2,1), a zero restart and score
    ``sim - tau``. A path is accepted when it reaches an end cell with positive
    score, has coverage at least ``min_coverage`` over its own steps and no
    consecutive run of cells with ``sim < tau`` longer than ``max_low_run``.
    """
    rows, cols = len(sim), len(sim[0])
    if any(not (0 <= r < rows and 0 <= c < cols) for r, c in starts + ends):
        return False, {"reason": "outside region", "cells": 0}
    # dp[r][c] = (score, path list)
    dp = [[None] * cols for _ in range(rows)]
    for r, c in starts:
        if valid[r][c]:
            dp[r][c] = (max(0.0, sim[r][c] - tau), [(r, c)])
    for r in range(rows):
        for c in range(cols):
            if not valid[r][c]:
                continue
            own = sim[r][c] - tau
            best = dp[r][c]
            for dr, dc in ((1, 1), (1, 2), (2, 1)):
                pr, pc = r - dr, c - dc
                if pr < 0 or pc < 0 or dp[pr][pc] is None:
                    continue
                prev_score, prev_path = dp[pr][pc]
                if prev_score <= 0:
                    continue
                cand = prev_score + own
                if best is None or cand > best[0]:
                    best = (cand, prev_path + [(r, c)])
            if best is None:
                best = (max(0.0, own), [(r, c)])
            dp[r][c] = best
    best = None
    for r, c in ends:
        if dp[r][c] is not None and dp[r][c][0] > 0:
            if best is None or dp[r][c][0] > best[0]:
                best = dp[r][c]
    if best is None:
        return False, {"reason": "no path", "cells": 0}
    path = best[1]
    low_run = worst = 0
    valid_count = 0
    for r, c in path:
        valid_count += int(bool(valid[r][c]))
        if sim[r][c] < tau:
            low_run += 1
            worst = max(worst, low_run)
        else:
            low_run = 0
    coverage = valid_count / len(path) if path else 0.0
    ok = worst <= max_low_run and coverage >= min_coverage
    return ok, {"reason": "ok" if ok else "low-run/coverage",
                "cells": len(path), "worst_low_run": worst,
                "coverage": coverage}


# ---------------------------------------------------------------------------
# Risk and budget
# ---------------------------------------------------------------------------
def risk_upper(n):
    if n <= 0:
        return None
    return 1.0 - 0.05 ** (1.0 / n)


def evidence_frame_pairs(budget):
    b = int(budget)
    ba = (2 * b) // 3
    bf = b - ba
    return {"B": b, "B_A": ba, "B_F": bf, "anchor_pairs": 3 * ba,
            "fusion_pairs": 5 * bf, "total_pairs": 3 * ba + 5 * bf}
