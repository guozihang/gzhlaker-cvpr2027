#!/usr/bin/env python3
"""Small deterministic checks of manuscript mathematics, not benchmark evaluation.

Standard library only. These scalar checks do not execute the NumPy prototype or
certify its evaluator, traceback, GPU backend, or real-data performance.
"""
import argparse
import json
from pathlib import Path


def diagonal_scores(similarities, restart, blocked=()):
    scores = []
    blocked = set(blocked)
    for i, similarity in enumerate(similarities):
        if i in blocked:
            scores.append(0.0)
            continue
        own = similarity - 0.6
        continuation = scores[i - 1] + own if i > 0 and i - 1 not in blocked else None
        if restart:
            scores.append(max(0.0, own, continuation if continuation is not None else 0.0))
        else:
            scores.append(continuation if continuation is not None else max(0.0, own))
    return scores


def checks():
    # For identical nonempty [0,0,10,20] boxes; epsilon is in both axis denominators.
    perfect = (10.0 / (10.0 + 1e-6)) * (20.0 / (20.0 + 1e-6))
    assert 0.999 < perfect < 1.0
    pairs = [(perfect, perfect), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
    denominators = [sum(row[k] != 1.0 for row in pairs) for k in (0, 1)]
    assert denominators == [2, 2]

    prefix = [0.0] * 10 + [0.95] * 5
    two_copies = [0.95] * 5 + [0.0] * 7 + [0.95] * 5
    z_prefix = diagonal_scores(prefix, True)
    c_prefix = diagonal_scores(prefix, False)
    z_second = diagonal_scores(two_copies, True, range(5))
    c_second = diagonal_scores(two_copies, False, range(5))
    assert abs(max(z_prefix) - 1.75) < 1e-12 and max(c_prefix) == 0.0
    assert abs(max(z_second) - 1.75) < 1e-12 and max(c_second) == 0.0

    single = len(range(0, 64, 2)) ** 2
    nested = sum(len(range(0, 64, s)) ** 2 for s in (2, 4, 8))
    assert single == 1024 and nested == 1344
    # Five original anchors can split into two rejected runs under a support minimum of 5.
    assert sum(len(run) >= 5 for run in ([0, 4], [100, 104, 108])) == 0
    # g_low counts intervening indices, not the difference between endpoint indices.
    assert 6 - 3 - 1 <= 2 and not (7 - 3 - 1 <= 2)
    # The same query copied into disjoint reference intervals has both min- and area-IoU 0.
    assert min(1.0, 0.0) == 0.0 and (10 * 0) / (100 + 100) == 0.0
    return {
        "kind": "deterministic_scalar_manuscript_checks",
        "benchmark_result": False,
        "prototype_executed": False,
        "checks_passed": 7,
        "perfect_nonempty_precision_recall": perfect,
        "four_case_macro_denominators": denominators,
        "weak_prefix_best": {"zero_floor": max(z_prefix), "continuation": max(c_prefix)},
        "second_copy_after_blocking_first_best": {
            "zero_floor": max(z_second), "continuation": max(c_second)},
        "one_direction_grid_products_64x64": {"stride2": single, "strides248": nested},
        "scope": "Formula-level diagnostics only; no dataset, model, or benchmark was run.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(checks(), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    print(result, end="")
