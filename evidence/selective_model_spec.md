# `seltive model`: selective visual verification specification (proposed)

> **Superseded scope, 2026-10-19:** the user now requests JEV for pre-RANSAC anchor filtering and post-alignment segment fusion. The [round-four execution plan](../FastVCL_CVPR2027_第四轮审查与执行方案.md) defines the new two-stage design, actions, budget and experiments. The post-localization-only scope below is historical; implementation and real-model validation remain pending.

Date: 2026-10-18. Status: **PROPOSED / NOT IMPLEMENTED / NOT EVALUATED**. This is the
interface and experiment specification requested in the round-two plan. It does not claim a
backend, a prompt, a selection policy or a measured benefit.

The user-requested name is exactly **`seltive model`**; it is kept verbatim in the figure,
the manuscript and this file. “JEV” is the historical internal name for the same branch.
The spelling is intentional and must not be “corrected” by a later editor.

## 1. What the branch is

`seltive model` is an **optional post-localization verification branch**. It consumes a
fixed candidate pool produced by the core FastVCL pipeline (candidate intervals plus matched
indices) and original A/B frame context, and returns a three-way verdict per selected
candidate. It is not a replacement for candidate discovery, not a new localizer, and not part
of the fixed-feature H1–H3 comparison.

The conservative default is:

- an **unselected** candidate keeps the core prediction;
- an **UNCERTAIN** verdict keeps the core prediction;
- a **failed** call (timeout, parse error, backend error) keeps the core prediction;
- a **decisive** verdict (COPY / NOT_COPY) may change the output only under a frozen fusion
  policy; that policy is `OPEN` and must be validated separately.

The branch cannot recover a copy that never entered the candidate pool. Candidate recall and
verification benefit are separate research questions and must be reported separately.

## 2. Inputs and prerequisites

### 2.1 Candidate records

For each core candidate \(c\):

| Field | Meaning | Required |
|---|---|---|
| `candidate_id` | Stable hash of the four endpoints and the source track id | yes |
| `a_s, b_s, a_e, b_e` | Half-open feature-index interval, core output | yes |
| `q_core` | Core score, uncalibrated | yes |
| `track_id` | Track/tube that produced the candidate | yes |
| `matched_nodes` | Core path nodes `(i,j)` used for the interval, if retained | recommended |
| `support` | Core anchor support and distinct A/B times | recommended |
| `core_action` | `keep` for every candidate at the start of verification | yes |

### 2.2 Original frames and the feature-index → frame map

The branch requires original frames, not only ISC features. The map must be **verified per
video**, not assumed:

- `video_id`, source path, container/decoder version;
- source frame count, nominal fps, variable-frame-rate flag;
- the exact feature extraction rule (every frame, fixed stride, fixed fps, scene-cut
  sampling, …) and its config hash;
- `sample_times_sec` (strictly increasing, length equal to the feature count) **or** a
  documented `feature_index -> source_frame` formula with an explicit offset and rounding
  convention;
- a boundary test on at least three videos (first/middle/last feature index) comparing the
  mapped frame to a human-checked timestamp;
- a hash of the frame list or timestamp table used by the run.

If the map is missing or ambiguous, the branch must refuse to run (`BLOCKED_MAPPING`), not
guess. A feature index is not a source frame and not a second.

### 2.3 Frame context

The verifier may receive, per candidate:

- A and B frames at the two boundaries (`a_s`, `a_e-1`, `b_s`, `b_e-1`);
- one or more interior matched pairs;
- a small temporal neighbourhood around each boundary (before/after);
- optional downscaled overview strips.

The exact set is `OPEN` (see §4). It must be declared per run and held fixed across the E6
arms. Frame extraction must be deterministic and cached by `(video_id, frame_index,
decode_config_hash)`.

## 3. Output schema

The backend must return a machine-parseable object, not free text:

```json
{
  "candidate_id": "sha256:...",
  "verdict": "COPY | NOT_COPY | UNCERTAIN",
  "confidence": 0.0,
  "evidence": ["short reason", "..."],
  "model_version": "...",
  "prompt_version": "..."
}
```

Rules:

- `verdict` is one of the three enum values; any other value is a parse failure, not a
  fourth class.
- `confidence` is optional and uncalibrated; it is not a probability unless calibrated on a
  declared set. Do not use it in a formula without validation.
- `evidence` is for audit and error analysis, not for automatic parsing of a decision.
- A response that cannot be parsed, validated against the schema, or tied to the correct
  `candidate_id` is `ERROR`/`UNCERTAIN` (depending on the declared failure policy), never
  silently `COPY` or `NOT_COPY`.
- The raw response, parsed response, latency, token counts, retries and cache status are
  logged.

## 4. Selection policy (`OPEN`)

### 4.1 Budget units

Declare one primary budget and report all:

- verifier calls per pair;
- frames sent per candidate and per pair;
- input/output tokens per call and per pair;
- wall-clock/queue time per pair;
- monetary cost per 1,000 pairs (if a paid API is used).

The budget is fixed **before** seeing test results. It is matched across E6 arms.

### 4.2 Candidate selection signals

Candidate signals available without new labels:

- `q_core` (score), rank within the pair;
- anchor support, distinct A/B times, path length;
- core path density, gap count, boundary strength;
- disagreement/uncertainty signals if a validated model exists;
- candidate length and position (A/B);
- random selection as a control.

The proposed selector is `OPEN`. A cheap deterministic baseline (e.g. top-$k$ by `q_core`)
and uniform random selection are required controls. A learned selector trained on
verification outcomes is a separate method and must not be presented as the same branch.

### 4.3 Determinism and de-duplication

- Selection must be deterministic given the pair, candidate pool, budget and seed.
- Candidates already covered by a decisive verdict for the same physical copy should not be
  re-verified; the de-duplication rule is `OPEN` but must be declared.
- Every candidate gets a disposition: `selected`, `unselected_budget`, `selected_and_kept`,
  `selected_and_changed`, `uncertain`, `failed`. Counts must sum to the candidate pool.

### 4.4 No ground truth at inference

GT boxes, GT key presence, split membership or test labels must never influence selection,
prompting, fusion or retry. A verifier-oracle analysis is allowed only as a separately
labelled ceiling, never as a deployed policy.

## 5. Sampling and prompt (`OPEN` but constrained)

The following must be fixed in a run manifest:

- frame layout: separate A/B images, side-by-side, or a labelled grid;
- resolution and JPEG/PNG encoding quality;
- number of frames per candidate and how they are chosen (boundaries, interior,
  uniform, neighbourhood);
- whether frames are sampled at native source fps or at feature-index positions;
- prompt text/version, system message and output schema;
- image ordering and labels (`A`, `B`, timestamps/indices) so the model cannot confuse axes;
- maximum tokens, temperature/decoding parameters and seed if the backend allows;
- language of the prompt (English for the draft);
- content-safety handling.

The prompt must ask for the schema in §3 and must not ask the model to compare against GT.
The exact prompt is not fixed in this document because no backend has been selected.

## 6. Backend (`OPEN`)

No backend is selected. Candidate classes:

1. a hosted multimodal API (paid; requires explicit user authorization and a data-upload
   decision);
2. a local open-weight multimodal model (hardware and license review required);
3. a small trained verifier on frame pairs (this would introduce training and is a different
   method, not the training-free core).

For any backend, record:

- provider/model identifier and immutable version or checkpoint hash;
- API endpoint/region and data-retention terms;
- image preprocessing and tokenizer version;
- deterministic/non-deterministic flags, seed support and temperature;
- timeout, rate limit, retry policy;
- cost per call and per 1,000 pairs;
- hardware (for local models: GPU model, memory, precision).

The name `seltive model` does not imply a particular model, training source or capability.
Do not infer a backbone from the name.

## 7. Failure handling, retries and caching

- Per-call timeout and a maximum retry count are declared before the run.
- Retries use bounded exponential backoff; the same candidate/frame set is retried, not a
  re-selected candidate.
- Failure classes: `timeout`, `rate_limit`, `network`, `auth`, `invalid_response`,
  `schema_error`, `content_blocked`, `out_of_memory`, `backend_error`.
- A failure never becomes an empty prediction. The candidate keeps the core result and is
  counted in the E6 failure table.
- A cache key includes candidate hash, frame hashes, model version, prompt version,
  preprocessing config and decoding parameters. Cache hits are reported separately from live
  calls; cached and live costs are not mixed.
- Retries count toward the call budget or are reported separately; they cannot be hidden.

## 8. Fusion policy (`OPEN`)

The only default that is currently defensible is **retain the core result unless a frozen
policy says otherwise**. Options that require separate validation:

| Option | Action | Required evidence |
|---|---|---|
| Conservative | COPY confirms; NOT_COPY deletes only if precision is high enough on a declared calibration set; UNCERTAIN keeps | precision/recall of NOT_COPY, false-deletion rate, full-set F1 |
| Score update | multiply or add a calibrated factor to `q_core` | calibration data, monotonicity, threshold re-selection |
| Re-rank only | use verdict to reorder; output set unchanged | re-ranking utility at fixed set size |
| Hard delete | remove NOT_COPY candidates | false-deletion audit on true copies; recall loss |
| Hard add | add candidates not in the core pool | forbidden: the branch cannot discover unseen copies |

No arbitrary weight (e.g. “+0.2 for COPY”) may be introduced without a calibration set and a
declared fusion equation. Fusion must be applied identically across E6 arms that use the
same backend, except for the arm that intentionally varies selection.

## 9. E6 experiment design (proposed, not run)

### 9.1 Fixed factors

- Same core candidate pool (hash), same pair list, same GT, same evaluator.
- Same backend/model version, prompt, frame budget, call budget and fusion rule.
- Same hardware and cache policy (or cache disabled for all arms).
- Same threshold-selection protocol; no test tuning.

### 9.2 Arms

1. **Core only**: no verification.
2. **Random selection**: uniform random candidates at the same budget.
3. **Cheap rule**: e.g. top-$k$ by `q_core` or lowest support, declared before the run.
4. **Proposed selective rule**: the selector under test.
5. Optional **oracle selection** (analysis ceiling only; never deployed).

### 9.3 Metrics

Whole-set (not selected-subset only):

- official P/R/F1 with the four denominators;
- candidate recall before and after verification;
- true candidates deleted (false deletions), false candidates corrected;
- unchanged/uncertain/failed counts;
- test negative-pair FAR (if the backend can run on negatives);
- full-set recall loss vs core-only;
- added latency and cost: frame acquisition/decoding, preprocessing, queue/network, model
  inference, retries, fusion, cache hit rate;
- per-candidate verdict confusion against a human-audited subset, if available (this is a
  diagnostic, not the official metric).

### 9.4 Statistics

- Pair is the default unit; if videos repeat across pairs, use the video-cluster unit or
  report the dependence limitation.
- Report paired differences on the same pairs and a confidence interval; five seeds of the
  selector/backend (if stochastic) are not data significance.
- Predeclare the primary metric and the decision rule. Do not select the best arm on test.

### 9.5 Acceptance

E6 is reportable only when:

1. the frame map is verified and frozen;
2. the backend/version/prompt is frozen and its cost is measured;
3. the candidate pool is identical across arms and hashed;
4. the full-set metrics and failure counts are complete;
5. the fusion policy is frozen before test;
6. the added cost is measured end-to-end, not only model latency.

Until then, the branch is an interface and a figure, not a result.

## 10. Privacy, security and cost

- Original frames may contain identifiable people, logos or sensitive content. Do not upload
  them to an external service without explicit permission and a data-handling decision.
- Prefer local/offline backends for development; record any external transfer.
- Store only what is needed: frame hashes, derived images, responses and costs; avoid
  retaining full videos in the repository.
- A paid API must not be called during paper-writing or CI; it requires explicit
  authorization and a budget.
- The verifier must not be used to circumvent content licenses or to reconstruct videos.

## 11. Open decisions

| ID | Decision | Status | Blocking |
|---|---|---|---|
| S1 | Feature-index → source-frame map and extraction rule | `OPEN` | E6 cannot start |
| S2 | Backend/model/version and provider | `OPEN` | E6 cannot start |
| S3 | Frame sampling/layout/resolution | `OPEN` | E6 comparability |
| S4 | Prompt and output schema final text | `OPEN` | parsing/fusion |
| S5 | Selection signal and budget allocation | `OPEN` | E6 arms |
| S6 | Fusion policy for decisive verdicts | `OPEN` | any output change |
| S7 | Failure/retry/caching policy | `OPEN` | cost accounting |
| S8 | Negative calibration data for NOT_COPY precision | `MISSING` | hard-delete option |
| S9 | Human-audited verdict subset | `MISSING` | verifier accuracy diagnostic |
| S10 | Privacy/data-upload approval | `OPEN` | external backend |

## 12. Current status

- The branch appears in the framework figure (main Fig. 1) and the Method as a proposed extension; it is excluded from
  the core algorithm, core tables and H1–H3 timing.
- No backend, frame map, prompt, selector or fusion policy is implemented.
- No verifier accuracy, cost or benefit is measured. No paid API was called.
- The historical JEV router is anchor-level and is **not** the candidate-level branch
  specified here; do not cite it as an implementation.
- The branch cannot recover copies absent from the candidate pool, and it adds visual input
  and cost beyond the fixed-feature comparison.

The next step is not to “turn on” a model. It is to freeze S1–S4 on a small development
subset, build the frame map and schema tests, then run E6 with the controls in §9. Until
then, the manuscript must keep the branch labelled as proposed and must not report a
verification benefit.
