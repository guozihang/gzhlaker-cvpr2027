# FastVCL 第二轮全文审查记录

日期：2026-10-18。结论：完成一次全文实质修订，仍是缺少正式实证的研究草稿。
接手入口：[第二轮执行方案](../FastVCL_CVPR2027_第二轮审查与执行方案.md)、[启动 Prompt](../FastVCL_CVPR2027_第二轮Agent启动Prompt.md)。

## 1. 审查范围与证据边界

读取全部主文和补充材料、7 份证据文件、旧执行文档及图表脚本；重点复核外部原型的 `evaluate.py`、`tube.py`、`segments.py` 和 JEV 历史决策，以及 TransVCL 的 `metric/eval.py`。原型 HEAD 仍为 `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，本轮未修改原型、对照或 GT。

数据规模与历史运行状态沿用 2026-10-17 审计记录，本轮没有重跑全数据统计、模型或基准。默认 `python3` 缺少 NumPy；本轮只执行标准库标量数学检查。区分“源码核对”“公式检查”“实际模型评测”，没有将任何主张提升到 BENCHMARK_VERIFIED。

## 2. 关键发现、修订和未决事项

| 级别 | 发现 | 本轮处理 | 实现/实验是否已解决 |
|---|---|---|---|
| P0 | 完美非空预测被说成会自动排除，忽略了分母 epsilon | 公式补 `1e-6`；纠正正文/补充；保留精确哨兵逻辑 | 论文已修，实际 evaluator parity 待做 |
| P0 | 伪代码未把 segments 加入 C，无正分仍先回溯 | 增加 C 合并和回溯前停止 | 仅伪代码修正 |
| P0 | finite 条件在公式中缺失 | 显式写入并说明稳定精度 | 未重新运行归一化测试 |
| P0 | “短段绝不检出”和“切分不减少候选”两个过强结论 | 限定单网格内部支持；说明子段拒绝 | 数学逻辑与标量反例已核查 |
| P0 | 原型负续接与拟议零下界混淆 | 保留冲突并限定为受控 E3 | 代码仍未修，不预判优劣 |
| P0 | 原型 margin、支持条目计数与文字独立支持不一致 | 明确拟议 zero margin、distinct support，与原型分开 | 新差异进入下一轮契约 |
| P1 | 段间隙 off-by-one、平滑顺序不明 | 明确 intervening-index gap，负 cosine 先截断 | 代码位置核查；实际输出对照待做 |
| P1 | STB 基线既说共享去重又排除 min-IoU | 共享输出规则，去重另做 E4 | 独立可运行 baseline 待实现 |
| P1 | 提案消融强制相同真实候选数量，混淆 E1/E3 | E1 固定配置上限与预算，E3 固定相同 Tube | 实验未运行 |
| P1 | 嵌套尺度天然等预算的错误前提 | 给出 1,024/1,344 单向计数反例 | 真实 executed dots 待记录 |
| P1 | Candidate recall 当成逐帧路径覆盖，MAE 有幸存者偏差 | envelope 诊断；冻结匹配、报告 recall/count/common cohort | 诊断实现仍缺 |
| P1 | 用输出阈值扫描论证计算加速 | 质量—成本点改为计算预算配置 | 测量仍缺 |
| P1 | 只列 DP 内存或 chunk forward 和作为全流程 | 加 coarse/Top-K/RANSAC/输出开销及 pair assembly | 系统计时仍缺 |
| P1 | seltive model 只在图中，旧文档又禁止它 | 摘要/Method/补充明确接口、额外输入/成本、E6；覆盖旧禁令 | backend/selection/fusion 仍 OPEN |
| P1 | 已冻结、已载权重、已预注册等无产物支持的措辞 | 改为 audited snapshot / proposed protocol | 不冒称冻结完成 |
| P2 | 41,800 分母、硬编码 Eq. 5/7、E4 同扫两因素 | 41,798、语义引用、独立 sweep 行 | 文档已修 |
| P2 | 大量重复状态段落、空白文献结果块、过强 first/novel | 压缩引言/相关工作/结论；移除无数值的文献比较块 | 正文仍需进一步压页 |
| P2 | 横向图缩为单栏不可读、消融表漂进参考文献 | Fig1/3 恢复跨栏；Fig4 原生单栏重排；提前安排表格浮动 | 已进行 PDF 渲染检查，最终页数见构建记录 |

不把“修了论文”写成“修了算法”。尤其 zero margin 与 distinct support 是明确的拟议规范，不是已经验证的性能改进。min-IoU 的一对多例子同样适用于 area-IoU，已删除隐含独占优势。

## 3. 执行过的轻量检查

命令：`python3 scripts/check_paper_semantics.py --output evidence/round2_math_checks.json`。

7 组确定性检查通过：epsilon/哨兵、弱前缀、屏蔽第一段后的第二段、嵌套网格预算、切分后支持不足、间隙 off-by-one、min/area-IoU 对照。相同 10×20 区间的标量得分为 `0.9999998500000175`；两种简化对角 DP 的正/负行为与文稿反例一致。

这些检查不是对 NumPy 原型的运行，更不覆盖 traceback、所有步集、GPU 或真实基准。没有用它们填充结果表。旧补充材料中的反例现明确给出 0.0/0.95 相似度与对角坐标，避免缺少输入的不可复核数值。

主文与补充材料均使用离线 Tectonic 缓存构建。最终构建、实际页数、版面检查与已知警告见 [README_BUILD.md](../README_BUILD.md)。`git diff --check` 通过；抽取文本无 `??`、本机用户名或绝对路径。

## 4. 当前最重要的开放问题

1. **机制价值**：与强 STB 的相对增益未测，经典组件重组不等于新颖性。
2. **方法/代码契约**：零下界、tie、margin、支持与评分需要最终选择和逐例验证。
3. **评价与数据**：没有完整协议/特征内容冻结；val 全正例；共享视频依赖与诊断匹配实现未解决。
4. **实际开销**：缺少同语义 scan/direct parity 和受控端到端测量；无 GPU 实测。
5. **seltive model**：需要真实视觉后端、帧映射、选择/融合规则，单独 E6；不能借核心 feature-only 计时隐藏成本。
6. **投稿版篇幅**：当前稿仍超过暂定 8 页正文目标；应迁移冗余解释/表格，而不是缩小图中文字。当前不宣称投稿就绪。

## 5. 本轮官方与文献来源检查

- [CVPR 2027 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers)：核实截止日期及同期工作说明；LLM 细则仍待更新。
- [官方 author kit](https://github.com/cvpr-org/author-kit)：当前历史说明仍为 2026 更新；2027 AuthorGuidelines 地址返回 404，不能假装模板/政策完全确认。
- [TransVCL 原始论文页面](https://ojs.aaai.org/index.php/AAAI/article/view/25158)、[RTR 官方页面](https://eccv2024.ecva.net/virtual/2024/poster/1083)：核对学习式模型与训练范围。
- [SAM arXiv](https://arxiv.org/abs/2305.15679)：本轮核对元数据；HTML 全文未取得，不声称本轮重新完整验证 RANSAC 细节。
- VCSL CVF HTML 返回 403；已有本地文本与两个本地 evaluator 文件可读。本轮以源码确认 epsilon 逻辑。没有新一轮穷尽性文献检索，不作“未发现即不存在”的判断。

## 6. 交付与继续方式

第二轮方案将下一步拆为 W1–W6，每项说明依赖、产物和验收；启动 Prompt 可以直接给其他模型。旧的 `fastvcl_cvpr2027*.md` 顶部已标明历史版本并链接新入口，避免接手模型继续执行过时禁令或错误论断。

本轮输出是更自洽的论文草稿与可执行交接文件。真正的科研闭环仍需实现一致性、强基线、冻结协议和完整实验。
