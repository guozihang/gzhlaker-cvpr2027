> **历史版本，已由 2026-10-18 第二轮方案取代。** 请使用 [第二轮审查与执行方案](FastVCL_CVPR2027_第二轮审查与执行方案.md) 和 [第二轮 Agent 启动 Prompt](FastVCL_CVPR2027_第二轮Agent启动Prompt.md)。下文保留作历史记录；其中 JEV 禁令、部分数学/评价解释及旧文件链接不再作为当前执行依据。用户要求保留的 `seltive model` 以第二轮定义为准。

# FastVCL：CVPR 2027 初版论文与证据组织执行方案

> **版本：v2.1（修订优化版）｜2026-10-17**
>
> **当前事实基线：用户明确说明，代码尚未完成，目前仅处于初步跑通阶段。** 仓库历史文档中的“完成”“通过”“VERIFIED”“COMPLETE”等标签均属于阶段性开发记录，不能替代当前判断，更不能证明算法无误、实验完整或核心贡献已成立。
>
> **本轮核心目标：** 指导写作 Agent 产出一份科学诚实、数学定义自洽、论证连贯、可直接编译的匿名英文 CVPR 论文初稿；先将已生成的矢量示意图与空结果图实际编入正文版式，后续再随算法定型与冻结评测更新。
>
> **研究范围边界：** 给定 Query/Reference 视频对、固定预提取 ISC 逐帧特征、下游不引入任何新增训练参数。**本方案冻结研究问题与任务边界，但不冻结原型缺陷、临时超参数或尚未完成消融论证的启发式细节。**

## 0. 任务定位：本阶段写什么、不写什么

论文工作名暂定为：**FastVCL: Training-Free Sparse-to-Tube Video Copy Localization**。其中 `Fast` 仅为项目代号；在获得同协议、同硬件的端到端实测对比前，正文不得宣称“已证实加速”。若后续实验结论使论文定位转向“质量—成本权衡分析”或“候选覆盖与局部精化机制研究”，应同步调整标题与摘要口径。

本阶段交付物是**研究假设清晰、数学定义完备、实现状态透明、实验数据显式留白的完整论文初稿**：

* **允许并鼓励在 Method 中给出严格、自洽的拟议算法规范（标记为 `PROPOSED`）**，并在内部证据文件中逐项记录拟议规范与当前原型代码的差异。

* **严禁两类极端倾向：** 一是以“代码未定型/实验未跑完”为由只交提纲、目录或空泛套话；二是为了让初稿显得“像终稿”而把未验证设计包装成已验证结论，或把局部开发指标塞入正式主结果表。

全文围绕以下核心研究问题展开：

> 在给定视频对与固定预训练逐帧描述子的前提下，能否仅利用稀疏对应提议将高分辨率时序对齐限制在少量有时间几何证据支撑的有限局部管道（Finite Tubes）内，在控制短片段漏检与边界退化的同时，改善复制定位质量与实际计算开销之间的权衡？

这一问题意识比单纯声称“把 Top-$K$、RANSAC 与局部 DP 拼起来所以更快”更具学术审查价值，但**它本身是一个待检验的科学假设，而非既定事实**。论文必须正面回答三个可证伪子问题：**稀疏候选覆盖率（H1）、局部管道边界恢复（H2）、端到端系统净收益（H3）**；任一环节在实测中失效，都必须如实收窄或修正论文主张。

### 0.1 范围约束与操作授权

* **任务与输入边界：** 输入固定为给定 Query（视频 $A$）与 Reference（视频 $B$）的预提取 ISC 特征序列 $[T, 256]$；仅解决视频对内的复制片段起止定位（Pairwise Video Copy Localization），不涉及全库视频级检索（Video-Level Retrieval）。

* **方法主线与待论证项：** 候选流水线为“稀疏对应提议 $\rightarrow$ 多条局部线性时间轨迹拟合 $\rightarrow$ 支持区间切分与有限 Tube 构建 $\rightarrow$ 带内局部动态规划对齐 $\rightarrow$ 双轴去重与多段输出”。其中多尺度采样、A/B 独立相位、Mutual Top-$K$ 规则、轨迹双轴约束及局部 DP 重启机制均属待消融验证的设计选择，不得预先宣称为最优。

* **“Training-Free” 的严格界定：** 仅指**下游定位器不包含任何需要梯度训练或微调的参数**。必须如实说明：（1）上游 ISC 特征提取器本身经过大规模预训练；（2）在验证集（`val`）上选择阈值与超参数仍使用了监督标注信息，因此绝不能表述为“完全无监督（unsupervised）”“零标注（label-free）”或“超参数无关（parameter-free）”；同时，HV、TN、DP、DTW 等传统方法同样不训练下游参数，不能把 `Training-free` 当作相对于所有基线的独有优势。

* **严禁越界扩展：** 不引入 DINOv2、JEV、VLM、可学习分歧预测器或任何微调模块；不修改作为对照基准的 TransVCL 推理逻辑。写作 Agent 的职责是完成论文撰写、数学规范整理、文献核查、图表脚本与证据管理，**不在本轮直接改写 FastVCL 核心推理代码或启动大规模评测作业**。

* **指令优先级与冲突处理：** 用户后续明确指示优先于本文件；仓库内历史文档若与代码现状或本方案冲突，必须在 `evidence/implementation_status.md` 中显式记录冲突点，不得静默采信旧文档中的乐观表述。

### 0.2 统一证据状态分级（Claim-Level Evidence Grading）

所有关键论断必须按**具体主张粒度**标注证据状态，严禁以文件存在或单测通过替代实验证明：

| 证据状态 | 严格定义 | 正文与内部文档允许的表述方式 | 
| ----- | ----- | ----- | 
| `SOURCE_VERIFIED` | 已核对一手论文原文或官方仓库，并记录具体章节、公式或代码位置 | 可作为带适用范围限定的背景事实与基线机制描述 | 
| `PROPOSED` | 数学定义与算法逻辑已明确给出，但代码尚未实现或尚未通过实测验证 | 正文用 “We formulate / propose / investigate …”；内部台账标明 `PROPOSED` 及实现差距 | 
| `IMPLEMENTED_UNVALIDATED` | 原型代码中存在对应分支，但尚未验证其数学等价性、边界鲁棒性或实际收益 | 仅作为内部实现现状记录；不得直接转化为论文性能贡献 | 
| `PILOT_ONLY` | 仅在合成样本、冒烟测试、小样本子集（如 `dev1000`）或不完整运行中观测到 | 仅可用于工程诊断或问题动机说明，必须注明样本规模与覆盖限制，严禁进入正式主表 | 
| `BENCHMARK_VERIFIED` | 在冻结协议、完整数据集划分下完成评测，原始预测与计时日志可复核 | 可写入正式实验结果表、摘要与结论中的实证结论 | 
| `MISSING / CONFLICT` | 关键材料缺失、来源相互矛盾，或代码实现与数学定义不一致 | 正文用醒目 `\TODO{...}` 占位，并在 `evidence/missing_evidence.md` 单列阻断项 | 

## 1. 先核查现有材料，再组织论文叙事

### 1.1 本机路径与只读核查原则

| 资产角色 | 本机绝对路径 | 访问与使用原则 | 
| ----- | ----- | ----- | 
| 论文工作区 | `/Users/gzhlaker/Documents/code/gzhlaker_cvpr2027` | 主写作目录；直接复用现有 LaTeX 工程并保留用户已有修改 | 
| FastVCL 原型 | `/Users/gzhlaker/Documents/code/FastVCL` | **只读核查**当前代码逻辑、配置与历史日志；不将其当作不可更改的终稿规范 | 
| TransVCL 对照 | `/Users/gzhlaker/Documents/code/gzhlaker_transvcl` | **只读核查**分块推理机制、评估入口与数据处理协议 | 
| 数据集线索 | `/Users/gzhlaker/Downloads/VCSL` | 结合审计文档、清单行数与 SHA256 校验核实版本，不凭文件夹名称主观臆断 | 

若跨机器执行，先探测实际路径；若某路径不存在，在证据清单中标记 `MISSING` 并继续完成不依赖该路径的写作任务，严禁伪造“已读取某文件”的核查记录。

**推荐核查顺序：**

1. 阅读本方案、同目录《写作 Agent 启动 Prompt》以及论文目录下的 `main.tex`、`preamble.tex`、`sec/`、`main.bib`、`figures/README.md`。

2. 对照阅读 FastVCL 的 `README.md`、`docs/IMPLEMENTATION_STATUS.md`、`docs/VCSL_ASSET_AUDIT.md`、`docs/GPU_VERIFICATION.md` 与 `results/` 下的原始 JSON 产物，甄别历史文档中的阶段性乐观表述与实际产物之间的差距。

3. 核查 `configs/isc_only.yaml` 及 `fastvcl/{sparse,trajectory,tube,segments,pipeline,evaluate,measure}.py`（必要时含 `fastvcl/backends/`），厘清当前默认执行路径。

4. 阅读 `docs/METHOD_DECISIONS.md` 与 `docs/EXPERIMENT_PROTOCOL.md`，区分“早期设计设想”与“当前代码实际行为”。

5. 核查 TransVCL 的 `run.py`、`transvcl/models/`、`evaluation.py`、`metric/eval.py` 与 `docs/REPOSITORY_GUIDE.md`。

6. 若环境中未找到旧版《`FastVCL_第一层_零训练执行文档.md`》，直接记为未提供，不得将其他文档静默冒充为该文件。

### 1.2 2026-10-17 只读核查快照（用于防错，不代表验收通过）

2026-10-17 快照时，FastVCL `HEAD` 为 `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，TransVCL `HEAD` 为 `4b57976da5ad1b38f999c96aba315e63a272acdf`。写作 Agent 执行时应重新记录最新 commit、工作区 `git status --short` 及 `git diff` 摘要。以下核查事实必须在写作中严格遵守：

| 核查发现 | 原始证据位置 | 写作与实验规约约束 | 
| ----- | ----- | ----- | 
| 正式配置默认使用单尺度 `stride=4`、`top_k=1`；多尺度处于可选/未默认开启状态 | `FastVCL/configs/isc_only.yaml` | 严禁把“默认采用多尺度稀疏匹配”写成既定实现事实，也不得预设多尺度必然带来正收益 | 
| 某次 `val` 运行仅完成 `8,075 / 41,798` 对，其余 `33,723` 对为 `SKIPPED` | `results/layer1_final_20261014/val/run_summary.json` | 属于不完整历史运行，严禁将其指标填入正式 `val` 主结果表 | 
| 旧配置 `val_full` 虽遍历完整清单，但存在 `1 ERROR` | `results/layer1_complete_20261014/val_full/val/run_summary.json` | 不能算作零故障完整评测，更禁止与新配置的部分运行结果拼接 | 
| `dev1000` 的 `metrics.json` 实际统计 `n_pairs=200`（输入清单为 1,000 行），即使标有 `COMPLETE` | `results/layer1_complete_20261014/dev1000/val/metrics.json` | 目录名与 `COMPLETE` 标签均不代表有效评分样本量；必须分别核对总对数、完成数与有效分母 | 
| 仅有 CPU 小样本 Tube 耗时剖析；GPU 文档明确记录尚未完成真卡运行验收 | `results/l15_g1/tube_profile_*.json`、`docs/GPU_VERIFICATION.md` | CPU 剖析仅可用于定位实现瓶颈；Python 参考测试通过不等于 CUDA 内核已在真实 GPU 上验证加速 | 
| 默认配置开启了 `profiling.enabled: true` | `FastVCL/configs/isc_only.yaml` | 正式端到端延迟评测必须显式关闭细粒度探针，防止探针同步与记录开销污染 `T_localize` | 
| 论文工程仍包含 CVPR 2026 模板说明正文与示例 BibTeX 条目 | `main.tex`、`README.md`、`main.bib` | 仅改年份宏不代表已符合 CVPR 2027 官方模板；必须清理模板示例正文与虚拟文献条目 | 

## 2. 论文立论：科学假设、反例边界与创新性审查

### 2.1 核心叙事与基线公平描述

现有视频复制定位（VCL）方法主要沿三条路线演进：（1）基于全帧或粗采样相似度图的几何投票与路径搜索（如 HV、TN、DP、DTW）；（2）在二维相似度图上训练卷积/检测器的学习式方法（如 SPD）；（3）利用自注意力与交叉注意力进行端到端特征交互和边界回归的模型（如 TransVCL）。

本文切入的结构性矛盾是：**用于发现潜在复制假设的“粗候选搜索”与用于确定精确起止时刻的“高分辨率时序对齐”，是否必须共享同样稠密的全矩阵计算域？** 我们的基本思路是用低成本稀疏采样与稳健轨迹拟合提议少量局部管道（Finite Tubes），再仅在管道内部执行高分辨率局部对齐。同时必须坦诚交代该建模的前提与失效边界：局部线性轨迹假设依赖于片段内的近似匀速单调对应，面对**高度重复背景、极短复制片段（短于采样跨度）、剧烈非线性变速、倒放或强画中画/拼接编辑**时可能退化。

**严禁将基线塑造成失真的“稻草人”：**

* 本地核查表明，TransVCL 的 `run.py::load_features_list` 已将长视频特征按最大长度 `1200` 切分为特征块（chunk pairs）送入网络，因此**绝不能在引言或相关工作中声称“TransVCL 必须一次性在显存中分配整段超长视频的完整** $M \times N$ **矩阵”**，也不能笼统将所有注意力模块简写为全序列长度上的严格二次复杂度。

* 与 TransVCL 的理论及实测对比，应聚焦于**跨块特征交互（Self-/Cross-Attention）、块内稠密相关图（Correlation & Softmax）生成以及二维检测头开销**与本文“固定特征 + 稀疏锚点提议 + 窄带局部 DP”之间的计算结构差异。

### 2.2 三个必须独立检验的可证伪假设

| 假设编号 | 核心科学假设 | 所需实证证据 | 否定或收窄该假设的观测条件 | 
| ----- | ----- | ----- | ----- | 
| **H1 候选覆盖** | 在显著减少帧间点积次数的条件下，稀疏匹配与轨迹拟合仍能以高召回率覆盖真实复制片段 | 候选区间召回率 vs. 实际点积次数/粗阶段耗时曲线；按片段长度（极短/中/长）、相对相位偏移与重复场景的分桶诊断 | 若粗阶段即漏掉大量真实片段（尤其是短片段），后续 Tube 精化无论如何设计都无法挽回 | 
| **H2 边界恢复** | 有限 Tube 内的局部动态规划能实质性改善粗轨迹外接框的起止边界精度，而非单纯增加额外计算 | 固定同一批候选轨迹，对比“直接输出粗轨迹支持框”“固定宽度标准局部对齐”与“本文拟议 Tube 精化”的最终 F1 及起止边界误差（Boundary MAE/IoU） | 精化后 F1 无显著提升，或提升完全来自盲目扩大搜索带宽、消耗接近全矩阵的算力 | 
| **H3 系统净收益** | 减少精细对齐搜索域所节省的算术量，能够转化为真实硬件上的端到端延迟与内存优势 | 同机器、同协议、同特征下的准确率—延迟（F1–Latency）曲线、峰值内存（CPU RSS / GPU Peak）、分阶段耗时占比与完成率 | Python 循环、前驱扫描或数据搬运开销主导总耗时，导致实测速度反而不如向量化全矩阵基线或传统 TN/DP | 

### 2.3 创新性（Novelty）独立审查与强简单基线

Mutual Nearest Neighbor（MNN）、Top-$K$ 匹配、RANSAC 直线拟合、带状动态规划（Banded DP/DTW）、多尺度采样与 GPU 并行化均为计算机视觉与序列对齐中的经典工具。将它们简单串联或赋予新名词，**并不自然构成达到 CVPR 标准的算法创新**。

为此，论文与实验设计必须强制设立一个**简单组合强基线（Simple Sparse-to-Band Baseline）**：

> **单尺度网格（如固定 stride** $s$**）+ 互近邻/Top-**$K$ **锚点 + 标准 RANSAC 直线拟合 + 固定半宽** $w$ **的标准 Smith-Waterman 局部对齐。**

在此基础上，本文最多聚焦**一个经过反例诊断与消融证实的核心机制增量**（例如：针对嵌套网格冗余与跨视频相对相位偏移的采样预算分配策略，或针对同斜率断续复制与背景吞噬的双轴紧凑度/局部重启机制）。写作 Agent 必须在 `evidence/claims_ledger.md` 中逐项登记：

1. 最接近的既有文献机制（如 TN 的图路径、HV 的参数空间投票、Chou et al. 的模式匹配或 TCSVT 2024 的时序一致性重排）；

2. 本文机制与上述方法及“简单组合强基线”的**精确数学差异**；

3. 专门针对该差异构造的**失败反例场景**与单变量消融实验（E1–E4）；

4. 若当前原型尚未体现超越简单组合强基线的明确机制，必须在 `claims_ledger.md` 中如实标记 `NOVELTY_GAP`，绝不靠堆砌未验证模块或拔高修辞掩盖缺口。

正文总结的候选贡献点严格控制在 **3 条以内**：（1）面向固定特征视频复制定位的 Sparse-to-Tube 计算解耦框架与可证伪分析视角；（2）一个经受单变量消融检验的候选覆盖或局部边界恢复机制（待实测确认后定稿）；（3）同协议下涵盖传统几何/对齐方法与学习式方法的质量—效率—失效边界基准分析。

## 3. 相关工作核查：覆盖经典基石与 2024–2026 前沿，杜绝跨协议混排

下表提供必须核查的一手文献入口。**列出入口不代表已读完全文；写作 Agent 必须实际核对方法细节、特征类型、训练需求与评估协议，并在 `evidence/related_work_matrix.md` 中记录阅读深度（全文/章节/仅摘要）。**

| 代表性工作 | 已核实的一手来源链接 | 核心机制与本文对比核查重点 | 
| ----- | ----- | ----- | 
| **VCSL** (CVPR 2022) | [arXiv HTML 全文](https://www.google.com/search?q=https%3A%2F%2Farxiv.org%2Fhtml%2F2203.02654v2) · [官方仓库](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Falipay%2FVCSL) | 定义给定视频对定位任务与段级 copy-overlap P/R/F1 指标；提供 HV、TN、DP、DTW（传统零训练）与 SPD（学习式）基准实现及数据划分说明 | 
| **TransVCL** (AAAI 2023) | [AAAI 出版页](https://www.google.com/search?q=https%3A%2F%2Fojs.aaai.org%2Findex.php%2FAAAI%2Farticle%2Fview%2F25158) · [arXiv](https://www.google.com/search?q=https%3A%2F%2Farxiv.org%2Fabs%2F2211.13090) · [官方代码](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Ftransvcl%2FTransVCL) | 自注意力/交叉注意力特征增强 + Softmax 相似度图 + 区域检测头；需结合本地 `run.py` 核实其 `max_length=1200` 分块推理与实际计时口径 | 
| **Self-Supervised VCL with Regional Token Representation (RTR)** (ECCV 2024) | [ECCV 2024 官方页](https://www.google.com/search?q=https%3A%2F%2Feccv.ecva.net%2Fvirtual%2F2024%2Fposter%2F1083) · [官方代码](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Feccv1818rtr%2FECCV1818) | 引入 Regional Token 与传递性自监督生成复制对训练检测器；虽无需人工标注，但**仍包含表征与检测器训练且特征不同于固定 ISC**，不能将系统级差异直接归因为定位算法本身 | 
| **Fast Video Deduplication and Localization With Temporal Consistence Re-Ranking** (IEEE TCSVT 2024) | [IEEE Xplore 原文](https://www.google.com/search?q=https%3A%2F%2Fieeexplore.ieee.org%2Fdocument%2F10577179%2F) · [作者仓库](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Fengrchrishenry%2Floc_aware_video_dedup) | 检索与时序一致性重排序/定位结合；必须核查其问题定义（是否含全库检索过滤）、特征维度与计时起止范围，明确与本文纯视频对定位的异同 | 
| **FiGVCL: Fine-Grained Benchmark and Method for Video Copy Localization** (IEEE TPAMI 2025) | [IEEE CSDL / DOI](https://www.google.com/search?q=https%3A%2F%2Fdoi.org%2F10.1109%2FTPAMI.2025.3595625) · [PubMed 记录](https://www.google.com/search?q=https%3A%2F%2Fpubmed.ncbi.nlm.nih.gov%2F40758515%2F) · [官方仓库](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2Fvslab-vcl%2FFiGVCL) | 2025 年发表的细粒度视频复制定位基准与方法（Vol. 47, No. 11, pp. 10457–10474）；必须核查其细粒度转换类型、评价协议及与 VCSL 的关系 | 

**必须补充核查并正确引用的经典方法与特征来源（防止错引或漏引）：**

* **ISC 描述子来源：** Yokoo et al., *Contrastive Learning with Large Memory Bank and Negative Embedding Subtraction for Accurate Copy Detection* (`arXiv:2112.04323`, NeurIPS 2021 Image Similarity Challenge 冠军方案) 及数据集报告 Douze et al., *The 2021 Image Similarity Dataset and Challenge* (`arXiv:2106.09672`)。

* **传统定位基线原始文献：**

  * **HV（Hough Voting / 霍夫投票）：** Douze et al., *Circulant Temporal Encoding for Video Retrieval and Temporal Alignment*, IJCV 2016；Jiang et al., *VCDB: A Large-Scale Database for Partial Copy Detection in Videos*, ECCV 2014。

  * **TN（Temporal Network / 时序网络路径）：** Tan et al., *Scalable Detection of Partial Near-Duplicate Videos by Visual-Temporal Consistency*, ACM MM 2009。

  * **局部序列对齐与模式匹配：** Smith & Waterman, *Identification of Common Molecular Subsequences*, J. Mol. Biol. 1981；Chou et al., *Pattern-Based Near-Duplicate Video Retrieval and Localization on Web-Scale Videos*, IEEE TMM 2015。

* **重要分类纠错：** **VCSL 论文 §5.2 明确指出，SPD（Similarity Pattern Detection）是基于深度网络在相似度图上训练的目标检测式方法，绝不能将其与 HV、TN、DP、DTW 一起归类为“无需训练的传统几何/动态规划算法”。**

* **CVPR 2027 同期工作（Contemporaneous Work）官方界定：** 根据 [CVPR 2027 Call for Papers](https://www.google.com/search?q=https%3A%2F%2Fcvpr.thecvf.com%2FConferences%2F2027%2FCallForPapers)，**2026 年 9 月 15 日之后**首次公开出现的论文属于同期工作（需检索、引用并讨论，但不强制要求完成实验对比）；**2026 年 9 月 15 日及之前**公开的工作均属在先工作（Prior Work），必须全面检索并在相关工作与实验设计中正面回应。

* **表格隔离原则：** 实验章节必须将“本工作在冻结协议、同一 ISC 特征下统一复现/运行的公平对比”**与**“直接引用自原论文、特征或协议可能不同的文献参考值”严格分表（或在表中用明确的横线区块与表注隔离），严禁将不同特征、不同测试清单下的数字混排后加粗宣称“SOTA”。

## 4. Method 数学规范：先建立无歧义定义，再对齐实现差距

Method 每一小节都必须清晰回答五个问题：**（1）输入张量与定义域是什么；（2）执行什么数学运算或离散决策；（3）为什么需要该步骤；（4）引入了什么计算/内存代价；（5）在什么退化条件下会失效。** 内部通过 `evidence/method_spec.md` 锁定拟议数学规范，通过 `evidence/implementation_status.md` 逐项记录当前原型代码与该规范的偏差。

### 4.1 输入表示、有效掩码与半开区间坐标约定

设给定视频对包含 Query 视频 $A$ 与 Reference 视频 $B$，其固定预提取 ISC 逐帧特征矩阵分别为：

$$
F_A \in \mathbb{R}^{M \times d}, \qquad F_B \in \mathbb{R}^{N \times d}, \qquad d = 256,
$$

其中 $M, N \in \mathbb{Z}_{\ge 1}$ 为特征帧数，离散帧索引采用从 $0$ 开始的整数集合 $i \in \{0, 1, \dots, M-1\}$ 与 $j \in \{0, 1, \dots, N-1\}$。

**预处理与有效行掩码：** 为避免污染共享原始特征文件，所有归一化均在内存副本上进行。定义有效行指示掩码 $m_i^A, m_j^B \in \{0, 1\}$：当第 $i$ 行特征满足非空、全部分量有限（finite）且 $\ell_2$ 范数 $\|F_{A,i}\|_2 > \varepsilon$（如 $\varepsilon = 10^{-12}$）时，$m_i^A = 1$ 并计算单位向量 $\bar{f}_i^A = F_{A,i} / \|F_{A,i}\|_2$；否则记 $m_i^A = 0$，$\bar{f}_i^A = \mathbf{0}$。同理定义 $m_j^B$ 与 $\bar{f}_j^B$。任意两帧间的余弦相似度记为：

$$
S_{ij} = \begin{cases} \langle \bar{f}_i^A, \bar{f}_j^B \rangle, & \text{if } m_i^A = 1 \text{ and } m_j^B = 1, \\ -\infty, & \text{otherwise.} \end{cases}
$$

> **符号一致性要求：** 正文与公式中必须用上标区分 $\bar{f}_i^A$ 与 $\bar{f}_j^B$（或统一写为 $S_{ij}$），严禁写成无上标的 $\langle \bar{f}_i, \bar{f}_j \rangle$，以免在 $i=j$ 时混淆两段视频的特征行；视频标识 $A, B$ 也不得与 batch size 符号混用。

**输出与坐标语义：** 算法输出为预测复制片段集合：

$$
\mathcal{Y} = \left\{ (a_s, b_s, a_e, b_e, q) \;\middle|\; 0 \le a_s < a_e \le M,\; 0 \le b_s < b_e \le N,\; q \in \mathbb{R} \right\}.
$$

其中 $[a_s, a_e)$ 与 $[b_s, b_e)$ 为特征索引轴上的**左闭右开区间**（半开区间长度分别为 $a_e - a_s$ 与 $b_e - b_s$），$q$ 为未校准的排序置信分数（非概率值）。在送入 VCSL 官方评估器前，必须显式说明从特征索引到评估器输入坐标的映射、过滤与整数截断规则；除非明确乘以帧采样间隔并通过时间戳校验，否则不得将特征索引直接混称为“秒（seconds）”或“原视频原始帧号”。

### 4.2 稀疏对应提议：区分“采样网格”“点积计算”与“锚点保留”

设稀疏采样计划集合为 $\mathcal{G}$。每个采样计划 $g \in \mathcal{G}$ 由两轴步长 $(s_A^g, s_B^g) \in \mathbb{Z}_{\ge 1}^2$ 与初始相位 $(p_A^g, p_B^g)$（满足 $0 \le p_A^g < s_A^g,\; 0 \le p_B^g < s_B^g$）参数化，对应的有效采样索引集合定义为：

$$
I_A^g = \{ p_A^g + k s_A^g : k \in \mathbb{Z}_{\ge 0} \} \cap \{ i \in \{0, \dots, M-1\} : m_i^A = 1 \},
$$

$$
I_B^g = \{ p_B^g + k s_B^g : k \in \mathbb{Z}_{\ge 0} \} \cap \{ j \in \{0, \dots, N-1\} : m_j^B = 1 \}.
$$

在单个采样计划 $g$ 内部，仅对子网格 $(i, j) \in I_A^g \times I_B^g$ 评估相似度 $S_{ij}$，并定义带阈值 $\tau$ 的网格内双向 Top-$K$（Mutual Top-$K$）锚点集：

$$
\mathcal{A}_g = \left\{ (i, j) \in I_A^g \times I_B^g \;\middle|\; j \in \operatorname{TopK}_{B,g}^{(K)}(i),\; i \in \operatorname{TopK}_{A,g}^{(K)}(j),\; S_{ij} \ge \tau \right\},
$$

其中 $\operatorname{TopK}_{B,g}^{(K)}(i) \subseteq I_B^g$ 表示在集合 $I_B^g$ 中与 $i$ 相似度最高的前 $K$ 个索引（需明确定义分数并列时的确定性 tie-breaking 规则，如优先取较小索引或保留全部并列项后再截断）。当合并多个采样计划时，**必须先在原始帧坐标** $(i, j)$ **上执行集合去重**，再按分数排序施加全局锚点上限（anchor cap $C_{\max}$）：

$$
\mathcal{A} = \operatorname{Cap}_{C_{\max}}\!\left( \bigcup_{g \in \mathcal{G}} \mathcal{A}_g \right).
$$

**Method 中必须正面剖析的四个关键边界与反例：**

1. **嵌套同相位网格的集合包含关系與去重必要性：** 若两轴均取零相位 $p_A^g = p_B^g = 0$，则 `stride=4` 和 `stride=8` 的采样点集满足 $I^8 \subset I^4 \subset I^2$。此时叠加粗尺度**不会访问任何超出 `stride=2` 的新帧位置**；其唯一作用是改变粗网格内的局部 Top-$K$ 竞争邻域。若跨计划合并时不按 $(i, j)$ 坐标去重，重合锚点将在后续 RANSAC 中被重复计入内点支持度，造成伪增益；因此多尺度实验必须与“同预算/单独 `stride=2`”严格对照。

2. **同步相位偏移 vs. 独立相对相位偏移：** 若片段在视频 $A$ 中始于偶数帧而在视频 $B$ 中始于奇数帧，同步平移 $(p_A, p_B) = (p, p)$ 仍可能错过真实对应对角线；而完整枚举两轴独立相位 $(p_A, p_B) \in \{0, \dots, s-1\}^2$ 实质上等价于将全矩阵拆分为 $s^2$ 个子网格。禁止将原型尚未实现的独立相位搜索画成已验收模块。

3. **短片段漏检的采样下界：** 在单网格步长 $s$ 下，若要求一条候选轨迹至少包含 $h_{\min}$ 个来自不同 $A$ 轴采样时刻的锚点，则被检出片段在 $A$ 轴上的持续长度必须至少跨越 $(h_{\min}-1)s + 1$ 个特征帧。这只是能够形成候选的**必要非充分条件**，必须在文中如实说明短片段的漏检风险。

4. **Top-**$K$ **锚点数不等于独立时序证据数：** 当 $K > 1$ 时，$\mathcal{A}_g$ 不再是一对一的严格互最近邻（Strict MNN）。同一个 $i \in I_A^g$ 产生的至多 $K$ 个配对共享同一查询时刻，在静止镜头或周期性重复纹理下极易形成团状伪锚点，因此后续轨迹评估必须统计**去重后的独立投影时刻数**，而非原始锚点对数量。

### 4.3 多轨迹稳健拟合与双轴支持区间切分

给定去重锚点集 $\mathcal{A} = \{(i_m, j_m, S_{i_m j_m})\}_{m=1}^{|\mathcal{A}|}$，局部时间对应关系建模为一族分段仿射直线：

$$
j \approx \alpha_r i + \beta_r, \qquad \alpha_r \in [\alpha_{\min}, \alpha_{\max}] \subset (0, +\infty).
$$

注意：斜率 $\alpha_r$ 是**两个特征索引轴之间的步进比**；仅当两视频的特征抽帧率完全一致且恒定时，$\alpha_r$ 才对应播放倍速比。

**稳健拟合与双轴合法性约束：** 每轮迭代从剩余锚点中通过固定随机种子的 RANSAC（或确定性假设生成）采样点对 $(i_1, j_1), (i_2, j_2)$（要求 $|i_2 - i_1| \ge \Delta_{\min}$），计算初始 $(\alpha, \beta)$ 并筛选内点集。为区分“正向残差 vs. 双轴残差”，必须明确定义内点判定准则（例如 $B$ 轴残差 $|j - (\alpha i + \beta)| \le \epsilon_B$，或同时要求反投影残差 $|i - (j - \beta)/\alpha| \le \epsilon_A$）。对内点集做加权最小二乘重拟合后，必须**重新校验斜率范围与内点支持度**：

* **独立时序支持度：** 内点在 $A$ 轴与 $B$ 轴上的不同时刻集合 $|\pi_A(\mathcal{I}_r)| \ge h_{\min}^A$ 且 $|\pi_B(\mathcal{I}_r)| \ge h_{\min}^B$；

* **最小时间跨度：** $\max \pi_A(\mathcal{I}_r) - \min \pi_A(\mathcal{I}_r) \ge L_{\min}^A$ 且 $\max \pi_B(\mathcal{I}_r) - \min \pi_B(\mathcal{I}_r) \ge L_{\min}^B$；

* **同轨长间隙切分（Gap Splitting）：** 将同一条拟合直线上的内点按 $i$ 升序排列为 $(i_{(1)}, j_{(1)}), \dots, (i_{(k)}, j_{(k)})$。若相邻内点满足 $i_{(t+1)} - i_{(t)} > g_{\max}^A$ 或 $|j_{(t+1)} - j_{(t)}| > g_{\max}^B$，必须在间隙处将其切分为独立的子轨迹段，防止将同斜率但中间隔有长段非复制内容的两个片段错误合并为一个跨越整段视频的巨型粗框。

* **多段复制保留：** 在迭代提取多条轨迹并移除已解释内点时，不得粗暴删除同一查询区间 $[a_s, a_e)$ 映射到参考视频不同位置 $[b_{s,1}, b_{e,1})$ 与 $[b_{s,2}, b_{e,2})$ 的合法多次复制。同时需在 Limitations 中明确：固定正斜率区间 $[\alpha_{\min}, \alpha_{\max}]$ 不支持倒放（$\alpha < 0$）或极端倍速，连续非线性加减速仅能由多条局部线性轨迹近似。

### 4.4 有限管道（Finite Tube）构建与带内局部动态规划

对每条通过检验的子轨迹段 $r$（其内点支持区间为 $[i_{\min}^r, i_{\max}^r] \times [j_{\min}^r, j_{\max}^r]$），构建**有限搜索管道（Finite Tube）** $\mathcal{T}_r$，而非横跨 $[0, M)$ 全长的无限对角带。设两端边界扩展余量为 $e_A \in \mathbb{Z}_{\ge 0}$，管道在 $A$ 轴上的有效搜索范围为：

$$
\ell_r = \max(0,\; i_{\min}^r - e_A), \qquad u_r = \min(M,\; i_{\max}^r + 1 + e_A), \qquad L_r = u_r - \ell_r.
$$

对于每个查询帧 $i \in \{\ell_r, \dots, u_r - 1\}$，记轨迹中心在 $B$ 轴上的整数取整位置为 $c_r(i) = \operatorname{round}(\alpha_r i + \beta_r)$，管道半宽为 $w_r \in \mathbb{Z}_{\ge 0}$（最大带宽 $W_r = 2w_r + 1$）。则管道 $\mathcal{T}_r$ 内的合法网格单元集合定义为：

$$
\mathcal{T}_r = \left\{ (i, j) \in \{\ell_r, \dots, u_r - 1\} \times \{0, \dots, N - 1\} \;\middle|\; j = c_r(i) + \delta,\; \delta \in \{-w_r, \dots, +w_r\} \right\}.
$$

> **术语与范围澄清：** $e_A$ 控制沿时间轨迹两端的延伸长度（用于恢复稀疏采样未命中的真实起止边界），$w_r$ 控制垂直于轨迹方向的局部容差带宽（吸收帧率抖动与局部小幅变速）。当前原型若使用固定常数 $(e_A, w_r)$，正文不得将其夸大表述为“自适应不确定性引导带宽（uncertainty-guided adaptive tube）”。

**带内局部对齐（Local Alignment）的拟议数学规范 vs. 原型实现冲突：**
为在有限管道 $\mathcal{T}_r$ 内定位精确起止边界并允许提前终止或重新开始，拟议的标准局部对齐（Smith-Waterman 型带零下界截断）状态转移定义为：对任意 $(i, j) \in \mathcal{T}_r$，令单步匹配收益为 $r_{ij} = S_{ij} - \tau_{\mathrm{align}}$（当 $m_i^A = 0$ 或 $m_j^B = 0$ 时 $r_{ij} = -\infty$），前驱步长集合为 $\mathcal{S} \subseteq \{1, \dots, \Delta_A\} \times \{1, \dots, \Delta_B\}$，对应的合法带内前驱集合为 $\mathcal{P}_r(i, j) = \{ (i - \Delta i, j - \Delta j) \in \mathcal{T}_r : (\Delta i, \Delta j) \in \mathcal{S} \}$。则局部累计得分 $H_{ij}$ 应满足：

$$
H_{ij} = \max\left( 0,\; r_{ij},\; \max_{(u, v) \in \mathcal{P}_r(i, j),\; H_{uv} > 0} \bigl[ H_{uv} + r_{ij} - \lambda_{\mathrm{gap}}\, g(i - u, j - v) \bigr] \right).
$$

**必须显式记录并交接的原型代码冲突（严禁直接照抄代码注释或掩盖问题）：**

* **冲突现象：** 核查 `fastvcl/tube.py::local_dp` 发现，其文档字符串（docstring）虽然写有外层 `max(0, ...)`，但实际 Python 执行分支在存在合法前驱时直接赋值为续接得分 `score + best_prev`，**既未对负累计分做零下界截断（zero-floor reset），也未在** $r_{ij}$ **优于负前驱续接时将回溯起点重置为当前格**；同时 `_step_predecessors` 中涉及带内相对列索引 $\delta \in \{0, \dots, W_r-1\}$ 与绝对坐标 $j$ 的转换。

* **科学后果与诊断反例：** 若不加零下界截断与起点重置，会导致两个严重缺陷：（1）**长低相似前缀污染**：当扩展余量 $e_A$ 将一段非复制背景纳入管道前端时，连续负收益会使 $H_{uv} \ll 0$，要么拖垮后续真实复制段的累计分使其无法检出，要么在回溯时将整段背景前缀吞入预测框；（2）**同轨断续片段错误桥接**：同一管道内的两段独立复制若间隔一段中等长度负分间隙，只要累计分未彻底归零，回溯就会将其连成单个过长片段。

* **本轮写作处理原则：** 在 Method 正文中明确写出**数学上自洽的局部对齐定义（带** $H_{uv} > 0$ **续接条件与明确的回溯起止准则）并标记为 `PROPOSED`**；在 `evidence/implementation_status.md` 中完整记录 `fastvcl/tube.py::local_dp` 的当前行为差异及上述四个诊断单测场景（长负分前缀 + 真复制、单帧弱响应、同轨双段长间隙、非零斜率导致相邻行带中心 $c_r(i)$ 移动时的列偏移映射）。

### 4.5 多段输出、双轴去重与方法固有边界

从所有管道提取候选路径区间对 $(a_s, b_s, a_e, b_e, q)$ 后，需经过最小长度过滤、置信度阈值过滤及跨管道非极大值抑制（NMS）/合并：

* **双轴重叠度量：** 两个二维区间对 $Y_1 = ([a_{s,1}, a_{e,1}), [b_{s,1}, b_{e,1}))$ 与 $Y_2 = ([a_{s,2}, a_{e,2}), [b_{s,2}, b_{e,2}))$ 的重叠度采用双轴一维 IoU 的最小值：
  

  $$
  \operatorname{IoU}_{\min}(Y_1, Y_2) = \min\bigl( \operatorname{IoU}_1([a_{s,1}, a_{e,1}), [a_{s,2}, a_{e,2})),\; \operatorname{IoU}_1([b_{s,1}, b_{e,1}), [b_{s,2}, b_{e,2})) \bigr).
  $$

  
  必须阐明采用 $\min(\operatorname{IoU}_A, \operatorname{IoU}_B)$ 而非单轴 IoU 或二维面积 IoU 的原因：当同一段查询片段 $[a_s, a_e)$ 在参考视频的不同时间段被重复复制两次时，其 $\operatorname{IoU}_A = 1$ 但 $\operatorname{IoU}_B = 0$，使用 $\min(\operatorname{IoU}_A, \operatorname{IoU}_B) = 0$ 可天然保留这类一对多合法复制，避免误删。

* **合法空输出与运行异常隔离：** 无任何候选超过阈值时输出空列表 `[]`（状态记为 `EMPTY`），这是负例对或低置信对的合法预测结果；而文件缺失、异常抛出、超时或内存溢出必须记为 `ERROR` 或 `SKIPPED`，严禁静默转换为 `[]`。

* **局部精化的能力边界：** Tube 精化只能在其覆盖域 $\bigcup_r \mathcal{T}_r$ 内修正边界；若某真实复制片段在粗匹配与轨迹拟合阶段完全未被任何 $\mathcal{T}_r$ 覆盖，Tube 精化不可能凭空恢复该片段。严禁在正常推理中使用 Ground Truth 边界生成 Tube（任何使用 GT 诱导区域的实验必须单独标为 `Oracle-Tube Diagnostic`，绝不进入正式对比主表）。

### 4.6 复杂度分析：区分理想渐近界与当前实现的真实算术/扫描开销

复杂度分析必须同时报告**算术运算量**与**实现级扫描开销**，不得用理想化的 `O(LW)` 掩盖原型瓶颈：

1. **粗匹配阶段：** 理论网格对数为
   

   $$
   Q_{\mathrm{coarse}}^{\mathrm{grid}} = \sum_{g \in \mathcal{G}} \vert{}I_A^g\vert{}\,\vert{}I_B^g\vert{} \approx MN \sum_{g \in \mathcal{G}} \frac{1}{s_A^g s_B^g}.
   $$

   
   注意：只要采样步长 $s_A^g, s_B^g$ 为固定常数，穷举子网格点积对视频长度 $M, N$ 而言**仍然是** $\Theta(MN)$ **二次复杂度**（仅常数因子缩小为 $\sum_g (s_A^g s_B^g)^{-1}$）。必须严格区分三个不同概念：**（a）不常驻保存完整** $M \times N$ **浮点矩阵（内存优化）；（b）保留的锚点集合** $\vert{}\mathcal{A}\vert{} \ll MN$**（输出稀疏）；（c）粗匹配点积次数是否为次二次（算术复杂度）**。此外，若实现中双向 Top-$K$ 或多网格未复用已算点积，应以实际执行的点积次数 $Q_{\mathrm{coarse}}^{\mathrm{actual}}$ 计入 $O(d \, Q_{\mathrm{coarse}}^{\mathrm{actual}})$。

2. **Tube 精化阶段（揭示 `O(LW)` 与原型 `O(P L W^2)` 的差距）：** 设第 $r$ 条管道长度为 $L_r$，带宽为 $W_r = 2w_r + 1$，多路径重复提取次数为 $P_r$。

   * **带内相似度计算：** 若每个管道只计算一次带内余弦相似度并缓存 $(L_r \times W_r)$ 表，开销为 $O\bigl(d \sum_r L_r W_r\bigr)$；若每次路径提取重复计算，则乘上 $P_r$。

   * **DP 状态转移与前驱寻址：** 在拟议规范中，给定当前格 $(i, j)$（带内偏移 $\delta_i = j - c_r(i)$）和步长 $(\Delta i, \Delta j) \in \mathcal{S}$，前驱格在行 $u = i - \Delta i$ 中的绝对列号为 $v = j - \Delta j$，因此其在行 $u$ 带内的相对列下标可通过**直接偏移运算** $\delta_u = (j - \Delta j) - c_r(u)$ 在 $O(1)$ 时间内定位，单次 DP 复杂度为严格 $O(L_r W_r \vert{}\mathcal{S}\vert{}) = O(L_r W_r)$。

   * **当前原型瓶颈说明：** 核查 `fastvcl/tube.py::_step_predecessors` 可见，当前原型在非零步长下遍历前驱行的全部 $W_r$ 个带内列来检查绝对坐标差，导致单格寻址退化为 $O(\Delta_A W_r)$，单条管道总转移开销达到 $O(P_r L_r W_r^2)$。论文在复杂度小节必须如实区分“直接偏移寻址下的 $O(L_r W_r)$ 复杂度”与“原型未索引扫描的 $O(P_r L_r W_r^2)$ 开销”。

3. **内存峰值分解：** 显式区分常驻输入特征内存 $O((M+N)d)$、分块粗匹配工作区、单管道 DP 表 $O(L_r W_r)$、Python 对象开销、进程最大驻留集（CPU Peak RSS）与 GPU 峰值显存（`max_memory_allocated` / `max_memory_reserved`）。顺序处理各条 Tube 时，数值工作区峰值取决于 $\max_r (L_r W_r)$ 而非 $\sum_r L_r W_r$，但若候选轨迹爆炸、管道高度重叠或保存全部中间轨迹对象，仍可能抵消局部化带来的节省。

## 5. 实验协议与可证伪验证矩阵

### 5.1 数据集版本锁定与防泄漏调参协议

主实验基于冻结版本的 **VCSL** 数据集；VCDB 或其他数据集仅在协议核实且本地特征/标注完备时作为泛化补充，严禁把未实际运行的外部数据集写入已完成实验。

**本地数据版本历史线索（执行时必须重新校验 SHA256 与行数）：**
根据 `FastVCL/docs/VCSL_ASSET_AUDIT.md` 记载，本地 VCSL 验证集（`val`）包含 `41,798` 个视频对且**全部为正例对（100% positive pairs）**；测试集（`test`）清单为 `54,630` 对（其中 `27,315` 对在标注 JSON 中无对应 key，按该版本官方评测逻辑解释为真实负例对），而邻近 TransVCL 仓库附带的旧版清单为 `55,530` 对。因此：

* **严格统一清单与评估器：** 所有对比方法必须运行在**完全相同的特征文件、同一个 pair list CSV、同一份 GT JSON 和同一个评估器实现**上，并在 `evidence/experiment_manifest.md` 中记录文件的 SHA256 校验和与有效对数。

* **验证集全正例的重要推论：** 由于本地 `val` 划分全为正例对，**在 `val` 上根本无法测量真实负例误报率（Negative-Pair FAR / FPR），也不能声称在 `val` 上选出的阈值已经验证了对负例对的抑制能力！** 正文与表格中对应 `val` 的负例 FAR 必须明确标注为 `N/A (positive-only split)`。

* **超参数与阈值冻结铁律：** 算法结构与候选预算先在开发子集或 `val` 上确定；**每个对比方法（包括 HV/TN/DP/DTW、TransVCL、简单组合基线与 FastVCL）必须各自在 `val` 上独立网格搜索其最优置信度阈值** $\tau_{\mathrm{conf}}$（因为不同方法的输出分数尺度与分布完全不同，强制使用同一个数值阈值属于不公平对比）。一旦锁定配置与各自最优阈值，立即冻结代码 commit 与配置文件，在 `test` 上**仅执行单次正式评估**，严禁根据 `test` 结果反向挑选配置或事后修改“精度相当（matched-accuracy）”的容差定义。

* **异常与缺失零容忍：** 任何方法的 `ERROR / SKIPPED / OOM / Timeout` 必须单独统计并报告完成率（Completion Rate），严禁将其静默当作空预测 `[]` 混入分母，也严禁按方法各自剔除运行失败的困难样本。

### 5.2 评价指标精确定义与四个分母记录要求

主评价指标采用 VCSL 官方段级 **Copy-Overlap Precision (**$\bar{P}$**)、Recall (**$\bar{R}$**) 与 F1**：

* 对每个视频对 $p$，设预测区间集合为 $\mathcal{D}_p$，真实标注区间集合为 $\mathcal{G}_p$。单对精确率重叠比 $P_p$ 与召回率重叠比 $R_p$ 按两轴（Query 轴与 Reference 轴）与匹配区间的交集总长度除以对应总长度计算（详见 VCSL 论文 §3.2 与 `metric/eval.py`）。

* **数据集级聚合语义（Macro-Averaging with Empty-Set Sentinel Exclusion）：** 本地 `metric/eval.py` 对空集返回哨兵值 `1` 并在数据集级求均值时将其排除，即数据集平均精确率 $\bar{P}$ 的分母为**产生非空预测的有效样本对数** $N_{\mathrm{pred}>0}$，数据集平均召回率 $\bar{R}$ 的分母为**具有非空真实标注的正例样本对数** $N_{\mathrm{gt}>0}$，最终数据集 F1 定义为两者的调和平均：
  

  $$
  \mathrm{F1} = \frac{2 \bar{P} \bar{R}}{\bar{P} + \bar{R}}, \qquad \text{注意：}\mathrm{F1} \neq \frac{1}{\vert{}P\vert{}} \sum_{p} \mathrm{F1}_p.
  $$

* **强制报告四个计数分母：** 鉴于历史日志中曾出现 `dev1000` 清单有 1,000 行但 `metrics.json` 中 `n_pairs=200` 的歧义，所有正式与诊断实验的 `metrics.json` 及表格说明必须同时列出四个整数：**（1）清单总对数 `n_expected`；（2）成功处理完的对数 `n_processed`；（3）计入** $\bar{P}$ **分母的非空预测对数 `n_precision_denom`；（4）计入** $\bar{R}$ **分母的正例对数 `n_recall_denom`**。

* **Legacy 评估分支陷阱：** 本地旧版 `evaluation.py` 在 `conf != 0` 与 `conf == 0` 时走不同的过滤与坐标整数截断分支。所有方法必须通过同一套经过核实的评估入口评测；若对除零保护等工程崩溃做修复，不得改变非退化样本上的官方指标数值。

* **自定义诊断指标的严格区分：** 为检验 H1 与 H2，可额外报告**候选管道段级覆盖率（Tube Segment Recall @ IoU** $\ge \theta$**）**、**起止边界平均绝对误差（Boundary MAE，以特征帧为单位并注明匹配条件）**及**测试集负例对误报率（Negative-Pair FAR，即** $27,315$ **个真实负例对中输出至少一个预测段的对数占比）**。必须在文中明确声明这些属于**自定义诊断指标（Diagnostic Metrics）**，不得与 VCSL 官方 copy-overlap F1 混为一谈；同时由于 VCSL 仅提供起止区间框而非逐帧稠密对应真值，严禁宣称测量了“真实逐帧匹配召回率（frame-level ground-truth correspondence recall）”。

### 5.3 最小可证伪实验矩阵（E0–E5）

实验章节的每一张表、每一组曲线都必须对应检验 H1–H3 或创新性增量，不做无信息量的模块累加堆砌：

| 实验编号 | 核心检验问题与对照组设计 | 严格控制的变量 | 必须报告的观测指标与证伪判据 | 
| ----- | ----- | ----- | ----- | 
| **E0 外部基准对比** | 官方传统零训练基线（**HV、TN、DP、DTW**）与学习式基线（**TransVCL**；若 SPD 权重/特征可对齐则一并纳入）vs. **FastVCL** | 同一 ISC 特征、同一 `val`/`test` 清单、同一评估器；各方法在 `val` 上独立调优阈值后冻结 | Copy-overlap $\bar{P}/\bar{R}/\mathrm{F1}$、负例 FAR（`test`）、端到端延迟 `T_localize`（Mean/P50/P95）、内存峰值、完成率 | 
| **E1 创新性守门消融** | **简单组合强基线**（单尺度 `stride` + Mutual Top-$K$ + 标准 RANSAC + 固定半宽标准 Smith-Waterman 局部对齐）vs. **拟议 FastVCL** | 相同特征、相同粗阶段点积预算、相同硬件后端；逐项列出唯一新增机制 | 若拟议方法相比简单组合强基线在相同预算下无显著 F1、短片段召回或边界精度提升，则诚实标记 `NOVELTY_GAP` | 
| **E2 粗阶段采样与相位（检验 H1）** | 单尺度 `stride=4` vs. 单尺度 `stride=2` vs. 同相位嵌套多尺度 `{2,4,8}`（去重前后对比）vs. 独立相位偏移 | 显式记录各方案的真实点积数 $Q_{\mathrm{coarse}}^{\mathrm{actual}}$ 与保留锚点数 $\vert{}\mathcal{A}\vert{}$；必须包含\*\*等计算预算（Iso-Budget）\*\*对照点 | 候选段覆盖率 vs. 实际点积数/粗阶段耗时曲线；按片段长度（如 $<15, [15,60), \ge 60$ 帧）分桶召回率 | 
| **E3 管道局部精化机制（检验 H2）** | （a）直接输出粗轨迹外接支持框 vs.（b）管内全局 DTW（无零截断）vs.（c）原型无零截断 `local_dp` vs.（d）拟议带零下界重启的局部对齐 | **锁定完全相同的上游候选轨迹集合**，隔离上游随机性对下游精化评估的干扰 | 最终 $\bar{P}/\bar{R}/\mathrm{F1}$、已匹配片段的起止边界 MAE、长负分前缀与同轨双段反例上的误合并率、精化阶段耗时 | 
| **E4 轨迹约束单变量消融** | 基准配置 vs. 移除双轴独立支持度约束 vs. 移除同轨长间隙切分（Gap Split）vs. 扫描管道延伸余量 $e_A$ 与半宽 $w_r$ | **每次仅改变一个机制或超参数（Leave-One-Out / Single-Factor）**，固定 RANSAC 随机种子 | 候选轨迹数量、总评估网格单元数 $\sum_r L_r W_r$、重复纹理下的伪轨迹比例、F1 与延迟变化 | 
| **E5 系统实现与计算耗时分解（检验 H3）** | 原型未索引前驱扫描 vs. 直接偏移寻址 $O(LW)$ CPU 实现 vs. 向量化全矩阵基线（及完成真卡验收后的 GPU/CUDA 后端） | 明确硬件型号、线程数、浮点精度、冷热缓存与输入规模分桶（按 $M \times N$ 分位数） | 粗匹配、RANSAC、Tube 相似度、DP 转移、后处理各阶段耗时占比；证实算术量削减是否真正转化为 wall-clock 加速 | 

> **消融设计红线：** 严禁把 `w/o geometry` 实现为“直接跳过轨迹拟合导致输出 0 个候选 Tube、F1=0”的虚假消融；若要评估几何拟合的作用，其替代方案必须是在相同点积预算下 directly around top-scoring anchor clusters 构建局部窗口或直接运行全图稀疏路径搜索。

### 5.4 公平计时边界与统计复核规约

为确保与 TransVCL 及传统方法的效率对比经得起审稿推敲，主计时口径固定为：

* **核心定位耗时 `T_localize`（主表报告口径）：** 从原始预提取特征张量 $F_A, F_B$ **已驻留 CPU 内存**且模型/算子已完成初始化开始计时，直至当前视频对的五元组预测列表 $\mathcal{Y}$ 在内存中构造完毕为止。**必须包含：** 特征复制与 $\ell_2$ 归一化、分块组装、CPU\$\\leftrightarrow$GPU 张量搬运（若使用 GPU）、稀疏点积与 Top-$K$、RANSAC 拟合、Tube 构建与局部 DP、后处理去重。

* **单独分离报告的辅助耗时：** 磁盘 `.npy/.npz` 特征读取耗时 `T_io`、结果序列化写出耗时 `T_export`、首次进程启动/JIT 编译耗时 `T_init`，以及包含磁盘 I/O 的总挂钟时间 `T_wall`。由于各方法均从预提取 ISC 特征出发，**未包含原视频解码与 ISC 骨干网络抽帧耗时，正文中严禁将 `T_localize` 包装为“从原始视频流出发的端到端实时处理速度”**。

* **硬件、批次与缓存控制：** 在同一台物理机器上完成所有对比；显式固定并报告 CPU 型号、绑核/线程数（`OMP_NUM_THREADS` / `torch.set_num_threads`）、GPU 型号（若有）、浮点精度（FP32/FP16）、PyTorch/NumPy 版本。测量时关闭 `profiling.enabled`，执行至少 1 轮完整预热（warmup）后再独立测量 $\ge 3$ 轮（严禁从结果缓存文件直接读回跳过计算）；若使用 GPU，每次计时起止处必须调用 `torch.cuda.synchronize()`。

* **视频对延迟 vs. TransVCL 块对（Chunk-Pair）延迟：** TransVCL 将长视频拆分为多个 $\le 1200$ 帧的块对进行 batch 推理，评估时必须将其还原并汇总为**每个原始视频对（Per-Video-Pair）的总延迟**后再计算 Mean / P50 / P95，绝不能把单个分块对的推理耗时直接当作完整长视频对的耗时。

* **加速比统计量声明：** 数据集总耗时比 $\left(\sum_p T_p^{\mathrm{base}}\right) \big/ \left(\sum_p T_p^{\mathrm{ours}}\right)$（受长视频对主导）与逐对加速比几何/算术均值 $\operatorname{mean}_p(T_p^{\mathrm{base}} / T_p^{\mathrm{ours}})$ 数学含义不同，必须在表注中明确声明所用的定义并同时提供 P50/P95 分位数。针对 RANSAC 等含随机采样的步骤，需固定默认种子并在代表性子集上报告多随机种子（如 5 个不同 seed）的标准差。

### 5.5 论文正文最少三张核心表格规范

1. **Table 1（Main Comparison under Frozen VCSL Protocol）：**

   * 列字段：`Method | Venue | Feature | Learned Localizer? | Extra Training in This Work? | Val P | Val R | Val F1 | Test P | Test R | Test F1 | Test Neg-FAR (%) | Mean Latency (ms) | Run ID / Source`

   * 规范：上半区为**文献原报参考值**（注明原论文协议差异，不参与同行加粗争优）；下半区为**本文冻结协议下同 ISC 特征实测对比**（HV、TN、DP、DTW、TransVCL、Simple Baseline、FastVCL）。注意 TransVCL 与 SPD 的 `Learned Localizer?` 必须填 `Yes`（即使本实验直接加载其官方预训练权重未重新训练），而 HV/TN/DP/DTW 与 FastVCL 填 `No`。

2. **Table 2（System Efficiency, Memory & Stage Breakdown）：**

   * 列字段：`Method | Hardware & Backend | Precision | Evaluated Pairs (Done/Total) | T_localize Mean / P50 / P95 (ms) | Throughput (pairs/s) | CPU Peak RSS (MB) | GPU Peak Mem (MB) | Test F1`

   * 规范：纯 CPU 运行的方法在 `GPU Peak Mem` 列填 `N/A`（严禁填 `0` 混淆概念）；未测项目统一填 `\TODO{PENDING}` 或 `--` 并在表注说明。

3. **Table 3（Controlled Mechanism & Hypothesis Ablations for H1–H3）：**

   * 列字段：`Exp ID | Variant Description | Exact Single-Factor Change | Coarse Dot Products (M) | Tube Cells Evaluated (K) | Cand. Recall (%) | Boundary MAE | Val/Test F1 | T_localize (ms)`

   * 规范：清晰对应 E1–E4 的单变量对照，用真实算术工作量（点积数与 Tube 评估格数）支撑效率与精度的因果解释。

## 6. 图表规范：立即插入四张既有占位图，后续按数据驱动替换

工作区 `figures/` 目录下**已经生成好四张占位图**（每张均含可编辑 `.svg`、矢量 `.pdf` 与预览 `.png`，由 `scripts/generate_paper_placeholders.py` 驱动，详细说明见 `figures/README.md`，插入代码参考 `figures/placeholders.tex`）。写作 Agent **必须在第一轮就把这四张 `.pdf` 实际通过 `\includegraphics` 编入 LaTeX 正文**，不得只留文字框或另交一份“画图计划”。

| 图文件标识（`figures/`） | 当前占位图属性 | 初稿正文使用与图注强制规范 | 后续替换为正式图所需的核验材料 | 
| ----- | ----- | ----- | ----- | 
| `fig_1_teaser.pdf` | 稠密全矩阵/分块计算域 vs. Sparse-to-Tube 局部计算域的概念示意 | 置于 Introduction；图注必须标明 `Conceptual schematic`，**不得将其画成或声称为 TransVCL 内部网络架构的精确解剖图** | 方法定型后与最终符号对齐；若加入实测 F1–Latency 对比点，必须绑定真实 `run_id` | 
| `fig_2_framework.pdf` | 五阶段拟议流水线架构图 | 置于 Method 开篇；保留图中 `PROPOSED DESIGN` 标识，图注逐阶段对应 §4.1–§4.5 的数学符号 | 代码与数学规范完全对齐后移除 `PROPOSED` 水印并核对模块输入输出维度 | 
| `fig_3_sparse_tracks.pdf` | 人工构造的二维时间平面锚点、同轨间隙切分与有限 Tube 几何示意图 | 置于 Method（§4.3–§4.4）；**图注必须明确声明为人工合成的算法原理图（Illustrative schematic on synthetic coordinates），严禁在正文中当作真实视频对的定性实验结果引用** | 替换为真实 VCSL 样本对（记录 `pair_id`、预测框、GT 框与实际锚点/Tube 输出）后方可移入或新增 Qualitative Results | 
| `fig_4_tradeoff.pdf` | 仅含坐标轴框架与 `RESULTS PENDING` 水印的空白实验版式图 | 置于 Experiments；**不含任何伪造数据点或虚构平滑曲线**，用于锁定实验章节排版与讨论结构 | 读取冻结协议下多操作点（operating points）的真实 `metrics.json` 与 `per_pair_timing.jsonl` 自动绘制 | 

**图表制作与视觉质量铁律：**

* **严禁使用文生图模型（Diffusion/Image-Gen）生成含数学符号、文字标签、精度曲线或伪造视频帧的科研图表**；架构与几何图统一使用 SVG/TikZ 矢量绘制，数据图表统一由 Python（Matplotlib）从真实结构化日志自动生成。

* 论文编译优先引用矢量 `.pdf`；字号在最终双栏/跨栏排版尺寸下必须清晰可读（轴标签建议不小于 8 pt），曲线与散点必须同时利用颜色 + 线型/点形（marker shape）双重编码，确保黑白打印或色觉障碍读者可无歧义区分。

* 若后续制作定性对比图但本地仅有 `.npy` 特征而无原始视频帧图像，应直接绘制**真实特征自相似/互相似局部热力图 + 锚点轨迹 + 预测/GT 区间对比图**，绝对禁止用生成或无关图像冒充原视频画面。

## 7. 证据工程与实验交接规范（`evidence/`）

在论文工作区根目录下创建并维护 `evidence/` 目录（仅存放轻量化 Markdown 台账与 JSON 摘要模式说明，不拷贝大体积特征文件，且注意**不要把含本机个人用户名的绝对路径写进匿名论文 PDF 正文**）：

| 证据文件名 | 必须包含的核心内容 | 
| ----- | ----- | 
| `evidence/method_spec.md` | 拟议算法（v2.1）的完整数学定义、符号表、所有超参数的物理含义与默认值、未决设计分支及其取舍判据 | 
| `evidence/implementation_status.md` | 逐模块对照表：\`数学章节 | 
| `evidence/claims_ledger.md` | 全文核心论断台账：\`Claim ID | 
| `evidence/related_work_matrix.md` | 文献核查矩阵：\`论文与年份 | 
| `evidence/experiment_manifest.md` | 数据集清单版本、行数、文件 SHA256、正负例构成、评估器脚本路径、软硬件环境指纹、阈值调优与冻结规约 | 
| `evidence/experiment_plan.md` | H1–H3 与 E0–E5 的一一映射、执行优先级、预期观测与**证伪退路预案**（区分内部研究预期与真实实验结果） | 
| `evidence/missing_evidence.md` | 按阻断投稿的严重程度排序的证据缺口清单，置顶列出**最紧急的 5 项阻断性实验/核查任务**及所需具体产物 | 

**面向后续实验 Agent 的标准日志接口（Schema）：**
为实现“实验跑完即可由脚本一键更新图表”，实验产物应提供（或通过适配脚本映射为）以下结构化字段；无数据时填 `null`，严禁伪造样例数据充当实验输出：

```
run_metadata.json:
  run_id: string
  method: string                  # e.g., "FastVCL_proposed", "SimpleBaseline", "TransVCL", "TN", "HV", "DP", "DTW"
  code_commit: string
  dirty_diff_sha256: string | null
  config_sha256: string
  dataset_version: string
  split: "dev" | "val" | "test"
  pairs_csv_sha256: string
  gt_json_sha256: string
  feature_manifest_sha256: string
  evaluator_entrypoint: string
  coordinate_convention: "half_open_feature_index_[start,end)"
  frozen_protocol_id: string
  random_seed: int
  hardware: {cpu_model: string, num_threads: int, gpu_model: string | null}
  backend: "cpu_python" | "cpu_numba_cpp" | "cuda"
  precision: "fp32" | "fp16"
  timing_scope: "T_localize_in_memory_features_to_segments"
  profiling_enabled: false        # 正式测速时必须为 false

predictions.json:
  "<query_id>-<ref_id>": [[a_s, b_s, a_e, b_e, score], ...]

status.jsonl:
  {"pair_id": "...", "status": "OK" | "EMPTY" | "ERROR" | "SKIPPED", "reason": null | "...", "M": 1200, "N": 950}

metrics.json:
  split: string
  n_expected: int                 # 清单总行数
  n_processed: int                # 成功执行完（OK + EMPTY）的对数
  n_error_or_skipped: int         # ERROR + SKIPPED 对数
  n_precision_denom: int          # 非空预测有效分母对数
  n_recall_denom: int             # 正例 GT 有效分母对数
  n_negative_pairs: int           # 真实负例对数（val 上为 0）
  precision: float
  recall: float
  f1: float
  negative_pair_far: float | null # val 上必须为 null
  confidence_threshold: float
  threshold_selected_on: "val"
  protocol_id: string

per_pair_timing.jsonl:
  {"pair_id": "...", "repeat": 0, "is_warmup": false, "t_localize_ms": 4.21, "t_io_ms": 0.85, "t_export_ms": 0.12,
   "stage_ms": {"normalize": 0.15, "coarse_match": 1.80, "ransac": 0.45, "tube_sim": 0.90, "tube_dp": 0.76, "post": 0.15},
   "actual_dot_products": 142000, "tube_cells_evaluated": 8500, "num_tubes": 3,
   "cpu_rss_bytes": 512000000, "gpu_peak_allocated_bytes": null, "status": "OK"}

```

## 8. 英文论文初稿结构、写作规范与构建要求

### 8.1 复用现有 LaTeX 工程与目录结构

直接在 `/Users/gzhlaker/Documents/code/gzhlaker_cvpr2027` 现有工程上修改，清理模板自带的排版说明正文与虚拟文献，保留用户已有配置，**不要另起炉灶新建第二套 `paper/main.tex` 目录**。

```
main.tex                          # 主论文编译入口（保持匿名审稿模式）
preamble.tex                      # 宏包、数学符号宏与醒目 \TODO{...} 定义
main.bib                          # 经核实的真实 BibTeX 文献库（清除模板示例条目）
sec/0_abstract.tex                # 摘要（诚实反映研究设计与待补实验状态）
sec/1_intro.tex                   # 引言（含 fig_1_teaser.pdf）
sec/2_related_work.tex            # 相关工作（覆盖 VCSL、传统几何/对齐、学习式与 2024–2026 新近工作）
sec/3_method.tex                  # 方法（含 fig_2_framework.pdf 与 fig_3_sparse_tracks.pdf、算法伪代码及复杂度分析）
sec/4_experiments.tex             # 实验协议、H1–H3 验证矩阵、Tables 1–3 与 fig_4_tradeoff.pdf
sec/5_conclusion.tex              # 结论、局限性与待完成验证说明
supplementary.tex                 # 补充材料独立入口（详细实现差异审计、超参数表、额外诊断规范）
figures/                          # 四张已有矢量图（.pdf/.svg/.png）及说明
tables/                           # 拆分为独立可自动更新的 .tex 表格文件（可选或内嵌于 sec/4_experiments.tex）
scripts/                          # 占位图生成脚本与后续日志转图表脚本
evidence/                         # 第 7 节规定的 7 个证据管理文件
README_BUILD.md                   # 编译命令、工具链版本、已知警告与更新流程说明

```

### 8.2 各章节内容重点与表达禁区

| 章节（建议占页预算，总计约 8 页主文） | 初稿必须完成的实质内容 | 严禁出现的违规表述 | 
| ----- | ----- | ----- | 
| **Abstract**（150–200 词） | 界定给定视频对复制定位任务与全矩阵对齐的计算矛盾；简述固定 ISC 特征下的 Sparse-to-Tube 拟议流水线；点明围绕候选覆盖、边界恢复与实测开销的三个核心研究问题；以醒目占位符标明正式结果待冻结评测补齐 | 严禁写 “Extensive experiments demonstrate that FastVCL achieves state-of-the-art accuracy and $X\times$ speedup” 等未验证结论 | 
| **1. Introduction**（约 1.5 页，含 Fig. 1） | 任务背景；现有传统方法（HV/TN/DP/DTW）与学习式方法（SPD/TransVCL/RTR/FiGVCL）在粗搜索与细对齐上的计算权衡；提出 H1–H3 三个可证伪假设；以条件式/研究设计口径列出不超过 3 条贡献 | 严禁声称所有现有方法都需要训练，或声称 TransVCL 无法分块处理长视频 | 
| **2. Related Work**（约 0.8 页） | 分三小节：（1）视频复制检测与定位基准（VCDB/VCSL/FiGVCL）；（2）经典零训练时序对齐与几何投票（HV/TN/DP/DTW/Smith-Waterman）；（3）学习式相似度图检测与高效定位（SPD/TransVCL/RTR/TCSVT 2024），精准指出与本文最接近机制的异同 | 严禁写成互不关联的摘要罗列；严禁把 SPD 列为零训练传统方法 | 
| **3. Method**（约 2.3 页，含 Fig. 2 & Fig. 3） | 严格按 §4.1–§4.6 展开：问题形式化与有效掩码、稀疏网格与跨计划去重 Mutual Top-$K$、多轨迹拟合与双轴支持/间隙切分、有限 Tube 构建与带零下界局部 DP、双轴 $\min(\operatorname{IoU}_A, \operatorname{IoU}_B)$ 去重、完整伪代码与真实复杂度分析 | 严禁漏写 $\bar{f}_i^A, \bar{f}_j^B$ 区分；严禁照搬 `tube.py` 的无截断负分续接注释漏洞；严禁把固定步长粗匹配称为次二次复杂度 | 
| **4. Experiments**（约 2.8 页，含 Tables 1–3 & Fig. 4） | 完整写出数据集版本协议、评价指标公式与四个分母、公平计时边界 `T_localize`、验证集调参冻结规则；完整布设 E0–E5 实验小节、三张结构化空表与 Fig. 4，并详细阐述每张表用于验证或证伪哪条假设 | 严禁将历史不完整运行（如 `8,075/41,798`）或 `dev1000`（`n_pairs=200`）填入正式主表；严禁在 `val` 上报告负例 FAR | 
| **5. Conclusion & Limitations**（约 0.6 页） | 总结本文提出的 Sparse-to-Tube 理论框架与可证伪评估体系；坦诚剖析短片段采样下界、固定正斜率范围、重复纹理伪锚点及候选爆炸等固有局限；标明最终实证结论待冻结实验完成后定稿 | 严禁把研究计划复述为已被证实的客观规律 | 

**推荐的初稿 Abstract 英文模板（可根据最终符号微调，但必须保留诚实边界）：**

> Video copy localization aims to identify corresponding temporal intervals within a given pair of untrimmed videos. While dense frame-to-frame matching and learned interaction networks provide strong localization accuracy, evaluating fine-grained alignments across the entire temporal product space incurs substantial computation and memory overhead. In this work, we investigate whether sparse correspondence proposals can reliably restrict high-resolution temporal alignment to a small set of locally consistent regions without additional model training. Starting from fixed pretrained ISC frame descriptors, the proposed **FastVCL** pipeline extracts mutual Top-$K$ anchors on sparse sampling grids, estimates piecewise-linear temporal tracks with dual-axis support and gap-splitting constraints, and refines segment boundaries via zero-floored local dynamic programming strictly within finite tubes. Rather than treating sparse-to-fine cascading as guaranteed acceleration, we formulate three falsifiable hypotheses examining candidate coverage on short segments, boundary recovery within finite tubes, and end-to-end latency trade-offs against both classical alignment baselines (HV, TN, DP, DTW) and learned localizers (TransVCL). `\TODO{EMPIRICAL RESULTS PENDING: Insert protocol-frozen VCSL validation/test F1, negative-pair FAR, and measured latency statistics after full benchmark verification.}`

### 8.3 编译验证与匿名安全检查

* 在 `preamble.tex` 中定义醒目的可见占位宏（例如 `\newcommand{\TODO}[1]{\textcolor{red}{\textbf{[TODO: #1]}}}`），**严禁通过将 `\TODO` 定义为空白来伪造“无待办项”的完成假象**。

* 使用本机可用 TeX 引擎（如已检测到的 `tectonic`，或 `pdflatex`/`bibtex`）执行真实编译，记录完整命令行、退出码与输出 PDF 页数/文件大小于 `README_BUILD.md`。若编译因缺失特定 TeX 宏包失败，必须如实报告具体报错信息并保留全部可编译源码，严禁谎称编译成功。

* 核查生成的 PDF：（1）无 `?` 未定义引用或空文献 `[]`；（2）四张 PDF 图均正常渲染且无越界溢出；（3）PDF 元数据、正文与补充材料中不包含作者姓名、GitHub 个人账号或 `/Users/gzhlaker/...` 本机路径，严格满足双盲审稿要求。

## 9. 执行顺序、动态定位与验收清单

### 9.1 五步标准工作流

1. **只读核查与台账建档：** 核对代码与历史产物，先写出 `evidence/implementation_status.md` 与 `evidence/method_spec.md`，锁定数学符号与原型差异。

2. **文献精读与矩阵建立：** 核实 §3 所列经典与 2024–2026 文献，完成 `evidence/related_work_matrix.md` 并更新 `main.bib`。

3. **正文撰写与占位图集成：** 编写 `sec/0_abstract.tex` 至 `sec/5_conclusion.tex`、`supplementary.tex` 及三张标准空表，将 `fig_1`–`fig_4` 编入正文并完成编译与版式自检。

4. **实验规约与缺口交接：** 完成 `evidence/claims_ledger.md`、`experiment_manifest.md`、`experiment_plan.md` 与 `missing_evidence.md`，明确最紧急的 5 项实验任务与 JSON 日志接口。

5. **实测闭环后置更新（待实验完成后执行）：** 校验真实实验覆盖率与协议一致性 $\rightarrow$ 自动渲染正式图表 $\rightarrow$ 按实测结果重写摘要、贡献与结论。

**基于未来真实实验结果的三种诚实定稿策略：**

* **情形 A（与强基线精度相当或更优，且端到端 `T_localize` 显著降低，单变量消融支持核心机制）：** 正常主張固定特征下的质量—效率帕累托改进与核心机制贡献。

* **情形 B（端到端明显更快，但相比 TransVCL 或全矩阵 DP 存在一定精度折损）：** 将论文诚实定位为“面向资源受限场景的零训练精度—延迟权衡分析与故障诊断”，明确量化精度损失来源（如短片段漏检率）。

* **情形 C（简单组合强基线或传统 TN/DP 已能达到同等精度与速度，或拟议机制无净收益）：** 立即收窄主张，聚焦于系统性消融诊断与负结果分析，绝不强行包装虚假创新点。

### 9.2 初稿交付逐项验收清单

* \[ \] **状态诚实性：** 明确体现“代码仅初步跑通”，严格区分 `PROPOSED` 拟议规范、`IMPLEMENTED_UNVALIDATED` 原型现状与 `PILOT_ONLY` 开发诊断，无任何虚构实验数值。

* \[ \] **章节完整性：** Abstract、Introduction、Related Work、Method、Experiments、Conclusion & Limitations 及 Supplementary 全部为实质性学术英文正文，非大纲罗列。

* \[ \] **数学严密性：** 显式区分 $\bar{f}_i^A$ 与 $\bar{f}_j^B$；正确定义离散网格集合 $I_A^g, I_B^g$；明确跨网格 $(i,j)$ 去重规则；完整给出带 $H_{uv}>0$ 与零下界截断的局部对齐公式，并如实记录 `tube.py::local_dp` 的无截断冲突。

* \[ \] **复杂度诚实性：** 明确固定步长粗匹配仍为 $\Theta(MN)$，区分直接偏移寻址的 $O(LW)$ 与原型扫描前驱行全列的 $O(PLW^2)$。

* \[ \] **文献与分类准确性：** 涵盖 VCSL、TransVCL、RTR (ECCV 2024)、TCSVT 2024、FiGVCL (TPAMI 2025) 及 ISC/HV/TN/Smith-Waterman 原始文献；**准确将 SPD 归为学习式检测方法而非零训练传统基线**；修正 ECCV 2024 官方链接并遵守 CVPR 2027 同期工作时间线（2026-09-15）。

* \[ \] **实验与指标严谨性：** 包含 E0–E5 实验设计、Simple Baseline 守门对照、四个分母记录要求（`n_expected / n_processed / n_precision_denom / n_recall_denom`）、`val` 全正例不报负例 FAR 的说明及 `T_localize` 计时边界。

* \[ \] **图表与构建可复核：** 四张既有 `.pdf` 占位图已实际编入正文并带准确图注；三张核心空表结构完整；`evidence/` 下 7 个文件与 `README_BUILD.md` 齐全，记录了真实编译状态。

## 10. CVPR 2027 官方关键时间节点与合规要求

根据 2026-10-17 核实的 [CVPR 2027 Call for Papers](https://www.google.com/search?q=https%3A%2F%2Fcvpr.thecvf.com%2FConferences%2F2027%2FCallForPapers) 与 [Dates and Deadlines](https://www.google.com/search?q=https%3A%2F%2Fcvpr.thecvf.com%2FConferences%2F2027%2FDates) 官方页面：

* **Paper Enrollment / Registration Deadline（论文注册截止）：** **2026-11-10 23:59 AoE**（官方注明 `Date is fixed, no extension will be given`；所有共同作者必须提前激活 OpenReview 个人主页，无机构邮箱的新账号审核最长需 2 周，务必提前完成）。

* **Paper Submission Deadline（正式论文提交截止）：** **2026-11-16 23:59 AoE**（固定截止，无延期）。

* **Supplementary Materials Deadline（补充材料截止）：** **2026-11-23 23:59 AoE**。

* **Reviews Released & Rebuttal Period：** **2027-01-25 至 2027-02-01 AoE**；**Final Decisions：** **2027-02-25 AoE**；**Main Conference（西雅图）：** **2027-06-20 至 2027-06-25**。

* **同期工作分界线（Contemporaneous Work Cutoff）：** **2026-09-15** 之后首次公开的工作视为同期工作，此前公开的均属在先工作。

* **模板与政策合规说明：** 当前本地工作区使用的是 CVPR 2026 LaTeX 模板宏包；初稿阶段可先复用该匿名双栏模板推进内容，但必须在 `README_BUILD.md` 中标明模板年份状态，待 CVPR 2027 官方 Author Kit 确认后第一时间核对宏包年份、页数上限、双盲匿名规则与 LLM 使用声明政策。