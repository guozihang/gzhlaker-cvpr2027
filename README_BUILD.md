# Build record and draft status

Last checked: **2026-10-19, round 4 (manuscript-only update)**. This is a research draft with
pending experiments, not a submission-ready paper. The main entry point is now 12 pages (body
to about page 10; references on pages 11–12); the supplement is a separate 10-page entry
point. The fallback template's 8-page body target is **not met** after adding the two-stage
decision specification and the E6 matrix. No table cell was filled from a new run.

## Current outputs

| Entry point | Exit | PDF | Pages | Bytes |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 12 | 486,175 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 10 | 361,246 |

## What changed in round 4 (paper only)

- Title is now *FastVCL: Budgeted Visual Decisions for Sparse-to-Tube Video Copy Localization*.
  The abstract, introduction, related work, method, experiments and conclusion were rewritten
  for the two decision points.
- Method §3.7 specifies one shared `seltive model` with a budgeted anchor filter
  ($\mathcal A_0\to\mathcal A_1$) and a budgeted fragment-fusion decision
  ($\mathcal C_0\to\mathcal Y$), including abstention, geometry and connection gates, one
  pair budget, cache keys and the failure contract. The detailed specification and the E6
  matrix moved to supplementary §13.
- `main.bib` gains Visual Jev (arXiv:2609.25845) and VideoJev (arXiv:2610.18615), checked
  against the arXiv records on 2026-10-19.
- `scripts/generate_framework.py` now draws one shared model box with two directed insertions
  and original frames as the additional input; the old post-hoc-verification-only arrow is
  gone. SVG/PDF/PNG were regenerated.
- No prototype, dataset, visual model, GPU or paid call was run. All result cells remain
  `\TODO{PENDING}`; no accuracy, FAR or latency number is claimed.

## Reproduce the build

Engine: Tectonic 0.17.0, XeTeX backend. The project-local cache avoids network downloads;
use `TECTONIC_CACHE_DIR`, not a changed HOME directory.

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex
python3 scripts/generate_framework.py
python3 scripts/check_paper_semantics.py --output evidence/round2_math_checks.json
git diff --check
```

The prototype and evaluator checks need the NumPy interpreter; they are read-only and were
**not rerun** in this round:

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
The default shell Python still lacks NumPy; the DSH runtime above has NumPy 2.3.5. The scalar
manuscript check uses only the standard library.

## Checks and visual review

- Both builds exit 0. The final logs contain no overfull boxes and no undefined citations or
  cross-references.
- `git diff --check` passes.
- Main pages were rendered. The framework figure is on page 4 and remains full width; Table 1
  is on page 9; the E6 discussion is on page 10. The supplement's new §13, its decision record
  schema, E6 matrix (Table 5) and decision algorithm (Algorithm 1 in the supplement) were
  rendered and checked for truncation.
- Non-fatal warnings remain: invalid UTF-8 comments in `lineno.sty`/`algorithm.sty`,
  Times-family substitutions under XeTeX, and included PDF 1.7 figures versus output PDF 1.5.
  They are not manuscript reference errors.
- The round-3 prototype checks (646 tests, 211 parity cases, 8 contract probes) are historical
  in this build. The round-4 engineering plan was **not** executed: `evidence/claims_ledger.md`,
  `implementation_status.md`, `experiment_plan.md`, `missing_evidence.md` and
  `selective_model_spec.md` were deliberately left untouched because this round was scoped to
  the paper, so their status text may lag the manuscript.

## Template and page budget

The local package is the **CVPR 2026 author kit**, with `confYear=2027` for the draft label.
It is not certified as the official final 2027 kit. The
[2027 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) lists registration on
2026-11-10, papers on 2026-11-16 and supplements on 2026-11-23 (AOE); the AuthorGuidelines URL
still returned 404 on 2026-10-19. Recheck the official kit and policies before submission.

The body now ends around page 10, about two pages over the fallback 8-page body target. This
was accepted for this round because the two-stage method and its experiment matrix are the
substance of the update. Candidate cuts for a later pass, in order: (1) move the formal
validity-mask definitions and the predecessor-addressing derivation to the supplement;
(2) compress the restart-history and scoring-support paragraphs; (3) move the metric-epsilon
discussion (already summarized) entirely to the supplement; (4) tighten §3.7 further.
Do not shrink the framework figure below legibility or hide the pending-result markers.

## Files and regeneration

- Paper: `main.tex`, `preamble.tex`, `main.bib`, `sec/*.tex`.
- Supplement: `supplementary.tex` (separate entry point). It holds the sampling derivations,
  the teaser/anchor/trade-off figures, the efficiency and ablation matrices, the full
  two-decision specification, the E6 matrix and the audit details.
- Fig. 2 source: `scripts/generate_framework.py`; outputs SVG/PDF/PNG. It is the only figure
  compiled into the main text.
- All figures: `scripts/generate_paper_placeholders.py`, which delegates Fig. 2 to the
  dedicated generator. No experimental values are generated.
- Evidence and audit: `evidence/round4_review.md`, `evidence/round4_source_snapshot.json`,
  `evidence/round4_math_checks.json`, `evidence/round4_evaluator_parity.json`,
  `evidence/round4_contract_probes.json`, plus the earlier round-2/3 material.
- Execution plan for the next engineering round:
  `FastVCL_CVPR2027_第四轮审查与执行方案.md` (W0–W6).

The prototype remains unchanged. Zero-floor recurrence, distinct segment support and zero
output margin are proposed semantics requiring implementation alignment. The optional
`seltive model` has no validated backend, frame map or action threshold. No formal accuracy,
speed, GPU or verifier benefit is established by this build.
