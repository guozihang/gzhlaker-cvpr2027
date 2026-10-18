# Missing Evidence (ranked by submission-blocking severity)

Legend: `MISSING` = no artifact exists; `CONFLICT` = artifacts disagree; `PILOT_ONLY` =
only small/incomplete diagnostics exist. Each row states the exact artifact that would
close the gap and the acceptance criterion.

## Top-5 blockers (must be closed before any empirical claim)

### B1. No frozen, zero-error benchmark result (`MISSING`)

*What exists:* one near-complete val execution (41,797/41,798 scored, 1 ERROR), one
interrupted run (8,075/41,798, 33,723 SKIPPED), 200-pair and 20-pair development runs.
*What is missing:* a single frozen protocol with a complete val (0 ERROR, 0 SKIPPED), a
frozen threshold per method, and one test execution with all denominators.
*Required artifact:* `run_metadata.json`, `status.jsonl`, `metrics.json`,
`per_pair_timing.jsonl` for each method, plus `frozen_protocol.json` with config and feature
digests.
*Acceptance:* `n_processed == n_expected`, `n_error_or_skipped == 0`; thresholds recorded as
selected on val; test run executed once; Table 1 lower block filled from these files only.

### B2. The Simple Sparse-to-Band baseline does not exist as a runnable method (`MISSING`)

*What is missing:* a separate entry point implementing exactly one grid + mutual Top-$K$ +
standard RANSAC + fixed-width band + the shared restricted-step zero-floored DP, with no extra dual-axis support/span checks,
no gap splitting and one path; use the same scoring, min-IoU and threshold protocol as the
core. E4 tests dedup changes independently. This round-two design supersedes the old baseline.
*Required artifact:* its own config, run id, predictions and metrics on the same pairs.
*Acceptance:* equal coarse dot-product budget and equal hardware; otherwise the novelty gate
is invalid. Without it, no claim beyond "a pipeline exists" is admissible (`NOVELTY_GAP`).

### B3. Local-DP semantics unresolved and E3 not run (`CONFLICT`)

*What exists:* two different semantics (proposed zero-floor vs. prototype unconditional
continuation); a deterministic 15-row counterexample; partial unit coverage (2 of 4 required
diagnostics).
*What is missing:* the two missing unit tests (long negative prefix; same-track two copies
with a long gap at the DP layer), a decision on the default, and a controlled E3 comparison
on identical candidate tubes.
*Required artifact:* unit tests + E3 table (variants a–d) + per-regime breakdown.
*Acceptance:* the chosen default is documented; the paper's Method matches the code; E3
shows whether the zero floor helps, does nothing, or hurts.

### B4. No hardware-verified acceleration and no valid timing (`MISSING`)

*What exists:* CPU stage profiling on small dev subsets (PILOT_ONLY); a CUDA backend that has
never run on a GPU; historical timings contaminated by a ×1000 unit bug and by
`profiling.enabled=true` in the shipped config.
*What is missing:* real-GPU functional parity, then same-machine three-round timing with
`profiling=false`, warm-up, thread pinning and P50/P95; a direct-offset $O(LW)$ DP
implementation for the E5 comparison.
*Required artifact:* GPU verification log + timing JSONL + hardware fingerprint.
*Acceptance:* CPU/CUDA prediction parity on the same bands; measured, not projected, wall
clock; TransVCL chunk times summed per video pair.

### B5. External baselines are not reproducible in the audited environment (`MISSING`)

*What exists:* VCSL reference implementations of HV/TN/DP/DTW/SPD in principle; TransVCL
source; **no torch, no TransVCL checkpoint, no SPD weights** in the audited environment; the
adjacent repository's data is a different VCSL version (55,530 pairs / 27,765 keys).
*What is missing:* a runnable environment with the official weights, and a decision on
whether SPD can be aligned to the same ISC features.
*Required artifact:* environment lockfile + checkpoint hashes + per-method predictions on the
same CSVs/GT.
*Acceptance:* every Table 1 row is either (i) measured here under the frozen protocol or
(ii) explicitly labelled as a quoted value from a different protocol and excluded from any
ranking/bolding.

## Additional evidence gaps (not blocking, but must be disclosed)

| ID | Gap | Status | Consequence |
|---|---|---|---|
| G1 | No full content digest over all 12,254 feature files | `MISSING` | dataset version is only partially pinned (metadata hashes exist) |
| G2 | No frozen `frozen_protocol.json` | `MISSING` | thresholds/report cannot be certified |
| G3 | Multi-scale and independent-phase effects only in 20-pair unpaired diagnostics | `PILOT_ONLY` | no claim about H1 variants |
| G4 | RANSAC seed variance not measured (5 seeds) | `MISSING` | no error bars on any stochastic stage |
| G5 | No qualitative figure on a real pair (only a synthetic schematic) | `MISSING` | no qualitative claim; Fig. 3 must stay labelled synthetic |
| G6 | No SPD/TransVCL timing under the same `T_localize` boundary | `MISSING` | Table 2 learned-localizer rows stay pending |
| G7 | No negative-pair FAR anywhere (val is positive-only) | `MISSING` | test FAR pending; val must read N/A |
| G8 | No per-length-bucket candidate recall | `MISSING` | H1 cannot be evaluated |
| G9 | No boundary MAE implementation frozen | `MISSING` | H2 secondary metric pending |
| G10 | Code paths for independent phases + multi-scale are mutually exclusive | `CONFLICT` | combination cannot be claimed |
| G11 | `dev1000` metrics are over 200 pairs | `CONFLICT` (resolved as internal) | never use 1,000 as denominator |
| G12 | Historical `val_full` has 1 ERROR | `CONFLICT` (resolved as PILOT) | not a benchmark row |

## Closure checklist for the next experimental agent

1. Implement B2 and run E1 on the same pairs/budget/hardware.
2. Add the four DP diagnostics; choose the default semantics; rerun E3.
3. Produce a zero-error complete val for the frozen default; freeze thresholds; run test once.
4. Re-measure with `profiling.enabled=false`, warm-up, ≥3 rounds, thread pinning.
5. Only then fill Tables 1–3 and Fig. 4, and rewrite Abstract/Conclusion with measured
   language. Until then, every result cell stays `\TODO{PENDING}`.

## Round-two additional gaps (2026-10-18)

| ID | Gap | Required evidence |
|---|---|---|
| R2-G1 | Proposed zero output margin / distinct-support score differ from code | explicit semantic decision, exact small cases, isolated controlled comparisons |
| R2-G2 | No actual evaluator run in current shell | locked environment, source hashes, perfect/empty/false-alarm/undefined cases versus reference |
| R2-G3 | Diagnostic box matching and common cohort not implemented | deterministic matching rules, valid-GT denominator, matched counts and recall |
| R2-G4 | No shared-video dependence audit | split overlap report and defensible uncertainty unit; otherwise avoid significance language |
| R2-G5 | seltive model only partially specified | index-to-frame manifest, backend, selector, decisive-verdict fusion, E6 and total added cost |
| R2-G6 | No frozen budget-matching tolerance/operating-point set | development-only decision log, actual per-pair and aggregate dot counts |

The round-two writing fixes do not close B1–B5. A CPU-only study does not need to wait for
GPU access if it limits its claims appropriately. Main-paper table acceptance still requires
complete real-data artifacts under the finalized protocol.

## Round-three updates (2026-10-18)

| ID | Previous gap | What changed | Remaining gap |
|---|---|---|---|
| R2-G1 | Proposed zero margin / distinct support differ from code | Paper now states `1e-8`, zero margin and distinct-both-axes support explicitly; probes document the code's row margin and stored-entry count | No code change; E4/E1 must still test the two rules on identical inputs |
| R2-G2 | No evaluator execution | Function-level parity: 211 synthetic cases, 0 mismatch, macro/sentinels/denominators/`conf=0` and a 5-row status case | No file-level reference-vs-port run on real predictions/GT |
| B3 | DP semantics unresolved, E3 not run | 646 unit tests pass; probes add the weak-prefix and blocked-second-copy cases with exact scores | No zero-floor implementation, no E3 on identical tubes, no new unit tests in the prototype |
| R3-G1 | Validity threshold not audited | Paper aligned to code `1e-8`; the loader rejects non-finite files | Helper-level `isfinite` gap remains; boundary test missing |
| R3-G2 | RANSAC draw description | Paper no longer claims a minimum draw separation | If a minimum separation is desired, it is a new constraint and needs a test |
| R3-G3 | \(e_A=0\) fallback | Documented: the code pads by `half_width + margin` when no explicit range | E4 must pass an explicit range; no code change |
| R3-G4 | Threshold location | Paper now says threshold is evaluator-side | Core-side threshold is not implemented and should not be claimed |
| R3-G5 | F1/de-dup wording | Paper now shows the `+1e-6` F1 guard and start-coordinate tie-break | No code change needed; parity check covers the guard |

The paper corrections do not close B1, B2, B4 or B5. A CPU-only controlled study is still
possible without GPU access, but it requires the STB baseline, a frozen protocol and complete
real-data runs.
