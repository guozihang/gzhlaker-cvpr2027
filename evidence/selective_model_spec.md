# `seltive model`: current two-stage specification (proposed)

Date: 2026-10-20; **fusion/budget rules repaired 2026-10-25 (round 6)**. Status: **PROPOSED /
NOT IMPLEMENTED / NOT EVALUATED**. This file is the current specification requested in round
five and kept consistent with the round-six repair of `Conn`, coverage, per-axis geometry and
one-pair-at-a-time merging. It supersedes the 2026-10-18 post-localization scope, which is
retained only as a historical note at the end. It does not claim a backend, a prompt, a
selection policy or a measured benefit.

The user-requested name is exactly **`seltive model`**; it is kept verbatim in the figure,
the manuscript and this file. “JEV” is the historical internal name for the same branch. The
spelling is intentional and must not be “corrected” by a later editor.

## 1. What the branch is

`seltive model` is an optional branch that asks one pretrained/post-trained multimodal model a
small number of questions about original A/B frames. It is inserted at two intervention
points:

1. **Anchor filtering, before geometric fitting.** A decisive `NOT_COPY` may remove a
   doubtful anchor from $\Anch_0$; the remaining anchors become $\Anch_1$.
2. **Fragment fusion, after segment extraction.** A decisive `MERGE` may join two fragments
   that are plausibly one continuous copy; the remaining set becomes $\mathcal Y$.

The branch is **selection-only** at the anchor stage, **conservative** (only decisive
verdicts act, and geometry or connection evidence can veto), **abstaining** per item, and
outside the fixed-feature core comparison. It cannot recover an anchor absent from
$\Anch_0$, a copy absent from $\mathcal C_0$, or a boundary unsupported by any path.

The final output of the core is $\mathcal Y$; $\mathcal C_0$ is produced by the core and is
never an input to the main flow. Fixed $\mathcal C_0$ is used only by the isolated E6-F
experiment.

## 2. Prerequisites

- A verified feature-index-to-frame map for each video (source frame count, exact sampling
  rule, timestamps, rounding convention, boundary test on at least three videos).
- Original A/B frames, not only ISC features.
- A frozen model revision, adapter/readout, prompt, option order, image sampling, crop,
  resolution and missing-frame policy.
- A declared budget, cache policy and failure policy.

If the map is missing or ambiguous, the stage returns `UNAVAILABLE` and does not run. A
feature index is not a source frame and not a second.

## 3. Items and evidence boards

An item is either an anchor $a=(i,j)$ or an ordered segment pair $(c_u,c_v)$.

- **Anchor board:** the match and its immediate sampled neighbours on each side, at most 3
  paired positions (6 source frames).
- **Fusion board:** both fragment interiors, both boundary sides and, when available, the gap
  interior, at most 5 paired positions (10 source frames). Overlapping positions are
  de-duplicated; a missing frame is marked missing, never replaced from another time.

Each tile records side, timestamp, feature index, cell id and question id. The anchor prompt
asks whether the two sides show the same underlying footage, explicitly allowing crop, speed
change, overlay and re-encoding, and explicitly rejecting topical, person or action
similarity. The segment prompt asks whether the fragments are parts of one continuous copy and
whether the proposed connection interval is covered. Options are fixed and ordered:
`COPY / NOT_COPY / UNCERTAIN` and `MERGE / KEEP_SEPARATE / UNCERTAIN`. Raw candidate scores,
option order and normalisation are stored; a free-form JSON answer is a control, not the main
readout.

## 4. Anchor filtering

All selectors start from the same $\Anch_0$, the coordinate-deduplicated and capped anchor
set. No selector may pre-delete an anchor. For an anchor $(i,j)$, let $\mathcal C_B(i)$ be
the B coordinates compared with A index $i$ in any executed plan, merged by original
coordinate and de-duplicated, and $\mathcal C_A(j)$ the analogous A set. Define

\[
\mu_B(i,j)=S_{ij}-\max_{j'\in\mathcal C_B(i)\setminus\{j\}}S_{ij'},\qquad
\mu_A(i,j)=S_{ij}-\max_{i'\in\mathcal C_A(j)\setminus\{i\}}S_{i'j}.
\]

A side is **missing** when its competitor set is empty; $\mu=\min(\mu_A,\mu_B)$ only when
both sides exist. This compares the current match with its strongest competitor on each axis,
not always with the second-ranked partner. Cross-plan duplicates are removed by original
coordinate; no unrecorded full-resolution scan is added. A missing side is logged and enters
the selector as the neutral rank $1/2$.

The default selector groups anchors on a two-dimensional grid of width twice the finest
sampling stride and visits groups round-robin. Inside a group,

\[
\pi(a)=\tfrac12\operatorname{rank}(-\mu(a))+\tfrac12\operatorname{rank}(\rho(a)),
\]

where both ranks are normalised in $\Anch_0$, $\rho$ is the normalised residual to a local
pre-fit line, and larger is preferred. Missing margin, missing geometry or a singleton pool
gets $1/2$; ties use $(i,j)$; random controls use a fixed seed. Pre-fit geometry is charged to
measured time.

The action is

\[
D(a)=\mathbf 1[a\in\mathcal Q]\mathbf 1[\text{verified}]
\mathbf 1[p^{\text{anc}}_N\ge\tau_A]
\mathbf 1[p^{\text{anc}}_N-\max(p^{\text{anc}}_C,p^{\text{anc}}_U)\ge\delta_A],
\]

and only $D(a)=1$ removes $a$: $\Anch_1=\Anch_0\setminus\{a:D(a)=1\}$. `COPY`, `UNCERTAIN`,
unselected, over-budget and failed anchors keep coordinates and weight. The old prototype
rule that multiplies `COPY` weights by $1.25$ is not inherited. Tracks are refitted on
$\Anch_1$ and dual-axis support/span are revalidated. Development grids are
$\tau_A\in\{0.90,0.95,0.98\}$ and $\delta_A\in\{0.15,0.30\}$; they are operating points, not
calibrated probabilities.

Modes: `off` calls the core directly; `shadow` logs decisions but returns
$\Anch_1=\Anch_0$ and must match core output item by item; `on` applies only $D(a)=1$. In
`on` mode a single failure or abstention promises only that item's fallback, not global
equality. `shadow` uses an independent random stream and must not perturb RANSAC.

## 5. Fragment fusion

From $\mathcal C_0$ after near-duplicate removal, a legal directed edge $(c_u,c_v)$ requires:

1. consistent temporal order and disjointness in the first version,
   $a_e^u\le a_s^v$ and $b_e^u\le b_s^v$;
2. A and B gaps within frozen caps $G_A,G_B$, with raw and normalised gaps recorded;
3. boundary-map agreement is checked direction by direction, never against a pooled
   tolerance: the two A-to-B residuals $|m_u(a)-b|$ at $a\in\{a_s^v,a_e^v\}$ must each be at
   most $\kappa_B$, and the two B-to-A residuals $|m_v^{-1}(b)-a|$ at
   $b\in\{b_s^u,b_e^u\}$ each at most $\kappa_A$;
4. a connector from $(a_e^u,b_e^u)$ to $(a_s^v,b_s^v)$ with slope in
   $[\alpha_{\min},\alpha_{\max}]$; a zero gap is legal only when both axes are zero, and a
   single-axis zero gap has no finite connector slope and is rejected.

Thresholds and inverse slopes must be finite; a missing or degenerate map makes the edge
unavailable. A pair with
$\operatorname{IoU}_A\ge\theta_{\mathrm{dedup}}$ but
$\operatorname{IoU}_B<\theta_{\mathrm{dedup}}$ is the same A interval at another B position,
hence a separate copy, and is excluded. Neighbours use a deterministic per-fragment cap;
edge and truncation counts are recorded.

The first-version selector groups edges by the earlier fragment's A position on a grid of
width twice the finest stride and visits groups round-robin. Within a group it sorts by
$\tilde g=\max(\mathrm{gap}_A/G_A,\mathrm{gap}_B/G_B)$, then by the maximum
threshold-normalised boundary-map error $\max(\max e_B/\kappa_B,\max e_A/\kappa_A)$, then by
$(c_u.\mathrm{id},c_v.\mathrm{id})$, and selects at most $B_F$ edges. No learned benefit predictor is used.

The connection check `Conn` is fixed before the model call and is a *certification* pass,
separate from the local DP that proposes paths. Its region
$R_e=[a_e^u-\eta_A,a_s^v+\eta_A)\times[b_e^u-\eta_B,b_s^v+\eta_B)$ is clipped to the video;
if its area exceeds $L_cW_c$, the edge is unavailable and the truncation is recorded. Support
nodes are path nodes of $u$ with A index in $[a_e^u-\beta_A,a_e^u)$ and of $v$ with A index in
$[a_s^v,a_s^v+\beta_A)$; an empty set gives `Conn=0`. Only valid left support nodes with
positive scores seed the bounded DP; no other cell starts a path and no cell restarts one. It
propagates the declared steps with score $S_{ij}-\tau_{\mathrm{conn}}$ while the cumulative
score stays positive. A cell merely adjacent to the right fragment is not sufficient: the
backtraced path must start at a left support node and end at a right support node, and both
memberships are checked. Ties use score, then end coordinates, then step order. Coverage is
interval-based, $\min(d_A/s_A,d_B/s_B)$ over the endpoint spans, and low-score runs are counted
on path nodes; skipped indices and invalid cells in the bounding box are logged separately.
Only the single highest-scoring path is tested; if it fails, the edge is rejected in this
conservative first version, which does not claim to enumerate all feasible paths. A reused
path passes the same endpoint, region, step and quality tests. Failure keeps the fragments
separate; the region is never enlarged until a path appears; all attempted and failed cell
visits are counted.

With geometric legality $G$,

\[
M(u,v)=G(u,v)\land\mathrm{Conn}(u,v)\land[p^{\mathrm{fus}}_M\ge\tau_F]
\land[p^{\mathrm{fus}}_M-\max(p^{\mathrm{fus}}_S,p^{\mathrm{fus}}_U)\ge\delta_F],
\]

and only $M=1$ merges. `KEEP_SEPARATE`, `UNCERTAIN`, failure and budget exhaustion retain both
fragments. The first version merges only original disjoint pairs of $\mathcal C_0$, processed
in the frozen selector order; a pair is eligible only when neither member has been consumed.
An accepted merge consumes exactly its two members, creates no new edge, performs no second
model call, and triggers no set-level re-verification or propagation to a third fragment. If
reconstruction fails, the action is rejected and both members remain available;
same-A/different-B duplicates stay separate. Endpoints are rebuilt from merged path nodes and
de-duplicated anchors; support and $q$ are recomputed by the core score rule, never by
$\max(q_u,q_v)$ or a product with the visual probability. Development grids are $\tau_F\in\{0.90,0.95,0.98\}$ and
$\delta_F\in\{0.15,0.30\}$; if no pair meets the risk and recall targets, fusion stays in
shadow.

## 6. Budget, retries and cost

| Item | Starting definition | Accounting |
|---|---|---|
| Anchor evidence | match + neighbours; at most 3 pairs / 6 source frames | source frames, boards, tokens separate |
| Fusion evidence | interiors, boundaries, gap; at most 5 pairs / 10 source frames | overlaps de-duplicated; missing marked; no gap midpoint for overlap |
| Question budget | $B\in\{0,4,8,12\}$; $q_A\le\lfloor2B/3\rfloor$, $q_A+q_F\le B$; initial $B_A=\lfloor2B/3\rfloor$, $B_F=B-B_A$ | one logical question once; cache hit counts; unused A may move to F, never reverse; $3B_A+5B_F$ is only the fixed-allocation special case |
| Retry | default off; if enabled at most one per question plus cap $R$ | extra execution charged; report $B+R$ |
| Connection | fixed $R_e$, cap $L_cW_c$; reuse or bounded DP | all attempts and failed cell visits counted |

The two stages share one pair budget; starting fusion must not reopen the pair budget. With
at most 3 paired positions per anchor question and 5 per fusion question,
$N_{\mathrm{paired}}\le3q_A+5q_F\le5B$ and
$N_{\mathrm{slots}}\le6q_A+10q_F\le10B$. At $B=12$, transferring all eight anchor questions
permits 60 paired positions and 120 source-frame slots, not 44.
Questions, frames, unique/repeated frames, tokens, forward passes, cache hits, memory and time
are logged separately. The cache key binds frame-content and index-map hashes, question type,
coordinates, layout, option order, prompt and checkpoint/adapter/readout revision. Failures
are never cached as `NOT_COPY` or `MERGE`. Prefix sharing is attempted only for identical
frame sets, layout, prompt prefix and revision; the two stages are not one forward pass.

## 7. Risk and required evidence

Action labels require human review or traceable transform truth; model self-labels and
“inside a GT rectangle” are weak proxies and cannot justify a hard action. Report separately:

- true-copy anchor deletion rate over all $\Anch_0$ and over queried true anchors;
- deletion action error (wrongly deleted true anchors / all deletions, `N/A` if none);
- wrong-fusion rate (wrong accepted merges / all accepted merges), plus correct opportunities
  among legal edges and missed merges;
- asked, verified, acted, abstained and failed counts;
- full-set P/R/F1/FAR, paired recall difference and boundary MAE on a common-GT cohort.

Targets are a 1% true-anchor deletion rate, a 1% wrong-fusion rate and a 0.5 percentage-point
recall drop; they are operating targets, not certificates. With $n$ independent zero-error
trials the one-sided 95% bound is $1-0.05^{1/n}$: 1.98% at $n=150$, 0.997% at $n=299$ and
0.994% at $n=300$. At least 299 effective trials are needed for a bound no larger than 1%.
Video-correlated observations violate independence; grouped intervals are predeclared;
thresholds are selected on `dev_calibration` and frozen to `dev_audit`.

The fusion experiment must additionally report correct fusion opportunities, legal-edge
coverage, `Conn` pass rate and questions asked versus actions executed. It must compare
“`Conn` only” with “`Conn` + visual” on the same $G$, the same `Conn` and a fixed selected edge
set. If core evidence cannot pass `Conn`, the visual branch has no repair opportunity; if
`Conn` already completes every safe merge, the model adds cost without demonstrated benefit.

## 8. Implementation status (2026-10-20)

- The prototype at HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8` is unchanged and its 646
  tests pass (10 CUDA tests skipped). It does not implement the zero-floor variant, the
  strongest-competitor margin, the fusion selector, `Conn` or the shared pair budget described
  here.
- The old post-hoc anchor verifier remains the only visual path in the prototype. Its default
  `NOT_COPY` deletion and `COPY ×1.25` rule are not inherited by this specification.
- The local data snapshot has no source videos and no verified frame map; no model weights or
  API credentials were available. No visual call was made.
- `scripts/round5_reference.py` is a paper-side reference for margin, selector, fusion
  geometry, `Conn`, risk bound and budget counting. It is not the prototype.

## 9. Historical note

The 2026-10-18 version of this file specified only post-localization candidate verification.
That scope is superseded: it assumed a fixed candidate pool and a verifier-style
accept/reject step, whereas the current design inserts the model before fitting and after
segment extraction and shares one budget. The historical post-only material is not a current
contract. The user-facing name and the “proposed, not evaluated” status are preserved.

Primary external references used for the design boundary (not for FastVCL results):
[Visual Jev](https://arxiv.org/abs/2609.25845), [VideoJev](https://arxiv.org/abs/2610.18615).
These papers do not establish two-video copy identity; that transfer remains our untested
hypothesis.
