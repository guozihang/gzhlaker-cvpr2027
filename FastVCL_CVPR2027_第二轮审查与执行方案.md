# FastVCL：第二轮论文审查与执行方案

> **2026-10-19 更新：** 当前执行入口为[第四轮方案](FastVCL_CVPR2027_第四轮审查与执行方案.md)。用户最新要求 JEV 用于锚点过滤与片段融合，覆盖本文件“仅候选后置核验”的范围限定；其余有效的 core/评估约束继续保留。本文件作为历史方案。

版本：R2 / 2026-10-18。面向接手现有工程的模型，不是从零生成论文的提示词。

## 1. 任务和当前结论

本轮已经直接修改 `sec/0_abstract.tex` 至 `sec/5_conclusion.tex`、`supplementary.tex` 及证据文件。接手时先读修改后的文件，不要从旧方案重新生成。用户确认代码仅初步跑通；目前没有可进入主表的冻结基准结果。

下一轮目标：让**方法定义、实际实现、可执行实验和论文主张逐项对应**，然后完成剩余篇幅和图表优化。不要将继续润色等同于研究问题已经解决。当前最有价值的科学问题仍是：稀疏候选能否保留足够覆盖，局部对齐能否改善边界，以及这些收益能否抵消系统开销。

用户明确要求保留 JEV 并命名为 **`seltive model`**，拼写按用户要求保留。它已在 Fig. 2、摘要、Method 和补充材料中作为拟议视觉核验分支出现。旧方案“不允许 JEV”的规则已被后续用户指令覆盖，不得再以该旧规则删除模块。

文件优先级：用户最新指令 → 本轮方案与最新代码/一手来源 → 本轮修订后的论文和证据文件 → 历史方案。文件之间不一致时查证，不把任意一个 Markdown 当作事实来源。

## 2. 工作区和默认操作范围

| 材料 | 路径 | 本轮写作模式权限 |
|---|---|---|
| 论文 | `/Users/gzhlaker/Documents/code/gzhlaker_cvpr2027` | 编辑、生成图表、编译、轻量检查 |
| 原型 | `/Users/gzhlaker/Documents/code/FastVCL` | 读取代码和既有产物 |
| 对照 | `/Users/gzhlaker/Documents/code/gzhlaker_transvcl` | 读取入口、分块和评价实现 |
| 数据线索 | `/Users/gzhlaker/Downloads/VCSL` | 读取清单与元数据；不可改 GT |

默认继续论文审查，不改外部研究代码、不启动全量实验、不调用付费视觉 API、不提交会议。若用户明确交付“实现并执行研发任务”，再进入第 6 节的工程任务；既有授权无需重复确认。缺少环境或数据时完成不依赖它们的文稿、配置规范和验收设计，具体记录缺失项。

不得覆盖他人未提交修改，不自动 commit/push。不要修改系统 HOME；构建使用项目缓存变量。

## 3. 必须先读的材料

按依赖顺序：

1. `evidence/round2_review.md`：本轮发现、已修正内容、验证边界。
2. `main.tex`、`sec/*.tex`、`supplementary.tex`：当前论文本身。
3. `evidence/method_spec.md` 与 `evidence/implementation_status.md`：规范与原型差异。
4. `evidence/experiment_plan.md`、`experiment_manifest.md`、`missing_evidence.md`：实验、冻结和缺失项。
5. `evidence/claims_ledger.md`、`related_work_matrix.md`：论断依据、文献阅读深度。
6. `figures/README.md`、`scripts/generate_framework.py`、`scripts/generate_paper_placeholders.py`、`README_BUILD.md`：图源和构建。

开始前记录论文和原型 HEAD、dirty 状态。R2 审查时原型 HEAD 为 `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，tracked 工作树干净；后续必须重新检查，不能把这个状态当成永久事实。原型数字与硬件记录仍属于历史审计，不是这轮新实验。

## 4. 本轮已经纠正的内容：禁止重新引入

| 问题 | 正确口径 | 后续检查 |
|---|---|---|
| 完美预测被评价器剔除 | 非空重叠计算的两个轴分母都有 `+1e-6`，普通完美预测略小于 1，仍参加平均；精确等于 1 的哨兵另行过滤 | 实际执行 reference/port，覆盖 dtype、空输入、conf=0 |
| 伪代码候选集合始终为空 | 提取后执行候选集合合并；无正分时先停止，再谈回溯 | 与实现逐步对齐 |
| 有效掩码漏掉 finite | 显式检查全部分量 finite，再用稳定精度求范数 | NaN、Inf、零向量、极大有限值 |
| 短复制“必然不可检出” | `(h−1)s+1` 是单一网格内部独立锚点跨度下界，不能排除外部锚点/扩展 Tube 带来的候选 | 不外推到多相位或最终召回定理 |
| 切分只会增加候选 | 切分后重验可拒绝所有子段，接受数可以减少 | 5 个锚点拆为 2+3、支持阈值 5 |
| “标准 Smith–Waterman” | 这里是限制步集的 Smith–Waterman-style 局部 DP，非经典插入/删除递推 | 比较项明确步集、起止规则和代价 |
| 输出边界、平滑和间隙含糊 | 负 cosine 先截断再平滑；间隙数为两强节点索引差减 1；拟议输出 margin=0 | 原型 margin=2 与拟议定义尚未统一 |
| 独立支持与原型混用 | 拟议支持计数去重，原型存储 A 锚点条目不保证 Top-K>1 时独立 | 单独验证 A/B 成员关系和边界容差 |
| min-IoU 的错误优势论证 | 不同参考区间的例子只能反驳 A-only 去重，area-IoU 也保留它们 | 找真正区分规则的案例并消融 |
| STB 基线自相矛盾 | 共享评分、min-IoU、阈值规则，单独消融去重；基线用单路径、无额外双轴检查/切分 | 不偷偷弱化对手 |
| E1 强行固定真实候选数 | 固定配置预算与上限，报告实际候选数；只有 E3 冻结相同候选/Tube | 不能后验丢弃候选凑数 |
| stride 2 等于 {2,4,8} 预算 | 64×64 输入下单向分别为 1,024 与 1,344；按实际执行数匹配 | 双向和 tie rescan 也计入 |
| Tube envelope 等于真实路径覆盖 | 它只是候选框诊断，不能证明带内合法路径或逐帧真值覆盖 | GT 只有区间，不能编造稠密 GT |
| 边界 MAE 越低就越好 | 同时报匹配数、召回和共同 GT cohort；防止幸存者偏差 | 匹配采用先最大基数、再最大总 min-IoU |
| 阈值扫描证明加速 | 后处理阈值通常不改变已执行计算；扫描 stride/width/path budget 等真实开销因素 | 所有测试操作点预先声明 |
| 41,800 与实际清单冲突 | 验证集为 41,798；FAR 在该全正例划分不可测 | 不能四舍五入分母 |
| 已冻结、已加载、已预注册 | 当前只是审计快照和拟议协议；没有对应产物就不能写完成时 | 每一状态需要文件/日志证明 |

`python3 scripts/check_paper_semantics.py` 的 7 项检查是标准库标量数学检查，**不执行 NumPy 原型**。其结果不能拿来关闭算法实现验收或填论文指标。

## 5. seltive model 的研究定位

保留现有图中候选后置核验的位置：核心候选区间与匹配索引 → 选择证据 → A/B 原始帧视觉核验 → 结果融合。历史锚点级 router 不等于这个候选级扩展已实现。

已明确的接口约束：

- 输入需要原视频帧和验证过的 feature-index→frame/timestamp 映射。
- 输出枚举为 COPY / NOT_COPY / UNCERTAIN。
- 未被选择、弃权、失败的候选保留核心结果。
- 选择策略、具体后端、确定性 verdict 如何融合仍是 OPEN，不能自行写成已验证的硬删除/降权公式。
- 它不能恢复从未进入候选池的复制。核验收益和候选召回必须分开研究。

先形成 `evidence/selective_model_spec.md`，逐项写：模型/版本与能力来源、帧映射、每候选采样、预算单位、选择信号、去重、提示词与解析、超时重试、融合、参数选择数据、缓存策略。未定项显式 OPEN。不以模块名字推断模型能力或训练来源。

E6 使用固定候选池比较 core-only、随机选择、便宜规则选择、拟议策略；固定后端、融合与调用/帧/token 预算。报告全集 F1/Recall/FAR、真实候选误删、假候选纠正、未选/弃权/失败，以及新增端到端时间与费用。只在“被选中子集”报告正确率不足以证明系统价值。

核心表是固定 ISC 输入比较；E6 多了原帧与模型资源，另行报告。计入帧获取/解码、预处理、排队/网络、推理、失败/重试、融合，区分缓存与在线读取。不能只报告几毫秒路由时间来代表整个核验模块。

## 6. 下一轮工作包：依赖、产物与验收

### W1 — 规范与实现逐项对照（最高优先级）

读取 `fastvcl/{sparse,trajectory,tube,segments,pipeline,evaluate}.py` 和实际配置，产出 `evidence/spec_code_contract.md`。每行包括：论文定义、代码函数/行、差异、计划选择、实现状态、所需反例。

必须涵盖：零下界/负续接、正分与零分指针、步集与原始索引、round 半整数规则、失效/blocked 单元、跨路径屏蔽、低质量间隙 off-by-one、边界 margin、distinct 支持、分数、去重、最终 cap 与阈值。

验收：不存在“论文写已实现但代码仍不同”的条目；每个未决分支有明确后续比较。不要因原型现有注释而认定递推正确，也不要因数学反例而宣称零下界必然提高真实 F1。

### W2 — 可执行语义检查与简单强基线

若已获实现任务授权，在原型隔离分支实现配置化两种 DP 与 direct-offset 变体；保留旧行为用于复现，不能静默替换历史结果。完整 STB 定义以 `evidence/experiment_plan.md` 为准。

验收至少包含：长弱前缀、强段内短弱点、同轨两复制长间隙、斜率导致带中心移动、全无效、部分无效、屏蔽重复路径、tie、重复 A 锚点、margin=0/2 和一步间隙边界。对照显式小网格 oracle，核对 score、path、endpoints，而非只检查非空。

评价器验收：完美/部分/无交集、空预测、空 GT、全空分母、conf=0/正阈值、坐标整数化；与 reference 逐例对照。出现 error/skipped 不改成空预测。

产物：变更清单、可复现命令、检查输出、baseline 独立入口和配置。若只有写作权限，则完成 W1 与上述验收契约，明确 W2 未执行。

### W3 — 冻结诊断与数据协议

产出 `evidence/diagnostic_protocol.md` 与拟议 `frozen_protocol` schema，未完成字段为 null/OPEN，不制造“冻结成功”文件。

固定 candidate envelope、空 Tube、合法 GT、min-IoU=0.5 的诊断匹配、最大基数匹配及 ties、长度桶（取 A/B 最短时长）、MAE 与共同 cohort、cell/dot 计数。官方指标仍用原 GT，诊断过滤必须单独报分母。

冻结开发集/验证集/测试集用途、视频身份/来源重叠审计、阈值 grid/objective/tie、seed 集、预算容差、硬件/精度、特征内容与所有输入 hash。验证集全正例不能调负例 FAR；缺负例开发数据就把 FAR 保留为最终测试诊断。不要从测试负例挑校准样本。

### W4 — 有意义的受控实验，而非先跑全量

顺序：开发数据 E1/E3 → 修正实现/规范 → E2/E4/E5 的受控诊断 → 冻结配置集 → 完整 validation → 一次预声明的 test campaign。多个预声明方法/seed 不等于违规重复选测试；禁止的是根据 test 结果再选设置。

- E1 固定预算/上限，报告真实候选数，full-system 与 single-factor 分开。
- E2 按实际双向/tie dot 数匹配；无法匹配时如实画真实预算点，不补无用计算凑预算。
- E3 相同候选和 Tube hash，独立报告漏检/新增匹配/共同 cohort；oracle Tube 只作诊断，非理论性能上界。
- E4 每行一个因素，宽度与延伸分开，默认不含多尺度/独立相位。
- E5a 同语义 scan/direct parity 后计时；E5b full-matrix 改搜索域，不能混成纯索引消融。
- 五 seed 只能反映拟合方差，不自动等于统计显著。配对置信区间必须说明共享视频依赖；做不到就限制结论。

每个正式 run 必须有 metadata、config、predictions、status、metrics、per-pair timing 和输入/hash 信息。完整率、四分母、所有失败与缺测必须可核对。`dev1000` 不能以名称充当 1,000 个 scored pairs。

### W5 — 论文论证和篇幅

保持三条主线：H1 候选覆盖、H2 边界恢复、H3 实测收益。E6 是额外视觉信息下的独立扩展。不要把协议说明、经典组件组合或换名字当成已证实创新。

继续核对最近工作原文，只写阅读深度支持的机制事实；未找到同名论文不能证明 first/novel。补强与最接近系统的输入、候选生成、细对齐域、训练、成本边界对照。性能增益与学术新颖性是两个门槛。

篇幅目标暂按现有模板正文 8 页，不靠缩字号、负间距或不可读缩图达标。建议依次迁移：网格性质详解 → 补充；状态/审计重复句 → 内部文件；完整实验矩阵与大消融空表 → 补充；Fig. 3 可移补充并在正文引用。保留 Fig. 2 完整核心与 seltive model，不把完整方法变成框名列表。是否迁移图表须保持全文引用和生成脚本一致。

最终摘要用实测结果替换占位须有证据；没有证据时保持当前研究草稿状态。不得为“更像论文”删掉全部未验证标记。

### W6 — 构建、图表和交接

运行主文与补充材料构建；检查总页数、正文结束页、表格位置、图中文字、公式、所有引用和匿名信息。用 PDF 渲染查看关键页面，不以编译 exit=0 代替版面检查。

更新 `README_BUILD.md` 的实际日志、页数和限制。新一轮 `round3_review.md` 必须按“已修改、已验证、尚未验证、下一步”写；交付可直接运行的命令与文件链接，不只写计划。

## 7. 可直接执行的论文检查命令

从论文根目录运行：

```bash
python3 scripts/check_paper_semantics.py --output evidence/round2_math_checks.json
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex
rg -n 'Overfull|Underfull|undefined references|undefined citations|Output written' main.log supplementary.log
git diff --check
```

按需运行 `python3 scripts/generate_framework.py` 更新 Fig. 2；总图生成器调用该脚本，保留 seltive model。图像不得包含编造的数据点、精度曲线、真实样本或 GT 标注。必要时从真实 run 生成结果图，保留脚本和原始数据链。

本轮默认 Python 无 NumPy；上述标量检查只用标准库。需要执行原型时先定位其锁定环境，不要将依赖缺失误写成算法检查已通过。

## 8. 官方来源与时间状态

2026-10-18 复核 [CVPR 2027 Call for Papers](https://cvpr.thecvf.com/Conferences/2027/CallForPapers)：注册 2026-11-10、投稿 2026-11-16、补充材料 2026-11-23（AoE）。同期工作分界为 2026-09-15，但受其影响的工作仍需引用讨论，不能理解为此后论文可以不看。

[官方 author-kit 仓库](https://github.com/cvpr-org/author-kit) 当前说明仍标注 CVPR 2026 更新。2027 AuthorGuidelines 地址本轮返回 404；CFP 的 LLM 政策仍称细节待更新。现有 2026 模板可继续用于草稿，但不能宣称 2027 最终模板、页数及作者 LLM 声明规则已完全确认。下一轮提交前再查官方页面；不要链接 Google 搜索结果冒充来源。

## 9. 接手模型最终汇报

交付：修改后的 LaTeX/PDF、审查报告、规范/实现差异契约、诊断协议、seltive model 规格、更新后的证据文件和构建记录。若已执行工程阶段，另附源代码 diff、测试日志、baseline 配置和 run artifacts。

最终消息简洁列出：这轮真正修正了什么；执行了哪些检查且结果如何；什么仍是提议或缺证据；主文/补充/报告的链接。没有跑过实验，就不要使用“验证有效”“显著提升”“完成复现”这样的措辞。
