# Experiment plan — round 2 (2026-10-18)

All comparisons are **PROPOSED / NOT RUN**. This file supersedes earlier E1 and budget
rules. See the Chinese round-two execution plan for task order and deliverable names.

## Hypotheses and decisions

| Hypothesis | Evidence needed | Failure interpretation |
|---|---|---|
| H1 candidate coverage | candidate-envelope recall versus executed coarse work, by length | missing proposal coverage, particularly short copies |
| H2 boundary recovery | identical tubes, endpoint MAE + matched count + recall + common cohort | MAE gain due only to selecting easier survivors is insufficient |
| H3 system benefit | paired quality–cost points, full core wall time and memory | less DP work with greater total latency is no speed advantage |
| E6 optional verification | fixed candidates, equal call/frame/token budget, whole-set utility | selected-case accuracy with recall loss or excessive added cost is insufficient |

## E0–E6 and fixed controls

| ID | Comparison | Held fixed | What may change / mandatory report |
|---|---|---|---|
| E0 | HV/TN/DP/DTW and compatible pretrained SPD/TransVCL | files, evaluator, splits, timing definition | method and per-method validation threshold; verify weights/input compatibility |
| E1 | Simple STB vs core, then one mechanism at a time | grid, matcher, trial budget, configured caps, hardware, post-processing | actual candidate count may change and must be reported |
| E2 | stride, nested scales, independent phases | downstream fitting/alignment and declared caps | executed dots, duplicates, candidate recall, length buckets; no assumed equal-budget stride-2 control |
| E3 | support box, band DTW, continuation, zero-floor | serialized tracks/tubes and common post-processing | alignment policy; both DP variants share steps/precision; distinguish matches lost/gained |
| E4 | support checks, splitting, dedup, extension, width | all other settings and seeds | one factor per row; width and extension are separate sweeps |
| E5a | scan vs direct addressing | same recurrence, inputs, steps, ties, outputs | indexing implementation only; require parity before timing |
| E5b | full-matrix vs tube DP | features, recurrence, declared protocol | search domain; never claim this is indexing-only |
| E6 | core / random selection / cheap selector / selective verifier | same core candidate pool, backend, fusion, call/frame/token budget | selection policy; whole-set F1/recall/FAR, failures and total added cost |

### Exact simple baseline (design, not implemented)

One zero-phase stride-4 grid, Top-1 mutual matching, shared cosine threshold/cap and seeded
RANSAC. Same slope bounds, residual criterion, trial cap and minimum distinct A inliers;
no extra B support/span checks and no gap splitting. Fixed finite width and A extension;
same zero-floor steps, smoothing, scoring, output threshold and min-IoU suppression;
one path per tube. Core adds dual-axis checks, gap splitting and bounded repeated paths.
Multi-scale/phases are **not** core defaults. Dedup changes are isolated in E4, not hidden
in the baseline. The proposed margin/support changes must be applied identically to both.

Hold configured budgets/caps equal; do not discard candidates post hoc to force equal
realized counts. For E3 reuse exact tube hashes. Headline full-system comparisons may alter
several mechanisms; explicitly label them as such, not single-factor ablations.

### Budget matching

Use executed coarse dots, including both directions and tie passes. {2,4,8} costs more
than stride 2. A proposed matching tolerance (e.g. 5% of aggregate executed work) must be
chosen before results; report per-pair mismatch too. If no discrete configuration matches,
show realized cost curves without an equal-budget claim. Never add useless computations
to pad budgets. Duplicate-anchor runs are corruption diagnostics only.

## Diagnostics to freeze before running

- Candidate recall: tube axis-aligned envelopes versus valid GT, any candidate at min axis
  IoU >= 0.5; report valid-GT denominator and exclusions. Empty tube has no envelope.
  This is box coverage, not legal-path or frame-correspondence recall.
- Length buckets use min(A duration, B duration): <15, [15,60), >=60 feature indices.
- Boundary MAE: four-endpoint mean absolute error after maximum-cardinality one-to-one
  matching at min-IoU >= 0.5, then maximum total min-IoU, then deterministic id ties.
  Report each method's matched count/recall and a common-GT cohort for paired differences.
- Official metric keeps original GT; custom diagnostics may separately omit invalid boxes
  only with frozen rules and counts. Never silently clean the official labels.
- Log similarity dot products, executed DP visits, per-attempt work and unique covered
  cells separately. Cache reuse is recorded, not presumed.
- Repeat headline RANSAC fits over five predeclared seeds. This estimates seed variation,
  not data uncertainty. For paired bootstrap, define the sampling unit and handle repeated
  video identities/provenance; if unavailable, state the limitation and avoid significance claims.

## Evaluation and tuning

1. Finish implementation semantics and source-level tests before selecting settings.
2. Audit development/validation/test video overlap; use official test only for final reporting.
3. Freeze threshold grid, objective, tie rule, score mode and coordinate conversion.
4. Select structure on development data and thresholds on validation. Validation is all
   positive; its scores are selection-biased and cannot calibrate negative-pair FAR.
5. Freeze all intended operating points/seeds, feature contents, CSV/GT/evaluator hashes,
   code/config hashes and model/checkpoint manifests. A single final test campaign may
   contain multiple **predeclared** configurations; no test-adaptive choice or redesign.
6. Primary tables require zero errors/skips and all four macro/completion denominators.
   Undefined macro metrics are null with reason, not zero. Ordinary nonempty perfect overlap
   stays below 1 because of epsilon; equality sentinels are handled exactly as the evaluator.

No FAR target can be promised from positive-only validation. A negative development set
requires provenance and separation from test; otherwise FAR remains a held-out diagnostic.

## Timing and quality–cost plane

Core: CPU-resident raw features and initialized operators to in-memory predictions. Include
normalization, transfers, all candidate stages, DP, traceback and post-processing. Separately
record I/O, export, initialization and backbone extraction. TransVCL includes every chunk
and pair assembly in actual pair wall time. Disable intrusive profiling, warm up, run at
least three rounds, fix threads/precision and synchronize GPUs. Report mean/P50/P95,
throughput with units, CPU RSS, GPU allocated/reserved peaks and stage residuals.

Compare matched hardware; separate heterogeneous-system operating points from algorithmic
speed claims. Scan/direct indexing must first agree on exact semantic outputs. GPU evidence
requires actual hardware execution. Vary stride/width/path budgets to generate real cost
points; a post-hoc confidence sweep alone does not reduce already-executed computation.

E6 additionally includes frame acquisition/decoding, preprocessing, network/queue/model
calls, retries and fusion. Distinguish cached from live acquisition and count failures.
Never compare this combined cost to a baseline whose input costs are excluded without
explicitly identifying the different timing scopes.

## Priority and completion gates

P0: resolve math/code discrepancies + implement strong STB baseline + freeze evaluator tests.
P1: controlled development E1/E3; determine whether a useful mechanism increment exists.
P1: fix diagnostic definitions, manifests, threshold protocol and data leakage audit.
P2: development E2/E4/E5 and uncertainty; freeze configuration set, then final test campaign.
P3: E6 only after backend, mappings, selection and fusion are specified and independently
validated. CPU-only core study can complete without GPU; GPU and verifier claims stay pending.

Lack of baseline gain is not cured by renaming modules. A gain establishes utility under
its protocol, not novelty by itself. Revisit closest prior work and narrow claims as needed.

## Round-three constraints on the planned runs (2026-10-18)

1. **E1 must share the recurrence, margin, support and scoring rule** between the STB
   baseline and the core. The named structural change is the only difference. Do not compare
   a zero-floor core with a continuation baseline in E1; that is E3.
2. **E3 is the recurrence comparison**, on identical serialized tracks/tubes with hashes. The
   prototype uses negative continuation and never restarts when a predecessor exists; the
   paper's zero-floor rule is still `PROPOSED`. Report exact paths, matches gained/lost and
   the common cohort, not only F1.
3. **E4 zero-extension row:** pass an explicit A range. With `extension_a=0` and no explicit
   range, the code pads the A scan by `half_width + margin` and changes two factors.
4. **Margin and support units:** the prototype margin is counted in matched path rows and
   the support term uses stored A-anchor entries. If E4 tests the proposed zero margin or
   distinct-both-axes support, apply the same rule to both sides of that row and document it.
5. **Threshold:** the core pipeline writes scores; the evaluator applies `q>c` (legacy
   `c=0` skips filter and cast). A threshold sweep is not an upstream-compute experiment.
6. **Validity:** use the shared `1e-8` threshold; do not mix the old `1e-12` value into a run.
7. **Evaluator:** function-level parity is checked (`evidence/evaluator_parity.json`), but a
   file-level reference-vs-port run is still required before the first scored table.
8. **No result yet:** every cell stays `PENDING`; the 646 prototype tests and 8 probes are
   semantic checks, not benchmark evidence.

## Round-five execution order (2026-10-20)

Round five did not run an experiment. It fixed the order and the denominators that a later
run must use; no result cell was filled.

| Order | Experiment | Fixed / changed | Primary decision |
|---|---|---|---|
| 1 | Core consistency + E1/E3 | fix zero-floor, support and margin; E3 freezes tubes; E1 shares recurrence/scoring/post-processing | does core beat simple sparse-to-band at equal executed coarse work? |
| 2 | E6-A / E6-F shadow | same `A0` or `C0`; no action; real frames and traceable labels | is there enough discriminative information and a valid action opportunity? |
| 3 | E6-A / E6-F action controls | same model, board, thresholds, input pool, fixed selected edges | does the visual action beat random and cheap geometric rules without a severe recall loss? |
| 4 | E6-J four-cell + same-total-budget | core, A-only, F-only, A+F full reruns | is there a two-stage increment and a real budget effect? |
| 5 | Full quality--cost curve | predeclared B and core compute settings; same-machine timing | does extra budget buy a meaningful gain? |
| 6 | E0 external baselines and robustness | alignable classical/learned baselines; length/edit/negative buckets | is there external empirical value and a clear scope? |

The four-cell position experiment uses fixed `A=8`, `F=4`; the same-total-budget experiment
compares `A=12`, `F=12` and `A=8+F=4`. They are separate. Both report actual questions,
frames, tokens and time; matching question caps is not matching cost.

The fusion row must report correct opportunities, legal-edge coverage, `Conn` pass rate and
asked-versus-executed actions, and must compare `Conn`-only with `Conn`+visual on a fixed edge
set. Without these counts, selector differences are misattributed to the model.

The risk ledger separates true-anchor deletion (all `A0` and queried true anchors), deletion
action error, wrong-fusion, coverage/abstention and final full-set effect. The zero-error
one-sided 95% bound is `1 - 0.05^(1/n)`; 299 effective zero-error trials are needed for 1%.
Candidate edges are not accepted fusions, and video-correlated groups are not independent.
Thresholds are selected on `dev_calibration` and frozen to `dev_audit`.

Round-five stop conditions remain in force: no verified frame map -> no visual experiment;
no labels/audit -> shadow only; no fusion opportunity -> stop large visual spend; no
same-budget gain -> narrow the claim; insufficient resources -> shrink the predeclared set,
never report a partial run as complete.
