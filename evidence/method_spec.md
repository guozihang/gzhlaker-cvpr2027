# FastVCL Method Specification (v2.1 draft)

Status: this file fixes the **proposed** mathematical specification used by
`sec/3_method.tex`. Every item is marked `PROPOSED` unless a section explicitly says
`IMPLEMENTED` and cites the prototype location. The paper text must not silently promote a
`PROPOSED` definition to an implemented or validated one.

Scope: given one video pair, fixed pre-extracted ISC descriptors, no new trainable
downstream parameters. Pairwise localization only (no library retrieval).

---

## 0. Symbol table

| Symbol | Meaning | Domain |
|---|---|---|
| $A,B$ | query and reference video | labels, never batch size |
| $M,N$ | number of feature rows | $\mathbb{Z}_{\ge 1}$ |
| $d$ | descriptor dimension (ISC: 256) | fixed |
| $F_A,F_B$ | raw descriptor matrices | $\mathbb{R}^{M\times d}$, $\mathbb{R}^{N\times d}$ |
| $i,j$ | feature indices of $A$, $B$ | $0\le i<M$, $0\le j<N$ |
| $m_i^A,m_j^B$ | valid-row indicators | $\{0,1\}$ |
| $\bar f_i^A,\bar f_j^B$ | unit-normalised valid rows | $\mathbb{R}^d$, $\mathbf 0$ when invalid |
| $S_{ij}$ | cosine similarity (or $-\infty$) | $\mathbb{R}\cup\{-\infty\}$ |
| $\mathcal G$ | set of sampling plans | finite |
| $s_A^g,s_B^g$ | strides of plan $g$ | $\mathbb{Z}_{\ge1}$ |
| $p_A^g,p_B^g$ | phases of plan $g$ | $0\le p_A^g<s_A^g$, $0\le p_B^g<s_B^g$ |
| $I_A^g,I_B^g$ | valid sampled indices | subsets of $[0,M)$, $[0,N)$ |
| $K,\tau$ | Top-$K$ width, anchor cosine threshold | $\mathbb{Z}_{\ge1}$, $\mathbb{R}$ |
| $C_{\max}$ | anchor cap after merging | $\mathbb{Z}_{\ge1}$ |
| $\mathcal A$ | merged, de-duplicated anchor set | set of $(i,j,S_{ij})$ |
| $\alpha_r,\beta_r$ | slope/intercept of track $r$ | $\alpha_r\in[\alpha_{\min},\alpha_{\max}]$ |
| $\epsilon_B$ | inlier residual bound (index units) | $\mathbb{R}_{\ge0}$ |
| $h_A,h_B$ | minimum independent support per axis | $\mathbb{Z}_{\ge1}$ |
| $g_A,g_B$ | maximum intra-track gap per axis | $\mathbb{Z}_{\ge0}$ |
| $e_A$ | A-axis tube extension | $\mathbb{Z}_{\ge0}$ |
| $w_r,W_r$ | B-axis half-width, band width $2w_r+1$ | $\mathbb{Z}_{\ge0}$, $\mathbb{Z}_{\ge1}$ |
| $c_r(i)$ | rounded band centre | $\mathbb{Z}$ |
| $\mathcal T_r$ | finite tube (legal cell set) | set of $(i,j)$ |
| $\tau_{\mathrm{align}}$ | reward offset in the local DP | $\mathbb{R}$ |
| $\lambda_{\mathrm{gap}}$ | gap penalty per skipped step | $\mathbb{R}_{\ge0}$ |
| $\mathcal S$ | DP step set | $\{(1,1),(1,2),(2,1)\}$ |
| $H_{ij}$ | local alignment score | $\mathbb{R}_{\ge0}$ (proposed) |
| $q$ | uncalibrated segment confidence | $\mathbb{R}$ |

**Half-open convention.** A predicted copy is $(a_s,b_s,a_e,b_e,q)$ with
$0\le a_s<a_e\le M$, $0\le b_s<b_e\le N$. Lengths are $a_e-a_s$ and $b_e-b_s$.
Coordinates are **feature indices**, never seconds and never source-video frame numbers.
A conversion to seconds requires a separately verified timestamp map; the current protocol
does not use one.

---

## 1. Input normalisation and validity mask (`PROPOSED`, implemented in `fastvcl/sparse.py`)

For each row $F_{A,i}$ define
$m_i^A=1$ iff all entries are finite, the row is non-empty and
$\lVert F_{A,i}\rVert_2>\varepsilon$ (default $\varepsilon=10^{-12}$); then
$\bar f_i^A=F_{A,i}/\lVert F_{A,i}\rVert_2$, else $m_i^A=0$, $\bar f_i^A=\mathbf 0$.
The same rule defines $m_j^B,\bar f_j^B$. Then

$$
S_{ij}=
\begin{cases}
\langle \bar f_i^A,\bar f_j^B\rangle, & m_i^A=m_j^B=1,\\
-\infty, & \text{otherwise}.
\end{cases}
$$

Normalisation is performed on an in-memory copy; the feature files are never modified.
Invalid rows are never match nodes: they cannot start, continue or terminate a path, and
they contribute no evidence to the confidence score.

---

## 2. Sparse proposals (`PROPOSED`)

A sampling plan is $g=(s_A^g,s_B^g,p_A^g,p_B^g)$. The valid sampled sets are

$$
I_A^g=\{p_A^g+k s_A^g:k\in\mathbb Z_{\ge0}\}\cap\{i:m_i^A=1\},\qquad
I_B^g=\{p_B^g+k s_B^g:k\in\mathbb Z_{\ge0}\}\cap\{j:m_j^B=1\}.
$$

For a fixed $g$, define the deterministic Top-$K$ set
$\operatorname{TopK}_{B,g}^{(K)}(i)\subseteq I_B^g$ by the total order
$(i,j')\succ(i,j)$ iff $S_{ij'}>S_{ij}$, or $S_{ij'}=S_{ij}$ and $j'<j$; then
$j\in\operatorname{TopK}_{B,g}^{(K)}(i)$ iff fewer than $K$ elements of $I_B^g$ precede
$j$ in this order. Ties are therefore broken by the smaller original index, and the rule is
identical in both directions.

The plan-level anchor set and the merged set are

$$
\mathcal A_g=\{(i,j)\in I_A^g\times I_B^g:\;
j\in\operatorname{TopK}_{B,g}^{(K)}(i),\;
i\in\operatorname{TopK}_{A,g}^{(K)}(j),\;
S_{ij}\ge\tau\},
$$

$$
\mathcal A=\operatorname{Cap}_{C_{\max}}\Big(\operatorname{Dedup}_{(i,j)}
\bigcup_{g\in\mathcal G}\mathcal A_g\Big),
$$

where $\operatorname{Dedup}_{(i,j)}$ keeps exactly one entry per **original coordinate**
pair with the largest cosine (ties: smallest source-grid id), and
$\operatorname{Cap}_{C_{\max}}$ keeps the $C_{\max}$ entries with the largest cosine
(ties: smallest $i$, then smallest $j$).

**Facts that the paper must state (and that experiments must expose).**

1. If $p_A^g=p_B^g=0$ for all plans, then $s=8$ samples are a subset of $s=4$, which are a
   subset of $s=2$: $I^8\subset I^4\subset I^2$. Adding a coarser grid samples **no new
   coordinate**; it only changes the local Top-$K$ competition set of each row. Any
   "multi-scale gain" must therefore be explained by the changed competition, not by new
   coverage, and must be compared against a single fine grid at equal dot-product budget.
2. Merging without coordinate de-duplication would let the same $(i,j)$ support RANSAC
   more than once. The prototype merges with a dictionary keyed by $(i,j)$ and records
   `cross_scale_duplicates`; this is the required behaviour, not an optional one.
3. Independent phases $(p_A,p_B)\in\{0,\dots,s-1\}^2$ tile the full index product. A
   synchronous phase $(p,p)$ covers only displacements with $p_B-p_A\equiv0\pmod s$ and is
   strictly weaker. Multi-scale and independent phases are mutually exclusive in the
   current prototype (`$multi_scale_with_phases_refused`), so no experiment may claim the
   combination until it is implemented.
4. **Short-segment sampling bound.** With one grid of stride $s$, a track that contains
   $h$ anchors at distinct $A$ times occupies at least $(h-1)s+1$ feature frames, i.e.,
   $i_{\max}-i_{\min}\ge(h-1)s$. This is a
   necessary condition for the *track*, not a sufficient condition for recall: the anchors
   must also be mutual, above $\tau$, and survive RANSAC. Segments shorter than
   $(h_{\min}-1)s+1$ frames can never be proposed by that grid.
5. **Top-$K$ is not independent evidence.** The $K$ partners of one $A$ frame share the
   same query time. Support must be counted on distinct projected times
   $|\pi_A(\mathcal I_r)|$ and $|\pi_B(\mathcal I_r)|$, not on the number of anchor pairs.

---

## 3. Multi-track fitting and dual-axis validation (`PROPOSED`)

Each track is a local affine map $j\approx\alpha_r i+\beta_r$ with
$\alpha_r\in[\alpha_{\min},\alpha_{\max}]\subset(0,\infty)$. The slope is an
index-step ratio, not a playback-speed ratio, unless both videos share a verified constant
sampling rate.

**Hypothesis generation.** RANSAC draws an anchor pair $\{(i_1,j_1),(i_2,j_2)\}$ from the
remaining anchors, requires $|i_2-i_1|\ge\Delta_{\min}$, computes
$(\alpha,\beta)$, and scores the hypothesis by its inlier count. The draw is deterministic
given a per-pair seed derived from a cryptographic hash of the structured pair id (never
Python's randomised `hash()`).

**Inlier criterion.** An anchor is an inlier iff
$|j-(\alpha i+\beta)|\le\epsilon_B$. Because $\alpha\ge\alpha_{\min}>0$, this also bounds
the A-axis residual by $\epsilon_B/\alpha_{\min}$; the prototype uses this single-sided
criterion. A symmetric criterion that adds
$|i-(j-\beta)/\alpha|\le\epsilon_A$ is a **design option**, not an implemented fact.

**Refit and re-validation.** After a weighted or unweighted least-squares refit, a run is
accepted only if all of the following hold:

$$
\alpha_{\min}\le\alpha_r\le\alpha_{\max},\qquad
\max_{(i,j)\in\mathcal I_r}|j-(\alpha_r i+\beta_r)|\le 1.5\,\epsilon_B,
$$

$$
|\pi_A(\mathcal I_r)|\ge h_A,\qquad |\pi_B(\mathcal I_r)|\ge h_B,
$$

$$
\max\pi_A(\mathcal I_r)-\min\pi_A(\mathcal I_r)\ge L_{\min}^A,\qquad
\max\pi_B(\mathcal I_r)-\min\pi_B(\mathcal I_r)\ge L_{\min}^B .
$$

The prototype sets $h_A=h_B=h_{\min}$ and checks
$\min(|\pi_A|,|\pi_B|)\ge h_{\min}$, which is the stricter of the two independent
requirements; the paper should state the implemented form and treat separate $h_A,h_B$ as a
design option.

**Gap splitting (same track, long silence).** Sort the inliers by $i$. Split between
consecutive inliers $(i_{(t)},j_{(t)}),(i_{(t+1)},j_{(t+1)})$ whenever

$$
i_{(t+1)}-i_{(t)}>g_A,\quad\text{or}\quad
j_{(t+1)}-j_{(t)}>g_B,\quad\text{or}\quad
j_{(t+1)}-j_{(t)}<-g_{\mathrm{back}} .
$$

Each resulting run is re-validated independently. This prevents two copies separated by a
long non-copy interval from being merged into a single giant coarse box. Multi-copy
retention is explicit: removing the inliers of one track must not remove the same query
interval at a different reference location; this is handled by the $\min(\mathrm{IoU}_A,
\mathrm{IoU}_B)$ rule in §6.

**Known limits.** Fixed positive slope range $[\alpha_{\min},\alpha_{\max}]$ excludes
reversal ($\alpha<0$) and extreme speed changes; continuous non-linear speed changes are
approximated only by several local lines. Minimum support makes segments shorter than the
sampling bound unreachable.

---

## 4. Finite tube (`PROPOSED`)

For an accepted track $r$ with inlier support interval
$[i_{\min}^r,i_{\max}^r]$,

$$
\ell_r=\max(0,i_{\min}^r-e_A),\qquad
u_r=\min(M,i_{\max}^r+1+e_A),\qquad
L_r=u_r-\ell_r .
$$

With $c_r(i)=\operatorname{round}(\alpha_r i+\beta_r)$ and half-width $w_r$, the tube is

$$
\mathcal T_r=\{(i,j):\ell_r\le i<u_r,\; j=c_r(i)+\delta,\; -w_r\le\delta\le w_r,\;0\le j<N\}.
$$

$e_A$ extends the search along the trajectory to recover boundaries that the sparse grid
did not hit; $w_r$ absorbs rate jitter and small local speed changes. The prototype uses
fixed constants; calling this an "uncertainty-guided adaptive band" would be false.

**Coverage limitation.** Refinement can only act inside $\bigcup_r\mathcal T_r$. A true
copy not covered by any tube cannot be recovered by the DP. No ground-truth boundary may be
used to construct a tube at inference; a GT-induced tube is an `Oracle-Tube Diagnostic` and
must never enter a main comparison table.

---

## 5. Local alignment (`PROPOSED`) and the prototype's alternative semantics

Let $r_{ij}=S_{ij}-\tau_{\mathrm{align}}$, with $r_{ij}=-\infty$ when either row is
invalid, and let $\mathcal P_r(i,j)=\{(i-\Delta i,j-\Delta j)\in\mathcal T_r:
(\Delta i,\Delta j)\in\mathcal S\}$ with
$\mathcal S=\{(1,1),(1,2),(2,1)\}$. The **proposed** recurrence is

$$
H_{ij}=\max\Big(0,\;r_{ij},\;
\max_{(u,v)\in\mathcal P_r(i,j),\,H_{uv}>0}
\big[H_{uv}+r_{ij}-\lambda_{\mathrm{gap}}\,g(i-u,j-v)\big]\Big),
$$

with $g(\Delta i,\Delta j)=\Delta i+\Delta j-2$. The zero term is a **restart**: a cell may
always abandon a bad prefix. A weak frame ($r_{ij}<0$) does not force a restart; it only
lowers the accumulated score, so a short weak stretch is bridged as long as the accumulated
score remains positive. This is the precise sense in which the zero floor is not "restart at
every weak frame".

Backtrace starts at $(i^\star,j^\star)=\arg\max_{(i,j)\in\mathcal T_r}H_{ij}$, provided
$H_{i^\star j^\star}>0$, and follows the predecessor that attained the maximum until a cell
whose score equals its own reward (a restart) or has no legal predecessor. The matched node
sequence is converted to half-open intervals by
$[i_{\text{first}},i_{\text{last}}+1)\times[j_{\text{first}},j_{\text{last}}+1)$.

**The prototype differs.** `fastvcl/tube.py::local_dp` initialises a cell without a legal
predecessor at $\max(0,r_{ij})$, but a cell **with** a legal predecessor is assigned the
continuation value unconditionally, even when negative and even when $\max(0,r_{ij})$ is
larger. Its docstring states this reading deliberately ("weak evidence, not absence of
evidence"). The two semantics are not equivalent:

| Regime | Proposed zero-floor | Prototype unconditional continuation |
|---|---|---|
| Long weak prefix before a true copy | prefix score reaches 0; copy restarts and is recoverable | prefix debt is carried; copy may never become positive |
| One weak frame inside a copy | bridged if accumulated score $>\lvert r\rvert$ | bridged unconditionally |
| Two copies separated by a long weak gap | second copy restarts | second copy inherits negative debt and may be lost |

A deterministic hand-constructed band (15 rows, one column, cosine 0.0 for rows 0–9 and
0.95 for rows 10–14, $\tau_{\mathrm{align}}=0.6$) gives prototype `best=0.0`,
`reachable=False`, and zero predictions, while the zero-floor recurrence gives
$H=1.75>0$ on the same input. The mirror case (positive copy, long weak gap, second
positive copy) makes the second copy's score negative under the prototype. These are
unit-level semantics diagnostics, not benchmark results; the exact commands are recorded in
`evidence/implementation_status.md`.

The proposed specification is a standard Smith-Waterman recurrence; its contribution here
is the *finite-tube domain* and the interaction between restart semantics and tube
extension, not the invention of local alignment. E3 must compare both semantics on identical
candidate tubes before any claim is made.

---

## 6. Multi-segment output and de-duplication (`PROPOSED`)

Two interval pairs $Y_1,Y_2$ are near-duplicates iff

$$
\min\big(\mathrm{IoU}_1([a_{s,1},a_{e,1}),[a_{s,2},a_{e,2})),\;
\mathrm{IoU}_1([b_{s,1},b_{e,1}),[b_{s,2},b_{e,2}))\big)\ge\theta_{\mathrm{dedup}} .
$$

$\min(\mathrm{IoU}_A,\mathrm{IoU}_B)$ is chosen over a single-axis IoU or a two-dimensional
area IoU because the same query interval copied twice to different reference times has
$\mathrm{IoU}_A=1$ but $\mathrm{IoU}_B=0$; the minimum keeps both, whereas an A-only rule
would delete a legal one-to-many copy. This is a **deduplication** rule; the official
evaluation metric is a different quantity (§5.2 of the paper).

**Status separation.** An empty prediction list is a legal output (`EMPTY`) for a negative
or low-confidence pair. A missing file, exception, timeout or OOM is `ERROR`/`SKIPPED` and
must never be converted to `[]`.

**Confidence.** The prototype score is
$q=0.7\cdot\mathrm{clip}(\bar s,0,1)+0.3\cdot\min(1,|\mathcal I_r^{\mathrm{seg}}|/
\max(1,L_A/\bar\Delta_A))$, where $\bar s$ is the mean smoothed path cosine and
$\bar\Delta_A$ is the median anchor spacing. It is uncalibrated and is **not** the
TransVCL/SPD objectness; thresholds are therefore selected per method, never shared as a
numerical constant.

---

## 7. Complexity

**Coarse stage.** For fixed strides,
$Q^{\mathrm{grid}}_{\mathrm{coarse}}=\sum_g|I_A^g||I_B^g|\approx MN\sum_g
1/(s_A^g s_B^g)$, which is $\Theta(MN)$ in the video lengths; fixed strides only reduce the
constant. Saving memory by streaming/tiling does not change the arithmetic order. The
prototype performs **two directional scans** (forward and backward Top-$K$) and a tie
re-scan, so the dot-product count actually executed is
$Q^{\mathrm{actual}}_{\mathrm{coarse}}\approx2MN\sum_g 1/(s_A^g s_B^g)$ plus tie work;
the paper must quote $Q^{\mathrm{actual}}$, not the idealized one-pass count.

**Tube stage.** With $L_r$ rows and $W_r=2w_r+1$ columns, the band similarity costs
$O(d\sum_r L_rW_r)$ if computed once per tube. Under direct offset addressing, a predecessor
with step $(\Delta i,\Delta j)$ is at
$\delta_u=(j-\Delta j)-c_r(i-\Delta i)$, so each transition is $O(1)$ and one DP is
$O(L_rW_r|\mathcal S|)=O(L_rW_r)$; with $P_r$ multi-path attempts,
$O(P_rL_rW_r)$. The prototype's `_step_predecessors` scans **all** $W_r$ columns of the
predecessor row for the non-diagonal steps, which is $O(W_r)$ per cell and
$O(P_rL_rW_r^2)$ per tube. The paper reports both the ideal and the implementation cost.

**Memory.** Input features $O((M+N)d)$; one band $O(L_rW_r)$; the DP tables
$O(L_rW_r)$; sequential tubes peak at $\max_r(L_rW_r)$ for numeric workspaces, but Python
objects, cached debug payloads and highly overlapping tubes can dominate in practice.

---

## 8. Default hyperparameters (prototype `configs/isc_only.yaml`)

These are development initial values, not tuned results.

| Group | Values |
|---|---|
| sampling | stride 4, Top-$K$ 1, $\tau=0.7$, mutual on, multi-scale off, independent phases off, cap 20,000, chunk 64 MB / 512 rows |
| RANSAC | $\epsilon_B=4.0$, $h_{\min}=5$, max tracks 8, $g_A=g_B=24$, $g_{\mathrm{back}}=1.0$, $L^A_{\min}=4$, $L^B_{\min}=8$, slope $[0.5,2.0]$, 2,000 iterations, confidence 0.99, unweighted LSQ |
| tube | $w=12$, $e_A=16$ (+2 boundary margin), $L^A_{\min}=3$, $L^B_{\min}=4$, min anchors 2, $\tau_{\mathrm{align}}=0.6$, $\lambda_{\mathrm{gap}}=0.1$, smooth 3, max 4 paths, low-quality gap 2, $\theta_{\mathrm{dedup}}=0.8$, max 64 segments |
| runtime | CPU/NumPy, float32 similarity / float64 DP, profiling disabled for timing |

---

## 9. Open design branches (must not be presented as settled)

1. Zero-floor DP vs. the prototype's unconditional continuation (§5). Decided by E3.
2. Multi-scale nesting vs. a single fine grid at equal budget (§2). Decided by E2.
3. Independent phases vs. synchronous phase; the combination with multi-scale is not
   implemented.
4. Separate $h_A,h_B$ vs. $\min(h_A,h_B)$; symmetric A-residual vs. B-residual only.
5. Adaptive $w_r,e_A$ from local residual statistics; currently fixed constants.
6. Whether the dual-axis gap-splitting and min-IoU rule produce a measurable increment over
   the simple sparse-to-band baseline. If not, `NOVELTY_GAP` must be reported.
