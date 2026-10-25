# Build record and draft status

Last checked: **2026-10-25, round 6 (semantic repair and official-template migration)**. This is a
research draft with pending experiments, not a submission-ready paper. The main entry point is
10 pages: the body ends on page 8, references occupy the rest of page 8 and page 9, and the
mandatory LLM Usage Statement is isolated on page 10. The supplement is a separate 12-page
entry point. No table cell was filled from a new run, no visual model was called, and no GPU
kernel was executed.

## Current outputs

| Entry point | Exit | PDF | Pages | Body end |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 10 | conclusion ends on page 8; references start on page 8 and end on page 9; LLM statement on page 10 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 12 | full supplement |

Both PDFs are git-ignored build products; Overleaf and the local commands below regenerate
them.

## What changed in round 6

- **P0-1 connection certification.** `Conn` is now a separate certification pass: it may be
  seeded only at valid left support nodes, may not restart, and must backtrack to a right
  support node. Only the single best path is tested; failure rejects the edge, and the text
  says the first version does not enumerate all feasible paths. Reused paths pass the same
  endpoint, region, step and quality checks. The planning counterexamples are now rejected.
- **P0-2 coverage and cost.** Coverage is interval-based,
  $\min(d_A/s_A,d_B/s_B)$ between the chosen endpoints, not path length. Skipped indices and
  invalid cells are logged separately, low-score runs are counted on path nodes, and
  `path_nodes`, `dp_cells_visited`, predecessor evaluations and similarity evaluations are
  distinct counters. Failed attempts are charged.
- **P0-3 geometry and merge scope.** Boundary-map residuals are compared per axis
  (A$\to$B against $\kappa_B$, B$\to$A against $\kappa_A$); non-finite thresholds and
  degenerate slopes are rejected, and a single-axis zero gap is invalid. Fusion now merges
  only original disjoint pairs of $\mathcal C_0$ in frozen selector order, consumes exactly
  the two members, adds no model call and performs no set-level re-verification or
  propagation. A failed reconstruction keeps both members.
- **P0-4 budget envelope.** With $q_A,q_F$ logical questions,
  $q_A\le\lfloor2B/3\rfloor$, $q_A+q_F\le B$,
  $N_{\rm paired}\le3q_A+5q_F\le5B$ and $N_{\rm slots}\le6q_A+10q_F\le10B$. The old fixed
  allocation $3B_A+5B_F$ is a special case; at $B=12$ a full transfer permits 60 paired
  positions and 120 slots, not 44. The E6-F "geometry / Conn only" row is listed with
  $Q=0$ model questions and a separate cap on checked edges.
- **P0-5 template and page budget.** Both entry points now use the official **CVPR 2027
  author kit v1** (archive and `cvpr.sty` hashes in `main.tex`); the review header no longer
  shows a Paper ID. The mandatory LLM Usage Statement was added. The body now ends on page 8,
  which meets the eight-page limit without shrinking fonts or changing margins.
- **Figure and evidence.** Fig. 2 was regenerated so the core proposal DP
  (`zero restart`) is visually distinct from the separate two-end `Conn` certification, and
  the fusion box states "pairwise merge · no model call". `evidence/round6_review.md` and the
  round-six JSON artifacts record the checks and the remaining gaps.

## Checks and visual review

- Round-six reference semantics: **35/35** deterministic probes pass
  (`evidence/round6_math_checks.json`), covering both `Conn` counterexamples, endpoint and
  reuse rules, interval coverage, per-axis thresholds, zero-gap handling, chain/shared-member
  merges, the transfer envelope and manuscript-text consistency.
- Manuscript scalar checks: **7** formula-level checks pass
  (`evidence/round6_paper_math_checks.json`).
- Evaluator parity: **211 cases, 0 mismatch**, macro/sentinel/accounting pass
  (`evidence/round6_evaluator_parity.json`).
- Contract probes: all **8** documented prototype behaviours observed
  (`evidence/round6_contract_probes.json`).
- Prototype suite (read-only rerun): **646 tests OK, 10 CUDA tests skipped, 43.101 s**
  (`evidence/round6_prototype_tests.log`). This is regression evidence for the unchanged
  prototype, not validation of the new rules.
- Both builds exit 0 with no undefined references/citations and no overfull boxes. Font
  substitution warnings under XeTeX and PDF-version warnings for included figure PDFs remain
  non-fatal.
- Pages were rendered and checked: main pages 1, 4, 8, 9 and 10; supplement pages 8, 10 and
  12. Tables, the framework figure, the algorithm and the statement are not truncated.
- `git diff --check` passes.
- All checks above are semantic, formula or read-only code checks. None is a dataset,
  model, GPU or benchmark result.

## Reproduce the build

Engine: Tectonic 0.17.0, XeTeX backend. The project-local cache avoids network downloads; use
`TECTONIC_CACHE_DIR`, not a changed HOME directory. If `--only-cached` reports a missing font,
run once without it and re-check the cache.

```bash
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex

python3 scripts/generate_framework.py
python3 scripts/check_paper_semantics.py --output evidence/round6_paper_math_checks.json
cd scripts && python3 -B check_round6_semantics.py --output ../evidence/round6_math_checks.json
cd .. && git diff --check
```

The parity, contract and prototype checks need the NumPy interpreter; they were rerun
read-only in this round:

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py \
    --output evidence/round6_evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py \
    --output evidence/round6_contract_probes.json

cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .
# 646 tests, OK, 10 CUDA tests skipped
```

On another machine, obtain the required Tectonic bundle normally before using
`--only-cached`. The default shell Python still lacks NumPy; the DSH runtime above has NumPy
2.3.5. The manuscript, round-six reference and scalar checks use only the standard library.

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
  hold references and the mandatory LLM Usage Statement. The body currently ends on page 8.
  `microtype` remains disabled (it is commented out in the official preamble too); no font
  size or margin was changed to gain space.
- References start at the bottom of page 8, continue to page 9, and the statement is on page
  10. A future text addition must be offset rather than pushed into page 9.

## Assets and blockers

- The local VCSL snapshot at `/Users/gzhlaker/Downloads/VCSL` has 12,254 ISC features. Summing
  `stat().st_size` gives **4,388,241,152 bytes**; summing `stat().st_blocks*512` gives
  **4,418,396,160 bytes**. These are logical-byte and allocated-block scopes, not evidence of
  a content change. Validation has 41,798 pairs and test 54,630 pairs; metadata hashes still
  match the audit.
- The snapshot contains **no source videos** (0 `.mp4/.mkv/.avi/.webm/.mov` files), no
  verified feature-index-to-frame map, no validated Visual Jev/VideoJev weights and no API
  credential. The machine is an Apple M2 arm64 with no CUDA GPU.
- The prototype HEAD remains `fdc3362b2418b316e16d6dfd68435e40c1b1afb8` (clean). The new
  zero-floor core, distinct support, strongest-competitor margin, fusion selector and `Conn`
  are still **not implemented** there; only `scripts/round6_reference.py` implements the
  repaired paper-side semantics.
- Consequently W6-1/W6-2 (core implementation and the 200-pair pilot), W6-3 (frames/backend),
  W6-4 (action audit) and W6-5 (full campaign) were not run. E6-A/F/J, E1/E3 and the
  independent audit remain unstarted, and no empirical claim is admissible.

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
- Round-six evidence: `evidence/round6_review.md`, `round6_source_snapshot.json`,
  `round6_math_checks.json`, `round6_paper_math_checks.json`,
  `round6_evaluator_parity.json`, `round6_contract_probes.json`,
  `round6_prototype_tests.log`.
- Execution plan for this round: `FastVCL_CVPR2027_第六轮论文优化执行计划.md`.

The prototype remains unchanged. The optional `seltive model` has no validated backend,
frame map or action threshold. No formal accuracy, speed, GPU or verifier benefit is
established by this build.
