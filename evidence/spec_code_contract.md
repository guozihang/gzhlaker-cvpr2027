# FastVCL specification–implementation contract (round 3)

Date: 2026-10-18. Scope: **read-only** audit of the prototype at
`../FastVCL`, commit `fdc3362b2418b316e16d6dfd68435e40c1b1afb8` (tracked work tree
clean), plus the reference evaluator `../gzhlaker_transvcl/metric/eval.py`. No prototype,
reference, dataset or GT file was modified. No benchmark was run.

This document is the item-by-item contract requested by the round-two plan (W1). It records
what the manuscript says, what the code does, where they differ, and which difference is a
**paper fix**, a **proposed but unimplemented rule**, or an **open decision**. It does not
promote any proposed rule to “implemented”.

**Round 6 note (2026-10-25):** this audit predates the round-six repairs of `Conn`, coverage,
per-axis geometry, merge scope and the budget envelope, which live in
`scripts/round6_reference.py` and are checked by `check_round6_semantics.py` (35/35). The
prototype is still at `fdc3362…` and none of those repaired rules is implemented there, so
the `CONFLICT`/`PROPOSED_ONLY` rows below still describe the prototype.

## 0. Evidence labels

| Label | Meaning |
|---|---|
| `MATCH` | Paper definition and observed code behaviour agree for the tested scope. |
| `DIFF` | Paper and code differ; the difference is named below and needs a decision. |
| `PROPOSED_ONLY` | The paper rule is a specification; no corresponding code path exists yet. |
| `OPEN` | No canonical choice yet; must be decided before a run is frozen. |
| `UNTESTED` | Behaviour is consistent with the code read but has no executable probe yet. |

Verification artefacts:

- `evidence/prototype_tests_summary.md` (full local log: `evidence/prototype_tests.log`):
  `646` unit tests, `OK (skipped=10)` (the 10 skips are CUDA tests; no GPU executed). Run with the DSH NumPy Python, see §5.
- `evidence/contract_probes.json`: eight hand-built probes of DP restart, A-range fallback,
  margin, stored-entry support and segment-gap behaviour.
- `evidence/evaluator_parity.json`: `211` synthetic evaluator cases, zero mismatch against
  the reference `metric/eval.py` at function level, including the `+1e-6` denominators,
  exact-1 sentinel exclusion, macro counts and `conf=0` legacy branch.

These artefacts do **not** execute an end-to-end pair, a feature file, a model checkpoint or
a GPU kernel. They are semantic checks, not benchmark evidence.

## 1. Master contract table

Line references are to the prototype files at the commit above, as read on 2026-10-18.

| ID | Item | Manuscript says | Code location and observed behaviour | Status |
|---|---|---|---|---|
| V1 | Finite rows | A row is valid only if every component is finite | `fastvcl/io.py:309-327` (`_check_finite32`) rejects non-finite feature files at load. `sparse.py:640-659` (`normalize_rows_with_mask`) itself does **not** test `isfinite`; a direct `Inf` row has norm `inf`, is marked valid and becomes `NaN` after division. | `MATCH` at pipeline boundary; helper-level `DIFF` (see C10) |
| V2 | Validity threshold | Audit start: Norm \(>10^{-12}\); paper corrected this round to \(10^{-8}\) | `sparse.py:49` `MIN_ROW_NORM = 1e-8`; `io.py:339` default `1e-8`; `tube.py:858-866` same rule. | Paper aligned to code; helper finite gap remains (see C1) |
| V3 | Invalid cells | Invalid rows are never match nodes, never evidence, never endpoints | `sparse.py:1422-1436, 1570-1581` mask sampling and anchors; `tube.py:909-933` masks band cells and writes `valid=False`; `tube.py:366-375` DP zeros invalid cells; `segments.py:286-288` requires `node_valid`. | `MATCH` |
| S1 | Sampling plan | Grid \(p+ks\) inside masks; multiple plans merged | `sparse.py:172-250` (`build_sampling_plan`), `1422-1426` (phase-aware index sets), `1277-1381` (merge). Multi-scale plus non-default independent phases is refused (`sparse.py:224-232`). | `MATCH`; combination refusal documented |
| S2 | Mutual Top-\(K\) and ties | Top-\(K\) by cosine, ties by smaller original index, mutual both directions | `sparse.py:749-790` (`_topk_rows`, full `(-score,index)` sort on a boundary tie), `1562-1613` (mutual sets and threshold). | `MATCH` |
| S3 | Anchor threshold | Keep \(\mathrm{Sim}_{ij}\ge\tau\) | `sparse.py:1576-1578` (`score < min_cosine` skipped). | `MATCH` |
| S4 | Merge and cap | De-duplicate by original \((i,j)\), keep max cosine, cap \(C_{\max}\) by score then index | `sparse.py:1344-1380`; cap at `1373-1378` keeps `(-cosine, a_idx, b_idx)`. | `MATCH` (dedup tie keeps first source; deterministic) |
| S5 | Nested grids / phases | Zero-phase 8/4/2 nested; independent phases tile the 2-D offset; synchronous phases do not | `sparse.py:172-250`, `108-170`; probes in `check_paper_semantics.py` count 1,024 vs 1,344 for 64×64. | `MATCH` |
| T1 | RANSAC pair draw | Audit start: “draws an anchor pair with \(|i_2-i_1|\ge\Delta_{\min}\)”; the claim was removed this round | `trajectory.py:339-358`: draws two anchors; rejects only equal A indices (`a[i1] == a[i2]`) and out-of-range slopes. No minimum A separation at draw time. `min_a_span=4` is checked later on the **whole run** (`446-451`). | Paper corrected to distinct A coordinates; no Δmin code |
| T2 | Inlier rule and slope bounds | \(|j-(\alpha i+\beta)|\le\epsilon_B\), \(\alpha\in[\alpha_{\min},\alpha_{\max}]\) | `trajectory.py:355-365` rejects slopes outside bounds before counting; `360-362` counts residual \(\le\epsilon_B\); best score is inlier count plus a \(10^{-6}\) residual tie-break (`366-370`). | `MATCH` |
| T3 | Inlier removal | “Accepted inliers are removed before the next round” | `trajectory.py:247-270`: inliers are removed **provisionally**; if every split run is rejected by the re-check, the anchors are put back for another hypothesis. | `DIFF` in wording only; behaviour is deliberate |
| T4 | Dual-axis support | \(|\pi_A|\ge h_A\), \(|\pi_B|\ge h_B\), with distinct times | `trajectory.py:440-445`: `min(unique_a, unique_b) >= min_inliers` (5 in the reference config). | `MATCH` |
| T5 | Span checks | \(\max\pi-\min\pi\ge L_{\min}\) on both axes | `trajectory.py:446-451`: `span_a >= min_a_span (4)`, `span_b >= min_b_span (8)`. | `MATCH` |
| T6 | Gap splitting | Split on large A gap, large positive B gap, backward B step | `trajectory.py:390-413`: exactly those three conditions, using `max_gap_a=24`, `max_gap_b=24`, `max_backwards_b=1.0` in `configs/isc_only.yaml`. | `MATCH` |
| T7 | Final track cap | Not specified in the main text | `trajectory.py:275-283`: after splitting, at most `max_tracks=8` tracks, preferring `(-n_anchors, start_a)`. | `PROPOSED_ONLY` in paper; add to supplement or leave as implementation detail |
| U1 | Tube A range | \(\ell=\max(0,i_{\min}-e_A)\), \(u=\min(M,i_{\max}+1+e_A)\) | `tube.py:180-188`; `refine_track_detailed` passes `a_range=(floor(start)-e_A, ceil(end)+e_A)` when `extension_a>0` (`706-717`). | `MATCH` for the formal config (`e_A=16`) |
| U2 | Rounding | \(c_r(i)=\mathrm{round}(\alpha i+\beta)\), ties to even | `tube.py:888-890`: `np.rint(centers)`; probe prints `[0.5,1.5,2.5,-0.5] -> [0,2,2,0]`. | `MATCH` |
| U3 | Band validity | Legal only if B in range and both rows valid | `tube.py:909-933`: out-of-range cells invalid; A/B validity applied; invalid cells `sim=0, valid=False`. | `MATCH` |
| U4 | \(e_A=0\) fallback | The tube is defined only by \(e_A\) and \(w_r\) | `tube.py:180-188`: if no explicit `a_range`, A padding is `half_width + margin`, not `e_A`. With `w=12, margin=0`, a track `[10,20)` scans `[0,32)`; with `e_A=16` it scans `[0,36)`. | `DIFF` for the `e_A=0` row (see C4) |
| D1 | Step set | \(\{(1,1),(1,2),(2,1)\}\) on original indices | `tube.py:234` `LOCAL_DP_STEPS`; `285-328` maps band columns to actual B-index differences. | `MATCH` |
| D2 | Reward and gap charge | \(r=\mathrm{Sim}-\tau_{\mathrm{align}}\); penalty \(\lambda(\Delta i+\Delta j-2)\) | `tube.py:377, 409-413`: reward offset and penalty on the **actual** edge `(da,db)`, not the nominal step. | `MATCH` |
| D3 | Restart | \(H=\max(0,r,\max_{H_{uv}>0}[H_{uv}+r-\lambda g])\) | `tube.py:428-438`: a cell with any legal predecessor takes the continuation **without comparing with `own` or 0**, and may be negative; only a cell with no legal predecessor starts at `max(0,own)`. A negative cell's backpointer is cleared. | `DIFF` (see C3) |
| D4 | Predecessor gate | Only predecessors with \(H_{uv}>0\) | `tube.py:319` uses `ok = valid & ~blocked`; `409-413` uses `H[prow,pcol]` regardless of sign. | `DIFF` (same root as C3) |
| D5 | Invalid/blocked cells | \(H=0\), no predecessor | `tube.py:369-375, 388-389`: unusable cells are skipped and keep `H=0`; `block_path_cells` (`250-268`) only blocks matched cells. | `MATCH` |
| D6 | Backtrace and ties | Start at largest \(H>0\); terminal ties smallest \((i,j)\); transition ties prefer restart, then step order | `tube.py:472-488`: starts at flat `argmax` (smallest row, then column) over usable cells. `414-418`: transition tie key `(-total, step_index, prow, pcol)`; step order is `(1,1),(1,2),(2,1)`, no restart candidate when a predecessor exists. | Terminal `MATCH`; transition **not** the proposed restart-first rule (`DIFF`, proposed only) |
| D7 | Multi-path and blocking | Block only matched cells; up to \(P_r\) attempts; include rejected extractions; recompute DP | `tube.py:727-759, 780-798`: each attempt re-runs `align_band` on the current blocked band; a reachable path is appended and its cells blocked immediately, before segment extraction. A path that later yields no segment still consumed its cells. | `MATCH` |
| D8 | Stop rule | If no positive unblocked path, stop before backtrace | `tube.py:444-453` returns `reachable=False` when `max H <= 0`; `546-552` returns an unreachable path; `740-741` breaks. | `MATCH` |
| G1 | Smoothing | Clamp negative cosines to zero, then centred edge-padded window of up to 3 matched nodes | `segments.py:85-123`: `weighted_scores` clamps to zero; `smoothed` uses a centred window and edge padding; for local-DP paths only match nodes are present. | `MATCH` |
| G2 | Gap off-by-one | Split when \(i_{t+1}-i_t-1>g_{\mathrm{low}}\) | `segments.py:311-314`: split when `gap_a > g_low + 1`; probe shows intervening 2 kept, intervening 3 split. | `MATCH` |
| G3 | Endpoints | Half-open `[first,last+1)` from matched nodes | `segments.py:339-344`; clamped and validated at `360-366`. | `MATCH` |
| G4 | Output margin | Proposed zero margin | `segments.py:334-336, 787-788`: `boundary_margin` expands the path-row span before taking endpoints; reference config is 2. Probe: margin 0 gives `[9,12)`, margin 2 gives `[8,14)` on the same path. The unit is **matched path rows**, not feature indices. | `DIFF` (see C5) |
| G5 | Minimum support | Distinct anchor support inside the segment | `segments.py:349-352`: counts stored `anchor_a` entries inside `[start_a-0.5, end_a+0.5)`; duplicates are counted separately; B-axis membership is not required. Probe: two identical A anchors pass `min_segment_anchors=2`, one distinct anchor fails. | `DIFF` (see C6) |
| G6 | Score | \(q=0.7\,\mathrm{clip}(\bar s,0,1)+0.3\min(1,n_A^{\mathrm{seg}}/\max(1,L_A/\bar\Delta_A))\) | `segments.py:353-362`: same shape; `mean_sim` over retained rows, `anchor_spacing` median positive gap (fallback 4), then clip to `[0,1]`. The support term uses the stored-entry count from G5. | Formula `MATCH`; support input `DIFF` |
| G7 | De-duplication | Min of per-axis IoU \(\ge\theta\); visit decreasing score, ties by endpoint coordinates | `segments.py:191-217`: `axis="min"` uses `min(IoU_A,IoU_B)`; order `(-score, start_a, start_b)`, stable for exact ties. No end-coordinate tie-break. | Rule `MATCH`; tie wording `DIFF` (see C9) |
| G8 | Segment cap | Apply configured cap | `segments.py:220-225`; `pipeline.py:358-367` applies cross-track dedup then `max_segments_per_pair=64`, then restores temporal order. | `MATCH` |
| G9 | Output confidence threshold | “apply … frozen confidence threshold” in the algorithm | No threshold in `pipeline._run_stages`; scores are written to predictions. Thresholding happens in `evaluate.py:421-469` (`q>c`; legacy `c=0` skips both filtering and integer truncation). | `DIFF` (see C7) |
| M1 | Per-pair metric | Product of two axis coverage ratios with \(+1e-6\) per axis | `evaluate.py:258-295`; reference `metric/eval.py:71-135` identical. | `MATCH` |
| M2 | Sentinel | Exclude values exactly equal to 1 separately per mean | `evaluate.py:298-327`; reference `evaluate_overall` identical. | `MATCH` |
| M3 | Denominators | Report \(n_{\text{expected}}\), \(n_{\text{processed}}\), \(|D_P|\), \(|D_R|\) | `evaluate.py:561-621` reports `n_pairs`, `n_input_rows`, `denominators`; the status file carries ok/empty/error/skipped. `metrics.json` does not itself contain `n_expected/n_processed/n_error/n_skipped`. | `MATCH` at run level; schema gap |
| M4 | F1 | \(2\bar P\bar R/(\bar P+\bar R)\) | `evaluate.py:574-576`: `2PR/(P+R+1e-6)`, which is 0 when both means are 0. | `DIFF` (see C8) |
| M5 | `conf=0` legacy branch | No score filter and no integer conversion at `c=0` | `evaluate.py:421-469`; reference `evaluation.py:12-18` skips the whole branch when `conf==0`. | `MATCH` |
| M6 | Failure status | ERROR/SKIPPED never rewritten as empty | `evaluate.py:543-551, 594-617`; `apply_conf_filter` refuses malformed input instead of the reference's bare `except: []`. | `MATCH` (deliberate deviation from reference's silent fallback) |
| C1 | Direct-offset DP bound | \(O(L_rW_r)\) per path with direct addressing | `eq:dpideal`; not implemented. The prototype's scan is `C2`. | `PROPOSED_ONLY` |
| C2 | Prototype scan bound | \(O(P_rL_rW_r^2)\) per tube | `tube.py:313-317` enumerates every predecessor row column for non-diagonal steps; `check_paper_semantics.py` and the source confirm. | `MATCH` |
| C3 | Coarse dot count | About \(2Q\) plus tie work | `sparse.py:1504-1509` runs forward and backward full sampled grids; `1519-1526` records `actual_dot_products`; `_blocked_topk` adds boundary-tie rescans. | `MATCH` |

## 2. Details of the differences that matter

### C1. Validity threshold: audit-start paper value \(10^{-12}\), code \(10^{-8}\)

`sparse.py:49` and `io.py:339` use `1e-8`; `tube.py:858-866` reuses the same rule. The
manuscript at audit start said `1e-12`; for a norm in \((10^{-12},10^{-8}]\) the paper would
call the row valid and the code drops it. This was a real specification mismatch, even though
both thresholds are numerically tiny.

**Decision implemented in this round:** the manuscript now uses `1e-8` and states that the
search and tube share the constant; segment extraction consumes the node-valid mask. This is
a paper correction, not a prototype change. If the research decision later becomes
\(10^{-12}\), the prototype must change and the change must be tested at the boundary; do not
leave the paper at one value and the code at another.

`normalize_rows_with_mask` does not test `isfinite` explicitly. `load_features` rejects
non-finite files first (`io.py:309-327`), so the pipeline has a finite precondition. A direct
call with `Inf` currently becomes `NaN` with `valid=True` (`normalize_rows_with_mask` probe).
The paper's finite term is therefore a **pipeline precondition**; the helper should be
hardened before it is reused as a public API. This is recorded as C10, not as a benchmark
bug.

### C2. RANSAC pair draw: no \(\Delta_{\min}\) at draw time

The manuscript at audit start said the pair was drawn with \(|i_2-i_1|\ge\Delta_{\min}\).
The code only rejects `a[i1] == a[i2]` (`trajectory.py:352-355`). A pair of adjacent A indices
can define a hypothesis; the accepted **run** must still satisfy `min_a_span=4` and
`min(unique_a,unique_b)>=5` (`440-451`). The paper no longer claims \(\Delta_{\min}\). If a
minimum pair separation is scientifically wanted, it is a new proposed constraint and needs
its own acceptance test.

### C3. Local-DP restart: the prototype is not the zero-floor recurrence

Probe (`evidence/contract_probes.json`, one-column diagonal bands, \(\tau=0.6\),
\(\lambda=0.1\)):

| Input | Proposed zero-floor (manuscript) | Prototype `local_dp` |
|---|---|---|
| 10 weak frames (cos 0.0) then 5 copy frames (0.95) | \(H\) reaches `1.75`; path found | all copy scores negative (`-5.05 … -3.65`); `best=0.0`, `reachable=false`, no path |
| strong 0.95, weak 0.10, strong 0.95 | \(H=[0.35, 0, 0.35]\); the second strong frame restarts | \(H=[0.35, -0.15, 0.20]\); the second strong frame inherits the deficit; the best path is still the first frame |
| two copies with 7 weak frames between, first copy blocked | second copy restarts at `0.35` and accumulates | blocked run leaves the unblocked 7-frame weak gap; the second copy is still negative |

The mechanism is precise: when a legal predecessor exists, the code computes
`H = own + max_pred(H_pred - gap)` and never compares with `max(0, own)`
(`tube.py:428-432`). If that value is negative, the backpointer is cleared (`433-438`), but
the negative `H` remains usable as a predecessor (`319` does not filter by `H>0`). The
negative cell can therefore be the first node of a traceback but cannot be a terminal; a
later strong frame pays the accumulated deficit.

**Decision:** keep the manuscript's zero-floor rule as `PROPOSED`, and keep the prototype
continuation as the compared variant. E3 must compare both on identical serialized tubes.
Do not describe the zero-floor rule as “implemented” or “fixing” the prototype. The
supplement's two hand cases remain valid; the probe adds the exact score table.

### C4. \(e_A=0\) silently changes the A padding factor

`candidate_a_range` (`tube.py:180-188`) pads by `half_width + margin` when no explicit
`a_range` is supplied. `refine_track_detailed` supplies an explicit range only when
`extension_a>0` (`706-717`). Therefore an E4 row with `e_A=0` does not test “no extension”:
it changes the A padding from `e_A` to `w+margin` (12 + 2 = 14 in the reference config).
Probe: `[10,20)` with `w=12, margin=0` scans `[0,32)`; with `e_A=16` it scans `[0,36)`.

**Decision:** E4 must pass an explicit A range for the zero-extension row, or hold
`extension_a>0` and vary it, so that only the named factor changes. The paper's tube
equation is correct for the formal configuration; the supplement should record this
implementation edge.

### C5. Output margin is counted in path rows, not feature indices

`extract_segments` first trims to the strong run, then expands by `boundary_margin` **path
rows** before taking the min/max A and B coordinates (`segments.py:334-344`). On a local-DP
path the rows are matched nodes, so two rows are not two original A indices. Probe on a
7-node path with a 3-node strong run: margin 0 gives `[9,12)`, margin 2 gives `[8,14)`, and
the score changes from `0.965` to `0.6675` because the mean includes the expanded rows.

**Decision:** the proposed zero margin is a specification change; the prototype's margin 2
must not be described as “2 feature indices”. E4 should test margin 0/2 on identical paths
and report both endpoints and score, not just the official metric.

### C6. Support counts stored entries, not distinct times, and only on A

`extract_segments` passes `path.anchor_a` (the A indices of the track anchors, one entry per
anchor) and counts entries in `[start_a-0.5, end_a+0.5)` (`segments.py:349-352`). With
Top-\(K>1\), a single A time can contribute several entries. Probe: anchors `(12,12)` pass
`min_segment_anchors=2`; a single distinct anchor 12 fails. The proposed score instead uses
distinct A times whose anchors lie inside **both** segment intervals; that rule is not
implemented.

**Decision:** keep the proposed distinct-support definition, and make it explicit in the
paper. E1's baseline and core must use the same support rule; otherwise the comparison
changes two things. E4 can compare stored-entry vs distinct support as a separate row.

### C7. Confidence threshold lives in the evaluator, not the core pipeline

The algorithm's last steps say “apply segment cap and frozen confidence threshold”. The
pipeline writes all post-dedup segments with scores; `evaluate.py` applies `score > conf`
and, in legacy mode, `conf=0` skips both filtering and integer truncation. There is no
frozen threshold in `FastPipeline`.

**Decision:** reword the algorithm to “apply the configured segment cap; the evaluation
protocol applies the declared confidence threshold”, and state the mode explicitly. If a
core-side threshold is desired, it must be implemented and frozen before it can be part of
the method. This also avoids claiming a threshold that no run has selected.

### C8. F1 zero guard

The paper's F1 equation has no epsilon; `evaluate.py:574-576` uses
`2PR/(P+R+1e-6)`, which is 0 for `P=R=0`. The reference `evaluation.py` uses the same
expression. The difference is below \(10^{-6}\) for positive means and only matters at the
undefined/all-zero boundary.

**Decision:** include the \(+\epsilon\) in the paper's wrapper equation and state that it is
the evaluator's zero guard. The manuscript already says “when both defined means are zero,
report F1 as zero using the declared wrapper rule”; the equation should make that rule
visible.

### C9. De-duplication tie-break

`dedupe_segments` sorts by `(-score, start_a, start_b)` and keeps the first of a duplicate
group; exact ties therefore fall back to collection order, not to end coordinates. The paper
says “ties by endpoint coordinates”. **Decision:** say “ties by start coordinates, then
collection order”, or add the end-coordinate rule to both paper and code. Do not leave the
paper claiming a deterministic rule the code does not implement.

### C10. Finite check at the helper boundary

`load_features` checks the whole array after float32 conversion (`io.py:309-327`), so the
formal pipeline cannot deliver `Inf`/`NaN` rows. `normalize_rows_with_mask` itself does not
check components: `Inf` has norm `Inf`, compares greater than `1e-8`, and divides to `NaN`
with `valid=True`. `NaN` has norm `NaN`, compares false and is zeroed. This is a helper-level
gap, not a pipeline-level result. **Decision:** document the loader precondition; harden the
helper before exposing it; add the boundary test in §4.

## 3. Canonical choices proposed for the next freeze

These are recommendations. They become binding only when a run's `frozen_protocol` records
them and the corresponding tests pass.

1. **Validity:** the paper now uses `1e-8`, one shared constant for loader/search/tube and
   node-valid propagation into segments. Keep the finite check at load and add one at the
   normalization helper.
2. **RANSAC:** the paper now describes “two anchors at distinct A coordinates”; `min_a_span`
   and the dual-axis checks remain post-fit constraints. A minimum draw separation is a new
   experiment, not an existing property.
3. **Recurrence:** the paper's zero-floor rule remains proposed; the prototype continuation
   is the current implementation. Freeze one only after E3 on identical tubes; the choice
   must be recorded in the config and both variants must remain reproducible.
4. **Margin:** adopt zero output margin in the proposed specification; record the
   prototype's row-based margin 2 as an implementation variant. Never call it a
   feature-index margin.
5. **Support:** define \(n_A^{seg}\) as distinct A times of track anchors whose A and B
   coordinates both lie inside the segment; apply the same rule to the STB baseline and the
   core in E1. The prototype's stored-entry count is a documented difference, not the
   proposed rule.
6. **Threshold:** remove it from the core algorithm; declare it in the evaluation protocol
   (legacy `q>c`, `c=0` no filter/no cast). Freeze it per method on validation.
7. **De-duplication:** keep min-axis IoU; state the start-coordinate tie-break and stable
   collection order. The A-only/A-vs-B example remains a contrast, not a proof of
   superiority over area IoU.
8. **E4 `e_A=0`:** pass an explicit A range or use `e_A>0`; the current fallback changes
   two factors.
9. **E1:** the STB baseline and the core must share the same recurrence, margin, support and
   scoring rule; E1 changes only the named structural mechanism(s). E3 is the separate
   recurrence comparison on identical tube hashes.
10. **Reporting:** keep official metric and custom diagnostics separate; report
    `n_expected/n_processed/|D_P|/|D_R|`, errors and skips from the status file, not only
    `metrics.json`'s `n_pairs`.

## 4. Acceptance tests still required

| Test | Input | Expected / acceptance | Status |
|---|---|---|---|
| A1 norm boundary | rows with norms \(10^{-12},10^{-9},10^{-8},10^{-7}\) | invalid/invalid/valid/valid under `1e-8`; only the chosen constant | `MISSING` |
| A2 non-finite helper | `Inf`, `NaN`, overflow-to-Inf float32 | explicit rejection or invalid mask; never a `valid=True` NaN row | `MISSING` |
| A3 RANSAC draw | anchors with adjacent A indices, enough span/support | accepted iff post-fit checks pass; no hidden draw constraint | `MISSING` |
| A4 DP exact path | four regimes (weak prefix, strong-weak-strong, two copies, invalid/blocked) | exact `H`, path and endpoints for both recurrences; ties and terminal choice included | `PARTIAL` (probes document scores; no E3) |
| A5 \(e_A=0\) | same track with explicit range vs default | the explicit range changes only \(e_A\); outputs and costs reported | `MISSING` |
| A6 margin | identical path, margin 0/2 | endpoints and score reported; row-vs-index unit documented | `PARTIAL` (probe) |
| A7 support | Top-\(K>1\), duplicate vs distinct anchors | proposed rule rejects the duplicate case; prototype differs as documented | `PARTIAL` (probe) |
| A8 threshold | low-score segment at pipeline output, evaluator `c=0` and `c>0` | pipeline keeps it; evaluator filters only in `c>0` mode; no silent cast at `c=0` | `MISSING` |
| A9 F1 boundary | `P=R=0`, `P=R=1`-like values, empty lists | declared value and denominator; no crash | `PARTIAL` (parity check) |
| A10 evaluator parity | 211 synthetic cases + reference | zero per-pair mismatch; macro/denominator parity | `DONE` at function level |
| A11 E1 baseline parity | same config, only named mechanism differs | diffs confined to the named change; candidate counts reported | `MISSING` |
| A12 E3 tube identity | serialized tracks/tubes + hashes | both recurrences read identical tubes; only alignment changes | `MISSING` |

## 5. Reproduction log

Environment: macOS arm64, DSH NumPy Python 3.12, NumPy 2.3.5; no CUDA, no GPU execution.
Commands (run from the paper root):

```bash
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

# 1. Prototype unit tests (read-only; 646 pass, 10 CUDA skips)
cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .

# 2. Evaluator parity (211 synthetic cases; zero mismatch)
cd ../gzhlaker_cvpr2027
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py \
    --output evidence/evaluator_parity.json

# 3. Contract probes (8 behaviours; all observed)
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py \
    --output evidence/contract_probes.json
```

The test summary is `evidence/prototype_tests_summary.md`; the full local log is
`evidence/prototype_tests.log`. The first line of this audit is the
source snapshot; re-run `shasum -a 256` on the five files in
`evidence/round2_source_snapshot.json` before trusting the line numbers. The prototype
tracked work tree was clean before and after the probes; no file was written under
`../FastVCL`.

## 6. Bottom line

The manuscript and the prototype agree on most of the candidate, tube, metric and output
mechanics. The blocking differences are:

1. validity threshold: paper corrected to `1e-8`; helper-level finite check remains;
2. RANSAC draw: the unsupported minimum-separation claim was removed;
3. local DP restart semantics (proposed vs current; E3 needed);
4. output margin unit and stored-entry support (proposed vs current; E4/E1 needed);
5. confidence threshold location (paper wording fix);
6. F1 zero guard and de-dup tie wording (paper fix).

None of these differences is resolved by compiling the paper. The next implementation agent
must change code only under explicit authorization, keep the old behaviour reproducible, and
attach the A1–A12 tests before any result is promoted.
