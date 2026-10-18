# FastVCL method specification — round 2, 2026-10-18

Status: **PROPOSED**, not a claim that the prototype implements this specification.
Normative equations and algorithm: `sec/3_method.tex`. The prototype remains read-only;
its HEAD on this audit is `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`.
The round-two report records corrections to the previous version.

## 1. Scope and inputs

Core input: fixed pre-extracted ISC matrices $F_A\in R^{M\times256}$ and
$F_B\in R^{N\times256}$. Output: half-open feature-index intervals
$(a_s,b_s,a_e,b_e,q)$, with valid nonempty intervals on both axes. No conversion to
seconds or source-video frames is implied. No new downstream parameters are trained in
this core; descriptor pretraining and validation-based tuning are disclosed.

A row is valid iff every component is finite and its safely accumulated L2 norm exceeds
$10^{-8}$. Feature files are checked finite at load; the finite term is a precondition for
direct callers. The prototype uses the same $10^{-8}$ constant in the loader, search, tube and
segment stages. Normalize valid rows, keep an explicit validity mask, and assign invalid
similarities $-\infty$. Invalid or blocked cells cannot be match nodes or endpoints.

## 2. Sparse candidates

A plan $g=(s_A,s_B,p_A,p_B)$ chooses original indices $p_A+ks_A$, $p_B+ks_B$ within
bounds and masks. Tiled cosine comparisons retain mutual Top-$K$ at $S_{ij}\ge\tau$;
use at most the available number of valid partners. Break score ties by original index.
Merge by original $(i,j)$, retain maximal cosine, then cap by decreasing score and $(i,j)$.
The default is a **single zero-phase stride-4 grid, Top-1**, not multi-scale or multi-phase.

Zero-phase grids 8/4/2 are nested. Adding a coarser plan changes Top-K competition but adds
no new sampled coordinate beyond the fine grid; it still adds arithmetic. For 64-by-64
inputs, stride 2 has 1,024 one-direction pairs; {2,4,8} has 1,344. These are not equal
budgets. Independent phase pairs differ from synchronous phases; the prototype refuses
multi-scale plus non-default independent phases.

For one stride-$s$ grid, $h$ distinct A anchor times span at least $(h-1)s+1$ indices.
A shorter copy cannot supply $h$ anchor times wholly within itself. This **does not prove
that all such copies are undetectable**: outside anchors, tube extension and merged phases
change that reasoning. Top-K partners at one time are not independent temporal support.

## 3. Tracks and tubes

Fit $j\simeq\alpha_r i+\beta_r$ by seeded RANSAC with positive bounded slopes and
B-residual threshold. Sample distinct A positions. Refitted runs must pass slope,
residual, distinct A/B support and span checks. Split on large A gaps, large positive B
gaps or backward B steps, and re-validate each run. Accepted track count can **increase or
decrease** after splitting; no monotonicity is claimed.

The tube has A support $[\ell_r,u_r)$ extended by $e_A$ and clipped to $[0,M)$, and B
center $c_r(i)=\mathrm{round}(\alpha_ri+\beta_r)$ with integer offsets $[-w_r,w_r]$
clipped to $[0,N)$. $L_r=u_r-\ell_r$, $W_r=2w_r+1$. The prototype uses NumPy `rint` (ties-to-even); this was verified by a probe. No adaptive width or extension is currently specified.

## 4. Alignment and extraction

Let $r_{ij}=S_{ij}-\tau_{align}$ and steps $\{(1,1),(1,2),(2,1)\}$. On usable cells,
$$H_{ij}=\max(0,r_{ij},\max_{(u,v)\in Pred(i,j),H_{uv}>0}
 [H_{uv}+r_{ij}-\lambda((i-u)+(j-v)-2)]).$$

This is **Smith–Waterman-style**, not the canonical insertion/deletion recurrence. The
prototype never restarts at a cell with a legal predecessor: it keeps the continuation even
when negative, and a negative cell may still serve as a predecessor. It clears the
backpointer of a negative cell, so such a cell cannot start a traceback, but a later strong
cell inherits the deficit. The proposed rule restarts at the current cell and accepts only
predecessors with $H>0$. Proposed tie policy: smallest terminal $(i,j)$; at a cell, restart
before tied predecessor choices, then the listed step order. The prototype chooses the
smallest step index and has no restart candidate when a predecessor exists. Backtrace uses
stored choices. For each positive path, extract segments then block only its match cells;
rerun at most $P_r$ attempts, including rejected paths. Check for a positive score **before**
tracing. Append each extracted set into the global candidate collection. Greedy extraction
does not optimize a global multi-path objective.

Clamp negative cosines to zero before centered, edge-padded smoothing over at most three
matched nodes. Strong means smoothed similarity $\ge\tau_{seg}$. Split strong-node runs
when $i_{t+1}-i_t-1>g_{low}$; this counts intervening original indices. Trim to strong
endpoints and emit $[i_{first},i_{last}+1)$ and $[j_{first},j_{last}+1)$. Proposed output
margin is zero, independent of tube search extension. The prototype expands by
`boundary_margin` **matched path rows** (default 2) before taking endpoints; this is not a
feature-index margin and also changes the score because the mean covers the expanded rows.

Apply minimum durations and distinct anchor support. Define $n_A^{seg}$ as the number of
distinct A times of track anchors whose A and B coordinates both lie inside the segment
intervals. The prototype counts stored A-anchor entries over the A interval only; duplicates
from Top-$K>1$ are not removed. With $\bar\Delta_A$ the
median positive gap between distinct track A times (fallback 4),
$$q=0.7\operatorname{clip}(\bar s,0,1)+0.3\min(1,n_A^{seg}/\max(1,L_A/\bar\Delta_A)).$$

Greedy de-duplication visits decreasing score with endpoint tie breaks, suppressing pairs
whose minimum A/B interval IoU reaches the configured threshold. Apply output cap; the confidence threshold is declared at evaluation, not in the core
pipeline. Disjoint reference copies survive this rule **and area-IoU**; that example only
contrasts with A-only suppression. Distinct support/zero margin are proposed clarifications,
not assertions about current code. Ties in de-duplication are by start coordinates, then
collection order; the paper no longer claims an end-coordinate tie-break.

## 5. Cost accounting

Coarse grid count is $Q=\sum_g|I_A^g||I_B^g|$; with valid rows and fixed strides this is
$\Theta(MN)$. Actual forward/backward/tie-rescan dot products must be logged. Top-K selection,
normalization, RANSAC (up to $O(RI|A|)$ hypothesis scoring), sorting, refits and output
suppression are additional costs. Direct band offsets use $(j-\Delta j)-c_r(i-\Delta i)$;
array column adds $w_r$. DP costs $O(P_rL_rW_r)$ with direct lookup, versus the prototype's
row-scanning bound $O(P_rL_rW_r^2)$. Band cosines cost $O(dL_rW_r)$ when computed once.

Separate executed similarity dot products, DP cell visits and unique covered coordinates.
Workspace includes coarse tiles, Top-K retention, anchors/candidates, and one tube's DP
arrays; do not report only the tube term as total memory. Overlap duplicates work even if
bands are processed sequentially. Log process RSS and actual allocations as well as bounds.

## 6. seltive model (JEV) — proposed optional extension

The exact user-requested name is **seltive model**. Preserve it in the framework figure
(main Fig. 1) and the Method.
Input: selected core candidates/matched indices plus original A/B frame context, requiring
verified index-to-frame mapping. Output: COPY / NOT_COPY / UNCERTAIN. Unselected,
uncertain and failed cases retain the core prediction. Selection, backend and decisive
verdict fusion remain **OPEN**; no arbitrary score weight or hard deletion is established.

No claim that the historical anchor-level router implements the proposed candidate-level
branch. No extra training or model capability is inferred from the name. Core H1–H3 timing
and fixed-feature rows exclude it. E6 uses a fixed candidate pool and matched verification
budget, measures whole-set utility, recall loss and added end-to-end cost including frames,
model calls and retries. It cannot recover never-proposed copies.

## 7. Implementation differences still to resolve

1. Prototype continuation vs proposed zero floor, including exact traceback/ties. The
   prototype keeps a negative continuation and has no restart candidate when a predecessor
   exists; the proposed rule restarts and accepts only $H>0$ predecessors.
2. Scanned vs direct predecessor indexing; semantic parity first, speed measurement second.
3. Prototype output boundary margin 2 vs proposed zero margin; the prototype unit is
   **matched path rows**, not feature indices, and the margin also changes the score.
4. Prototype counts stored A anchor entries and uses A-only membership/tolerance; proposed
   score uses distinct times within both intervals. Top-K > 1 can expose this difference.
5. Finite-check helper, RANSAC draw separation, output-threshold location and the
   \(e_A=0\) A-range fallback; band rounding, smoothing and gap off-by-one are verified.
6. seltive model is an interface/design extension; no backend or complete candidate-level
   fusion implementation was verified.

The item-by-item line-level audit is `evidence/spec_code_contract.md`; executable probes are
`evidence/contract_probes.json`, and the 211-case evaluator parity result is
`evidence/evaluator_parity.json`. A writing agent must not mark these fixed because this
specification compiles. The next implementation agent must supply source changes and semantic
checks, then fresh experiments.
