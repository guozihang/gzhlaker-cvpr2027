# Build record and draft status

Last checked: **2026-10-18, round 3**. This is a research draft with pending experiments,
not a submission-ready paper. The main text ends on page 8; references occupy page 9. The
supplement is a separate 7-page entry point.

## Current outputs

| Entry point | Exit | PDF | Pages | Bytes |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 9 | 414,370 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 7 | 334,451 |

The round-two draft had 12 pages (body to page 11). Round three moves the sampling-property
derivations, the efficiency and ablation matrices, and the teaser/anchor/trade-off figures
into the supplement, and tightens prose. The main body now fits the fallback template's
8-page target without reducing font size, margins or figure width. This is a fallback
template result, not a certification against the final CVPR 2027 kit.

## Reproduce the build

Engine: Tectonic 0.17.0, XeTeX backend. The project-local cache avoids network downloads;
use `TECTONIC_CACHE_DIR`, not a changed HOME directory.

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex
python3 scripts/check_paper_semantics.py --output evidence/round2_math_checks.json
git diff --check
```

The prototype and evaluator checks need the NumPy interpreter; they are read-only:

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .

cd ../gzhlaker_cvpr2027
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py \
    --output evidence/evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py \
    --output evidence/contract_probes.json
```

On another machine, obtain the required Tectonic bundle normally before using `--only-cached`.
The default shell Python still lacks NumPy; the DSH runtime above has NumPy 2.3.5. The
scalar manuscript check uses only the standard library.

## Checks and visual review

- Both builds exit 0. Final logs contain no overfull/underfull boxes and no undefined
  citations or cross-references.
- Extracted main/supplementary text contains no `??`, local username or absolute machine path.
  The review-mode author block is anonymous. This is a text/source check, not a claim that
  every possible PDF metadata channel has been audited.
- `git diff --check` passes.
- Prototype unit suite: 646 tests, 0 failures, 10 CUDA skips; summary in
  `evidence/prototype_tests_summary.md` (full local log: `evidence/prototype_tests.log`).
- Evaluator function parity: 211 synthetic cases, 0 per-pair mismatch; macro, exact-1
  sentinels, denominators, `conf=0` and a five-row status case match the reference
  (`evidence/evaluator_parity.json`).
- Contract probes: 8 behaviours observed, including weak prefix, strong–weak–strong, blocked
  second copy, A-range fallback, ties-to-even, margin 0/2, duplicate-vs-distinct support and
  the gap boundary (`evidence/contract_probes.json`).
- The 7 deterministic scalar checks still pass; the report says `benchmark_result=false` and
  `prototype_executed=false` because it is a separate standard-library check.
- Main pages were rendered for layout review. The framework figure is on page 3 and remains
  full width. Table 1 is on page 8. Figures 1–3, Tables 3–4 and the reserved trade-off
  plane are in the supplement. The two full-width matrices and the verification-scope note
  share page 7 of the 7-page supplement; there is no overfull box.
- The title no longer contains a manual `\\` line break. In this toolchain, a title break
  caused a XeTeX font error (`OT1/cmr/bx/n/12` not loadable) at a later section; removing the
  break fixes the build. The title still wraps naturally and remains anonymous.

Existing non-fatal warnings remain: invalid UTF-8 comments in `lineno.sty`/`algorithm.sty`,
Times-family substitutions under XeTeX, and included PDF 1.7 figures versus output PDF 1.5.
They are not new undefined manuscript references. Logs are `main.log` and
`supplementary.log`.

## Template and page budget

The local package is the **CVPR 2026 author kit**, with `confYear=2027` for the draft label.
It is not certified as the official final 2027 kit. On 2026-10-18, the
[official kit README](https://github.com/cvpr-org/author-kit) still records a CVPR 2026 update;
the 2027 AuthorGuidelines URL returned 404. The
[2027 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) is available, but its LLM
policy details are still pending. Recheck the official kit and policies before submission.

The main body reaches **page 8**, within the fallback template's 8-page body target; references
begin on page 9. Do not call this compliant with the final 2027 rules or ready to submit.
Further reduction should not shrink the framework figure or hide the pending-result markers.

## Files and regeneration

- Paper: `main.tex`, `preamble.tex`, `main.bib`, `sec/*.tex`.
- Supplement: `supplementary.tex` (separate entry point). It now holds the sampling
  derivations, the teaser/anchor/trade-off figures, the efficiency and ablation matrices and
  the audit details.
- Fig. 2 source: `scripts/generate_framework.py`; outputs SVG/PDF/PNG. It is the only figure
  compiled into the main text.
- All figures: `scripts/generate_paper_placeholders.py`, which delegates Fig. 2 to the
  dedicated generator. No experimental values are generated.
- Evidence and audit: `evidence/round3_review.md`, `evidence/spec_code_contract.md`,
  `evidence/diagnostic_protocol.md`, `evidence/selective_model_spec.md`,
  `evidence/implementation_status.md`, `evidence/claims_ledger.md`,
  `evidence/missing_evidence.md`, `evidence/evaluator_parity.json`,
  `evidence/contract_probes.json`, `evidence/prototype_tests_summary.md`.
- Current handoff: `FastVCL_CVPR2027_第二轮审查与执行方案.md` and
  `FastVCL_CVPR2027_第二轮Agent启动Prompt.md`. Old `fastvcl_cvpr2027*.md` files are historical
  and point to these replacements.

The prototype remains unchanged. Zero-floor recurrence, distinct segment support and zero
output margin are proposed semantics requiring implementation alignment. The optional
`seltive model` still lacks a finalized backend, selection and decisive-verdict fusion. No
formal accuracy, speed, GPU or verifier benefit is established by this build.
