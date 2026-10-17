# Build Record and Template Status

## 1. Template status (not the official CVPR 2027 kit)

This project is built on the **CVPR 2026 author kit** (`cvpr.sty`, review mode) as a
fallback. `main.tex` sets `\confYear{2027}` and `\confName{CVPR}` so that the draft is
labelled for the target venue, but **this is not the official CVPR 2027 author kit**. The
2027 kit must be dropped in and the page limit, anonymity rules and LLM-use policy re-checked
once it is published. Do not claim template compliance in the paper or in any external
message.

The review option is enabled (`\usepackage[review]{cvpr}`), which replaces the author block
with ``Anonymous CVPR submission'' and adds line numbers. The source deliberately contains a
generic anonymous author field; no real name, institution, email, repository URL or machine
path is present.

## 2. Toolchain and commands

| Item | Value |
|---|---|
| Engine | Tectonic 0.17.0 (XeTeX backend) |
| Bundle | default Tectonic bundle |
| Main file | `main.tex` |
| Supplementary file | `supplementary.tex` (separate entry point) |
| Bibliography | `main.bib`, BibTeX via Tectonic (`ieeenat_fullname.bst`) |

The local sandbox does not allow writes to `~/Library/Caches`, where Tectonic keeps its
bundle. The build below therefore redirects `HOME` into the project. On a normal machine,
`tectonic main.tex` is enough.

```bash
# main paper
HOME="$PWD/.home" tectonic --keep-logs main.tex
# supplementary material
HOME="$PWD/.home" tectonic --keep-logs supplementary.tex
```

Recorded build (2026-10-17):

| File | Exit | Output | Pages | Bytes |
|---|---|---|---|---|
| `main.tex` | 0 | `main.pdf` | 13 | 525,881 |
| `supplementary.tex` | 0 | `supplementary.pdf` | 4 | 85,411 |

No overfull or underfull boxes were reported in either build. There are no undefined
references and no ``??'' in the extracted text.

### Non-fatal warnings

* 24 × ``Trying to include PDF file with version (1.7), which is newer than current output
  PDF setting (1.5)'' — the four vector figures were exported by a newer producer than
  XeTeX's default PDF version. Rendering is unaffected.
* 5 × `lineno.sty:296` and 5 × `algorithm.sty:11` ``Invalid UTF-8 byte or sequence'' — these
  come from bytes inside the style packages, not from the manuscript. The replaced code
  points are comments/formatting and do not affect output.
* `TU/ptm/*` font-shape warnings: `times` is designed for pdfLaTeX and is substituted under
  XeTeX. The PDF remains legible and uses a Times-like serif. If a strict Times match is
  required, switch the engine to pdfLaTeX or add a XeTeX font setup; neither changes the
  content.

## 3. What is in the PDF

* Abstract, Introduction, Related Work, Method, Experiments, Conclusion and Limitations are
  all full English prose, not an outline.
* All four vector figures are included through `\includegraphics`:
  `figures/fig_1_teaser.pdf` (Introduction), `figures/fig_2_framework.pdf` and
  `figures/fig_3_sparse_tracks.pdf` (Method), `figures/fig_4_tradeoff.pdf` (Experiments).
* Three structured tables are included: Table 1 (main comparison), Table 2 (efficiency and
  memory), Table 3 (controlled ablations). Every numeric cell is a placeholder; the captions
  and notes state this in red.
* The supplement contains the implementation audit, hyperparameter table, metric details,
  deterministic DP counterexamples, the log schema and the status of development runs.

## 4. Page budget: over the 8-page limit

The current draft is **13 pages**, of which the body ends on page 12 and the references
occupy the remainder. It therefore exceeds the 8-page body limit of the CVPR template by
about four pages. This is a deliberate draft-stage trade-off: the protocol and the
implementation audit are part of the contribution and were not cut to fit. Before submission,
the following trims are the lowest-risk ones, in order:

1. Move the metric derivation (Section 4.2) to the supplement and keep only the definition
   and the four denominators in the main paper.
2. Compress E0--E5 into one table plus one paragraph each; keep Table 3 as the only ablation
   float.
3. Shorten Related Work to the three paragraphs that matter (VCSL protocol; HV/TN/DP/DTW;
   learned localizers) and move the 2025--2026 list to the supplement.
4. Reduce Fig. 1 and Fig. 3 to 0.8 column width (they are already at 0.92 text width).
5. Move the "Four properties" discussion to the supplement and keep the two that affect H1
   (nesting and the sampling bound).

Do not cut the negative-pair-FAR explanation, the four-denominator paragraph or the
zero-floor/continuation caveat: those are exactly the points that keep the draft honest.

## 5. Anonymity and verification

Checks performed after the final build:

```bash
gs -q -dNOPAUSE -dBATCH -sDEVICE=txtwrite -sOutputFile=/tmp/main.txt main.pdf
grep -inE "$USER|/Users/|Documents/code|github\\.com|@" /tmp/main.txt
grep -n "??" /tmp/main.txt
```

The extracted text contains no user name, no absolute path, no repository URL and no email
address. The review mode suppresses the author block. The same strict grep was run on the
supplementary PDF and returned no hits.

## 6. Files and update workflow

* `main.tex`, `preamble.tex`, `main.bib`, `sec/0_abstract.tex`--`sec/5_conclusion.tex`,
  `supplementary.tex`: paper sources.
* `figures/`: four `.pdf` figures plus `.svg` sources and `.png` previews; `figures/README.md`
  documents their status.
* `evidence/`: seven audit/ledger files (`method_spec.md`, `implementation_status.md`,
  `claims_ledger.md`, `related_work_matrix.md`, `experiment_manifest.md`,
  `experiment_plan.md`, `missing_evidence.md`).
* `scripts/generate_paper_placeholders.py`: regenerates the four schematic figures.

When a frozen run becomes available:

1. Replace the `--` cells in `sec/4_experiments.tex` from that run's `metrics.json` only.
2. Update the figure/table captions to state the run id, number of pairs and four
   denominators.
3. Regenerate Fig. 4 from the real `per_pair_timing.jsonl`; remove the `RESULTS PENDING`
   label only after the points exist.
4. Re-run both builds and re-check anonymity.

## 7. Known limitations of the build

* The 2027 template is not official; page limits and anonymity should be re-checked.
* The font substitution (`TU/ptm`) is cosmetic and due to XeTeX.
* The body is over the 8-page limit; see Section 4.
* The paper reports no benchmark number. That is intentional and is stated in the abstract,
  the experiment section and the conclusion.
