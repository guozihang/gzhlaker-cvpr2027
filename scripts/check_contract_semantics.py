#!/usr/bin/env python3
"""Read-only probes of prototype semantics named in evidence/spec_code_contract.md.

This script imports the prototype but never writes to it and never reads dataset files.
It records what the code does on hand-built bands, next to the manuscript's proposed
rule, so the contract can cite an executable observation rather than a comment.

Usage:
    python3 scripts/check_contract_semantics.py --output evidence/contract_probes.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT.parent / "FastVCL"


def proposed_zero_floor(similarities, valid=None, reward=0.6, gap_penalty=0.1):
    """The manuscript's one-column recurrence: H=max(0,r,max_{H_prev>0}(H_prev+r))."""
    sim = np.asarray(similarities, dtype=float)
    if valid is None:
        valid = np.ones_like(sim, dtype=bool)
    valid = np.asarray(valid, dtype=bool)
    H = np.zeros_like(sim)
    for row in range(sim.size):
        if not valid[row]:
            continue
        own = float(sim[row]) - reward
        continuation = None
        if row > 0 and valid[row - 1] and H[row - 1] > 0.0:
            continuation = H[row - 1] + own - gap_penalty * 0.0  # (1,1): no gap
        H[row] = max(0.0, own, continuation if continuation is not None else 0.0)
    return H


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if str(PROTOTYPE) not in sys.path:
        sys.path.insert(0, str(PROTOTYPE))
    from fastvcl import tube as T  # noqa: E402
    from fastvcl.segments import AlignmentPath, extract_segments  # noqa: E402
    from fastvcl.types import Track  # noqa: E402

    def proto_dp(values, valid=None, blocked=None):
        sim = np.asarray(values, dtype=float).reshape(-1, 1)
        ok = np.ones_like(sim, dtype=bool) if valid is None else np.asarray(valid).reshape(-1, 1)
        block = np.zeros_like(ok) if blocked is None else np.asarray(blocked).reshape(-1, 1)
        b_index = np.arange(sim.shape[0], dtype=np.int64)[:, None]
        H, pr, pc, ps, best, reachable, reason = T.local_dp(
            sim, ok, b_index, reward_offset=0.6, gap_penalty=0.1, blocked=block)
        nodes = T.traceback_local(H, pr, pc, ok, blocked=block) if reachable else []
        return {
            "H": [round(float(v), 6) for v in H[:, 0]],
            "best": float(best),
            "reachable": bool(reachable),
            "path_rows": [int(r) for r, _c in nodes],
            "reason": reason,
        }

    weak_prefix = [0.0] * 10 + [0.95] * 5
    strong_weak_strong = [0.95, 0.10, 0.95]
    two_copies_gap = [0.95] * 5 + [0.0] * 7 + [0.95] * 5

    dp_probes = {
        "weak_prefix_then_copy": {
            "prototype": proto_dp(weak_prefix),
            "proposed_zero_floor": {
                "H": [round(float(v), 6) for v in proposed_zero_floor(weak_prefix)],
                "best": float(proposed_zero_floor(weak_prefix).max()),
            },
        },
        "strong_weak_strong": {
            "prototype": proto_dp(strong_weak_strong),
            "proposed_zero_floor": {
                "H": [round(float(v), 6) for v in proposed_zero_floor(strong_weak_strong)],
                "best": float(proposed_zero_floor(strong_weak_strong).max()),
            },
        },
        "two_copies_after_blocking_first": {
            "prototype": proto_dp(two_copies_gap, blocked=[1, 1, 1, 1, 1] + [0] * 12),
            "proposed_zero_floor": {
                "H": [round(float(v), 6)
                      for v in proposed_zero_floor(two_copies_gap,
                                                   valid=[False] * 5 + [True] * 12)],
                "note": "invalid rows stand in for blocked rows; the proposed rule has no blockers",
            },
        },
        "invalid_row": {
            "prototype": proto_dp([0.95, 0.95, 0.95], valid=[True, False, True]),
            "proposed_zero_floor": {
                "H": [round(float(v), 6)
                      for v in proposed_zero_floor([0.95, 0.95, 0.95],
                                                   valid=[True, False, True])],
            },
        },
    }

    # --- Tube A-range fallback: paper Eq. 13 uses only e_A. -------------------------
    track = Track(slope=1.0, intercept=0.0, anchors=(), start_a=10.0, end_a=20.0,
                  start_b=10.0, end_b=20.0)
    range_probes = {
        "a_range_none_w12_margin2": list(T.candidate_a_range(track, 100, 12, 2)),
        "a_range_none_w12_margin0": list(T.candidate_a_range(track, 100, 12, 0)),
        "a_range_explicit_extension16": list(T.candidate_a_range(
            track, 100, 12, 2, a_range=(max(0, int(np.floor(10)) - 16),
                                        min(100, int(np.ceil(20)) + 16)))),
        "np_rint_ties_to_even": [int(v) for v in np.rint([0.5, 1.5, 2.5, -0.5])],
    }

    # --- Segment margin and stored-entry support ------------------------------------
    path_scores = np.array([0.1, 0.95, 0.95, 0.95, 0.1, 0.1, 0.1])
    path_a = np.array([8, 9, 10, 11, 12, 13, 14], dtype=np.int64)
    path_b = path_a.copy()
    path = AlignmentPath(path_a, path_b, path_scores, anchor_a=(9, 10), anchor_spacing=4.0,
                         smooth_window=1, mode="local_dp", reachable=True,
                         node_valid=np.ones_like(path_scores, dtype=bool))

    def seg(margin, min_anchors, anchors=path.anchor_a, gap=2):
        found = extract_segments(
            path, min_local_cosine=0.6, min_duration=3, boundary_margin=margin,
            n_a=100, n_b=100, dedupe_iou=0.8, max_segments=64, min_duration_b=1,
            min_segment_anchors=min_anchors, max_low_quality_gap_a=gap,
            dedupe_iou_axis="min", anchors_a=anchors)
        return [[float(v) for v in (s.start_a, s.start_b, s.end_a, s.end_b, s.score)]
                for s in found]

    margin_probes = {
        "same_path_margin0": seg(0, 2),
        "same_path_margin2": seg(2, 2),
        "duplicate_A_anchor_12_twice_min_support2": seg(0, 2, anchors=(12, 12)),
        "distinct_A_anchor_12_once_min_support2": seg(0, 2, anchors=(12,)),
    }

    # --- Gap off-by-one at the segment layer ---------------------------------------
    gap_path = AlignmentPath(
        np.array([0, 1, 2, 5, 6, 7], dtype=np.int64),
        np.array([0, 1, 2, 5, 6, 7], dtype=np.int64),
        np.full(6, 0.95), anchor_a=(0, 3, 6), anchor_spacing=3.0, smooth_window=1,
        mode="local_dp", reachable=True, node_valid=np.ones(6, dtype=bool))
    gap_ok = extract_segments(gap_path, min_local_cosine=0.6, min_duration=3,
                              boundary_margin=0, n_a=100, n_b=100, dedupe_iou=0.8,
                              max_segments=64, min_duration_b=1, min_segment_anchors=0,
                              max_low_quality_gap_a=2, dedupe_iou_axis="min")
    gap_split = AlignmentPath(
        np.array([0, 1, 2, 6, 7, 8], dtype=np.int64),
        np.array([0, 1, 2, 6, 7, 8], dtype=np.int64),
        np.full(6, 0.95), anchor_a=(0, 3, 6), anchor_spacing=3.0, smooth_window=1,
        mode="local_dp", reachable=True, node_valid=np.ones(6, dtype=bool))
    gap_bad = extract_segments(gap_split, min_local_cosine=0.6, min_duration=3,
                               boundary_margin=0, n_a=100, n_b=100, dedupe_iou=0.8,
                               max_segments=64, min_duration_b=1, min_segment_anchors=0,
                               max_low_quality_gap_a=2, dedupe_iou_axis="min")
    gap_probes = {
        "intervening_two_kept": [[s.start_a, s.end_a] for s in gap_ok],
        "intervening_three_split": [[s.start_a, s.end_a] for s in gap_bad],
    }

    observations = {
        "kind": "source_semantics_probes",
        "prototype_executed": True,
        "benchmark_result": False,
        "dataset_read": False,
        "scope": ("Hand-built bands only; no VCSL feature, GT or prediction file. "
                  "These probes document current code behaviour, not method quality."),
        "prototype_head": "fdc3362b2418b316e16d6dfd68435e40c1b1afb8",
        "dp": dp_probes,
        "tube_a_range": range_probes,
        "segment_margin_and_support": margin_probes,
        "segment_gap": gap_probes,
        "checks": {
            "weak_prefix_prototype_unreachable": (
                dp_probes["weak_prefix_then_copy"]["prototype"]["reachable"] is False),
            "weak_prefix_proposed_reaches_1_75": (
                abs(dp_probes["weak_prefix_then_copy"]["proposed_zero_floor"]["best"] - 1.75)
                < 1e-12),
            "strong_weak_strong_prototype_second_cell_negative": (
                dp_probes["strong_weak_strong"]["prototype"]["H"][1] < 0),
            "strong_weak_strong_proposed_second_cell_restarts": (
                dp_probes["strong_weak_strong"]["proposed_zero_floor"]["H"][1] == 0.0),
            "margin2_widens_endpoints_in_path_rows": (
                margin_probes["same_path_margin0"] != margin_probes["same_path_margin2"]),
            "duplicate_anchor_satisfies_support2": (
                len(margin_probes["duplicate_A_anchor_12_twice_min_support2"]) == 1
                and len(margin_probes["distinct_A_anchor_12_once_min_support2"]) == 0),
            "gap_two_kept_gap_three_split": (
                gap_probes["intervening_two_kept"] == [[0, 8]]
                and gap_probes["intervening_three_split"] == [[0, 3], [6, 9]]),
            "a_range_e0_uses_halfwidth_plus_margin": (
                range_probes["a_range_none_w12_margin0"] == [0, 32]
                and range_probes["a_range_none_w12_margin2"] == [0, 34]),
        },
    }
    observations["all_documented_behaviours_observed"] = all(observations["checks"].values())
    text = json.dumps(observations, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    if not observations["all_documented_behaviours_observed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
