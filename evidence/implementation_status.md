# Implementation Status and Prototype Audit

Read-only audit date: 2026-10-17. Prototype HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`
(work tree clean for tracked files). Reference implementation HEAD
`4b57976da5ad1b38f999c96aba315e63a272acdf`. This file records what the code **does**, not
what the research plan hopes it does.

## 1. What is actually implemented

| Stage | Location | State | Evidence grade |
|---|---|---|---|
| Row normalisation + finite/zero-norm mask | `fastvcl/sparse.py` (`normalize_rows_with_mask`, `MIN_ROW_NORM`) | implemented | `SOURCE_VERIFIED` (code read) |
| Single/multi-stride + independent-phase sampling plan | `fastvcl/sparse.py` (`build_sampling_plan`) | implemented, **default off** | `IMPLEMENTED_UNVALIDATED` |
| Mutual Top-$K$ anchors, deterministic tie-break | `fastvcl/sparse.py` (`_topk_rows`, `_sparse_mnn_single_phase`) | implemented | `IMPLEMENTED_UNVALIDATED` |
| Cross-grid $(i,j)$ de-duplication | `fastvcl/sparse.py` (`merged` dict, `cross_scale_duplicates`) | implemented | `IMPLEMENTED_UNVALIDATED` |
| Anchor cap | `sparse.max_anchors_per_pair` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Per-pair deterministic seed | `fastvcl/trajectory.py::derive_seed` (SHA-256 of structured pair id) | implemented | `IMPLEMENTED_UNVALIDATED` |
| RANSAC line fitting, slope bounds, adaptive iterations | `fastvcl/trajectory.py::_ransac_once` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Dual-axis support/span re-validation after refit | `_emit_tracks` | implemented ($\min(|\pi_A|,|\pi_B|)\ge h_{\min}$) | `IMPLEMENTED_UNVALIDATED` |
| Gap splitting on A gap, B gap, backwards B step | `_split_runs` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Finite tube construction | `fastvcl/tube.py::compute_band_similarity`, `candidate_a_range` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Band similarity with validity mask and out-of-range handling | `_band_similarity` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Local DP, backtrace, bounded multi-path | `local_dp`, `traceback_local` | implemented, **semantics differ from the proposed spec** | `CONFLICT` |
| Segment extraction, trimming, min duration/anchors, score | `fastvcl/segments.py::extract_segments` | implemented | `IMPLEMENTED_UNVALIDATED` |
| Two-axis min-IoU de-duplication | `segments.py::dedupe_segments(axis="min")` | implemented, default | `IMPLEMENTED_UNVALIDATED` |
| Official-compatible evaluation | `fastvcl/evaluate.py` | implemented and compared with the reference `metric/eval.py` | `SOURCE_VERIFIED` |
| Repeat measurement, RSS, stage timing | `fastvcl/measure.py`, `profiler.py` | implemented; one historical unit bug fixed | `IMPLEMENTED_UNVALIDATED` |
| CUDA backend | `fastvcl/backends/cuda.py`, `kernels/tube_local_dp.cu` | code exists, **never executed on a GPU** | `MISSING` (hardware) |
| Frozen protocol / full test run | — | not produced | `MISSING` |

## 2. Configuration facts (must constrain the paper)

* `configs/isc_only.yaml`: `sparse.stride=4`, `sparse.topk=1`, `sparse.min_cosine=0.7`,
  `sparse.multiphase=false`, `strides=null`, `phase_pairs=null`. **The formal default is a
  single zero-phase grid with Top-1 mutual matching.** Multi-scale and independent phases
  are implemented but not default. Do not describe multi-scale as an established fact.
* `tube.align=local_dp` is the formal alignment path; `argmax` and banded DTW remain for
  historical comparison.
* `tube.dedupe_iou_axis=min` is the formal de-duplication rule; `joint` is historical.
* `profiling.enabled: true` in the shipped config. It only controls per-tile
  `tracemalloc` measurement, but formal timing must set it to `false` to remove probe
  overhead.
* `compute.backend=cpu`, `precision=strict` (float64 DP). No GPU verification.
* `sparse.multi_scale_with_phases_refused`: a plan with both multi-scale and non-default
  independent phases is rejected rather than silently scanning the product grid.

## 3. Artifact facts (no optimistic labels)

| Run | Verified numbers | Grade | Permitted use |
|---|---|---|---|
| `layer1_final_20261014/val` | selected 41,798; OK 5,873; EMPTY 2,202; ERROR 0; SKIPPED 33,723; `completion=incomplete` | `PILOT_ONLY` | engineering only; **never** a main-table row |
| `layer1_complete_20261014/val_full/val` | all 41,798 attempted: OK 28,708 + EMPTY 13,089 + ERROR 1; metrics computed over `n_pairs=41,797`; P 0.9208 / R 0.5078 / F1 0.6546; 1 ERROR excluded | `PILOT_ONLY` | best available near-complete diagnostic, but not a zero-failure frozen evaluation; do not paste into Table 1 |
| `layer1_complete_20261014/dev1000` | list 1,000 rows, OK 680 / EMPTY 320 / ERROR 0, but `metrics.json` has `n_pairs=200`, `n_input_rows=1000`, P 0.9260 / R 0.5722 / F1 0.7073 | `PILOT_ONLY` | the directory name and `COMPLETE` label are not a sample-size claim |
| `isc_mvp` | 24 synthetic pairs, F1 0.8931 | synthetic | **never** a real-data result |
| `review_aprime_20261013/real_val20` | 20 real val pairs, F1 0.7350 | `PILOT_ONLY` | development diagnostic |
| `layer1_roundB/real_val20{,_c,_localdp}` | 20 real pairs, F1 0.7399 / 0.7158 / 0.7158 | `PILOT_ONLY` | development diagnostic; the three variants are not a controlled ablation (different pipeline settings) |
| `layer1_roundB/sampling_strides{2,248}` and `sampling_phase_pairs00010203` | 20 real pairs, F1 0.7262 / 0.7428 / 0.7633 | `PILOT_ONLY` | unpaired 20-pair diagnostics; no equal-budget control, no significance claim |
| GPU | no kernel ever executed | `MISSING` | report `BLOCKED_GPU_RUNTIME`, never a speed number |

Timing records are **not** benchmark evidence: `measure.measure_config` previously
multiplied already-millisecond stage values by 1000, so historical stage decompositions are
unusable; the fix is recorded in `docs/IMPLEMENTATION_STATUS.md` but no new formal three-round
measurement exists. The near-complete val run has `profiling.enabled=false` in its snapshot
(`chunk_rows=256`, not the current 512), so even its timing is a development observation.

## 4. Verified conflicts and their consequences

### C1. Local DP restart semantics (`CONFLICT`)

*The plan's claim.* `fastvcl/tube.py::local_dp` does not apply a zero-floor when a legal
predecessor exists.

*What the code does.* It computes `total = own + H[pred] - gap` for every legal
predecessor, selects the best, and assigns `H[row,col]=best_total` unconditionally; a cell
with no predecessor is `max(0, own)`. The docstring defends this: weak frames are "weak
evidence, not absence of evidence", so a path may continue through a negative accumulated
score. It does set the back-pointer to `-1` when `H<0`, so a negative cell cannot *start* a
traceback, but the score itself is not floored.

*Consequence.* The two semantics differ in the long-negative-prefix and
two-copies-with-a-long-gap regimes; the unit test
`test_local_dp_restarts_after_a_negative_run` does **not** catch this, because in that test
the global maximum lies in the first (positive) block, so the method passes while the second
block has a negative score. The required four diagnostic scenarios are therefore only
partially covered:

| Required diagnostic | Existing test | Verdict |
|---|---|---|
| long negative prefix + true copy | none | **MISSING** |
| single weak frame inside a copy | `test_a_short_weak_stretch_is_still_bridged_by_the_segment_layer` | present, but at the segment layer, not the DP layer |
| same track, two copies, long gap | `test_segments_do_not_cross_a_long_low_quality_break` | present at segment layer |
| non-zero slope, band-centre column shift | `test_a_slope_one_hole_needs_the_absent_two_two_step` and the brute-force oracle | present |

*Reproduction (deterministic, CPU, no data files).* Run from the prototype root:

```bash
python - <<'EOF'
import numpy as np
from fastvcl import tube as T
sim = np.zeros((15, 1)); sim[10:15, 0] = 0.95
valid = np.ones_like(sim, dtype=bool); b = np.arange(15)[:, None]
H, pr, pc, ps, best, reach, reason = T.local_dp(
    sim, valid, b, reward_offset=0.6, gap_penalty=0.1)
print(best, reach, reason, T.traceback_local(H, pr, pc, valid))
EOF
```

Observed: `best=0.0`, `reachable=False`, no prediction. The zero-floor recurrence gives
$H=1.75$ on the same band. Mirror case: `sim[0:5]=0.95`, `sim[12:17]=0.95`, gap rows 5–11 at
0.0; the prototype's second-block scores are all negative and the returned path covers only
rows 0–4.

*Required action before any paper claim.* Implement the zero-floor variant (or explicitly
choose the current semantics) and rerun E3 on identical candidate tubes. The paper currently
presents the zero-floor form as `PROPOSED` and the prototype's behaviour as a compared
variant, which is the only honest reading.

### C2. Predecessor addressing cost (`CONFLICT` / performance)

`_step_predecessors` enumerates all `n_cols` for steps `(1,2)` and `(2,1)` and filters by
the actual B-index difference. Per cell this is $O(W_r)$, per multi-path tube
$O(P_rL_rW_r^2)$, whereas the direct-offset formula
$\delta_u=(j-\Delta j)-c_r(i-\Delta i)$ is $O(1)$ per step. The intended complexity is
$O(L_rW_r)$ per path. Any wall-clock claim must state which one was measured.

### C3. Coarse-stage dot-product count (`CONFLICT` / fairness)

The implementation runs a forward Top-$K$ scan and a backward Top-$K$ scan separately and
adds a tie re-scan pass; `actual_dot_products` counts both directions and extra passes. The
idealized $Q_{\mathrm{coarse}}=|I_A||I_B|$ is therefore about half the real work. The paper
must report `actual_dot_products` (or explicitly normalize), especially in E2's iso-budget
comparison.

### C4. `dev1000` label vs. sample size (`CONFLICT`)

`run_summary.json` says `n_selected=1000`, `completion=complete`; `metrics.json` has
`n_pairs=200`. The two are consistent only if 800 pairs were scorable-out, which the
integrity block contradicts (`n_scorable=1000`, `scorable_keys` length 200). Treat the metric
as computed over 200 pairs. No table may use the 1,000-row denominator.

### C5. Historical `val_full` one-error run (`CONFLICT`)

All 41,798 pairs were attempted and 41,797 were scored; the single `ERROR` is excluded from
`metrics.json`. This is the best existing coverage but not a zero-failure frozen benchmark.
The plan's snapshot describes it as "1 ERROR" and forbids calling it complete; that is
correct. It must be reported as a PILOT diagnostic if used at all.

### C6. Template and anonymity

The project is still the CVPR 2026 author kit (`cvpr.sty`, template text, demo BibTeX). The
paper and supplementary must contain no author name, repository URL, machine path or
username. `README_BUILD.md` must state that this is a **CVPR 2026 kit used as a fallback**,
not the official 2027 kit.

## 5. Reference-system facts (TransVCL)

* `run.py::load_features_list` splits each feature sequence into chunks of at most 1,200
  frames and forms all chunk pairs; outputs are shifted back by `i*1200`, `j*1200` and
  concatenated. It is therefore **false** to say TransVCL must allocate the full $M\times N$
  matrix for the whole video pair.
* The network runs self-/cross-attention, a similarity map, and a detection head per chunk
  pair; the real cost structure is chunk pairs × (attention + dense in-chunk correlation +
  head).
* Per-video-pair latency must be obtained by summing chunk-pair latencies, not by quoting a
  single chunk.
* The official evaluator `metric/eval.py` reproduces the VCSL macro metric: per-pair
  precision/recall are **products** of the two axis coverage ratios, and dataset means
  exclude entries whose value is exactly 1. `fastvcl/evaluate.py` is a faithful port.

## 6. What the paper may and may not say

May say: the pipeline is specified; the prototype implements most stages; the local-DP
semantics are a live design choice; no frozen benchmark exists; all empirical claims are
pending.

May not say: "state of the art", "X× faster", "extensive experiments show", "validated on
VCSL test", "GPU accelerated", "multi-scale improves recall", "the default uses multi-scale",
"the local DP is standard Smith-Waterman" (it is not, in the prototype).

## 7. Bibliographic premise corrections (2026-10-17)

Three premises of the execution plan were checked against primary sources and do not hold.
They are recorded here because the plan asked that conflicts be made explicit rather than
silently followed.

1. **VCSL title.** The CVPR 2022 paper is "A Large-Scale Comprehensive Dataset and
   Copy-Overlap Aware Evaluation Protocol for Segment-Level Video Copy Detection"
   (He et al.). There is no paper titled "VCSL: Video Copy Segmentation and Localization";
   VCSL is the dataset name. The metric is defined in §4.2 "New Metric" (projection-length
   product P/R, harmonic F1), not §3.2. The bib entry uses the CVF page numbers
   (21086–21095); IEEE/Crossref list 21054–21063, a documented discrepancy.
2. **SPD attribution.** VCSL does not present or name SPD; the string "Similarity Pattern
   Detection" does not occur in it. SPD is defined in Jiang et al., ACM MM 2021, and appears
   in VCSL §2.2 as related work and in §5.1 as one of five re-implemented baselines. The
   classification used by the paper (learned detector, not a zero-training method) is
   correct; only the citation/location was wrong.
3. **Component novelty.** The plan's warning is confirmed and strengthened: RANSAC line
   fitting on the time plane is standard in the 2022–2023 VSC matching tracks (SAM,
   arXiv:2305.15679; VSC 2023 report, CVIU 2024); TransVCL already uses dense
   mutual/dual-softmax matching; Tian et al. (IEEE MultiMedia 2013) combine cascaded
   multi-granularity search with a 2D Hough transform; Smith–Waterman/DTW alignment for
   copies is old. The paper therefore cites these as precedents and claims only the
   finite-tube formulation, the coverage/refinement separation, the restart analysis and the
   protocol. `NOVELTY_GAP` remains until E1 is run.

A literature search for training-free / zero-shot pairwise VCL in the 2023–2026 window found
no direct precedent, but this is a search result (`PILOT_ONLY` as evidence), not a proof of
absence. It must be re-run before submission and is not used as a performance claim.
