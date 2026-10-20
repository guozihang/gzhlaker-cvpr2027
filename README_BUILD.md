# Build record and draft status

Last checked: **2026-10-20, round 5 (manuscript, specification and evidence sync)**. This is a
research draft with pending experiments, not a submission-ready paper. The main entry point is
10 pages (body to about the middle of page 9; references from page 9); the supplement is a
separate 12-page entry point. The fallback 8-page body target is **not fully met** (about 8.5
pages). No table cell was filled from a new run, no visual model was called, and no GPU kernel
was executed.

## Current outputs

| Entry point | Exit | PDF | Pages | Body end |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 10 | conclusion ends on page 9; references start page 9 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 12 | full supplement |

## What changed in round 5

- **Introduction and research questions.** Removed the absolute claim that more ISC
  comparisons cannot help; replaced `reversible` with per-item abstention and stated that only
  off/shadow must reproduce core item by item. Six hypotheses were compressed into three
  research questions (core, anchor filtering, fusion/allocation) and three contributions
  (method, mechanism, protocol), with no empirical claim.
- **Margin.** `eq:margin` now subtracts the strongest competitor after excluding the current
  match on each axis, uses the union of executed comparisons across plans, marks a missing
  side, and assigns the neutral selector rank 1/2. `K` was split into $K_{\rm nn}$ (neighbour
  count) and $B$ (question budget).
- **Fusion specification.** Added the legal-edge conditions (order/disjointness, gap caps,
  boundary-map agreement, connector slope, same-A/different-B exclusion), the grouped
  round-robin selector, the fixed $R_e$ and $L_cW_c$ connection check, one-round/no-propagation
  merge scope, member consumption, and endpoint/support/score recomputation.
- **Budget and cost.** Anchor evidence is at most 3 pairs / 6 frames; fusion evidence at most
  5 pairs / 10 frames. $B_A=\lfloor2B/3\rfloor$; cache hits count; unused anchor budget can
  move to fusion only; retries are off by default and worst case is $B+R$; connection cells
  are charged, including failures. The main flow is $A_0\to A_1\to$ tracks/tubes $\to C_0\to
  \mathcal Y$; fixed $C_0$ belongs only to E6-F.
- **Risk.** Split into true-anchor deletion (all $A_0$ and queried true anchors), deletion
  action error, wrong-fusion rate, coverage/abstention and full-set effect, with the
  zero-error $1-0.05^{1/n}$ bound and the 299-effective-trial requirement.
- **Tables and structure.** The core and augmented rows are separate tables. The formal
  validity mask, diagnostics, algorithm, full decision specification, risk ledger, budget table
  and E6 matrix live in the supplement. The main Method is organized as problem/core,
  two actions, and integration/cost.
- **Framework figure.** Regenerated with `one budget B` to match the renamed budget; the two
  call sites and the shared-model box are unchanged.
- **Evidence.** Added `evidence/round5_review.md`, `round5_assets.json`,
  `round5_source_snapshot.json`, `round5_math_checks.json`, plus rerun parity/contract/paper
  checks and a read-only 646-test prototype log. `claims_ledger.md`,
  `selective_model_spec.md`, `implementation_status.md`, `experiment_plan.md`,
  `missing_evidence.md` and `experiment_manifest.md` were synchronized.

## Reproduce the build

Engine: Tectonic 0.17.0, XeTeX backend. The project-local cache avoids network downloads;
use `TECTONIC_CACHE_DIR`, not a changed HOME directory. If `--only-cached` reports a missing
font, run once without it and re-check the cache.

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex

python3 scripts/generate_framework.py
python3 scripts/check_paper_semantics.py --output evidence/round5_paper_math_checks.json
cd scripts && python3 -B check_round5_semantics.py --output ../evidence/round5_math_checks.json
cd .. && git diff --check
```

The prototype, evaluator and contract checks need the NumPy interpreter; they are read-only
and were rerun in this round:

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .
# 646 tests, OK, 10 CUDA tests skipped

cd ../gzhlaker_cvpr2027
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py \
    --output evidence/round5_evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py \
    --output evidence/round5_contract_probes.json
```

On another machine, obtain the required Tectonic bundle normally before using
`--only-cached`. The default shell Python still lacks NumPy; the DSH runtime above has NumPy
2.3.5. The scalar manuscript and round-5 reference checks use only the standard library.

## Checks and visual review

- Both builds exit 0. Neither log has an undefined reference/citation or an overfull box after
  the final table adjustments. Non-fatal font-substitution warnings remain, and the supplement
  also reports float-specifier and hyperref PDF-string warnings; these are not manuscript
  reference errors.
- `git diff --check` passes.
- Main pages were rendered. Table 1 and Table 2 are on page 8; the conclusion and references
  start on page 9; the framework figure is on page 4. The supplement's new §14, budget/risk
  tables, E6 matrix and integration algorithm were rendered and checked for truncation
  (pages 8, 10 and 12).
- Round-five checks: 18/18 reference semantics (`round5_math_checks.json`), 7/7 paper scalar
  checks, 211 evaluator-parity cases with 0 mismatch, and 8 contract probes. These are
  formula/text/read-only checks, not benchmark results.
- Non-fatal engine warnings remain: invalid UTF-8 comments in `lineno.sty`/`algorithm.sty`,
  Times-family substitutions under XeTeX, and included PDF 1.7 figures versus output PDF 1.5.
  They are not manuscript reference errors.

## Assets and blockers

- The local VCSL snapshot at `/Users/gzhlaker/Downloads/VCSL` has 12,254 ISC features
  (4,418,396,160 bytes), 41,798 validation pairs and 54,630 test pairs; metadata hashes still
  match the audit.
- It contains **no source videos** (0 `.mp4/.mkv/.avi/.webm/.mov` files), no verified
  feature-index-to-frame map, no validated Visual Jev/VideoJev weights and no API credential.
  The machine is an Apple M2 arm64 with no CUDA GPU.
- The prototype HEAD remains `fdc3362b2418b316e16d6dfd68435e40c1b1afb8` (clean). The new
  margin, fusion selector, `Conn` and zero-floor rules are not implemented there; only
  `scripts/round5_reference.py` implements the paper-side reference semantics.
- Consequently E6-A/F/E6-J, E1/E3 on a frozen core, an independent audit and the full campaign
  were not run. The stop conditions in the round-five plan are triggered (no verified frame
  map; no labels/audit; no visual backend).

## Template and page budget

The local package is the **CVPR 2026 author kit**, with `confYear=2027` for the draft label.
It is not certified as the official final 2027 kit. The
[2027 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) lists registration on
2026-11-10, papers on 2026-11-16 and supplements on 2026-11-23 (AOE); the AuthorGuidelines URL
still returned 404 on 2026-10-20. Recheck the official kit and policies before submission.

The body ends on page 9, about 8.5 pages, half a page over the fallback 8-page target. The
remaining cut candidates, in order: (1) move the timing subsection to the supplement; (2)
compress the action-risk ledger to three lines plus a supplement reference; (3) move the E6 row
descriptions into the supplement matrix. Do not shrink the framework figure below legibility or
hide the pending-result markers.

## Files and regeneration

- Paper: `main.tex`, `preamble.tex`, `main.bib`, `sec/*.tex`.
- Supplement: `supplementary.tex` (separate entry point). It holds notation/validity, sampling
  derivations, the implementation audit, metric details, diagnostics, the augmented table, the
  full two-decision specification, budget and risk tables, the E6 matrix and the integration
  algorithm.
- Fig. 2 source: `scripts/generate_framework.py`; outputs SVG/PDF/PNG. It is the only figure
  compiled into the main text.
- All figures: `scripts/generate_paper_placeholders.py`, which delegates Fig. 2 to the
  dedicated generator. No experimental values are generated.
- Round-five evidence: `evidence/round5_review.md`, `round5_assets.json`,
  `round5_source_snapshot.json`, `round5_math_checks.json`, `round5_paper_math_checks.json`,
  `round5_evaluator_parity.json`, `round5_contract_probes.json`,
  `round5_prototype_tests.log`.
- Execution plan for this round: `FastVCL_CVPR2027_第五轮论文优化方案.md`.

The prototype remains unchanged. Zero-floor recurrence, distinct-both-axis support, zero output
margin, strongest-competitor margin, fusion selector and `Conn` are proposed semantics
requiring implementation and controlled comparison. The optional `seltive model` has no
validated backend, frame map or action threshold. No formal accuracy, speed, GPU or verifier
benefit is established by this build.
