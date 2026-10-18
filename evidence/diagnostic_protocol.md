# Diagnostic protocol (proposed, not frozen)

Date: 2026-10-18. Status: **PROPOSED / NOT IMPLEMENTED**. This document defines the custom
diagnostics used by H1–H3 and E1–E5. It is separate from the official VCSL metric: the
official numbers always use the original GT, the original evaluator and the original
prediction rows. No diagnostic filter may change an official score.

The definitions below are the ones a run must implement and record. A field marked `OPEN`
is not yet decided and cannot be filled by guessing after seeing results.

## 1. Unit and coordinate conventions

- Coordinates are **feature indices**, half-open `[start, end)` on both axes; no seconds and
  no source-frame numbers without a verified timestamp map.
- A pair has feature lengths `M, N`; valid indices are `0 <= i < M`, `0 <= j < N`.
- `length_a = a_e - a_s`, `length_b = b_e - b_s`; both must be positive.
- Predictions are the rows written by the method, before any evaluator-side confidence
  filter. The evaluator mode (`legacy`, `conf`, integer truncation) is recorded separately;
  diagnostics must state which rows they used.
- Every diagnostic reports its own denominator. Official and diagnostic denominators are
  never mixed.

## 2. GT validity and filtering

### 2.1 Official GT

The original GT JSON is loaded and scored unchanged, including annotations that are
degenerate or out of range. These anomalies are counted and disclosed (supplement §Dataset
composition); they are not silently repaired.

### 2.2 Diagnostic-valid GT

For custom diagnostics only, define a GT box as **diagnostic-valid** when all hold:

1. all four coordinates are finite;
2. `0 <= a_s < a_e <= M` and `0 <= b_s < b_e <= N`;
3. `length_a > 0` and `length_b > 0`.

Count and report:

- `n_gt_total`: all GT boxes for the pair;
- `n_gt_valid`: boxes passing 2.2;
- `n_gt_excluded`: `n_gt_total - n_gt_valid`;
- `excluded_reasons`: counts by `degenerate`, `out_of_range`, `nonfinite`, `reversed`.

Out-of-range boxes are **excluded**, not clipped; clipping would invent a different
interval. Candidate recall and boundary MAE use `n_gt_valid` as their denominator. Official
P/R/F1 still use `n_gt_total` through the official evaluator.

## 3. Candidate envelope and recall (H1)

### 3.1 Envelope

For a tube \(T_r\), let \(V_r\) be the set of cells with `valid=True` (in-range and both rows
valid). The diagnostic envelope is the axis-aligned hull

\[
\operatorname{env}(T_r)=
[\min_{c\in V_r} i(c),\ \max_{c\in V_r} i(c)+1)
\times
[\min_{c\in V_r} j(c),\ \max_{c\in V_r} j(c)+1).
\]

If \(V_r=\emptyset\), the tube has **no envelope** and is counted as `empty_tube`; it cannot
cover any GT. The envelope is a proposal-box diagnostic. It does **not** prove that a legal
DP path exists inside the tube, that every frame pair in the box is valid, or that the tube
covers the true frame correspondence. The paper must say this explicitly.

The candidate set for recall is the union of envelopes over all fitted tracks after the
frozen RANSAC/split stage. Segments produced by the refinement stage are a *different*
candidate set and must be reported separately if used (`candidate_stage` field:
`tube` or `segment`).

### 3.2 Matching and recall

A diagnostic-valid GT box \(G\) is covered by envelope \(E\) when

\[
\min(\operatorname{IoU}_A(G_A,E_A),\operatorname{IoU}_B(G_B,E_B))\ge 0.5 .
\]

Candidate recall is

\[
\mathrm{CandR}=\frac{\#\{G:\exists E,\ \min(\mathrm{IoU}_A,\mathrm{IoU}_B)\ge0.5\}}
{\#\{G:\text{diagnostic-valid}\}}.
\]

Report:

- `n_gt_valid`, `n_gt_covered`, `cand_recall`;
- `n_envelopes`, `n_empty_tubes`, `n_candidates` (anchors/tracks as applicable);
- recall by length bucket, using `min(length_a, length_b)`:
  `<15`, `[15,60)`, `>=60` feature indices;
- per-pair denominator and the aggregate micro denominator (sum covered / sum valid);
- for negative pairs, whether any envelope exists (a proposal-level false-alarm count, not
  the official FAR).

If a one-to-one diagnostic is needed, use maximum-cardinality bipartite matching between
envelopes and GT at the same threshold, then maximize total min-IoU, then deterministic
IDs. Label it `envelope_precision_diag`; never call it official precision.

### 3.3 What this does not measure

Candidate recall is not path recall, not segment recall and not per-frame correspondence
recall. A GT box can intersect an envelope while the tube contains no legal monotone path
through the copy. Conversely, a tube can contain a copy whose envelope is large and
uninformative. H1 is supported only if the frozen candidate stage retains coverage at a
declared executed budget; the envelope number alone cannot establish detection quality.

## 4. Boundary diagnostics (H2)

### 4.1 Matching

Match predictions \(P\) to diagnostic-valid GT \(G\) at

\[
\min(\operatorname{IoU}_A(P,G),\operatorname{IoU}_B(P,G))\ge0.5 .
\]

Build all eligible edges with weight \(w=\min(\mathrm{IoU}_A,\mathrm{IoU}_B)\). Use a
maximum-cardinality one-to-one matching; among maximum-cardinality matchings, maximize the
sum of weights; break remaining ties by the sorted `(prediction id, GT id)` pair. The
implementation must state the algorithm (e.g. Hungarian or augmenting-path) and the exact
tie-break. A greedy pass is not sufficient unless it is proved to return the same
cardinality/weight.

### 4.2 MAE and reporting

For each matched pair, compute the four absolute endpoint errors in feature-index units:

\[
|a_s^P-a_s^G|,\ |a_e^P-a_e^G|,\ |b_s^P-b_s^G|,\ |b_e^P-b_e^G|.
\]

Report the mean over all four values and all matched pairs (`bnd_mae`), plus:

- `n_pred`, `n_matched`, `n_gt_valid`, `match_recall = n_matched / n_gt_valid`;
- `n_unmatched_pred`, `n_unmatched_gt`;
- MAE by length bucket;
- the **common GT cohort**: GT boxes matched by both methods being compared. Compute
  paired differences only on this cohort, and report its size. A lower MAE on a smaller or
  easier cohort is not evidence of better boundaries;
- the matching threshold and IoU definition (per-axis union denominators).

### 4.3 Why the common cohort is mandatory

A refinement that drops difficult segments can lower MAE while losing recall. The paper must
report matched count, recall and the common cohort together. If the common cohort is too
small to support a comparison, report that fact and do not claim a boundary gain.

## 5. Execution and cost diagnostics

These are diagnostics of work actually performed, not theoretical bounds. They are logged
per pair and aggregated with explicit units.

| Field | Definition |
|---|---|
| `grid_pairs` | \(\sum_g |I_A^g|\,|I_B^g|\) for the executed plans (one direction) |
| `executed_dots` | Actual cosine dot products: forward scan + backward scan + boundary-tie rescans; use the prototype's `actual_dot_products` or an equivalent counter |
| `tie_rescan_pairs` | Pairs re-scored only to resolve a boundary tie |
| `band_dots` | Actual cosine evaluations inside bands, counted once per tube (multi-path blocking reuses them) |
| `band_cells` | \(\sum_r L_r W_r\), the band area, including invalid cells |
| `unique_covered_cells` | Union of valid band cells across tubes, deduplicated by original `(i,j)` |
| `tube_overlap_factor` | `sum_r L_r W_r / max(1, |union of band cells|)` |
| `dp_cells_visited` | Usable cells for which `H` was computed, including repeated attempts after blocking |
| `dp_unique_cells` | Union of cells that ever received a positive/zero `H` in any attempt |
| `n_tracks`, `n_tubes`, `n_paths`, `n_segments` | Counts after the frozen stage; state whether before/after caps |
| `n_blocked_cells` | Cells blocked by earlier paths |
| `n_empty_tubes` | Tubes with no valid cells |
| `n_attempts` | DP attempts, including attempts that yielded no segment |

Rules:

- Do not report `grid_pairs` as executed dots; the search runs both directions and may rescan
  ties.
- Do not report `band_cells` as cosine evaluations; invalid cells are not dotted, and
  multi-path attempts reuse the band.
- Do not report the DP bound as the whole-pipeline cost; normalization, coarse search,
  RANSAC, band similarity, traceback and post-processing are separate.
- Record counters from the actual run, not from a configuration or an estimate. A counter
  that is unavailable is `null`, never zero.

## 6. Budget matching and controlled comparisons

### 6.1 E2 (sampling)

- Compare executed coarse dots, not nominal stride. Include both directions and tie rescans.
- Declare an aggregate tolerance before results (recommended: 5% of aggregate executed
  work) and report per-pair mismatch as well.
- If no discrete configuration matches, plot realized budgets and state that the comparison
  is **not** iso-budget. Never add useless computations to pad a budget.
- Nested zero-phase grids add no new coordinates beyond the finest grid but add work and can
  change Top-\(K\) competition. Report the actual plan list, phases and per-grid counts.
- Multi-scale plus non-default independent phases is refused by the current configuration;
  do not present a combined grid that was never run.

### 6.2 E3 (recurrence/refinement)

- Reuse identical serialized tracks/tubes; record their SHA-256 and the serializer version.
- Compare only the alignment policy (support box, band DTW, continuation, zero-floor) with
  common post-processing.
- Report matches gained/lost, common-cohort metrics and the four denominators, not only F1.
- Oracle GT tubes are a diagnostic ceiling, never a deployable candidate set.

### 6.3 E4 (mechanism factors)

- One factor per row. Width and A extension are separate sweeps.
- For the \(e_A=0\) row, pass an explicit A range; the current code otherwise pads by
  `half_width + margin` and changes two factors (contract C4).
- Margin is counted in matched path rows in the prototype; state which unit a row uses and
  never call it a feature-index margin.
- The STB baseline and the core must share the same recurrence, margin, support and scoring
  rule; E4 changes only the named factor.
- De-duplication variants must be compared on cases where the rules actually differ; an
  A-same/B-different copy is kept by both min-IoU and area-IoU and does not distinguish them.

### 6.4 E5 (implementation)

- Require semantic parity (exact predictions) between scan and direct-offset before timing;
  a speed number with different predictions is not an indexing comparison.
- Full-matrix DP changes the search domain; report it separately.
- CPU/GPU rows identify hardware; only matched hardware supports an algorithmic speed claim.
- Do not use a post-hoc confidence sweep as an acceleration curve.

## 7. Threshold selection and evaluation modes

1. Freeze the structural configuration on development data; do not use test.
2. For each method independently, declare a threshold grid, objective and tie rule; select
   on validation. Record the selected value and label validation as selection-biased.
3. Freeze the value before test. Run test once for the predeclared configuration set.
4. Record the evaluator mode:
   - `legacy`: `conf=0` means no score filtering **and** no integer cast; `conf>0` filters
     `score > conf` and casts coordinates to int in the reference branch;
   - `strict`: always filters `score > conf` (a score exactly equal to `conf` is dropped)
     and casts only when filtering;
   - `integer_truncation=false` keeps float endpoints, required for seconds-based analyses.
5. Report `n_expected`, `n_processed`, `|D_P|`, `|D_R|`, `n_error`, `n_skipped`,
   `n_negative_pairs`, `negative_pair_far` separately. `metrics.json`'s `n_pairs` alone is
   not the completion accounting.
6. Negative FAR is test-only in this dataset. Validation is positive-only; it cannot select a
   false-alarm target. A negative development set needs independent provenance and a
   documented split; otherwise FAR is held out.

## 8. Video identity, dependence and uncertainty

The pair list may contain the same video in several pairs and across splits. Before any
uncertainty statement:

1. Build a video-identity table from the pair CSVs (query and reference IDs separately).
2. Count videos shared between development, validation and test; report the overlap counts
   and the number of pairs affected.
3. Choose the sampling unit before looking at results: pair-level only if the video overlap
   is judged negligible; otherwise a video-cluster or two-way cluster unit. State the choice
   and its limitations.
4. For paired comparisons, use the same pairs and a paired bootstrap or a paired test that
   respects the chosen unit. Five RANSAC seeds measure fitting variability only; they are not
   data uncertainty and are not a significance test.
5. If the dependence structure cannot be justified, report descriptive variation and
   explicitly withhold a significance claim.

## 9. Proposed `frozen_protocol` schema

A run is frozen only when every required field is non-null and the file's `frozen` flag is
`true`. Missing fields stay `null` or `"OPEN"`; no placeholder is promoted to a value.

```json
{
  "frozen": false,
  "protocol_id": null,
  "code": {"commit": null, "dirty_diff_sha256": null, "entry_point": null},
  "data": {
    "dataset": "VCSL",
    "split": null,
    "pair_csv_sha256": null,
    "label_json_sha256": null,
    "feature_content_digest": null,
    "feature_count": null,
    "feature_root": null
  },
  "evaluator": {"path": null, "sha256": null, "mode": null,
                 "integer_truncation": null, "coordinate_unit": "feature_index"},
  "method": {"name": null, "config_sha256": null, "seed": null,
             "recurrence": null, "margin": null, "support_rule": null,
             "dedupe": null, "cap": null},
  "threshold": {"selected_on": "validation", "value": null,
                 "grid": null, "objective": null, "tie_rule": null},
  "budget": {"executed_dots": null, "tolerance_fraction": null,
              "matching_rule": null},
  "diagnostics": {"candidate_iou": 0.5, "boundary_iou": 0.5,
                   "length_buckets": [15, 60], "common_cohort": true},
  "hardware": {"cpu": null, "gpu": null, "threads": null,
                "precision": null, "profiling": false},
  "timing_scope": {"start": null, "end": null, "included": null, "excluded": null},
  "uncertainty": {"unit": null, "method": null, "shared_video_overlap": null},
  "run_ids": [],
  "notes": []
}
```

The schema is a contract for a future freeze, not evidence that a freeze happened. The
current repository has **no** frozen protocol; every result cell remains pending.

## 10. Implementation status and acceptance

| Component | Status | Evidence / next step |
|---|---|---|
| Official evaluator port | `DONE` at function level | `evidence/evaluator_parity.json`: 211 cases, zero mismatch; macro/denominators and `conf=0` branch checked |
| Full evaluator file/run parity | `MISSING` | run the reference and the port on the same prediction/GT files, compare per-pair and aggregate |
| Candidate envelope | `MISSING` | implement hull of valid tube cells; unit test on empty/invalid/overlapping tubes |
| Candidate recall and length buckets | `MISSING` | implement §3; freeze IoU threshold and exclusions |
| Boundary matching + MAE + common cohort | `MISSING` | implement §4 with deterministic maximum-cardinality/weight matching |
| Execution counters | `PARTIAL` | prototype has `actual_dot_products`, band pairs, DP stats; add unique covered cells and per-attempt visits |
| `frozen_protocol` writer | `MISSING` | JSON schema above; refuse `frozen=true` with nulls |
| Video-overlap audit | `MISSING` | CSV identity table, cross-split counts, unit decision |
| Diagnostic tests | `MISSING` | A1–A12 in the contract; each with a deterministic fixture |

Acceptance for a diagnostic run: every reported number cites the script/commit, the input
hashes, the denominator and the threshold; the same definition is used for all methods; the
official table is produced separately and unchanged.

## 11. Bottom line

The diagnostics are specified here so that a future run cannot choose a flattering
denominator after seeing results. They are not implemented yet. The only completed check is
the function-level evaluator parity. H1/H2 remain untested, and no diagnostic number may be
reported as a benchmark result.
