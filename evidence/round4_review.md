# FastVCL 第四轮审查记录

日期：2026-10-19。任务范围：检查当前论文，结合近期 Jev 工作，制定锚点过滤与片段融合的新执行方案。本轮没有启动 DSH，没有改论文正文或原型实现，没有运行数据集、模型、GPU 或付费调用。

执行入口：[第四轮审查与执行方案](../FastVCL_CVPR2027_第四轮审查与执行方案.md)。

## 1. 已检查的材料

- `main.tex`、摘要、引言、相关工作、Method、Experiments、Conclusion；补充材料中的 JEV/E6 和框架图生成入口。
- 第二轮计划、第三轮审查、spec/code contract、selective-model spec、实验 manifest、claims、implementation status 和构建记录。
- 只读核查 `../FastVCL/fastvcl/{pipeline,router,visual_jev,segments,tube}.py` 的有关路径及历史 JEV 决策。
- 联网核查 TypeSafe 官方文档、Visual Jev/VideoJev 论文和作者代码、CVPR 2027 官方 CFP/author kit。

原型 HEAD 仍为 `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，检查时工作树干净；第二轮快照中的五个文件哈希未变。新增快照见 [round4_source_snapshot.json](round4_source_snapshot.json)。论文工作区开始时有用户未跟踪的 `README.md`、`rebuttal.tex`，本轮保留。

## 2. 本轮重要发现

| 编号 | 发现 | 证据位置/影响 |
|---|---|---|
| R4-01 | 现稿仍限定 JEV 为候选后置核验，且选择、后端和动作均 unspecified | `sec/3_method.tex` selective 小节；`selective_model_spec.md` §1；不能表达用户要求的两阶段 |
| R4-02 | 原型的真实接线位置是 RANSAC 前的锚点核验 | `pipeline.py::_run_stages → _verify`；与论文候选后置分支不是同一功能 |
| R4-03 | 旧动作默认 NOT_COPY 删除、COPY 权重乘 1.25 | `router.py::VerdictPolicy/apply_verdicts`；`pipeline.py::_verify` 直接构造默认 policy；需要开发验证和显式配置 |
| R4-04 | 锚点级 API 的类名并不说明接入了 Visual Jev/VideoJev | `visual_jev.py` 的通用 `describe`/JSON 路径、Null/Scripted client；需新增真实候选读出 adapter |
| R4-05 | 旧融合为区间条件并集与 max score | `segments.py::merge_overlapping_segments`；缺视觉关系、连接证据、来源和多次复制保护 |
| R4-06 | 预算按锚点阶段 begin_pair；新增融合需共用预算 | `pipeline.py::_verify` 调用 `begin_pair(pair.key)`；不能在第二阶段再次清零 |
| R4-07 | 当前训练/验证材料不能证明锚点真对应和融合真连续 | VCSL 区间标签不是逐帧 GT；需可追溯标注/变换真值，区分弱标签代理 |
| R4-08 | 老 E6 固定候选池只适用于后置局部研究 | 前置过滤改变轨迹和 Tube；新实验需分别固定 A0、C0，并完整重跑组合 |
| R4-09 | 代码/公式分歧仍存在且可重现 | 弱前缀 DP、零 extension fallback、margin 和重复锚点支持；见本轮 probes |
| R4-10 | 全文尚无 Jev 论文引用，核心标题不能替新增学习模型说明训练边界 | `main.bib`、`sec/2_related_work.tex`、`main.tex`；新增后端需单独记录训练来源和输入成本 |
| R4-11 | 旧 router 可在视觉核验前拒绝锚点；后端不可用并不恢复所有被拒锚点 | `_route` 只把 `verify` 恢复为 accepted，`rejected` 不恢复；新方案要求 selection-only 和 A0 恒等回退测试 |

特别区分：R4-03 中的硬删除是**已有代码默认行为**，不是已经证明有益的策略；R4-05 中旧融合函数存在，不代表用户要求的 JEV 融合已经实现。

## 3. 一手来源核查及设计影响

- **Visual Jev**：2026-09-22，作者论文/代码确认单图公共上下文、独立问题、候选读出及共享执行。证据板迁移到视频复制是新实验；不复制其通用性能数字为本文结论。[论文](https://arxiv.org/abs/2609.25845) · [作者代码](https://github.com/guanxuyu-sv/Visual-Jev)。
- **VideoJev**：2026-10-13，作者论文/代码确认视频 grounding/choice、Cached/Joint 及公开 4B/35B 模型。它提供更近期的时序后端候选，但双视频同源复制不是官方已验证任务。[论文](https://arxiv.org/abs/2610.18615) · [作者代码](https://github.com/MCG-NJU/VideoJev)。
- **概率与弃权**：Visual Jev 的证据充分性分支没有给出普遍改善决策的结论；VideoJev 明确报告过度自信。本计划将其作为“不假定概率校准”和“先 shadow”的依据。[Visual Jev 全文](https://arxiv.org/html/2609.25845v1) · [VideoJev 全文](https://arxiv.org/html/2610.18615v1)。
- **TypeSafe**：当前 State 页明确不支持 audio/video；本轮没有足够材料把旧“纯文本且不支持图片”表述继续写成最新绝对事实，也没有把第三方代理页面当官方能力来源。[官方 State](https://docs.typesafe.ai/concepts/state)。
- **CVPR 2027**：CFP 当前列出 11 月 10 日注册、16 日正文、23 日补充，均 AOE；AuthorGuidelines URL 仍返回 404。规则/模板仍需正式成稿时复核。[官方 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) · [官方 author kit](https://github.com/cvpr-org/author-kit)。

检索是围绕本轮 JEV 集成问题的定向核查，不是完整的新颖性检索，也没有测量“热度”排名。

## 4. 本轮实际执行的验证

| 检查 | 结果 | 范围 |
|---|---|---|
| `check_paper_semantics.py` | 7 组通过 | 公式/标量构造例，不执行数据集 |
| `check_evaluator_parity.py` | 211 cases，0 mismatch；macro/status/阈值分支通过 | 合成评分器函数一致性，不是完整真实数据文件认证 |
| `check_contract_semantics.py` | 8 个已记录行为全部复现 | 含尚未修复的反例；“复现成功”不等于“原型正确” |
| 源码快照 | 历史五文件哈希不变，新增共记录 11 个文件 | 只读审查 |
| 文档交付检查 | 新文档本地链接存在、JSON 可解析、代码围栏成对，`git diff --check` 通过 | 文档一致性，不验证拟议方法效果 |

产物：[round4_math_checks.json](round4_math_checks.json)、[round4_evaluator_parity.json](round4_evaluator_parity.json)、[round4_contract_probes.json](round4_contract_probes.json)。

代表性反例：弱前缀后接强复制段，原型 DP best=0、无路径，拟议零下界标量递推 best=1.75；同一路径 margin=0/2 产生不同端点；重复 A 锚点可满足当前支持阈值。这些支持下一步实现/对照的必要性，不证明新方法的真实召回提升。

复现命令：

```bash
python3 scripts/check_paper_semantics.py --output evidence/round4_math_checks.json
PYTHONDONTWRITEBYTECODE=1 /Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 -B scripts/check_evaluator_parity.py --output evidence/round4_evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 /Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 -B scripts/check_contract_semantics.py --output evidence/round4_contract_probes.json
git diff --check
```

本轮没有重跑 646 项原型完整套件；第三轮的测试记录属于历史验证。没有修改 TeX 或图，故没有重新编译或重新视觉审阅 PDF；9 页主 PDF（正文到第 8 页）和 7 页补充仅引用上轮构建记录。

## 5. 本轮交付与待办

已交付第四轮执行方案、此审查记录、三份重跑 JSON 和源码快照；在第二轮计划与旧 selective-model spec 顶部增加新方案链接，避免继续执行过时的 post-only 限定。

待执行：资产盘点、core 新变体、真实后端、锚点/融合动作、小试与独立 audit、完整基准、论文/图表更新。当前仍不能声称 JEV 有效、提高 F1 或加速系统。
