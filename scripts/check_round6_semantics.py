#!/usr/bin/env python3
"""Round-6 deterministic checks for the repaired connection/fusion semantics.

Standard library only.  The checker exercises ``round6_reference.py`` against
the counterexamples in ``evidence/round6_planning_snapshot.json``, an independent
brute-force path oracle, pairwise-merge cases and the transfer budget, then
checks that the manuscript states the same rules.  It does not execute the
FastVCL prototype, a dataset pair, a visual model or a GPU kernel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import round6_reference as R

ROOT = Path(__file__).resolve().parents[1]


def _read(*parts):
    return ROOT.joinpath(*parts).read_text()


def brute_force_best(sim, starts, ends, tau, steps):
    """Independent exhaustive walk search on a tiny grid.

    Returns the maximum positive score reaching an end cell, or ``None``.  It
    deliberately uses recursion rather than the reference DP so the accounting
    and score can be cross-checked.
    """
    rows, cols = len(sim), len(sim[0])
    ends = set(ends)
    best = None

    def walk(cell, score):
        nonlocal best
        r, c = cell
        if cell in ends and score > 0.0:
            best = score if best is None else max(best, score)
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if nr >= rows or nc >= cols:
                continue
            nxt = score + float(sim[nr][nc]) - float(tau)
            if nxt > 0.0:
                walk((nr, nc), nxt)

    for start in starts:
        own = float(sim[start[0]][start[1]]) - float(tau)
        if own > 0.0:
            walk(start, own)
    return best


def checks():
    results = []

    def record(name, passed, detail):
        results.append({"name": name, "passed": bool(passed), "detail": detail})

    # ------------------------------------------------------------------
    # Connection: the two planning counterexamples must now be rejected.
    # ------------------------------------------------------------------
    faint = [[0.1] * 5 for _ in range(5)]
    faint[3][3] = 0.9
    faint[4][4] = 0.9
    all_valid = [[True] * 5 for _ in range(5)]
    ok, det = R.connection_path(
        faint, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0
    )
    record(
        "conn_rejects_disconnected_suffix",
        not ok and det["reason"] == "no path",
        {"ok": ok, "reason": det["reason"], "dp_cells_visited": det["dp_cells_visited"]},
    )

    invalid_start = [row[:] for row in all_valid]
    invalid_start[0][0] = False
    ok, det = R.connection_path(
        faint, invalid_start, [(0, 0)], [(4, 4)], 0.6, 0, 1.0
    )
    record(
        "conn_rejects_invalid_start",
        not ok and det["reason"] == "empty left support",
        {"ok": ok, "reason": det["reason"]},
    )

    # Coverage is no longer valid_nodes/path_nodes: every traced node is valid,
    # but the B interval has a hole, so min(3/3, 3/4) = 0.75.
    sparse = [[0.1] * 4 for _ in range(3)]
    sparse[0][0] = sparse[1][2] = sparse[2][3] = 0.9
    sparse_valid = [[False] * 4 for _ in range(3)]
    for r, c in ((0, 0), (1, 2), (2, 3)):
        sparse_valid[r][c] = True
    ok, det = R.connection_path(
        sparse, sparse_valid, [(0, 0)], [(2, 3)], 0.6, 0, 1.0
    )
    record(
        "conn_rejects_gap_at_full_coverage",
        not ok
        and abs(det["coverage"] - 0.75) < 1e-12
        and det["coverage_a"] == 1.0
        and det["coverage_b"] == 0.75
        and det["skipped_b"] == 1,
        {"coverage": det["coverage"], "skipped_b": det.get("skipped_b")},
    )
    ok, det = R.connection_path(
        sparse, sparse_valid, [(0, 0)], [(2, 3)], 0.6, 0, 0.6
    )
    record(
        "conn_accepts_gap_when_threshold_allows",
        ok and det["path"] == [(0, 0), (1, 2), (2, 3)],
        {"ok": ok, "coverage": det.get("coverage"), "path": det.get("path")},
    )

    # A clean legal short connection is still accepted with its endpoints.
    diag = [[0.9 if r == c else 0.1 for c in range(5)] for r in range(5)]
    ok, det = R.connection_path(diag, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0)
    record(
        "conn_accepts_legal_short_connection",
        ok
        and det["path"][0] == (0, 0)
        and det["path"][-1] == (4, 4)
        and det["coverage"] == 1.0
        and det["path_nodes"] == 5,
        {"ok": ok, "path_nodes": det.get("path_nodes"), "coverage": det.get("coverage")},
    )

    # A single low-score node is legal only when the run cap allows it.
    one_low = [row[:] for row in diag]
    one_low[2][2] = 0.0
    ok_strict, det_strict = R.connection_path(
        one_low, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0
    )
    ok_lenient, det_lenient = R.connection_path(
        one_low, all_valid, [(0, 0)], [(4, 4)], 0.6, 1, 1.0
    )
    record(
        "conn_low_run_cap_is_effective",
        not ok_strict and det_strict["reason"] == "quality"
        and ok_lenient and det_lenient["worst_low_run"] == 1,
        {"strict": det_strict["reason"], "lenient_low_run": det_lenient.get("worst_low_run")},
    )

    ok, det = R.connection_path(
        diag, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 0.6,
        region=(0, 3, 0, 3), max_cells=4,
    )
    record(
        "conn_region_cap_rejects_without_dp",
        not ok and det["reason"] == "region cap"
        and det["region_cap_hit"] and det["dp_cells_visited"] == 0,
        {"reason": det["reason"], "area": det["region_area"]},
    )

    ok, det = R.connection_path(
        diag, all_valid, [], [(4, 4)], 0.6, 0, 0.6
    )
    record(
        "conn_empty_left_support",
        not ok and det["reason"] == "empty left support",
        det["reason"],
    )
    ok, det = R.connection_path(
        diag, all_valid, [(0, 0)], [], 0.6, 0, 0.6
    )
    record(
        "conn_empty_right_support",
        not ok and det["reason"] == "empty right support",
        det["reason"],
    )

    # Accounting must equal a hand-counted grid, and the DP score must match an
    # independent exhaustive walk oracle.
    small = [
        [0.9, 0.2, 0.1, 0.1],
        [0.2, 0.8, 0.9, 0.1],
        [0.1, 0.1, 0.7, 0.9],
        [0.1, 0.1, 0.2, 0.8],
    ]
    small_valid = [[True] * 4 for _ in range(4)]
    ok, det = R.connection_path(
        small, small_valid, [(0, 0), (0, 1)], [(3, 3)], 0.6, 2, 0.5
    )
    oracle = brute_force_best(small, [(0, 0), (0, 1)], [(3, 3)], 0.6, R.DEFAULT_STEPS)
    record(
        "conn_accounting_matches_enumeration",
        ok
        and det["dp_cells_visited"] == 16
        and det["similarity_evaluations"] == 16
        and det["predecessor_evaluations"] == 21
        and det["path_nodes"] == len(det["path"])
        and abs(det["score"] - oracle) < 1e-9,
        {
            "dp_cells_visited": det["dp_cells_visited"],
            "predecessor_evaluations": det["predecessor_evaluations"],
            "score": det["score"],
            "oracle": oracle,
        },
    )

    # Reused paths pass exactly the same tests and cost no DP visits.
    legal_path = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    ok, det = R.connection_path(
        diag, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0, reuse=legal_path
    )
    record(
        "conn_reuse_rechecks_and_costs_no_dp",
        ok and det["reused"] and det["dp_cells_visited"] == 0
        and det["predecessor_evaluations"] == 0,
        {"ok": ok, "reused": det["reused"], "dp": det["dp_cells_visited"]},
    )
    shifted = [(0, 1), (1, 2), (2, 3), (3, 4)]
    ok, det = R.connection_path(
        diag, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0, reuse=shifted
    )
    record(
        "conn_reuse_rejects_wrong_endpoints",
        not ok and det["reason"] == "start outside left support",
        det["reason"],
    )
    bad_step = [(0, 0), (1, 0), (2, 2), (3, 3), (4, 4)]
    ok, det = R.connection_path(
        diag, all_valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0, reuse=bad_step
    )
    record(
        "conn_reuse_rejects_undeclared_step",
        not ok and det["reason"] == "reused path uses an undeclared step",
        det["reason"],
    )

    # ------------------------------------------------------------------
    # Fusion geometry: per-axis thresholds, degenerate maps, zero gaps.
    # ------------------------------------------------------------------
    cfg = {"G_A": 48, "G_B": 48, "kappa_A": 1, "kappa_B": 4,
           "alpha_min": 0.5, "alpha_max": 2.0, "theta_dedup": 0.8}
    u = {"id": "u", "a_s": 0, "a_e": 10, "b_s": 0, "b_e": 10,
         "alpha": 1.0, "beta": 0.0}
    v_asym = {"id": "v", "a_s": 15, "a_e": 25, "b_s": 18, "b_e": 28,
              "alpha": 1.0, "beta": 3.0}
    legal, reasons, measures = R.fusion_edge(u, v_asym, cfg)
    record(
        "fusion_rejects_asymmetric_axis_tolerance",
        not legal and "boundary map" in reasons
        and measures["max_map_error_a"] == 3.0
        and measures["max_map_error_b"] == 3.0
        and measures["normalized_map_error"] == 3.0,
        {"reasons": reasons, "measures": measures},
    )

    v_ok = {"id": "v", "a_s": 15, "a_e": 25, "b_s": 15, "b_e": 25,
            "alpha": 1.0, "beta": 0.0}
    legal, reasons, measures = R.fusion_edge(u, v_ok, cfg)
    record(
        "fusion_accepts_small_symmetric_errors",
        legal and measures["max_map_error"] == 0.0,
        {"reasons": reasons, "measures": measures},
    )

    bad = dict(cfg, kappa_A=float("inf"))
    legal, reasons, _ = R.fusion_edge(u, v_ok, bad)
    record(
        "fusion_rejects_nonfinite_threshold",
        not legal and "invalid threshold" in reasons,
        reasons,
    )
    degenerate = dict(v_ok, alpha=0.0)
    legal, reasons, _ = R.fusion_edge(u, degenerate, cfg)
    record(
        "fusion_rejects_degenerate_slope",
        not legal and "degenerate map" in reasons,
        reasons,
    )
    zero_both = {"id": "w", "a_s": 10, "a_e": 20, "b_s": 10, "b_e": 20,
                 "alpha": 1.0, "beta": 0.0}
    legal, reasons, _ = R.fusion_edge(u, zero_both, cfg)
    record("fusion_accepts_zero_gap_both_axes", legal, reasons)
    zero_one = {"id": "w", "a_s": 10, "a_e": 20, "b_s": 11, "b_e": 21,
                "alpha": 1.0, "beta": 0.0}
    legal, reasons, _ = R.fusion_edge(u, zero_one, cfg)
    record(
        "fusion_rejects_single_axis_zero_gap",
        not legal and "single-axis zero gap" in reasons,
        reasons,
    )
    same_a = {"id": "w", "a_s": 0, "a_e": 10, "b_s": 20, "b_e": 30,
              "alpha": 1.0, "beta": 0.0}
    legal, reasons, _ = R.fusion_edge(u, same_a, cfg)
    record(
        "fusion_keeps_same_a_different_b_separate",
        not legal and "same-A different-B" in reasons,
        reasons,
    )
    reversed_pair = {"id": "w", "a_s": -5, "a_e": 1, "b_s": -5, "b_e": 1,
                     "alpha": 1.0, "beta": 0.0}
    legal, reasons, _ = R.fusion_edge(u, reversed_pair, cfg)
    record(
        "fusion_rejects_reversed_order",
        not legal and "order/overlap" in reasons,
        reasons,
    )

    # ------------------------------------------------------------------
    # Pairwise merge: one merge per chain, shared members, rebuild failure.
    # ------------------------------------------------------------------
    def rebuild(u_id, v_id):
        return {"a_s": 0, "a_e": 10, "b_s": 0, "b_e": 10, "score": 0.9}

    chain = [(1, 2), (2, 3)]
    out = R.pairwise_merge(chain, {(1, 2): "accept", (2, 3): "accept"}, rebuild)
    record(
        "merge_chain_only_one_pair",
        len(out["merges"]) == 1
        and out["merges"][0]["members"] == [1, 2]
        and out["actions"][1]["status"] == "skipped_consumed"
        and out["consumed"] == [1, 2],
        out,
    )

    shared = [(1, 2), (1, 3)]
    out = R.pairwise_merge(shared, {(1, 2): "accept", (1, 3): "accept"}, rebuild)
    record(
        "merge_shared_member_is_not_reused",
        len(out["merges"]) == 1
        and out["actions"][1]["status"] == "skipped_consumed",
        out,
    )

    def failing(u_id, v_id):
        return None if (u_id, v_id) == (1, 2) else {
            "a_s": 0, "a_e": 10, "b_s": 0, "b_e": 10, "score": 0.9
        }

    out = R.pairwise_merge(
        [(1, 2), (1, 3)], {(1, 2): "accept", (1, 3): "accept"}, failing
    )
    record(
        "merge_rebuild_failure_keeps_members",
        len(out["merges"]) == 1
        and out["merges"][0]["members"] == [1, 3]
        and out["actions"][0]["status"] == "rejected_rebuild",
        out,
    )

    out = R.pairwise_merge([(1, 2)], {(1, 2): "uncertain"}, rebuild)
    record(
        "merge_uncertain_keeps_fragments",
        not out["merges"] and out["actions"][0]["status"] == "uncertain"
        and out["consumed"] == [],
        out,
    )

    # ------------------------------------------------------------------
    # Transfer-aware budget.
    # ------------------------------------------------------------------
    env = R.evidence_envelope(12)
    record(
        "budget_envelope_transfer_case",
        env["fixed_pairs"] == 44
        and env["max_pairs"] == 60
        and env["max_source_slots"] == 120
        and env["max_q_a"] == 8,
        env,
    )
    ledger = R.budget_ledger(12, 0, 12)
    record(
        "budget_all_transferred_is_valid",
        ledger["valid"] and ledger["paired_positions"] == 60
        and ledger["source_frame_slots"] == 120
        and ledger["transferred_to_fusion"] == 8,
        ledger,
    )
    fixed = R.budget_ledger(12, 8, 4)
    record(
        "budget_fixed_allocation_is_special_case",
        fixed["valid"] and fixed["paired_positions"] == 44
        and fixed["source_frame_slots"] == 88,
        fixed,
    )
    over_a = R.budget_ledger(12, 9, 0)
    over_total = R.budget_ledger(12, 8, 5)
    record(
        "budget_rejects_quota_violations",
        not over_a["valid"]
        and "anchor quota exceeded" in over_a["violations"]
        and not over_total["valid"]
        and "total budget exceeded" in over_total["violations"],
        {"over_a": over_a["violations"], "over_total": over_total["violations"]},
    )

    # ------------------------------------------------------------------
    # Manuscript must state the repaired rules, not the old ones.
    # ------------------------------------------------------------------
    method = _read("sec", "3_method.tex")
    experiments = _read("sec", "4_experiments.tex")
    supplement = _read("supplementary.tex")

    record(
        "method_conn_is_anchored",
        "left support node" in method
        and "right support node" in method
        and "no other cell can start" in method
        and "zero restart" not in method
        and "adjacent to a support node" not in method,
        {"anchored": True},
    )
    record(
        "method_coverage_is_interval_based",
        "distinct A indices" in method
        and "skipped" in method
        and "min(d_A/s_A,d_B/s_B)" in method,
        {"coverage_interval": True},
    )
    record(
        "method_fusion_is_axis_wise",
        "each be at most $\\kappa_B$" in method
        and "each at most $\\kappa_A$" in method
        and "pooled maximum" not in method
        and "re-verified" not in method,
        {"axis_wise": True},
    )
    record(
        "method_budget_transfer_bound",
        "3q_A+5q_F" in method
        and "6q_A+10q_F" in method
        and "5B" in method
        and "10B" in method,
        {"budget_bound": True},
    )
    record(
        "supplement_matches_repaired_rules",
        "left support node" in supplement
        and "right support node" in supplement
        and "each at most" in supplement
        and "3q_A+5q_F" in supplement
        and "zero restart" not in supplement
        and "re-verified" not in supplement,
        {"supplement_repaired": True},
    )
    record(
        "experiments_do_not_call_conn_only_a_model_row",
        "No model question" in experiments or "no model call" in experiments,
        {"conn_only_accounted": True},
    )

    return {
        "kind": "deterministic_round6_semantics_and_notation_checks",
        "benchmark_result": False,
        "prototype_executed": False,
        "model_executed": False,
        "checks_passed": sum(1 for r in results if r["passed"]),
        "checks_total": len(results),
        "all_passed": all(r["passed"] for r in results),
        "results": results,
        "scope": (
            "Reference-rule and manuscript-text checks only; no VCSL pair, "
            "prototype, visual model, GPU or benchmark was run."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = checks()
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    raise SystemExit(0 if payload["all_passed"] else 1)
