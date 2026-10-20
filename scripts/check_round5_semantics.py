#!/usr/bin/env python3
"""Round-5 deterministic checks: manuscript semantics, not benchmark evaluation.

Standard library only. The checker exercises the reference definitions in
``scripts/round5_reference.py`` and asserts that the manuscript contains the
round-5 rules (strongest-competitor margin, K_nn/B naming, risk denominators,
shadow contract). It does not execute the prototype, a dataset pair or a model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import round5_reference as R

ROOT = Path(__file__).resolve().parents[1]


def _read(*parts):
    return (ROOT.joinpath(*parts)).read_text()


def checks():
    results = []

    def record(name, passed, detail):
        results.append({"name": name, "passed": bool(passed), "detail": detail})

    by_a = {
        0: {0: 0.95, 1: 0.80, 2: 0.75},
        1: {0: 0.80, 1: 0.70, 2: 0.60},
        2: {0: 0.75, 1: 0.60, 2: 0.50},
    }
    by_b = {j: {i: by_a[i][j] for i in by_a} for j in range(3)}
    m00 = R.strongest_competitor_margin((0, 0), by_a, by_b)
    m01 = R.strongest_competitor_margin((0, 1), by_a, by_b)
    old_second_rank_margin_01 = 0.80 - 0.75
    record(
        "margin_uses_strongest_competitor",
        abs(m00["margin"] - 0.15) < 1e-12
        and abs(m01["margin"] - (-0.15)) < 1e-12
        and abs(old_second_rank_margin_01 - 0.05) < 1e-12,
        {"top1": m00, "second": m01, "old_second_rank": old_second_rank_margin_01},
    )

    single = R.strongest_competitor_margin((0, 0), {0: {0: 0.9}}, {0: {0: 0.9}})
    record(
        "margin_missing_single_partner",
        single["margin"] is None and single["missing"] == ["A", "B"],
        single,
    )

    tied = R.strongest_competitor_margin(
        (0, 0),
        {0: {0: 0.9, 1: 0.9}, 1: {0: 0.9, 1: 0.1}},
        {0: {0: 0.9, 1: 0.9}, 1: {0: 0.9, 1: 0.1}},
    )
    record("margin_tie_is_zero", tied["margin"] == 0.0, tied)

    anchors = [(0, 0), (1, 0), (2, 0), (4, 4), (5, 4)]
    margins = {(0, 0): 0.20, (1, 0): 0.10, (2, 0): 0.05,
               (4, 4): 0.30, (5, 4): None}
    residuals = {(0, 0): 0.1, (1, 0): 0.2, (2, 0): 0.3,
                 (4, 4): 0.4, (5, 4): 0.2}
    selected, visits = R.selector_order(anchors, margins, residuals, 2, 3)
    record(
        "selector_round_robin_and_missing_neutral",
        len(selected) == 3
        and visits[(0, 0)] == 2
        and visits[(1, 1)] == 1
        and selected[0] == (2, 0),
        {"selected": selected, "visits": {str(k): v for k, v in visits.items()}},
    )

    config = {"G_A": 48, "G_B": 48, "kappa_A": 4, "kappa_B": 4,
              "alpha_min": 0.5, "alpha_max": 2.0, "theta_dedup": 0.8}
    u = {"id": "u", "a_s": 0, "a_e": 10, "b_s": 0, "b_e": 10,
         "alpha": 1.0, "beta": 0.0}
    v = {"id": "v", "a_s": 15, "a_e": 25, "b_s": 15, "b_e": 25,
         "alpha": 1.0, "beta": 0.0}
    legal, reasons, measures = R.fusion_edge(u, v, config)
    record("fusion_legal_disjoint_pair", legal and not reasons,
           {"reasons": reasons, "measures": measures})

    overlap = dict(v, a_s=5, a_e=15, b_s=5, b_e=15)
    _, reasons_overlap, _ = R.fusion_edge(u, overlap, config)
    record("fusion_rejects_order_overlap", "order/overlap" in reasons_overlap,
           reasons_overlap)

    far = dict(v, a_s=80, a_e=90, b_s=80, b_e=90)
    _, reasons_far, _ = R.fusion_edge(u, far, config)
    record("fusion_rejects_gap_cap", "gap cap" in reasons_far, reasons_far)

    shifted = dict(v, b_s=30, b_e=40)
    _, reasons_shift, _ = R.fusion_edge(u, shifted, config)
    record("fusion_rejects_boundary_map", "boundary map" in reasons_shift,
           reasons_shift)

    no_map = dict(v)
    no_map.pop("alpha")
    _, reasons_map, _ = R.fusion_edge(u, no_map, config)
    record("fusion_missing_map_unavailable", "missing map" in reasons_map,
           reasons_map)

    sim = [[0.9 if r == c else 0.1 for c in range(5)] for r in range(5)]
    valid = [[True] * 5 for _ in range(5)]
    ok, detail = R.connection_path(sim, valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0)
    record("conn_accepts_clean_path", ok, detail)

    broken = [row[:] for row in sim]
    broken[2][2] = 0.0
    ok_broken, detail_broken = R.connection_path(
        broken, valid, [(0, 0)], [(4, 4)], 0.6, 0, 1.0
    )
    record("conn_rejects_low_score_run", not ok_broken, detail_broken)

    ok_no_path, detail_no_path = R.connection_path(
        sim, valid, [(0, 0)], [(0, 4)], 0.6, 0, 1.0
    )
    record("conn_rejects_no_path", not ok_no_path, detail_no_path)

    bounds = {n: R.risk_upper(n) for n in (150, 299, 300)}
    record(
        "risk_bound_matches_planning_values",
        abs(bounds[150] - 0.019773438164508494) < 1e-12
        and abs(bounds[299] - 0.009969146792899286) < 1e-12
        and abs(bounds[300] - 0.00993608194445772) < 1e-12
        and R.risk_upper(298) > 0.01,
        {str(k): v for k, v in bounds.items()},
    )

    budget = R.evidence_frame_pairs(12)
    record(
        "budget_accounting",
        budget["B_A"] == 8 and budget["B_F"] == 4
        and budget["total_pairs"] == 44,
        budget,
    )

    method = _read("sec", "3_method.tex")
    abstract = _read("sec", "0_abstract.tex")
    experiments = _read("sec", "4_experiments.tex")
    supplement = _read("supplementary.tex")
    record(
        "manuscript_margin_rule",
        r"\setminus\{j\}" in method
        and r"\setminus\{i\}" in method
        and r"K_{\rm nn}" in method
        and r"K_A" not in method
        and r"K_F" not in method,
        {"method_has_competitor_sets": True},
    )
    record(
        "manuscript_notation_and_shadow",
        r"Top-$K_{\rm nn}$" in abstract
        and "independent random stream" in method
        and "shadow" in method.lower(),
        {"abstract_has_Knn": True},
    )
    record(
        "manuscript_risk_denominators",
        "queried true anchors" in experiments
        and "wrongly accepted merges" in experiments
        and r"all $\Anch_0$" in experiments,
        {"risk_denominators_present": True},
    )
    record(
        "supplement_contract_present",
        r"1-0.05^{1/n}" in supplement
        and "299" in supplement
        and "Conn" in supplement
        and r"K_{\rm nn}" in supplement,
        {"supplement_contract_present": True},
    )

    return {
        "kind": "deterministic_round5_semantics_and_notation_checks",
        "benchmark_result": False,
        "prototype_executed": False,
        "model_executed": False,
        "checks_passed": sum(1 for r in results if r["passed"]),
        "checks_total": len(results),
        "all_passed": all(r["passed"] for r in results),
        "results": results,
        "scope": (
            "Formula- and text-level checks only; no VCSL pair, prototype, model, "
            "GPU or benchmark was run."
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
