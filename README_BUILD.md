# Build record and draft status

Last checked: **2026-10-28, round 7 (recovery and boundary decisions)**. This is a research
draft with pending experiments, not a submission-ready paper. The main entry point is 9 pages:
the body ends on page 7, references occupy pages 8--9, and the mandatory LLM Usage Statement is
on page 9. The supplement is a separate 4-page entry point. No ladder row was executed, no JEV
model was called, and no GPU kernel was run.

## Current outputs

| Entry point | Exit | PDF | Pages | Body end |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 9 | conclusion ends on page 7; references start on page 8; LLM statement on page 9 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 4 | full supplement |

Both PDFs are git-ignored build products; Overleaf and the local commands below regenerate
them.

## What changed in round 7

- **New story.** The paper is now about recovering copies that the strict anchor stage misses
  and refining segment boundaries with structured decisions, not about anchor filtering or
  box fusion. Title: *FastVCL: Recovering Missed Copies and Refining Boundaries with Structured
  Decisions*.
- **Method rewritten against the frozen `add-jev` code.** Strict branch, shadow RANSAC
  (inliers 5 -> 3, tracks 8 -> 12, same anchors), hard gate, Noul admission at 0.75,
  boundary candidates C0--C4 with feature revalidation, Choice at 0.65, and dual-axis dedupe
  (`IoU_A >= 0.8` AND `IoU_B >= 0.8`). The DP is written with the actual asymmetric restart
  rule: a legal predecessor keeps a negative continuation, an isolated cell starts at
  `max(0, r)`.
- **Ordering stated honestly.** `BoundaryStage.refine` runs per track inside `_run_tubes`
  (`fastvcl/core/localize.py:546-549`) before merge/dedupe (`localize.py:492-499`). The text,
  caption and figure say so, and the text records the consequence: a call can be spent on a
  segment that dedupe later collapses.
- **Experiments rewritten as a protocol.** Table 1 is the VCSL/VCDB main comparison (VCDB
  left blank because it was not evaluated); Tables 2--3 are the recovery and boundary ablations,
  every cell pending; Tables 4--5 are the historical single-factor VCSL runs. The 25-row
  workbook transcription is in the supplement. RQ1--RQ3 falsifiers, controls C1--C8 and the
  metric definitions are stated; no accuracy or latency gain is claimed.
- **Figure regenerated.** `scripts/generate_round7_framework.py` draws (a) strict, (b) shadow
  recovery, and (c) boundary choice before the dual-axis merge, in a plain serif style; the
  disabled independent loose sparse branch is omitted and noted in the caption/figure note.
- **Supplement rebuilt.** 4 pages: evidence grades, reference configuration, strict branch and
  DP, recovery gate, boundary construction, dedupe, historical diagnostics, ladder, evaluation
  protocol, reproducibility and limitations.

## Checks and visual review

- Manuscript scalar checks: **8** formula-level checks pass
  (`evidence/round7_paper_math_checks.json`): score weights, asymmetric DP restart, dedupe
  conjunction, call budget, grid size and threshold ordering.
- Both builds exit 0 with no overfull boxes and no undefined references/citations. Font
  substitution warnings under XeTeX and PDF-version warnings for included figure PDFs remain
  non-fatal.
- Pages were rendered and checked: main pages 1, 3, 6 and 7; supplement page 1. Tables and the
  framework figure are not truncated. Tables 1--5 use footnotesize/scriptsize with fixed
  `tabcolsep`; the supplement historical table is full width.
- `git diff --check` passes.
- All checks above are semantic, formula or read-only checks. None is a dataset, model, GPU or
  benchmark result.

## Reproduce the build

Engine: Tectonic 0.17.0, XeTeX backend. The project-local cache avoids network downloads; use
`TECTONIC_CACHE_DIR`, not a changed HOME directory. If `--only-cached` reports a missing font,
run once without it and re-check the cache.

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex

python3 scripts/generate_round7_framework.py
python3 scripts/check_paper_semantics.py --output evidence/round7_paper_math_checks.json
git diff --check
```

Page count without a PDF library:

```bash
gs -q -dNOSAFER -dNODISPLAY -c "(main.pdf) (r) file runpdfbegin pdfpagecount = quit"
```

Raster review of a single page:

```bash
gs -q -dNOSAFER -sDEVICE=png16m -r120 -dFirstPage=6 -dLastPage=6 \
   -sOutputFile=/tmp/p6.png main.pdf
```

On another machine, obtain the required Tectonic bundle normally before using
`--only-cached`. The manuscript and scalar checks use only the standard library.

## Template and page budget

- The official `author-kit-CVPR2027-v1-latex.zip` was downloaded on 2026-10-25 from
  <https://media.eventhosts.cc/Conferences/CVPR2027/author-kit-CVPR2027-v1-latex.zip> with
  SHA-256
  `7271bdbb0d2f20043b101c3bb10cba67a8c7f2711f0067b395f9f27451c43121`.
  Its `cvpr.sty` is byte-identical to this repository's
  (`1cd7f434b13d41c475df4a1901a5d82d9ca8b80b8cf6205dc4602a5c164286b4`) and
  `ieeenat_fullname.bst` is byte-identical as well
  (`e38e6166bd7b1e6d23a1b79dcdb55c656e4fcdbe91bdf6b50d827e6b5d1aacfc`). `preamble.tex` is
  project-specific by design.
- The CVPR 2027 guidelines allow eight body pages including figures and tables; extra pages
  hold references and the mandatory LLM Usage Statement. The body currently ends on page 7,
  leaving room for one more page of text before the limit.
- `microtype` remains disabled; no font size or margin was changed to gain space.

## Assets and blockers

- The local VCSL snapshot at `/Users/gzhlaker/Downloads/VCSL` has 12,254 ISC features. It
  contains **no source videos**, no verified feature-index-to-frame map, no validated
  Visual Jev/VideoJev weights and no API credential. The machine is an Apple M2 arm64 with no
  CUDA GPU.
- The FastVCL `add-jev` branch is at `7c04959` and implements the frozen pipeline used by the
  paper. The ladder (F0--F3, C1--C8) requires a JEV backend and the full split; neither was
  available, so no ladder row was run.
- Tables 4--5 and the supplement table come from `evidence/round7_no_jev_experiments.csv` and
  `evidence/round7_workbook_audit.json` (25 rows, VCSL test split). No external baseline is
  tabulated: published numbers use different features, pair counts and metrics and were not
  rerun under this protocol. VCDB was not evaluated.

## Files and regeneration

- Paper: `main.tex`, `preamble.tex`, `main.bib`, `sec/*.tex`.
- Supplement: `supplementary.tex` (separate entry point).
- Figure source: `scripts/generate_round7_framework.py`; outputs `figures/framework.svg`,
  `.pdf`, `.png`. It is the only figure compiled into the main text.
- Round-seven evidence: `evidence/round7_config_evidence.json`,
  `evidence/round7_paper_math_checks.json`, `evidence/round7_planning_snapshot.json`,
  `evidence/round7_historical_experiments.md`, `evidence/round7_no_jev_experiments.csv`,
  `evidence/round7_workbook_audit.json`.
- Execution plan for this round: `FastVCL_CVPR2027_第七轮论文修改方案.md`.

No benchmark result is established by this build.
