# Claims Ledger

Every claim that appears in the paper must have an entry here. Grades follow the execution
plan: `SOURCE_VERIFIED`, `PROPOSED`, `IMPLEMENTED_UNVALIDATED`, `PILOT_ONLY`,
`BENCHMARK_VERIFIED`, `MISSING`, `CONFLICT`.

**Global verdict (round 6, 2026-10-25): still no claim in this paper is
`BENCHMARK_VERIFIED`.** The definitional repairs C25–C29 are reference-checked in
`scripts/round6_reference.py` (35/35 deterministic probes), but they are not implemented in
the prototype and no dataset, model or GPU run exists. The novelty gate (E1) has not been
run; the ledger therefore carries an explicit **`NOVELTY_GAP`** marker (see C18).

| ID | Claim (paper wording, abbreviated) | Grade | Evidence / basis | What would refute it | Allowed placement |
|---|---|---|---|---|---|
| C1 | VCL takes a video pair and outputs corresponding temporal intervals; evaluation is segment-level copy-overlap | `SOURCE_VERIFIED` | VCSL paper §4.2 "New Metric" (Eqs. 3–7, projection-length P/R product; verified in the CVF PDF); `metric/eval.py`; prototype `evaluate.py`. **Correction:** the execution plan's "§3.2" is wrong; §3.2 is not the metric section. | a different official metric definition | Intro, Related, Exp. |
| C2 | The official dataset-level score is the harmonic mean of macro $\bar P,\bar R$, where each per-pair value is the product of the two axis coverage ratios and entries equal to 1 are excluded from the means | `SOURCE_VERIFIED` | `metric/eval.py::precision_recall`, `evaluate_overall`; ported in `fastvcl/evaluate.py` | a different evaluator being used for a table | Exp. §metric |
| C3 | Local VCSL `val` has 41,798 pairs and is 100% positive | `SOURCE_VERIFIED` | row count 41,799 incl. header; 0 missing GT keys; SHA-256 `f7065467…` | a different val file | Exp. data |
| C4 | Local VCSL `test` has 54,630 pairs, of which 27,315 have no GT key and are treated as negatives under the audited local loader convention | `SOURCE_VERIFIED` | key-missing count 27,315; CSV SHA-256 `b52c1b5f…`; `VCSL_ASSET_AUDIT.md` | official re-release or different negative convention | Exp. data |
| C5 | "Training-free" means no new trainable downstream parameters; ISC is pretrained; thresholds are tuned on val | `SOURCE_VERIFIED` | config; VCSL/ISC descriptions; per-method threshold protocol | a learned component being introduced | Abstract, Intro, Exp. |
| C6 | Fixed-stride coarse matching remains $\Theta(MN)$; it saves memory, not arithmetic order | `PROPOSED` (elementary derivation) | $|I_A||I_B|\approx MN/(s_As_B)$ | a sub-quadratic candidate generator | Method complexity |
| C7 | Under direct offset addressing the tube DP is $O(L_rW_r)$ per path | `PROPOSED` | predecessor is $j-\Delta j$ at row $i-\Delta i$, $O(1)$ lookup | a required search that cannot be indexed | Method complexity |
| C8 | The prototype's predecessor scan is $O(P_rL_rW_r^2)$ | `IMPLEMENTED_UNVALIDATED` | `_step_predecessors` loops over all `n_cols` for `(1,2)/(2,1)` | a code change to direct indexing | Method complexity, Suppl. |
| C9 | With zero phases, $I^8\subset I^4\subset I^2$; coarser grids add no coordinates and merging must de-duplicate by $(i,j)$ | `SOURCE_VERIFIED` (set algebra) + `IMPLEMENTED_UNVALIDATED` (dedup) | `build_sampling_plan`, `sparse_mnn_detailed` merge | phases not zero, or different strides | Method §3.2, E2 |
| C10 | A track with $h$ anchors at distinct A times occupies at least $(h-1)s+1$ frames ($i_{\max}-i_{\min}\ge(h-1)s$); a shorter copy cannot supply all $h$ internal A-grid times; final detection is not ruled out | `PROPOSED` (proof immediate) | pigeonhole on the arithmetic progression | anchors not on one grid | Method §3.2, Limitations |
| C11 | Top-$K$ anchors are not independent temporal evidence; support counts distinct projected times | `SOURCE_VERIFIED` (def.) + `IMPLEMENTED_UNVALIDATED` | `min(unique A, unique B)>=min_inliers` | — | Method §3.3 |
| C12 | $\min(\mathrm{IoU}_A,\mathrm{IoU}_B)$ keeps a one-to-many copy that an A-only IoU would delete | `PROPOSED` (worked example) + `IMPLEMENTED_UNVALIDATED` | `dedupe_segments(axis="min")`; tests `test_overlap_on_a_but_a_different_b_is_kept` | a case where it deletes a legal copy | Method §3.6 |
| C13 | TransVCL chunks long videos at $\le1200$ frames and reassembles offsets; it does not allocate the full pair matrix | `SOURCE_VERIFIED` | `run.py::load_features_list` and offset loop | a different TransVCL inference entry point | Related, Exp. protocol |
| C14 | SPD is a learned detector on similarity maps, not a zero-training geometric baseline | `SOURCE_VERIFIED` | Jiang et al., ACM MM 2021 (defines "Similarity Pattern Detection"); VCSL re-implements SPD as one of five baselines in §5.1 and describes it in §2.2. **Correction:** the execution plan's "VCSL §5.2 explicitly presents SPD" is false; the string does not occur in VCSL, and §5.2 is not an SPD section. The classification (learned, not zero-training) is nevertheless correct. | a different SPD description | Related, Table 1 |
| C15 | The prototype local DP is not zero-floored; the proposed recurrence is | `CONFLICT` | code at `tube.py::local_dp`; deterministic 15-row diagnostic (see `implementation_status.md`) | a code change, or an argument that the two are equivalent | Method §3.5, Suppl. |
| C16 | No frozen VCSL benchmark result exists for FastVCL; all main-table values are pending | `MISSING` | run summaries: incomplete 8,075/41,798; near-complete run with 1 ERROR; no frozen protocol; no test run | a complete, zero-error, frozen run | Abstract, Exp., Conclusion |
| C17 | No GPU/CUDA result exists; the kernel has never executed on hardware | `MISSING` | `GPU_VERIFICATION.md` (`BLOCKED_GPU_RUNTIME`); 10 CUDA tests skipped | a real-GPU verification log | Exp. efficiency |
| C18 | The increment of FastVCL over the Simple Sparse-to-Band baseline is **unproven** | `MISSING` → **`NOVELTY_GAP`** | E1 not run; no controlled comparison exists | controlled E1 utility evidence plus a separate novelty comparison with prior work | Intro contribution, Exp. E1, Conclusion |
| C19 | The only existing real-data diagnostics are 20–1,000-pair development runs and one near-complete val run with 1 ERROR | `PILOT_ONLY` | §3 of `implementation_status.md` | a complete frozen run | Suppl. only, labelled |
| C20 | Dual-axis gap splitting prevents merging two same-slope copies across a long silence | `PROPOSED` + `IMPLEMENTED_UNVALIDATED` | `_split_runs`; `test_segments_do_not_cross_a_long_low_quality_break` (segment layer) | a case where the split harms a legal long copy | Method §3.3, E4 |
| C21 | A tube can only refine inside its own coverage; uncovered copies cannot be recovered | `PROPOSED` (definition) | tube definition | — | Method §3.4, Limitations |
| C22 | Thresholds must be tuned per method because scores are uncalibrated and semantically different | `SOURCE_VERIFIED` | `METHOD_DECISIONS.md` D5; TransVCL objectness vs. local score | a calibrated common score | Exp. protocol |
| C23 | The `dev1000` metrics file is computed over 200 pairs, not 1,000 | `CONFLICT` (verified) | `metrics.json n_pairs=200` vs `run_summary n_selected=1000` | a re-score over 1,000 | internal only; never a table |
| C24 | The near-complete val run (41,797 scored, 1 ERROR) is not a benchmark-verified result | `PILOT_ONLY` | `run_summary.json`, `metrics.json` | zero-error frozen rerun | Suppl. status only |
| C25 | `Conn` certifies a bridge only when the backtracked path starts at a valid left support node and ends at a right support node; it cannot restart, and only the best path is tested | `PROPOSED` (reference-checked) | `scripts/round6_reference.py::connection_path`; 35/35 probes in `round6_math_checks.json`, including the planning counterexamples | any accepted path whose endpoints are not support nodes, or that starts inside the region | Method, Suppl. |
| C26 | Coverage is interval-based, $\min(d_A/s_A,d_B/s_B)$ over the selected endpoint spans, not path length; skipped indices lower it | `PROPOSED` (reference-checked) | same reference and probes; small-grid enumeration agrees with the DP counters | a gap-spanning path that reports coverage 1 | Method, Suppl. |
| C27 | Boundary compatibility is per axis: A-to-B residuals compare with $\kappa_B$ and B-to-A residuals with $\kappa_A$; a pooled maximum is invalid | `PROPOSED` (reference-checked) | reference `fusion_edge`; asymmetric-threshold probe is rejected | a pooled-threshold acceptance under asymmetric $\kappa$ | Method, Suppl., E6-F |
| C28 | Fusion merges one original disjoint pair at a time in frozen selector order, consumes both members, adds no model call and triggers no set-level re-verification | `PROPOSED` (reference-checked) | reference merge probes: three-fragment chain yields one merge; shared-member edge is refused; failed reconstruction retains members | an unaccounted second merge or acceptance of a consumed member | Method, Suppl., E6-F |
| C29 | With $q_A,q_F$ logical questions, evidence is bounded by $3q_A+5q_F\le5B$ paired positions and $6q_A+10q_F\le10B$ slots; the fixed-allocation $3B_A+5B_F$ is only a special case (44 is not the worst case at $B=12$) | `PROPOSED` (arithmetic + probe) | `round6_reference.py` budget envelope; `eq:evidence-bound`; transfer probe at $B=12$ gives 60/120 | an accounting log exceeding these bounds, or a claim that 44 is the upper bound | Method, Suppl. |

## Round 6 status (2026-10-25)

- **Closed as specification/reference:** P0-1 anchored `Conn`, P0-2 interval coverage, P0-3
  per-axis geometry and one-pair merging, P0-4 transfer-aware budget bound, P0-5 official
  2027 template and LLM statement. The manuscript, supplement and `round6_reference.py`
  agree; 35/35 deterministic probes pass. These checks are definitional, not empirical.
- **Still open:** prototype implementation of the new core (W6-1), E1/E3 pilot (W6-2),
  frame map/backend (W6-3), action audit (W6-4), full campaign (W6-5). C15 remains
  `CONFLICT`, C16/C18 remain `MISSING`, C19/C24 remain `PILOT_ONLY`.
- **Not changed by this round:** no table value, no model call, no GPU timing, no benchmark
  claim. See `evidence/round6_review.md` for the execution record.

## Novelty gate (must be resolved before submission)

The candidate mechanisms to investigate are: (i) finite-tube zero-floored local alignment with
tube-relative predecessor addressing, (ii) dual-axis support/gap-splitting, (iii)
min-IoU one-to-many-preserving de-duplication, and (iv) an iso-budget sampling analysis.
Each is a combination or a careful application of known tools (Mutual NN, RANSAC,
Smith-Waterman, banded DP). **None has been shown to beat the Simple Sparse-to-Band
baseline at equal dot-product budget.** The paper therefore states the research question and
the falsification protocol, and marks the mechanism-level increment as an open hypothesis.
If E1 shows no gain, the honest final action is to retitle/reframe as a negative-result or
trade-off study and keep the unresolved novelty finding in the internal ledger; it must not be papered over
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

## User-requested selective verification extension (proposed, outside core evaluation)

| ID | Claim | Grade | Basis | Refutation / status |
|---|---|---|---|---|
| C29 | The optional `seltive model` (JEV) uses selected candidates and original A/B frame context; unselected/uncertain/failed cases retain core output | `PROPOSED` | Main framework figure (Fig. 1), Method selective-verification subsection, supplementary E6 | Backend, frame mapping, selection and decisive-verdict fusion remain open; not in core comparisons. User instruction overrides the old prohibition. Preserve the module. |

## Round-two corrections and added claims (2026-10-18)

| ID | Claim | Grade | Basis / limitation |
|---|---|---|---|
| C30 | Ordinary nonempty perfect overlap remains below 1 due to `+1e-6` on both axis denominators | `SOURCE_VERIFIED` + scalar check | Both local evaluator sources inspected; 10-by-20 identical boxes give 0.9999998500000175. Prior paper/supplement assertion of automatic exclusion was wrong. No actual NumPy evaluator execution in this round. |
| C31 | Gap splitting followed by re-validation may reduce accepted proposal count | `SOURCE_VERIFIED` (algorithm reasoning) | Five anchors split into runs of 2 and 3, each below support minimum 5; scalar counterexample. |
| C32 | Nested {2,4,8} and stride 2 do not automatically have equal dot-product budgets | `SOURCE_VERIFIED` (counting) | 64-by-64, one direction: 1,344 vs 1,024; actual two-direction/tie work must be logged. |
| C33 | A-only overlap example does not distinguish min-IoU from area IoU | `SOURCE_VERIFIED` (geometry) | Both keep disjoint reference intervals; E4 must use cases where rules differ. |
| C34 | Candidate-envelope recall is a box diagnostic, not dense correspondence coverage | `PROPOSED` definition | GT supplies interval boxes; an envelope overlap does not prove a legal tube path. |
| C35 | Post-localization confidence-only sweeps do not generally reduce upstream work | `SOURCE_VERIFIED` (timing boundary) | Quality–cost points must vary compute settings or measure an actual early-exit policy. |
| C36 | Proposed margin and distinct-support rules differ from prototype | `CONFLICT` | `segments.py::extract_segments` uses boundary margin and stored A entries; method now states proposed zero margin and distinct support explicitly. |

`round2_math_checks.json` contains formula-level checks, not benchmark evidence or prototype
acceptance. No claim has become `BENCHMARK_VERIFIED`. The current bibliography review is
not exhaustive; lack of a matching title is never proof of novelty.

## Round-three corrections and checks (2026-10-18)

Round-three update to C30: the evaluator port now has a function-level parity check on 211
synthetic cases (0 mismatch), including the `+1e-6` denominators, exact-1 sentinels, macro
counts, the `conf=0` branch and a five-row status/accounting case. It is still not a full
file-level dataset run.

| ID | Claim | Grade | Basis / limitation |
|---|---|---|---|
| C37 | Feature validity uses a shared `1e-8` norm threshold; the old paper value `1e-12` was not the code value | `SOURCE_VERIFIED` (code) + paper corrected | `sparse.MIN_ROW_NORM`, `io.valid_row_mask`, `tube` reuse; rows in `(1e-12,1e-8]` are invalid in code. |
| C38 | The RANSAC draw imposes no minimum A separation; `min_a_span` is a post-fit run constraint | `SOURCE_VERIFIED` (code) + paper corrected | `trajectory._ransac_once` rejects only equal A; `_emit_tracks` enforces span 4, B span 8, support 5. |
| C39 | The prototype has no restart when a legal predecessor exists and keeps negative continuations; a negative cell can be a predecessor but not a traceback start | `SOURCE_VERIFIED` (code + probe) | `tube.local_dp`; `contract_probes.json`: weak prefix unreachable, `H=[0.35,-0.15,0.20]` on strong–weak–strong. |
| C40 | The prototype's output margin is counted in matched path rows and changes the score | `SOURCE_VERIFIED` (code + probe) | `segments.extract_segments`; margin 0 gives `[9,12)`, margin 2 gives `[8,14)` and score 0.6675. |
| C41 | The prototype counts stored A-anchor entries, not distinct times in both intervals | `SOURCE_VERIFIED` (code + probe) | Two duplicate A anchors pass `min_segment_anchors=2`; one distinct anchor fails. |
| C42 | Confidence thresholding is evaluator-side; the core pipeline writes all post-dedup segments | `SOURCE_VERIFIED` (code) + paper corrected | `pipeline._run_stages`; `evaluate.apply_conf_filter`; legacy `conf=0` skips filter and cast. |
| C43 | F1 uses a `+1e-6` zero guard, and de-duplication ties use start coordinates | `SOURCE_VERIFIED` (code) + paper corrected | `evaluate.py` F1 expression; `segments.dedupe_segments` sort key. |
| C44 | The evaluator port matches the reference on 211 synthetic function-level cases | `SOURCE_VERIFIED` (execution) | `evidence/evaluator_parity.json`; not a dataset/file-level certification. |
| C45 | Eight contract behaviours are executable and documented | `SOURCE_VERIFIED` (execution) | `evidence/contract_probes.json`; no benchmark result. |

No claim in this ledger becomes `BENCHMARK_VERIFIED` in this round. The paper fixes (C37,
C38, C42, C43) are specification corrections, not code fixes. The code differences C39–C41
remain unresolved.

## Round-five execution (2026-10-20)

Round five did not upgrade any empirical claim. It replaced the old second-rank margin with a
strongest-competitor margin, fully specified the two intervention points and their budget and
risk accounting, split the core and augmented tables, and recorded that the local snapshot has
no source video, visual backend or GPU. C29's post-localization-only wording is superseded in
scope by C46; the module name and the proposed status remain.

| ID | Claim | Grade | Basis / limitation | What would refute it |
|---|---|---|---|---|
| C46 | One shared `seltive model` is inserted before fitting ($\Anch_0\to\Anch_1$) and after candidate extraction ($\mathcal C_0\to\mathcal Y$); off/shadow must match core item by item, on mode only promises per-item fallback | `PROPOSED` | Main Method §3.2, supplement §14, framework figure, `round5_math_checks.json` text checks | an implementation that changes unselected/failed items or a shadow mismatch |
| C47 | The selector margin is the minimum of the A- and B-side differences to the strongest competitor after removing the current match; a missing side is neutral rank 1/2 | `PROPOSED` + scalar check | `eq:margin`, supplement `eq:s-margin`, `scripts/round5_reference.py`; top-1, second-rank, singleton, tie and cross-plan cases | a different competitor pool or a case where the rule is undefined |
| C48 | First-version fusion uses disjoint C0 pairs, gap caps, boundary-map agreement, connector slope, grouped round-robin selection and a bounded Conn region/path; accepted merges consume members and do not propagate | `PROPOSED` + reference check | Main Method, supplement §14, five edge cases and Conn path cases in `round5_math_checks.json` | an executable variant that behaves differently or an experiment showing no useful opportunity |
| C49 | Decision accounting is $B_A=\lfloor2B/3\rfloor$, 3 anchor frame pairs and 5 fusion frame pairs, cache hits count, retries are off by default and worst case is $B+R$, and connection cells are charged | `PROPOSED` | Main Method budget paragraph, supplement Table 6, `evidence_frame_pairs(12)=44` | a run that reports a different denominator or hides failed attempts |
| C50 | Risk is reported as true-anchor deletion, deletion action error, wrong-fusion, coverage/abstention and final effect; zero-error 95% bound is $1-0.05^{1/n}$ and needs at least 299 effective trials for 1% | `PROPOSED` analytic | Main Experiments §4.4, supplement risk ledger, scalar check of 150/299/300 | correlated samples treated as independent, or a different denominator |
| C51 | The revised main body is about 8.5 pages (10 pages total, references from page 9); the 8-page target is not met | `MISSING` (layout status) | `main.pdf`, `round5_source_snapshot.json` | a further cut that reaches 8 pages and is visually verified |
| C52 | The local snapshot contains ISC features and labels but no source videos, no verified frame map, no visual weights and no CUDA GPU; no visual call was made | `MISSING` | `round5_assets.json`, filesystem scan, prototype environment record | a verified video/frame manifest and a runnable backend |
| C53 | The prototype is unchanged and its 646-test suite passes; the new margin, fusion selector, Conn and zero-floor variants are not implemented there | `CONFLICT` / `MISSING` | `round5_prototype_tests.log`, prototype HEAD `fdc3362`, reference module only | a source change and a controlled comparison |
| C54 | The E1 novelty gate and all benchmark cells remain open | `MISSING` → `NOVELTY_GAP` | No frozen core or augmented run; all table cells remain `\TODO{PENDING}` | a complete zero-error frozen campaign and E1 |

The round-five reference checks are formula- and text-level only. The 646-test rerun shows no
regression in the existing prototype; it does not validate the proposed rules.
