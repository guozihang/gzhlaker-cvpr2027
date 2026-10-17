# Experiment Manifest and Frozen-Protocol Record

This manifest records the assets, hashes and conventions that any future run must reuse.
Hashes were recomputed on 2026-10-17 from the local VCSL copy, not copied from an old log.
No experiment in this draft is `BENCHMARK_VERIFIED`.

## 1. Dataset

| Item | Value |
|---|---|
| Dataset | VCSL (public video copy localization benchmark) |
| Local root | `<VCSL_ROOT>` (machine path intentionally omitted) |
| Feature directory | `eff256d/<video_id>.npy`, float32 `[T,256]` |
| Feature files | 12,254 |
| Feature bytes | 4,388,241,152 (≈4.09 GiB) |
| Train pairs | 97,033 (`pair_file_train.csv`) |
| Validation pairs | 41,798 (`pair_file_val.csv`) |
| Test pairs | 54,630 (`pair_file_test.csv`) |
| Test positive / negative | 27,315 / 27,315 (negatives = pairs with a missing GT key under the frozen local protocol) |
| Val positive / negative | 41,798 / **0** |
| Label keys | 166,146 (`label_file_uuid_total.json`) |
| Feature length | min 3, median 190, P95 1062.7, max 12,590 (audit) |
| Coordinate unit | feature index; half-open `[start,end)` |

### SHA-256 (recomputed)

| File | SHA-256 |
|---|---|
| `info/pair_file_val.csv` | `f7065467eb71340576c1f83ce6ada8810b02311d8d932c269069c414fa746f91` |
| `info/pair_file_test.csv` | `b52c1b5fb394d117d7f02206493331e78ba26fdb7ee344fc4302aba0cf231880` |
| `info/label_file_uuid_total.json` | `47d492e201741f10f970faedc6063feab06716dc604790fc5539af50b90a82ce` |

The audit additionally records
`pair_file_train.csv=e7fb88859e29dc872c10fc2b9e1a1a5c5a6516a6346ec685aec42ecef14a5c9c`,
`split_meta_pairs.json=840a3011b93556100ea6811120716ac3729d53afd24c39b6215a77eafd6d5329`,
`frames_all.csv=e9971d4bd08a31b03bc73fdf44b2f9d15e59ed7043b14af5ca410f2606e180b6`.

### What is *not* frozen

No full content hash of all 12,254 feature files exists. A later full run must build a
feature content digest and freeze it. The current pipeline can write
`features.content_digest`; it has not been run over the complete feature set.

## 2. Split semantics and leakage rules

* Val is 100% positive. **Negative-pair FAR cannot be measured on val.** It is measured only
  on the 27,315 key-missing test pairs; val entries in Table 1 must read
  `N/A (positive-only split)`.
* Test is evaluated once, after freezing. No test-driven threshold tuning, no post-hoc
  change of the metric tolerance, no per-method removal of hard pairs.
* All methods share the same feature files, the same pair CSV, the same GT JSON and the same
  evaluator. Old adjacent-repository VCSL data (55,530 pairs / 27,765 keys) must not be
  mixed with the current files.

## 3. Evaluator

| Item | Value |
|---|---|
| Reference | VCSL `metric/eval.py` (also shipped in the TransVCL repository) |
| Port | `fastvcl/evaluate.py::precision_recall`, `evaluate_overall_safe` |
| Per-pair precision | product of the two axis coverage ratios (intersection-over-prediction length per axis) |
| Per-pair recall | product of the two axis coverage ratios (intersection-over-GT length per axis) |
| Dataset aggregation | arithmetic mean over pairs whose per-pair value is **not exactly 1** (sentinel exclusion) |
| Reported F1 | $2\bar P\bar R/(\bar P+\bar R)$ with the macro means above |
| Coordinates | integer truncation in legacy-compatible mode; `conf=0` uses the legacy no-filter branch |
| Status handling | `ERROR`/`SKIPPED` never scored, never converted to `[]` |

**Denominators that every run must report** (and that Table 1/2 notes must reference):
`n_expected`, `n_processed`, `n_precision_denom`, `n_recall_denom`. The evaluator also
reports `excluded_precision_eq_1` and `excluded_recall_eq_1`, which explain why
`n_precision_denom` can be smaller than `n_processed`.

## 4. Threshold protocol

1. Fix the structural configuration (sampling, tube, RANSAC) on a development subset; do not
   touch test.
2. For **each method independently**, sweep its own confidence threshold on val and freeze
   the best one. Scores are not calibrated across methods (TransVCL/SPD objectness vs. the
   local alignment score), so a shared numerical threshold is not a fair comparison.
3. Record the frozen config SHA-256, the run id and the exact threshold.
4. Run test once. No second test selection.

## 5. Timing protocol (`T_localize`)

* **Start:** the raw feature tensors are already resident in CPU memory and all operators
  are initialised.
* **End:** the five-column prediction list for the pair exists in memory.
* **Included:** normalisation, masking, tiling, CPU↔GPU transfers (if any), sparse dot
  products/Top-$K$, RANSAC, tube construction, band similarity, local DP, post-processing,
  per-pair serialisation into the in-memory rows.
* **Separated:** `T_io` (feature read/validation), `T_export` (writing JSON), `T_init`
  (process start/JIT), `T_wall` (whole run).
* **Excluded from claims:** video decoding, ISC backbone extraction.
* **Controls:** same physical machine; fixed CPU model, thread count (`OMP_NUM_THREADS`,
  `torch.set_num_threads`), GPU model, precision, batch size, warm/cold cache; at least one
  warm-up round and ≥3 measured rounds; `profiling.enabled=false`; `torch.cuda.synchronize()`
  around GPU timing.
* **TransVCL:** sum chunk-pair times back to a per-video-pair total before computing
  Mean/P50/P95. Never report a single chunk-pair time as the video-pair time.
* **Speed-up definition:** state whether it is total-time ratio
  $\sum T^{\mathrm{base}}/\sum T^{\mathrm{ours}}$ or the per-pair mean ratio; report P50/P95;
  for RANSAC, report the standard deviation over ≥5 fixed seeds on a representative subset.

## 6. Hardware and software fingerprint (current machine, CPU only)

| Item | Value |
|---|---|
| Platform | macOS arm64 |
| Python | CPython 3.12.14 |
| NumPy | 2.3.5 |
| pandas | 3.0.1 |
| PyTorch | not installed |
| CUDA / CuPy | not available |
| GPU | none |
| Profiling in formal timing | must be `false` |

This machine cannot produce GPU numbers. CPU numbers from this machine are still usable if
the CPU model and thread count are reported, but they are **not** interchangeable with
GPU or cluster numbers.

## 7. Run artifacts required per method

`run_metadata.json`, `predictions.json`, `status.jsonl`, `metrics.json`,
`per_pair_timing.jsonl`, `config.snapshot.yaml`, `run_identity.json`, plus the evaluator
stdout. The exact schema is in §7 of the execution plan and summarised in the supplementary
material. A run is only admissible if the status file accounts for every selected pair.

## 8. Current admissibility

| Requirement | Status |
|---|---|
| Same features/CSV/GT/evaluator | possible; not yet executed for all methods |
| Frozen threshold per method | no frozen `frozen_protocol.json` exists |
| Zero-error complete val | no (best: 41,797/41,798 with 1 ERROR) |
| Single test run | not performed |
| GPU timing | not available |
| TransVCL weights and runtime | not available in the audited environment (no torch, no checkpoint found) |
| Simple Sparse-to-Band baseline | not implemented as a separate runnable method yet |

Conclusion: **every value in Tables 1–3 is pending.**
