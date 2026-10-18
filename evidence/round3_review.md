# FastVCL round-three review

Date: 2026-10-18. Scope: continue the round-two plan on the existing paper project. The
prototype and reference repositories were read-only; the paper, evidence and check scripts were
edited. No dataset, model, paid API, GPU kernel or submission was executed.

**Bottom line:** the manuscript is now internally more consistent and fits the fallback
template's 8-page body, and the evaluator port has a real function-level parity check. It is
still a research draft with **no benchmark result**, unresolved specification/code differences
and an unimplemented `seltive model`. It is not submission-ready.

## 1. Snapshot and environment

| Item | Value |
|---|---|
| Paper root | `/Users/gzhlaker/Documents/code/gzhlaker_cvpr2027` |
| Prototype | `../FastVCL`, HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`, tracked tree clean |
| Reference evaluator | `../gzhlaker_transvcl/metric/eval.py`, HEAD `4b57976da5ad1b38f999c96aba315e63a272acdf` |
| Source hashes | unchanged from `evidence/round2_source_snapshot.json` (rechecked with `shasum -a 256`) |
| Python for checks | DSH runtime Python 3.12, NumPy 2.3.5 |
| Build | Tectonic 0.17.0, XeTeX backend, project-local cache |
| GPU | none; 10 CUDA tests skipped |

No prototype file was written; `git -C ../FastVCL status --short` was empty before and after
the checks.

## 2. What was actually changed

### 2.1 New evidence and check scripts

- `evidence/spec_code_contract.md`: item-by-item paper/code contract with line references,
  status labels, detailed conflict sections (validity, RANSAC draw, DP restart, A-range
  fallback, margin, support, threshold, F1, de-dup tie), canonical choices and acceptance tests
  A1–A12.
- `evidence/diagnostic_protocol.md`: candidate envelope, GT filtering, candidate recall,
  boundary matching/MAE/common cohort, execution counters, budget matching, threshold/evaluation
  modes, video-dependence rules and a proposed `frozen_protocol` schema. **Not implemented.**
- `evidence/selective_model_spec.md`: inputs, verified frame-map requirements, output schema,
  selection/fusion/failure/caching contracts, privacy and E6 design for the user-requested
  `seltive model`. All backend/selection/fusion decisions remain `OPEN`.
- `scripts/check_evaluator_parity.py`: 211-case synthetic function-level parity harness.
- `scripts/check_contract_semantics.py`: 8 read-only probes of prototype semantics.
- `evidence/evaluator_parity.json`, `evidence/contract_probes.json`,
  `evidence/prototype_tests_summary.md` (full local log: `evidence/prototype_tests.log`).

### 2.2 Paper corrections

- Validity threshold changed from `1e-12` to `1e-8`, matching the prototype's shared
  `MIN_ROW_NORM`; the finite check is described as a load-time precondition.
- Removed the unimplemented RANSAC `|i2-i1| >= Delta_min` draw claim; the run-span/support
  constraints remain.
- Described the prototype's DP precisely: no restart when a legal predecessor exists, negative
  continuations persist, a negative cell can be a predecessor but not a traceback start.
- Stated that the prototype margin is counted in **matched path rows** (default 2), not feature
  indices, and that support counts stored A-anchor entries rather than distinct times in both
  intervals.
- Defined the proposed support as distinct A times whose anchors lie in both segment intervals.
- Moved the confidence threshold to the evaluation protocol; the core pipeline writes scores.
- Added the `+1e-6` F1 zero guard to the wrapper equation and changed the de-dup tie wording to
  start coordinates then collection order.
- Removed the manual `\\` in the title. In this toolchain it caused a XeTeX font error at a
  later section; the natural wrap builds cleanly and remains anonymous.

### 2.3 Page and layout changes

- Moved the sampling-property derivations, the efficiency matrix, the full E1–E5 matrix, the
  teaser figure, the anchor/tube figure and the empty trade-off plane to `supplementary.tex`.
- Kept the framework figure full width in the main text (now main Figure 1).
- Main body now ends on **page 8**; references occupy page 9; main PDF is 9 pages.
- Supplement is 7 pages. The two full-width matrices and the verification-scope note share
  page 7; no overfull box.
- All pending markers remain visible; no font or margin reduction was used.

### 2.4 Evidence-ledger updates

`evidence/method_spec.md`, `implementation_status.md`, `claims_ledger.md`,
`missing_evidence.md`, `experiment_plan.md`, `experiment_manifest.md`, `figures/README.md`
and `README_BUILD.md` were updated to the new findings and page counts. New claims C37–C45
record the source-level corrections and the parity/probe results; no claim became
`BENCHMARK_VERIFIED`.

## 3. What was verified

### 3.1 Builds and text checks

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex
```

- `main.tex`: exit 0, 9 pages; body ends page 8; references page 9.
- `supplementary.tex`: exit 0, 7 pages.
- No overfull/underfull boxes, no undefined citations or cross-references in the final logs.
- Extracted text has no `??`, local username or absolute machine path; the review author block
  is anonymous.
- `git diff --check` passes.
- Main pages and the supplement's key pages were rendered with Ghostscript and inspected;
  the framework figure is readable at full width.

### 3.2 Executed semantic checks

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .

cd ../gzhlaker_cvpr2027
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py \
    --output evidence/evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py \
    --output evidence/contract_probes.json
python3 scripts/check_paper_semantics.py --output evidence/round2_math_checks.json
```

| Check | Result |
|---|---|
| Prototype unit suite | 646 tests, 0 failures, 10 CUDA skips |
| Evaluator function parity | 211 cases, 0 per-pair mismatch; macro/sentinels/denominators/`conf=0` and a 5-row status case match |
| Contract probes | 8 behaviours observed, all documented |
| Scalar manuscript checks | 7 groups pass; still `benchmark_result=false`, `prototype_executed=false` |

Important distinction: the evaluator parity is **function-level**, not a file-level run of the
reference and port on the same real predictions/GT. The 646 tests are prototype tests, not
benchmark evidence. The probes do not implement the proposed recurrence, margin or support.

## 4. What is still not verified

1. **No benchmark result.** No frozen protocol, no zero-error complete validation, no test
   run, no FAR, no latency, no GPU. Every result cell remains pending.
2. **No implementation of the proposed rules.** Zero-floor recurrence, distinct-both-axes
   support, zero output margin, core-side threshold and the `FastVCL(fast)`/STB baseline entry
   point are not implemented in the prototype.
3. **No E1/E2/E3/E4/E5/E6.** The controlled comparisons are designed but not run. E3 on
   identical tubes does not exist.
4. **No file-level evaluator certification.** The synthetic parity check is done; the real
   prediction/GT files have not been scored by both implementations side by side.
5. **No diagnostics implementation.** Candidate envelope recall, boundary matching/MAE,
   common cohort, unique covered cells and the video-overlap audit are specified in
   `evidence/diagnostic_protocol.md` but not written or tested.
6. **No `seltive model` backend.** No model, frame map, prompt, selector, fusion policy or E6.
   The name is preserved; the capability is not claimed.
7. **Template status.** The local kit is the CVPR 2026 fallback with `confYear=2027`. The
   2027 AuthorGuidelines were not available; the 8-page body is a fallback-template result, not
   a 2027 compliance claim.
8. **Supplement layout.** The two full-width matrices and the verification-scope note share
   page 7 of the 7-page supplement. No content is missing.

## 5. Open specification/code differences (must not be called fixed)

| Difference | Paper status | Code status |
|---|---|---|
| Validity threshold | now `1e-8` | `1e-8`; helper-level finite gap |
| RANSAC draw | distinct A coordinates | distinct A; no Delta_min |
| DP restart | proposed zero-floor | negative continuation, no restart with predecessor |
| Output margin | proposed zero | 2 matched path rows |
| Support | distinct, both intervals | stored A entries, A-only |
| Threshold | evaluator-side | evaluator-side; no core threshold |
| F1 guard | `+1e-6` shown | `+1e-6` |
| De-dup tie | start coordinates | `(-score, start_a, start_b)` |

The first four remain `CONFLICT`/`PROPOSED_ONLY`; the last two are wording/accounting fixes.

## 6. Next steps (priority order)

1. **Freeze a semantic decision for the DP, margin and support** (or keep two variants), then
   implement it with the old behaviour reproducible. Add the A1–A12 tests from the contract.
2. **Implement the Simple Sparse-to-Band baseline** as a separate entry point sharing the
   chosen recurrence, margin, support and scoring; run E1 on development pairs with matched
   coarse work/caps.
3. **Implement the diagnostics** in `evidence/diagnostic_protocol.md` and the
   `frozen_protocol` writer; run a file-level reference-vs-port evaluator comparison.
4. **Run E2–E5 on development data**, then freeze and run a complete validation and one test
   campaign. Do not tune on test; do not fill tables from the historical one-error run.
5. **Decide the seltive-model backend and frame map** only if the user authorizes the extra
   input/cost; then run E6 with the controls in `evidence/selective_model_spec.md`.
6. **Recheck the official CVPR 2027 kit and policies** before submission; the current 8-page
   body is a fallback result, not a compliance statement.
7. Optionally improve the supplement float placement; do not shrink the framework figure or
   hide pending markers.

## 7. File entry points

- Paper: [main.pdf](../main.pdf) · [main.tex](../main.tex)
- Supplement: [supplementary.pdf](../supplementary.pdf) · [supplementary.tex](../supplementary.tex)
- Build record: [README_BUILD.md](../README_BUILD.md)
- Contract: [spec_code_contract.md](spec_code_contract.md)
- Diagnostics: [diagnostic_protocol.md](diagnostic_protocol.md)
- Selective model: [selective_model_spec.md](selective_model_spec.md)
- Evaluator parity: [evaluator_parity.json](evaluator_parity.json)
- Contract probes: [contract_probes.json](contract_probes.json)
- Prototype tests: [prototype_tests_summary.md](prototype_tests_summary.md) · [local log](prototype_tests.log)

## 8. Final status

The round-three work improves the paper's honesty and internal consistency, and it adds
executable checks for the evaluator and the most consequential prototype semantics. It does
**not** turn FastVCL into an empirically validated method. The core scientific questions
(candidate coverage H1, boundary recovery H2, system benefit H3, verifier value E6) remain
open, and the paper still says so in the abstract, experiments and conclusion.
