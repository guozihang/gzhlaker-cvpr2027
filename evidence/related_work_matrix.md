# Related-Work Verification Matrix

Checked 2026-10-17. `Depth` is what was actually read, not what the citation claims:
**F** = full text, **A** = abstract/introduction only, **M** = metadata only, **C** = code.
Every row lists the source actually fetched. Entries marked `UNVERIFIED` are not used as
factual claims in the paper.

## 1. Core benchmark and protocol

| Work | Venue / id | Task | Features | Training | Localizer | Protocol | This work | Depth | Source |
|---|---|---|---|---|---|---|---|---|---|
| VCSL (He et al.) | CVPR 2022, DOI 10.1109/CVPR52688.2022.02041 | segment-level video copy detection | ISC (256-d) | pretrained encoder; baselines re-implemented | HV/TN/DP/DTW + learned SPD | copy-overlap P/R (projection-length product), macro + sentinel exclusion | benchmark and metric used here | **F** | [CVF PDF](https://openaccess.thecvf.com/content/CVPR2022/papers/He_A_Large-Scale_Comprehensive_Dataset_and_Copy-Overlap_Aware_Evaluation_Protocol_for_CVPR_2022_paper.pdf) |
| VCDB (Jiang et al.) | ECCV 2014, DOI 10.1007/978-3-319-10593-2_24 | partial copy detection + localization | SIFT/BoW-era | no | Hough / matching | VCDB protocol | background only | **M** | [DOI](https://doi.org/10.1007/978-3-319-10593-2_24) |
| VSC 2023 (Pizzi et al.) | CVIU 2024, DOI 10.1016/j.cviu.2024.103997 | detection + localization challenge | learned descriptors | challenge solutions trained | various | µAP-style | related benchmark; RANSAC-line precedent | **A/M** | [DOI](https://doi.org/10.1016/j.cviu.2024.103997) |
| FiGVCL (Luo et al.) | TPAMI 2025, 47(11):10457–10474, DOI 10.1109/TPAMI.2025.3595625 | fine-grained VCL benchmark + method | fine-grained local embeddings | unsupervised strategy | learned | temporal-correspondence metric (full formula **UNVERIFIED**, paywalled) | related benchmark/method | **A** | [DOI](https://doi.org/10.1109/TPAMI.2025.3595625) |

**Corrections.** (i) The VCSL paper is *not* titled "VCSL: Video Copy Segmentation and
Localization"; VCSL is the dataset name. (ii) The metric is in §4.2 "New Metric", not §3.2.
(iii) The CVF PDF prints pages 21086–21095 while IEEE/Crossref lists 21054–21063; the bib uses
the CVF pages.

## 2. Classical zero-training methods

| Work | Venue / id | Mechanism | Relation | Depth | Source |
|---|---|---|---|---|---|
| Douze et al., circulant temporal encoding | IJCV 2016, 119(3):291–306, DOI 10.1007/s11263-015-0875-0 | circulant features + temporal alignment | HV-family precursor | **M/A** | [DOI](https://doi.org/10.1007/s11263-015-0875-0) |
| Tan et al., visual-temporal consistency | ACM MM 2009, pp. 145–154, DOI 10.1145/1631272.1631295 | temporal network of matched frames | TN baseline | **A** | [DOI](https://doi.org/10.1145/1631272.1631295) |
| Chou et al., pattern-based retrieval | IEEE TMM 2015, 17(3):382–395, DOI 10.1109/TMM.2015.2391674 | pattern matching + localization | DP/DTW-family precursor | **A** | [DOI](https://doi.org/10.1109/TMM.2015.2391674) |
| Smith & Waterman | J. Mol. Biol. 1981, 147(1):195–197, DOI 10.1016/0022-2836(81)90087-5 | local alignment with zero floor | zero-floor principle; our restricted step set differs from the canonical recurrence | **F** (standard) | [DOI](https://doi.org/10.1016/0022-2836(81)90087-5) |
| Tian et al., cascading framework | IEEE MultiMedia 2013, 20(3):72–86, DOI 10.1109/MMUL.2012.62 | multi-granularity + 2-D Hough | coarse-to-fine precedent | **M** | [DOI](https://doi.org/10.1109/MMUL.2012.62) |
| Liu et al., SAM | arXiv:2305.15679 | HRNet on similarity matrix + RANSAC line fit | RANSAC-line precedent | **F** | [arXiv](https://arxiv.org/abs/2305.15679) |

## 3. Learned localizers

| Work | Venue / id | Training | Key mechanism | Relation | Depth | Source |
|---|---|---|---|---|---|---|
| SPD (Jiang et al.) | ACM MM 2021, pp. 1618–1626, DOI 10.1145/3474085.3475301 | yes (detector) | detection on similarity map | learned baseline; **not** zero-training | **A/M** | [DOI](https://doi.org/10.1145/3474085.3475301) |
| TransVCL (He et al.) | AAAI 2023, 37(1):799–807, DOI 10.1609/aaai.v37i1.25158 | pretrained | attention enhancement + dense mutual/dual-softmax + detection head | planned learned comparator; chunked inference | **A** + **C** (`run.py`) | [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/25158) |
| RTR (Lu et al.) | ECCV 2024, LNCS 15070, pp. 18–35, DOI 10.1007/978-3-031-73254-6_2 | self-supervised (still trains) | regional token + transitive pairs | learned comparator; different features | **F/A** | [ECVA](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01818.pdf) |
| TCSVT 2024 (Henry et al.) | TCSVT 34(11):12006–12018, DOI 10.1109/TCSVT.2024.3420422 | image descriptors, no end-to-end localizer described | library retrieval + temporal-consistency re-ranking | different setting (library) and timing scope | **A** | [IEEE](https://ieeexplore.ieee.org/document/10577179) |
| iESTA (Ding et al.) | TCSVT 2025, 35(5):4409–4422, DOI 10.1109/TCSVT.2024.3517664 | yes | instance graph + transformer + spatial-temporal alignment | recent learned comparator | **M** | [DOI](https://doi.org/10.1109/TCSVT.2024.3517664) |
| VCSA (Li et al.) | ICASSP 2025, pp. 1–5, DOI 10.1109/ICASSP49660.2025.10888242 | yes (single-frame supervision) | contrastive + grid alignment | recent learned comparator | **M** | [DOI](https://doi.org/10.1109/ICASSP49660.2025.10888242) |
| MLT-Dedup (Wang et al.) | KDD 2026, pp. 8100–8111, DOI 10.1145/3770855.3818450 | yes | sparse clip retrieval + fine frame matching | closest efficiency system; library-scale, learned | **A** | [DOI](https://doi.org/10.1145/3770855.3818450) |
| Chen & Satoh, sampling analysis | MMM 2025, LNCS 15520, pp. 111–124, DOI 10.1007/978-981-96-2054-8_9 | no (analysis) | sampling interval vs. accuracy/speed | directly motivates H1/iso-budget | **A** | [DOI](https://doi.org/10.1007/978-981-96-2054-8_9) |

## 4. SPD attribution check

The execution plan states that "VCSL §5.2 explicitly classifies SPD as a learned detector".
This is **false**:

* The string "Similarity Pattern Detection" does not occur in VCSL.
* SPD is defined in Jiang et al., ACM MM 2021, and appears in VCSL §2.2 as related work and
  in §5.1 as one of five re-implemented baselines.
* The classification used by the paper (learned detector, not zero-training) is correct; the
  citation and section were wrong.

## 5. Novelty-overlap check

| Ingredient | Closest prior | Overlap | Consequence |
|---|---|---|---|
| Mutual NN matching | TransVCL (dense dual-softmax) | high, but dense | not novel per se |
| RANSAC line fit in the time plane | SAM; VSC 2023 solutions | high | not novel per se |
| Banded Smith-Waterman / DTW | Smith–Waterman; Chou; VCL DTW baselines | high | not novel per se |
| Sparse-to-fine for efficiency | Tian 2013; MLT-Dedup (KDD 2026) | high at the architecture level | not novel per se |
| Finite-tube refinement + zero-floor restart analysis + coverage/refinement separation + iso-budget protocol | none found as a controlled study | the claimed delta | must be tested by E1; `NOVELTY_GAP` until then |

A targeted search for training-free / zero-shot pairwise VCL in the 2023–2026 window
(OpenAlex title/abstract queries) returned no direct precedent. This is a search result, not
a proof of absence; it is graded `PILOT_ONLY` and must be repeated before submission.

## 6. Reading-depth honesty

`F` rows were read in full (or the relevant method/evaluation sections were read in full).
`A` rows were read only at abstract/introduction level; their hyperparameters, training
details and exact metric definitions are **not** independently verified here. `M` rows are
metadata-only and are cited for existence/positioning, not for mechanism details. No row is
used to justify a numerical comparison; all numbers are pending under the frozen protocol.

## Round-two source checks (2026-10-18)

Revisited the [AAAI TransVCL page](https://ojs.aaai.org/index.php/AAAI/article/view/25158)
and [ECVA RTR page](https://eccv2024.ecva.net/virtual/2024/poster/1083) for model/training
scope, plus [SAM metadata](https://arxiv.org/abs/2305.15679). This is a targeted check,
not a new exhaustive literature review. Detailed claims not supported by reading depth
were removed from the main Related Work; no first/absence-of-prior-work claim is made.
The CVF HTML request returned 403; the existing local VCSL text and evaluator code remain
the audit sources. The SAM HTML endpoint was unavailable; this round did not newly verify
its full method text. Existing historical F-depth entries are not upgraded by these checks.
