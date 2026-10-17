# Experiment Plan: Hypotheses, Falsification, and Priority

This is an internal plan. It contains **expected observations**, not measured results.
Every expectation below is falsifiable and none may be quoted as a finding.

## 1. Hypothesis-to-experiment map

| Hyp. | Statement | Primary experiment | Sufficient evidence to support | Observation that falsifies or narrows it |
|---|---|---|---|---|
| **H1** Candidate coverage | Sparse matching + track fitting still covers true copies at high recall while substantially reducing dot products | E2 (and the coverage column of E1) | Candidate recall vs. `actual_dot_products` curve dominates the baseline at several iso-budget points; short-segment bucket not disproportionately lost | Coarse stage misses many true copies, especially short ones; refinement cannot recover what no tube covers |
| **H2** Boundary recovery | Zero-floored local DP inside finite tubes improves boundary accuracy beyond the coarse support box, at modest cost | E3 + E4 | Same candidate tubes: F1 and boundary MAE improve significantly; gain is not explained only by a wider band or more cells | No significant F1/boundary gain, or the gain requires near-full-matrix work |
| **H3** Net system benefit | Reduced fine-alignment domain converts into measured wall-clock and memory benefit | E5 + Table 2 | On the same machine/protocol, `T_localize` and peak memory are lower at comparable F1 | Python loops, predecessor scans or transfers dominate; fastest method is a vectorised full-matrix baseline |

## 2. Experiment matrix (E0–E5)

### E0 — External baselines under one frozen protocol

* Comparators: HV, TN, DP, DTW (zero-training, classical), SPD and TransVCL (learned
  localizers, loaded pretrained, **no retraining in this work**), and optionally RTR /
  FiGVCL **only if** their features and protocol can be aligned to the same ISC features.
* Constants: same ISC features, same val/test CSVs, same GT, same evaluator, per-method val
  threshold, single test run.
* Report: $\bar P/\bar R/\mathrm{F1}$ (val, test), test negative FAR, completion rate,
  `T_localize` Mean/P50/P95, peak memory.
* Table 1: literature-reported values are separated from values measured here. Different
  features/protocols are never mixed into a single ranking.

### E1 — Novelty gate against the Simple Sparse-to-Band baseline

Exact baseline: one grid (fixed stride $s$) → mutual Top-$K$ → standard RANSAC straight-line
fit → **fixed half-width** band → standard Smith-Waterman (zero floor) local alignment →
threshold + dedupe. No dual-axis gap splitting, no multi-path, no min-IoU-specific
post-processing beyond the same threshold sweep.

* Match the coarse dot-product budget, the hardware backend and the candidate budget.
* Add exactly one proposed mechanism at a time; the headline comparison adds the whole set.
* **Gate:** if FastVCL does not beat this baseline on F1, short-segment recall or boundary
  MAE at equal budget, mark `NOVELTY_GAP` and reframe. Do not add modules to hide it.
* **Precedent note:** the baseline is deliberately close to published challenge recipes that
  fit a temporal line with RANSAC after a learned (SAM) or heuristic (VSC track) match
  proposal. The comparison is therefore against a realistic strong recipe, not a straw man.

### E2 — Sampling and phase (H1)

Variants: single stride 4; single stride 2; nested multi-scale {2,4,8} with and without
coordinate de-duplication; independent phase pairs; equal-budget single fine grid.
Sampling-interval efficiency has been studied before (Chen & Satoh, MMM 2025: much longer
intervals than 1 fps can preserve or slightly improve accuracy with large speed-ups). That
work motivates the curve but does not measure candidate coverage at an iso-budget operating
point, which is what E2 adds.
Record `actual_dot_products`, $|\mathcal A|$, `cross_scale_duplicates`, candidate recall and
latency by segment-length bucket ($<15$, $[15,60)$, $\ge60$ frames).

Decision rules:
* If {2,4,8} ≈ stride 2 at equal budget → the multi-scale story is dead; report it as a
  negative result and remove any claim of a multi-scale contribution.
* If de-duplication materially changes RANSAC inlier counts → the earlier naive merge was
  inflating support; report the corrected number only.
* If independent phases add coverage only at $s^2\times$ cost → report the trade-off curve,
  not a single point.

### E3 — Tube refinement (H2)

Variants on **identical candidate tracks**: (a) coarse support box; (b) global DTW over the
tube without zero floor; (c) prototype unconditional-continuation DP; (d) proposed
zero-floored DP. Also: (e) GT-induced tube as `Oracle-Tube Diagnostic` only, never in the
main table.

Metrics: final $\bar P/\bar R/\mathrm F1$, boundary MAE on matched segments, false-merge
rate on the long-prefix and two-copy counterexamples, refinement latency.

### E4 — Track constraints (single-factor)

Base config; remove dual-axis support; remove gap splitting; remove min-IoU (use
joint-envelope IoU); sweep $e_A$ and $w_r$. Change exactly one thing per row; fix the RANSAC
seed. Report candidate count, $\sum_r L_rW_r$, spurious-track ratio under repeated texture,
F1 and latency.

### E5 — Implementation and cost decomposition (H3)

* CPU: prototype predecessor scan vs. direct-offset $O(LW)$ implementation vs. a vectorised
  full-matrix DP baseline.
* GPU: only after real-hardware acceptance. Report separately and never infer GPU speed-up
  from CPU profiling.
* Report per-stage shares (normalise, coarse, RANSAC, band similarity, DP recurrences,
  traceback, post), dot products, tube cells, peak RSS/GPU memory, and completion rate.

## 3. Diagnostic metrics (custom, not official)

| Metric | Definition | Caveat |
|---|---|---|
| Candidate recall | fraction of GT segments with at least one candidate track/interval at $\min(\mathrm{IoU}_A,\mathrm{IoU}_B)\ge\theta$ | custom; $\theta$ and matching rule must be frozen |
| Boundary MAE | mean absolute endpoint error in feature frames over matched segments | only defined for matched segments; report $n$ |
| Negative-pair FAR | fraction of the 27,315 test negatives with ≥1 predicted segment | test only; val is `N/A` |
| Tube cells evaluated | $\sum_r L_rW_r$ over all tubes, summed over multi-path attempts | counts work, not unique cells |
| Candidate coverage curve | recall vs. `actual_dot_products` (and vs. coarse latency) | must use actual, not idealized, dot products |

These are **not** the official copy-overlap F1 and must never be reported as such. VCSL
provides interval boxes, not dense frame correspondence, so "frame-level correspondence
recall" cannot be measured and must not be claimed.

## 4. Execution priority

1. **P0** — Fix/decide the local-DP semantics; add the four counterexample unit tests; create
   the Simple Sparse-to-Band baseline as a real, runnable method.
2. **P0** — Freeze a protocol (feature digest, CSVs, evaluator, thresholds) and produce a
   zero-error complete val for the *current* default.
3. **P1** — Run E1 and E3 on identical candidates; this decides whether the paper has a
   mechanism contribution.
4. **P1** — Run the single test evaluation after freezing; compute negative FAR.
5. **P2** — E2/E4 sweeps and the iso-budget curves.
6. **P2** — Direct-offset DP implementation and E5 timing.
7. **P3** — Real-GPU acceptance (functional parity → controlled timing), then GPU E5.

## 5. Decision tree after the real experiments

* **Case A** (accuracy ≥ baseline and `T_localize` clearly lower, with a single-mechanism
  ablation supporting the core): claim a quality–cost Pareto improvement under fixed
  features. Still avoid "state of the art" unless all comparators are on the same protocol.
* **Case B** (clearly faster but some accuracy loss vs. TransVCL/full DP): reposition as a
  training-free accuracy–latency trade-off and failure analysis; quantify the loss source
  (e.g., short-segment miss rate).
* **Case C** (simple baseline or classical TN/DP matches both accuracy and speed, or the
  mechanism gives no net benefit): narrow the claims to a systematic diagnostic/negative
  result. Do not manufacture a novelty claim.

## 6. What would change the paper's title/framing

If H1 fails, "Sparse-to-Tube" is misleading; if H2 fails, drop "refinement" from the
contribution and present the tube as a candidate visualization only; if H3 fails, remove
"Fast" from any performance sentence and keep it only as a project name in a footnote.
