#!/usr/bin/env python3
"""Function-level parity check: FastVCL's evaluator port vs. the VCSL reference.

Read-only.  Imports both implementations, feeds them the same synthetic boxes, and
compares per-pair precision/recall, macro aggregation and the completeness/status
accounting.  This is **not** a benchmark run: no dataset, model or prediction file is
touched.  NumPy is required.

Usage:
    python3 scripts/check_evaluator_parity.py --output evidence/evaluator_parity.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT.parent / "FastVCL"
REFERENCE = ROOT.parent / "gzhlaker_transvcl"


def load_module(name: str, path: Path):
    if not path.exists():
        raise SystemExit(f"missing source: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def pred_boxes(rows):
    array = np.asarray(rows, dtype=float)
    if array.size == 0:
        return np.zeros((0, 4), dtype=float)
    if array.ndim != 2 or array.shape[1] < 4:
        raise ValueError(f"prediction rows must have >=4 columns, got {array.shape}")
    return array[:, :4]


def gt_boxes(rows):
    array = np.asarray(rows, dtype=float)
    if array.size == 0:
        return np.zeros((0, 4), dtype=float)
    return array.reshape(-1, 4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if str(PROTOTYPE) not in sys.path:
        sys.path.insert(0, str(PROTOTYPE))
    from fastvcl import evaluate as fast_eval  # noqa: E402

    ref = load_module("reference_metric_eval", REFERENCE / "metric" / "eval.py")

    cases = {
        "identical": ([[0, 0, 10, 20]], [[0, 0, 10, 20]]),
        "partial": ([[0, 0, 10, 20]], [[5, 5, 15, 30]]),
        "disjoint": ([[0, 0, 10, 20]], [[40, 40, 50, 60]]),
        "empty_pred": ([], [[0, 0, 10, 20]]),
        "empty_gt": ([[0, 0, 10, 20]], []),
        "both_empty": ([], []),
        "two_pred_one_gt": ([[0, 0, 5, 10], [5, 10, 10, 20]], [[0, 0, 10, 20]]),
        "overlapping_pred": ([[0, 0, 8, 20], [2, 0, 10, 20]], [[0, 0, 10, 20]]),
        "two_gt_one_pred": ([[0, 0, 10, 20]], [[0, 0, 5, 20], [5, 0, 10, 20]]),
        "touching": ([[0, 0, 5, 10], [5, 0, 10, 10]], [[0, 0, 10, 20]]),
        "float_coords": ([[0.5, 1.25, 9.75, 19.5]], [[0.5, 1.25, 9.75, 19.5]]),
    }
    rng = np.random.default_rng(20261018)
    random_cases = []
    for index in range(200):
        n_pred = int(rng.integers(0, 4))
        n_gt = int(rng.integers(0, 4))
        pred = []
        gt = []
        for _ in range(n_pred):
            a0 = float(rng.integers(0, 40))
            b0 = float(rng.integers(0, 40))
            pred.append([a0, b0, a0 + float(rng.integers(1, 20)),
                         b0 + float(rng.integers(1, 20)), float(rng.random())])
        for _ in range(n_gt):
            a0 = float(rng.integers(0, 40))
            b0 = float(rng.integers(0, 40))
            gt.append([a0, b0, a0 + float(rng.integers(1, 20)),
                       b0 + float(rng.integers(1, 20))])
        random_cases.append((pred, gt))
        cases[f"random_{index:03d}"] = (pred, gt)

    mismatches = []
    max_abs = 0.0
    for name, (pred, gt) in cases.items():
        expected = ref.precision_recall(pred_boxes(pred), gt_boxes(gt))
        got = fast_eval.precision_recall(pred_boxes(pred), gt_boxes(gt))
        for key in ("precision", "recall"):
            diff = abs(float(expected[key]) - float(got[key]))
            max_abs = max(max_abs, diff)
            if diff > 1e-12:
                mismatches.append({"case": name, "field": key,
                                   "reference": float(expected[key]),
                                   "port": float(got[key]), "abs_diff": diff})

    # Macro aggregation: reference returns (r, p); the port returns (r, p, meta).
    macro_cases = {
        "positive": {"precision": 0.5, "recall": 0.25},
        "perfect_sentinel": {"precision": 1.0, "recall": 1.0},
        "zero": {"precision": 0.0, "recall": 1.0},
    }
    ref_r, ref_p = ref.evaluate_overall(macro_cases)
    got_r, got_p, meta = fast_eval.evaluate_overall_safe(macro_cases)
    macro_ok = (abs(ref_r - got_r) < 1e-15 and abs(ref_p - got_p) < 1e-15
                and meta["n_recall_denominator"] == 1
                and meta["n_precision_denominator"] == 2)

    # End-to-end accounting on a tiny synthetic row set (no files, no dataset).
    rows = [
        {"name": "a", "gt": [[0, 0, 10, 20]], "pred": [[0, 0, 10, 20, 0.9]],
         "status": "OK"},
        {"name": "b", "gt": [[0, 0, 5, 5]], "pred": [], "status": "EMPTY"},
        {"name": "c", "gt": [], "pred": [[0, 0, 5, 5, 0.9]], "status": "OK"},
        {"name": "d", "gt": [], "pred": [], "status": "EMPTY"},
        {"name": "e", "gt": [[0, 0, 3, 3]], "pred": [], "status": "ERROR"},
    ]
    metrics = fast_eval.evaluate_pairs(rows, conf=0.0, filter_mode="legacy",
                                       integer_truncation=True,
                                       require_complete=False,
                                       keep_per_pair=True)
    end_to_end_ok = (
        metrics["n_pairs"] == 4
        and metrics["n_excluded_failed"] == 1
        and metrics["denominators"]["n_precision_denominator"] == 2
        and metrics["denominators"]["n_recall_denominator"] == 2
        and metrics["denominators"]["excluded_precision_eq_1"] == 2
        and metrics["denominators"]["excluded_recall_eq_1"] == 2
        and metrics["per_pair"]["a"]["precision"] < 1.0
        and metrics["per_pair"]["a"]["recall"] < 1.0
    )
    # Perfect nonempty overlap is retained: the sentinel test is exact equality.
    perfect_retained = 0.999 < metrics["per_pair"]["a"]["precision"] < 1.0
    # The wrapper F1 uses the reference's +1e-6 zero guard.
    f1_zero = 2 * 0.0 * 0.0 / (0.0 + 0.0 + 1e-6)

    result = {
        "kind": "evaluator_function_parity",
        "benchmark_result": False,
        "dataset_executed": False,
        "prototype_executed": True,
        "scope": ("Synthetic evaluator-function parity only. No VCSL features, model "
                  "or benchmark prediction file was read."),
        "prototype_head": "fdc3362b2418b316e16d6dfd68435e40c1b1afb8",
        "cases": len(cases),
        "random_cases": len(random_cases),
        "max_abs_per_pair_diff": max_abs,
        "mismatches": mismatches,
        "macro_ok": macro_ok,
        "macro_reference": {"recall": ref_r, "precision": ref_p},
        "macro_port": {"recall": got_r, "precision": got_p, "meta": meta},
        "end_to_end_accounting_ok": end_to_end_ok,
        "end_to_end_metrics": {
            "n_pairs": metrics["n_pairs"],
            "n_excluded_failed": metrics["n_excluded_failed"],
            "denominators": metrics["denominators"],
            "pair_a_precision": metrics["per_pair"]["a"]["precision"],
            "pair_a_recall": metrics["per_pair"]["a"]["recall"],
        },
        "perfect_nonempty_retained": bool(perfect_retained),
        "f1_zero_guard_value": f1_zero,
        "notes": [
            "conf=0 in legacy mode applies neither score filtering nor integer truncation.",
            "ERROR/SKIPPED rows are excluded from the metric, not counted as empty.",
            "The reference malformed-prediction except-branch is intentionally not ported; "
            "the port refuses malformed input instead of converting it to [].",
        ],
    }
    failures = [bool(mismatches), not macro_ok, not end_to_end_ok, not perfect_retained]
    result["passed"] = not any(failures)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
