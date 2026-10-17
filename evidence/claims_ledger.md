# Claims Ledger

Every claim that appears in the paper must have an entry here. Grades follow the execution
plan: `SOURCE_VERIFIED`, `PROPOSED`, `IMPLEMENTED_UNVALIDATED`, `PILOT_ONLY`,
`BENCHMARK_VERIFIED`, `MISSING`, `CONFLICT`.

**Global verdict at draft time: no claim in this paper is `BENCHMARK_VERIFIED`.** The
novelty gate (E1) has not been run; the ledger therefore carries an explicit
**`NOVELTY_GAP`** marker (see C18).

| ID | Claim (paper wording, abbreviated) | Grade | Evidence / basis | What would refute it | Allowed placement |
|---|---|---|---|---|---|
| C1 | VCL takes a video pair and outputs corresponding temporal intervals; evaluation is segment-level copy-overlap | `SOURCE_VERIFIED` | VCSL paper §4.2 "New Metric" (Eqs. 3–7, projection-length P/R product; verified in the CVF PDF); `metric/eval.py`; prototype `evaluate.py`. **Correction:** the execution plan's "§3.2" is wrong; §3.2 is not the metric section. | a different official metric definition | Intro, Related, Exp. |
| C2 | The official dataset-level score is the harmonic mean of macro $\bar P,\bar R$, where each per-pair value is the product of the two axis coverage ratios and entries equal to 1 are excluded from the means | `SOURCE_VERIFIED` | `metric/eval.py::precision_recall`, `evaluate_overall`; ported in `fastvcl/evaluate.py` | a different evaluator being used for a table | Exp. §metric |
| C3 | Local VCSL `val` has 41,798 pairs and is 100% positive | `SOURCE_VERIFIED` | row count 41,799 incl. header; 0 missing GT keys; SHA-256 `f7065467…` | a different val file | Exp. data |
| C4 | Local VCSL `test` has 54,630 pairs, of which 27,315 have no GT key and are treated as negatives under the frozen local protocol | `SOURCE_VERIFIED` | key-missing count 27,315; CSV SHA-256 `b52c1b5f…`; `VCSL_ASSET_AUDIT.md` | official re-release or different negative convention | Exp. data |
| C5 | "Training-free" means no new trainable downstream parameters; ISC is pretrained; thresholds are tuned on val | `SOURCE_VERIFIED` | config; VCSL/ISC descriptions; per-method threshold protocol | a learned component being introduced | Abstract, Intro, Exp. |
| C6 | Fixed-stride coarse matching remains $\Theta(MN)$; it saves memory, not arithmetic order | `PROPOSED` (elementary derivation) | $|I_A||I_B|\approx MN/(s_As_B)$ | a sub-quadratic candidate generator | Method complexity |
| C7 | Under direct offset addressing the tube DP is $O(L_rW_r)$ per path | `PROPOSED` | predecessor is $j-\Delta j$ at row $i-\Delta i$, $O(1)$ lookup | a required search that cannot be indexed | Method complexity |
| C8 | The prototype's predecessor scan is $O(P_rL_rW_r^2)$ | `IMPLEMENTED_UNVALIDATED` | `_step_predecessors` loops over all `n_cols` for `(1,2)/(2,1)` | a code change to direct indexing | Method complexity, Suppl. |
| C9 | With zero phases, $I^8\subset I^4\subset I^2$; coarser grids add no coordinates and merging must de-duplicate by $(i,j)$ | `SOURCE_VERIFIED` (set algebra) + `IMPLEMENTED_UNVALIDATED` (dedup) | `build_sampling_plan`, `sparse_mnn_detailed` merge | phases not zero, or different strides | Method §3.2, E2 |
| C10 | A track with $h$ anchors at distinct A times occupies at least $(h-1)s+1$ frames ($i_{\max}-i_{\min}\ge(h-1)s$); shorter segments are unreachable by that grid | `PROPOSED` (proof immediate) | pigeonhole on the arithmetic progression | anchors not on one grid | Method §3.2, Limitations |
| C11 | Top-$K$ anchors are not independent temporal evidence; support counts distinct projected times | `SOURCE_VERIFIED` (def.) + `IMPLEMENTED_UNVALIDATED` | `min(unique A, unique B)>=min_inliers` | — | Method §3.3 |
| C12 | $\min(\mathrm{IoU}_A,\mathrm{IoU}_B)$ keeps a one-to-many copy that an A-only IoU would delete | `PROPOSED` (worked example) + `IMPLEMENTED_UNVALIDATED` | `dedupe_segments(axis="min")`; tests `test_overlap_on_a_but_a_different_b_is_kept` | a case where it deletes a legal copy | Method §3.6 |
| C13 | TransVCL chunks long videos at $\le1200$ frames and reassembles offsets; it does not allocate the full pair matrix | `SOURCE_VERIFIED` | `run.py::load_features_list` and offset loop | a different TransVCL inference entry point | Related, Exp. protocol |
| C14 | SPD is a learned detector on similarity maps, not a zero-training geometric baseline | `SOURCE_VERIFIED` | Jiang et al., ACM MM 2021 (defines "Similarity Pattern Detection"); VCSL re-implements SPD as one of five baselines in §5.1 and describes it in §2.2. **Correction:** the execution plan's "VCSL §5.2 explicitly presents SPD" is false; the string does not occur in VCSL, and §5.2 is not an SPD section. The classification (learned, not zero-training) is nevertheless correct. | a different SPD description | Related, Table 1 |
| C15 | The prototype local DP is not zero-floored; the proposed recurrence is | `CONFLICT` | code at `tube.py::local_dp`; deterministic 15-row diagnostic (see `implementation_status.md`) | a code change, or an argument that the two are equivalent | Method §3.5, Suppl. |
| C16 | No frozen VCSL benchmark result exists for FastVCL; all main-table values are pending | `MISSING` | run summaries: incomplete 8,075/41,798; near-complete run with 1 ERROR; no frozen protocol; no test run | a complete, zero-error, frozen run | Abstract, Exp., Conclusion |
| C17 | No GPU/CUDA result exists; the kernel has never executed on hardware | `MISSING` | `GPU_VERIFICATION.md` (`BLOCKED_GPU_RUNTIME`); 10 CUDA tests skipped | a real-GPU verification log | Exp. efficiency |
| C18 | The increment of FastVCL over the Simple Sparse-to-Band baseline is **unproven** | `MISSING` → **`NOVELTY_GAP`** | E1 not run; no controlled comparison exists | E1 showing a significant gain at equal budget | Intro contribution, Exp. E1, Conclusion |
| C19 | The only existing real-data diagnostics are 20–1,000-pair development runs and one near-complete val run with 1 ERROR | `PILOT_ONLY` | §3 of `implementation_status.md` | a complete frozen run | Suppl. only, labelled |
| C20 | Dual-axis gap splitting prevents merging two same-slope copies across a long silence | `PROPOSED` + `IMPLEMENTED_UNVALIDATED` | `_split_runs`; `test_segments_do_not_cross_a_long_low_quality_break` (segment layer) | a case where the split harms a legal long copy | Method §3.3, E4 |
| C21 | A tube can only refine inside its own coverage; uncovered copies cannot be recovered | `PROPOSED` (definition) | tube definition | — | Method §3.4, Limitations |
| C22 | Thresholds must be tuned per method because scores are uncalibrated and semantically different | `SOURCE_VERIFIED` | `METHOD_DECISIONS.md` D5; TransVCL objectness vs. local score | a calibrated common score | Exp. protocol |
| C23 | The `dev1000` metrics file is computed over 200 pairs, not 1,000 | `CONFLICT` (verified) | `metrics.json n_pairs=200` vs `run_summary n_selected=1000` | a re-score over 1,000 | internal only; never a table |
| C24 | The near-complete val run (41,797 scored, 1 ERROR) is not a benchmark-verified result | `PILOT_ONLY` | `run_summary.json`, `metrics.json` | zero-error frozen rerun | Suppl. status only |

## Novelty gate (must be resolved before submission)

The candidate mechanisms are: (i) finite-tube zero-floored local alignment with
tube-relative predecessor addressing, (ii) dual-axis support/gap-splitting, (iii)
min-IoU one-to-many-preserving de-duplication, and (iv) an iso-budget sampling analysis.
Each is a combination or a careful application of known tools (Mutual NN, RANSAC,
Smith-Waterman, banded DP). **None has been shown to beat the Simple Sparse-to-Band
baseline at equal dot-product budget.** The paper therefore states the research question and
the falsification protocol, and marks the mechanism-level increment as an open hypothesis.
If E1 shows no gain, the honest final action is to retitle/reframe as a negative-result or
trade-off study and keep `NOVELTY_GAP` in the camera-ready notes; it must not be papered over
with new terminology.

## Literature-premise corrections (checked 2026-10-17)

The execution plan contains three bibliographic premises that do not survive checking.
They are corrected here and in the paper; the scientific classification they were used to
support is unchanged.

| # | Plan premise | Verified fact | Consequence |
|---|---|---|---|
| P1 | The VCSL paper is titled "VCSL: Video Copy Segmentation and Localization" | Exact title: "A Large-Scale Comprehensive Dataset and Copy-Overlap Aware Evaluation Protocol for Segment-Level Video Copy Detection" (He et al., CVPR 2022). VCSL is the dataset name, expanded in the abstract as Video Copy Segment Localization. Page numbers conflict between the CVF PDF (21086–21095) and IEEE/Crossref (21054–21063); the bib entry uses the CVF pages. | The paper calls it "the VCSL benchmark" and never quotes the wrong title. |
| P2 | VCSL §5.2 explicitly classifies SPD as a learned detector | SPD is **not** presented in any VCSL section; the phrase "Similarity Pattern Detection" does not occur in the paper. SPD is defined in Jiang et al., ACM MM 2021 ("Learning Segment Similarity and Alignment in Large-Scale Content Based Video Retrieval"), and appears in VCSL §2.2 (related work) and §5.1 (one of five re-implemented baselines). The metric is defined in VCSL §4.2, not §3.2. | The paper cites Jiang et al. 2021 for SPD and cites VCSL for the benchmark/protocol. The classification "learned, not zero-training" is correct. |
| P3 | The pipeline's ingredients are classical and need a strict novelty gate | Confirmed, and stronger than the plan states: RANSAC line fitting on the time plane is already standard in the 2022–2023 challenge matching tracks (SAM, arXiv:2305.15679; VSC 2023 report, CVIU 2024); TransVCL uses dense mutual/dual-softmax matching; Tian et al. (IEEE MultiMedia 2013) already combine cascaded multi-granularity search with a 2D Hough transform; Smith–Waterman/DTW alignment for copies is old. | The paper explicitly cites these as component precedents and claims only the finite-tube formulation, the coverage/refinement separation, the restart analysis and the protocol. `NOVELTY_GAP` remains until E1. |

## Additional claims added after the literature check

| ID | Claim | Grade | Basis | Refutation |
|---|---|---|---|---|
| C25 | Mutual matching, RANSAC line fitting and banded local alignment are individually precedented in VCL | `SOURCE_VERIFIED` | SAM (arXiv 2305.15679), VSC 2023 report (CVIU 2024), TransVCL (AAAI 2023), Tian et al. (IEEE MultiMedia 2013), Smith–Waterman (1981) | a paper showing the combination is itself novel |
| C26 | Sampling-interval efficiency for video copy detection has been analysed before | `SOURCE_VERIFIED` | Chen & Satoh, MMM 2025: longer intervals than 1 fps can preserve/slightly improve accuracy with large speed-ups | a contradictory study |
| C27 | No training-free pairwise VCL paper combining sparse anchors, robust line fit and banded refinement was found in the 2023–2026 window | `PILOT_ONLY` (literature search, not exhaustive) | OpenAlex title/abstract searches for "training-free" + "video copy" and "zero-shot" + "video copy" returned 0; targeted reading of the closest works | a single counterexample paper would invalidate the literature claim (not the method) |
| C28 | The closest recent efficiency system (MLT-Dedup, KDD 2026) is library-scale and learned, not a training-free pairwise localizer | `SOURCE_VERIFIED` | KDD 2026 paper metadata/abstract; sparse clip retrieval + fine frame matching | a training-free pairwise variant with the same design |
