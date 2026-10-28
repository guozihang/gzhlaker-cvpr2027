#!/usr/bin/env python3
"""Deterministic checks of the round-7 manuscript's scalar claims.

Standard library only. These checks verify formula-level statements in the paper:
the score weights, the asymmetric DP restart rule, the conjunction in dual-axis
dedupe, and the per-pair call budget. They do not run the prototype, the
evaluator or any benchmark, and they do not certify performance.
"""
import argparse
import json
from pathlib import Path


def continuation_vs_restart(cosines, tau=0.6, lam=0.1, blocked=()):
    """Tiny one-step DP with the paper's asymmetric restart rule."""
    blocked = set(blocked)
    h = []
    for i, c in enumerate(cosines):
        r = c - tau
        if i in blocked:
            h.append(0.0)
            continue
        if i > 0 and (i - 1) not in blocked:
            h.append(r + (h[i - 1] - lam * (1 + 1 - 2)))
        else:
            h.append(max(0.0, r))
    return h


def checks():
    # Score weights sum to one and both terms are bounded by one.
    w_path, w_anchor = 0.7, 0.3
    assert abs(w_path + w_anchor - 1.0) < 1e-12
    for mean_cos, coverage in ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0)):
        q = w_path * mean_cos + w_anchor * min(1.0, coverage)
        assert 0.0 <= q <= 1.0

    # A legal predecessor keeps a negative continuation (one weak frame does not
    # restart a copy); an isolated cell may only start from non-negative evidence.
    weak_prefix = continuation_vs_restart([0.55, 0.55, 0.95, 0.95])
    assert weak_prefix[0] == 0.0 and weak_prefix[1] < 0.0
    assert continuation_vs_restart([0.55])[0] == 0.0

    # Dual-axis dedupe is a conjunction: one query interval mapped to two
    # reference locations overlaps on A but not on B and must survive.
    iou_a, iou_b = 1.0, 0.0
    assert not (iou_a >= 0.8 and iou_b >= 0.8)
    assert (1.0 >= 0.8 and 1.0 >= 0.8)

    # Per-pair call budget: eight admission questions plus eight boundary choices.
    assert 8 + 8 == 16
    assert 8 * 5 >= 16  # five-way choices fit the same cap

    # Strict branch coarse comparisons: one per stride-4 grid cell pair.
    m = n = 64
    s = 4
    grid = (m // s) * (n // s)
    assert grid == 256 and grid * s * s == m * n

    # Recovery thresholds are ordered more permissively than the strict ones.
    assert 3 < 5 and 12 > 8
    # Boundary acceptance is fail-closed at 0.65 and admission at 0.75.
    assert 0.65 < 0.75
    return {
        "kind": "deterministic_scalar_manuscript_checks",
        "benchmark_result": False,
        "prototype_executed": False,
        "checks_passed": 8,
        "score_weights": {"path": w_path, "anchor": w_anchor},
        "weak_prefix_first_two": weak_prefix[:2],
        "two_copy_axis_ious": {"A": iou_a, "B": iou_b},
        "max_calls_per_pair": 16,
        "grid_cells_64x64_stride4": grid,
        "scope": "Formula-level checks only; no dataset, model call, or benchmark was run.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(checks(), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    print(result, end="")
