# Build record and current draft status

Last checked: **2026-11-08 — policy-guided dual-pathway revision**.

The current manuscript follows the Overleaf title and abstract from commit
00ded7723b12ec811f65d76c0e184e952d1f83df. The title command and entire abstract file
are unchanged, including the abstract's original end-of-file bytes.

The main text, framework, experiments, conclusion, and supplement now describe a front-end
policy selecting between a trainable encoder / learned-similarity / 2D-detector main branch
and a direct-similarity / anchor / RANSAC acceleration branch. Earlier round-specific evidence
and scripts are historical artifacts and do not validate this architecture.

## Evidence status

This is a research draft. The new policy, complete trainable main branch, and combined system
have not been trained or benchmarked in the available records. New comparison and ablation
tables are explicitly pending. The fixed abstract's competitive-accuracy and significant-speedup
claims still require experimental evidence.

All 25 historical workbook rows remain in the supplement; eight selected rows appear in the
main paper. Their numerical values were checked against
[evidence/round7_no_jev_experiments.csv](evidence/round7_no_jev_experiments.csv).
This checks transcription, not original predictions, configurations, evaluation, or timing.

The policy input, cost-aware supervision, training schedule, geometric interval conversion,
and conditional runtime model are proposed design specifications. Main-branch backbones,
training settings, checkpoints, and new evaluation runs remain outstanding.

## Build and visual checks

| Entry point | Exit | Pages | Layout |
|---|---|---|---|
| main.tex | 0 | 8 | body and references end on page 7; LLM statement on page 8 |
| supplementary.tex | 0 | 4 | configuration, supervision, evaluation details, historical table |

- Tectonic 0.17.0, cached XeTeX build; both entry points compile.
- No overfull boxes, undefined references, or undefined citations.
- Existing nonfatal package UTF-8/font-substitution warnings remain. Figure PDF 1.7 exceeds
  the engine's default PDF 1.5 setting and produces a nonfatal inclusion warning.
- Main pages 1, 2, 6, and 7 and supplement pages 1, 2, and 4 were visually reviewed.
- Protected-content equality, citation keys, local references, and historical values were
  checked; see [the audit](evidence/policy_revision_audit.json).
- Git whitespace validation passes.
- No dataset inference, model training, or performance measurement was run.

Both output PDFs are git-ignored build products. Overleaf regenerates them from the source.

## Build commands

Run from the repository root:

~~~bash
python3 scripts/generate_policy_framework.py
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex
git diff --check
~~~

Figure generation requires Python's standard library and rsvg-convert. SVG/PDF/PNG are
committed; Overleaf does not need to execute the Python script.

The old check_paper_semantics.py and round-specific checks describe older designs and must
not be presented as validation of this revision. Old generators can overwrite the current
framework. Use [generate_policy_framework.py](scripts/generate_policy_framework.py).

## Protected content

- Title: *FastVCL: Policy-Guided Dual-Pathway Network for Fast Video Copy Localization*
- Exact title-command SHA-256:
  29400bbdc792fce86103793c7f9b88ca073b4174316aa053476b2b4fe7e83443
- Entire sec/0_abstract.tex SHA-256:
  59165b0458966037c10777911c9dbe98fad7bd23bfda7e85c5c0a7ca41622823

See [revision notes](evidence/policy_revision_notes.md) for design changes and verified
reference sources. Official template files and formatting parameters were not modified.
