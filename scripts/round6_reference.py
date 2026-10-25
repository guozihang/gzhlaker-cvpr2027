#!/usr/bin/env python3
"""Round-6 reference semantics for the repaired connection and fusion rules.

This module is deliberately separate from ``round5_reference.py`` so that the
round-5 planning snapshot stays reproducible.  It implements the definitions
that the round-6 execution plan requires to be fixed:

* an anchored connection check whose path must start at a left support node and
  end at a right support node (no free restart inside the region);
* interval coverage over the selected endpoints instead of path length, with
  skipped and invalid positions accounted separately;
* final path accounting (``path_nodes``, ``dp_cells_visited``,
  ``predecessor_evaluations``, similarity evaluations and failures);
* axis-wise boundary-map thresholds for fusion geometry;
* pairwise-only fusion over the original candidate set with member consumption;
* the transfer-aware question and evidence bounds.

It is standard-library-only, small and deterministic.  Running it does not
execute the FastVCL prototype, a dataset pair, a visual model or a GPU kernel.
"""
from __future__ import annotations

import math

# Declared local steps; shared by the reference checker and the manuscript.
DEFAULT_STEPS = ((1, 1), (1, 2), (2, 1))


def _finite(x):
    """True for an int/float that is finite (booleans are rejected)."""
    return (
        isinstance(x, (int, float))
        and not isinstance(x, bool)
        and math.isfinite(float(x))
    )


def _fragment_complete(c):
    return isinstance(c, dict) and all(
        key in c for key in ("id", "a_s", "a_e", "b_s", "b_e", "alpha", "beta")
    )


def _iou(a0, a1, b0, b1):
    inter = max(0, min(a1, b1) - max(a0, b0))
    union = max(a1, b1) - min(a0, b0)
    return inter / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Anchored connection check
# ---------------------------------------------------------------------------
def _path_quality(path, sim, valid, tau, max_low_run, min_coverage):
    """Quality measures for a path already known to start/end at supports."""
    rows = [r for r, _ in path]
    cols = [c for _, c in path]
    a_min, a_max = min(rows), max(rows)
    b_min, b_max = min(cols), max(cols)
    span_a = a_max - a_min + 1
    span_b = b_max - b_min + 1
    distinct_a = len(set(rows))
    distinct_b = len(set(cols))
    coverage_a = distinct_a / span_a if span_a else 0.0
    coverage_b = distinct_b / span_b if span_b else 0.0
    low_run = worst_low_run = 0
    for r, c in path:
        if float(sim[r][c]) < float(tau):
            low_run += 1
            worst_low_run = max(worst_low_run, low_run)
        else:
            low_run = 0
    max_step_gap = 0
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        max_step_gap = max(max_step_gap, r2 - r1, c2 - c1)
    invalid_inside = 0
    for r in range(a_min, a_max + 1):
        for c in range(b_min, b_max + 1):
            invalid_inside += int(not bool(valid[r][c]))
    coverage = min(coverage_a, coverage_b)
    ok = coverage >= float(min_coverage) and worst_low_run <= int(max_low_run)
    return {
        "ok": ok,
        "coverage": coverage,
        "coverage_a": coverage_a,
        "coverage_b": coverage_b,
        "distinct_a": distinct_a,
        "distinct_b": distinct_b,
        "span_a": span_a,
        "span_b": span_b,
        "skipped_a": span_a - distinct_a,
        "skipped_b": span_b - distinct_b,
        "skipped_positions": (span_a - distinct_a) + (span_b - distinct_b),
        "invalid_inside_bbox": invalid_inside,
        "worst_low_run": worst_low_run,
        "max_step_gap": max_step_gap,
    }


def connection_path(
    sim,
    valid,
    starts,
    ends,
    tau,
    max_low_run,
    min_coverage=0.6,
    steps=DEFAULT_STEPS,
    reuse=None,
    region=None,
    max_cells=None,
):
    """Certify a bridge between the left and right fragments.

    ``starts``/``ends`` are coordinate sets of the two support nodes.  The DP is
    seeded only at valid ``starts`` cells; no other cell can begin a path and no
    cell can restart one.  A cell is reachable only from a positive-score state
    along one of ``steps``.  Endpoints of the winning path are checked against
    ``starts`` and ``ends`` explicitly, then interval coverage and low-score runs
    are tested.  The single best path is certified; failure does not search for
    an alternative path in this first version.

    ``region`` is an optional half-open ``(r0, r1, c0, c1)`` box.  If its area
    exceeds ``max_cells`` the edge is unavailable and the cap hit is recorded.
    ``reuse`` is an optional previously verified path; it is re-checked under the
    same endpoint, region, step and quality rules and costs no DP visits.
    """
    rows = len(sim)
    cols = len(sim[0]) if rows else 0
    starts = {(int(r), int(c)) for r, c in starts}
    ends = {(int(r), int(c)) for r, c in ends}
    steps = tuple((int(dr), int(dc)) for dr, dc in steps)
    detail = {
        "ok": False,
        "reason": None,
        "path": [],
        "path_nodes": 0,
        "dp_cells_visited": 0,
        "predecessor_evaluations": 0,
        "similarity_evaluations": 0,
        "region_area": rows * cols,
        "region_cap_hit": False,
        "reused": False,
        "start": None,
        "end": None,
        "score": None,
    }

    # Region and basic availability checks are still counted as work.
    if region is None:
        r0, r1, c0, c1 = 0, rows, 0, cols
    else:
        if len(region) != 4 or any(not isinstance(x, int) for x in region):
            detail["reason"] = "invalid region"
            return False, detail
        r0, r1, c0, c1 = region
        if not (0 <= r0 < r1 <= rows and 0 <= c0 < c1 <= cols):
            detail["reason"] = "region outside grid"
            return False, detail
    area = (r1 - r0) * (c1 - c0)
    detail["region_area"] = area
    if max_cells is not None and area > int(max_cells):
        detail["reason"] = "region cap"
        detail["region_cap_hit"] = True
        return False, detail

    def inside(p):
        return r0 <= p[0] < r1 and c0 <= p[1] < c1

    left = sorted(p for p in starts if inside(p) and valid[p[0]][p[1]])
    right = sorted(p for p in ends if inside(p) and valid[p[0]][p[1]])

    if reuse is not None:
        return _check_reuse(
            reuse, sim, valid, starts, ends, left, right, inside,
            tau, max_low_run, min_coverage, steps, detail,
        )

    if not left:
        detail["reason"] = "empty left support"
        return False, detail
    if not right:
        detail["reason"] = "empty right support"
        return False, detail

    dp = [[None] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]
    visited = evals = sim_evals = 0
    for r in range(r0, r1):
        for c in range(c0, c1):
            if not valid[r][c]:
                continue
            visited += 1
            sim_evals += 1
            own = float(sim[r][c]) - float(tau)
            best = None
            best_parent = None
            if (r, c) in starts and own > 0.0:
                best = own
            for dr, dc in steps:
                pr, pc = r - dr, c - dc
                if pr < r0 or pc < c0:
                    continue
                evals += 1
                prev = dp[pr][pc]
                if prev is None or prev <= 0.0:
                    continue
                cand = prev + own
                if best is None or cand > best:
                    best = cand
                    best_parent = (pr, pc)
            if best is not None and best > 0.0:
                dp[r][c] = best
                parent[r][c] = best_parent

    best_end = None
    best_score = None
    for p in right:
        s = dp[p[0]][p[1]]
        if s is not None and s > 0.0 and (best_score is None or s > best_score):
            best_score = s
            best_end = p

    detail["dp_cells_visited"] = visited
    detail["predecessor_evaluations"] = evals
    detail["similarity_evaluations"] = sim_evals
    if best_end is None:
        detail["reason"] = "no path"
        return False, detail

    path = []
    cur = best_end
    while cur is not None:
        path.append(cur)
        cur = parent[cur[0]][cur[1]]
    path.reverse()
    start = path[0]

    detail["path"] = path
    detail["path_nodes"] = len(path)
    detail["start"] = start
    detail["end"] = best_end
    detail["score"] = best_score
    if start not in starts:
        detail["reason"] = "start outside left support"
        return False, detail
    if best_end not in ends:
        detail["reason"] = "end outside right support"
        return False, detail

    quality = _path_quality(path, sim, valid, tau, max_low_run, min_coverage)
    detail.update(quality)
    if not quality["ok"]:
        detail["reason"] = "quality"
        return False, detail
    detail["ok"] = True
    detail["reason"] = "ok"
    return True, detail


def _check_reuse(
    reuse, sim, valid, starts, ends, left, right, inside,
    tau, max_low_run, min_coverage, steps, detail,
):
    """Apply the full endpoint/region/step/quality test to a reused path."""
    path = [(int(r), int(c)) for r, c in reuse]
    detail["reused"] = True
    detail["path"] = path
    detail["path_nodes"] = len(path)
    if not path:
        detail["reason"] = "empty reused path"
        return False, detail
    if not left:
        detail["reason"] = "empty left support"
        return False, detail
    if not right:
        detail["reason"] = "empty right support"
        return False, detail
    if any(not inside(p) for p in path):
        detail["reason"] = "reused path outside region"
        return False, detail
    if any(not valid[r][c] for r, c in path):
        detail["reason"] = "reused path hits invalid cell"
        return False, detail
    start, end = path[0], path[-1]
    detail["start"] = start
    detail["end"] = end
    if start not in starts:
        detail["reason"] = "start outside left support"
        return False, detail
    if end not in ends:
        detail["reason"] = "end outside right support"
        return False, detail
    legal_steps = set(steps)
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        if (r2 - r1, c2 - c1) not in legal_steps:
            detail["reason"] = "reused path uses an undeclared step"
            return False, detail
    detail["similarity_evaluations"] = len(path)
    detail["score"] = sum(float(sim[r][c]) - float(tau) for r, c in path)
    quality = _path_quality(path, sim, valid, tau, max_low_run, min_coverage)
    detail.update(quality)
    if not quality["ok"]:
        detail["reason"] = "quality"
        return False, detail
    detail["ok"] = True
    detail["reason"] = "ok"
    return True, detail


# ---------------------------------------------------------------------------
# Axis-wise fusion geometry
# ---------------------------------------------------------------------------
def fusion_edge(u, v, config):
    """Return ``(legal, reasons, measures)`` for the repaired geometry rule.

    The A->B residuals are checked against ``kappa_B`` and the B->A residuals
    against ``kappa_A``; a pooled maximum is never used.  A zero gap is legal
    only when both axes are zero.  Thresholds and affine slopes must be finite;
    invalid values make the edge unavailable instead of silently passing.
    """
    if not (_fragment_complete(u) and _fragment_complete(v)):
        return False, ["missing map"], {"max_map_error": None}

    required_cfg = ("G_A", "G_B", "kappa_A", "kappa_B", "alpha_min", "alpha_max",
                    "theta_dedup")
    if not isinstance(config, dict) or any(k not in config for k in required_cfg):
        return False, ["missing config"], {}

    kappa_a, kappa_b = config["kappa_A"], config["kappa_B"]
    g_a, g_b = config["G_A"], config["G_B"]
    a_min, a_max = config["alpha_min"], config["alpha_max"]
    theta = config["theta_dedup"]
    if not (_finite(kappa_a) and _finite(kappa_b) and float(kappa_a) > 0
            and float(kappa_b) > 0):
        return False, ["invalid threshold"], {}
    if not (_finite(g_a) and _finite(g_b) and float(g_a) >= 0 and float(g_b) >= 0):
        return False, ["invalid gap cap"], {}
    if not (_finite(a_min) and _finite(a_max) and 0 < float(a_min) <= float(a_max)):
        return False, ["invalid slope range"], {}
    if not (_finite(theta) and 0 <= float(theta) <= 1):
        return False, ["invalid dedup threshold"], {}

    alpha_u, beta_u = u["alpha"], u["beta"]
    alpha_v, beta_v = v["alpha"], v["beta"]
    if not all(_finite(x) for x in (alpha_u, beta_u, alpha_v, beta_v)):
        return False, ["missing map"], {}
    reasons = []
    if float(alpha_u) == 0.0 or float(alpha_v) == 0.0:
        reasons.append("degenerate map")
        return False, reasons, {"max_map_error": None}

    if u["a_e"] > v["a_s"] or u["b_e"] > v["b_s"]:
        reasons.append("order/overlap")
    gap_a = v["a_s"] - u["a_e"]
    gap_b = v["b_s"] - u["b_e"]
    if gap_a < 0 or gap_b < 0:
        reasons.append("negative gap")
    if gap_a > g_a or gap_b > g_b:
        reasons.append("gap cap")

    err_b = [abs(float(alpha_u) * a + float(beta_u) - b)
             for a, b in ((v["a_s"], v["b_s"]), (v["a_e"], v["b_e"]))]
    err_a = [abs((b - float(beta_v)) / float(alpha_v) - a)
             for b, a in ((u["b_s"], u["a_s"]), (u["b_e"], u["a_e"]))]
    if any(e > float(kappa_b) for e in err_b) or any(e > float(kappa_a) for e in err_a):
        reasons.append("boundary map")

    if (gap_a == 0) != (gap_b == 0):
        reasons.append("single-axis zero gap")
    elif gap_a > 0:
        slope = gap_b / gap_a
        if not (float(a_min) <= slope <= float(a_max)):
            reasons.append("connector slope")

    iou_a = _iou(u["a_s"], u["a_e"], v["a_s"], v["a_e"])
    iou_b = _iou(u["b_s"], u["b_e"], v["b_s"], v["b_e"])
    if iou_a >= float(theta) and iou_b < float(theta):
        reasons.append("same-A different-B")

    measures = {
        "gap_a": gap_a,
        "gap_b": gap_b,
        "iou_a": iou_a,
        "iou_b": iou_b,
        "map_errors_b": err_b,
        "map_errors_a": err_a,
        "max_map_error_b": max(err_b),
        "max_map_error_a": max(err_a),
        "max_map_error": max(max(err_b), max(err_a)),
        "normalized_map_error": max(
            max(err_b) / float(kappa_b), max(err_a) / float(kappa_a)
        ),
    }
    return (not reasons), reasons, measures


# ---------------------------------------------------------------------------
# Pairwise-only fusion over the original candidate set
# ---------------------------------------------------------------------------
def _valid_rebuild(rebuilt):
    if not isinstance(rebuilt, dict):
        return False
    keys = ("a_s", "a_e", "b_s", "b_e", "score")
    if any(k not in rebuilt for k in keys):
        return False
    if not all(_finite(rebuilt[k]) for k in keys):
        return False
    return rebuilt["a_s"] < rebuilt["a_e"] and rebuilt["b_s"] < rebuilt["b_e"]


def pairwise_merge(edges, verdicts, rebuild=None):
    """Process the original candidate pairs once, in the given order.

    ``edges`` is an ordered sequence of ``(u_id, v_id)`` pairs from the original
    set; no new edge is ever created.  A pair is eligible only when neither
    member has already been consumed.  An accepted merge consumes exactly its
    two members.  If the endpoint/score reconstruction fails, the action is
    rejected and both members stay available.  There is no set-level
    re-verification and no propagation to a third fragment.
    """
    consumed = set()
    merges = []
    actions = []
    for u_id, v_id in edges:
        action = {"edge": [u_id, v_id], "status": None, "reason": None}
        if u_id in consumed or v_id in consumed:
            action["status"] = "skipped_consumed"
            action["reason"] = "member already consumed"
            actions.append(action)
            continue
        verdict = verdicts.get((u_id, v_id), "reject")
        if verdict != "accept":
            action["status"] = verdict if verdict in ("reject", "uncertain") else "reject"
            action["reason"] = "visual verdict is not accept"
            actions.append(action)
            continue
        rebuilt = rebuild(u_id, v_id) if rebuild is not None else None
        if not _valid_rebuild(rebuilt):
            action["status"] = "rejected_rebuild"
            action["reason"] = "endpoint/score reconstruction failed"
            actions.append(action)
            continue
        merges.append({"members": [u_id, v_id], "endpoints": dict(rebuilt)})
        consumed.update((u_id, v_id))
        action["status"] = "merged"
        action["reason"] = "accepted pair"
        actions.append(action)
    return {
        "merges": merges,
        "actions": actions,
        "consumed": sorted(consumed),
    }


# ---------------------------------------------------------------------------
# Transfer-aware question and evidence bounds
# ---------------------------------------------------------------------------
def evidence_envelope(budget):
    """Return fixed-allocation and transfer-aware evidence bounds for ``B``."""
    b = int(budget)
    b_a = (2 * b) // 3
    b_f = b - b_a
    return {
        "B": b,
        "B_A": b_a,
        "B_F": b_f,
        "fixed_pairs": 3 * b_a + 5 * b_f,
        "max_pairs": 5 * b,
        "max_source_slots": 10 * b,
        "max_q_a": (2 * b) // 3,
    }


def budget_ledger(budget, q_a, q_f, pairs_per_a=3, pairs_per_f=5,
                  slots_per_a=6, slots_per_f=10):
    """Check actual logical questions against the transfer contract.

    ``q_A`` counts anchor questions and ``q_F`` fusion questions actually asked,
    including cache hits.  Unused anchor quota may move to fusion, never the
    reverse.  The paired-position bound is ``3 q_A + 5 q_F <= 5B`` and the
    source-frame-slot bound is ``6 q_A + 10 q_F <= 10B``.
    """
    b = int(budget)
    b_a = (2 * b) // 3
    b_f = b - b_a
    violations = []
    if int(q_a) != q_a or int(q_f) != q_f:
        violations.append("question counts must be integers")
    q_a, q_f = int(q_a), int(q_f)
    if q_a < 0 or q_f < 0:
        violations.append("negative question count")
    if q_a > b_a:
        violations.append("anchor quota exceeded")
    if q_a + q_f > b:
        violations.append("total budget exceeded")
    paired = pairs_per_a * q_a + pairs_per_f * q_f
    slots = slots_per_a * q_a + slots_per_f * q_f
    if paired > 5 * b:
        violations.append("paired-position bound exceeded")
    if slots > 10 * b:
        violations.append("source-slot bound exceeded")
    return {
        "valid": not violations,
        "violations": violations,
        "B": b,
        "B_A": b_a,
        "B_F": b_f,
        "q_A": q_a,
        "q_F": q_f,
        "transferred_to_fusion": max(0, b_a - q_a),
        "unused": max(0, b - q_a - q_f),
        "paired_positions": paired,
        "source_frame_slots": slots,
        "paired_bound": 5 * b,
        "slot_bound": 10 * b,
    }
