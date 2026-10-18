# FastVCL 第二轮：给接手模型的启动 Prompt

请把以下内容连同论文目录交给模型。主方案是同目录
[FastVCL_CVPR2027_第二轮审查与执行方案.md](FastVCL_CVPR2027_第二轮审查与执行方案.md)。

---

你接手的是已经存在、可以编译的 FastVCL 英文论文工程。请继续修订，不要重新生成一篇平行论文。先完整阅读《FastVCL_CVPR2027_第二轮审查与执行方案.md》和 `evidence/round2_review.md`，再读当前 `sec/*.tex`、`supplementary.tex` 与证据文件。

用户明确：代码只初步跑通；图表可先占位；JEV 必须保留在框架中，名称为 **seltive model**。历史文件禁止 JEV 的条款已被用户后续要求覆盖。该分支已有正文接口说明和 E6 设计，但没有确定后端、融合政策或效果证据；不要删除它，也不要虚构其实现与收益。

本次默认执行写作与研究审计模式：编辑论文工程，读取 FastVCL/TransVCL 外部仓库，执行轻量数学检查和 LaTeX 构建。除非本次用户另行授权研发执行，不改外部算法代码、不跑全量评测、不调用付费模型、不投稿或推送。权限不足不应阻止能完成的文稿与验收契约工作。

按以下顺序实际做事：

1. 检查 HEAD/dirty 状态，核对 R2 已修正内容是否仍成立。不要将旧文件中的乐观状态当成事实。
2. 完成 `evidence/spec_code_contract.md`：逐项核对 DP、步集、tie、invalid/blocked、margin、平滑、间隙、distinct 支持、评分、去重和阈值。明确哪些只是 PROPOSED，哪些有当前源码依据。
3. 完成 `evidence/diagnostic_protocol.md`：候选 envelope、GT 过滤计数、边界匹配/common cohort、真实 dot/DP visits、阈值选择、视频身份依赖、预算匹配规则。严格区分官方指标和自定义诊断。
4. 完成 `evidence/selective_model_spec.md`：原帧映射、模型版本/视觉能力依据、选择预算、采样、枚举解析、失败处理、融合和 E6。未定项写 OPEN，不伪造“最终方案”。
5. 继续优化整篇论文的论证与篇幅，保留可检验主张和状态透明性；将详细审计、冗余表格或解释移入补充/内部文件，不缩字号凑页。优先保持框架图可读。
6. 同步证据台账，运行数学检查、主文/补充构建、引用与匿名检查，渲染关键 PDF 页检查。记录实际页数与剩余限制。
7. 交付 `evidence/round3_review.md`、修改后的 PDF 和下一步任务清单。不要停在建议或提纲。

不得回退的技术结论：

- 评价器分母有 `+1e-6`，普通非空完美预测通常小于 1，不会自动成为被排除的哨兵。
- `(h−1)s+1` 是单网格内部支持跨度下界，不是最终不可检出的定理。
- 切分后重验可减少候选；min-IoU 和 area-IoU 都保留参考时间不重叠的复制。
- 原型是负分续接；论文拟议零下界。margin、distinct 支持也有规范/实现差异，不能写成已经修好代码。
- E1 固定预算和配置上限，E3 才固定相同 Tube。STB 共享评分和去重，不能故意弱化。
- stride 2 与 {2,4,8} 不是天然等预算。阈值后处理扫描不是计算加速曲线。
- MAE 同时报匹配数/召回/共同 GT cohort；五 seed 方差不是数据显著性。
- 验证集 41,798 对且全正例；不能测负例 FAR。正式表无数据继续留空。
- `check_paper_semantics.py` 只做标量公式检查，不运行原型或证明真实效果。

论文路径：`/Users/gzhlaker/Documents/code/gzhlaker_cvpr2027`。
原型只读路径：`/Users/gzhlaker/Documents/code/FastVCL`。
对照只读路径：`/Users/gzhlaker/Documents/code/gzhlaker_transvcl`。
外部路径不可访问时，写清具体缺失并继续不依赖它的任务。不要声称读过不存在的文件。

使用主方案中的构建命令。当前仍采用 CVPR 2026 fallback 模板；提交前核实 2027 官方模板和政策。不要把编译成功当作投稿就绪。

最终用中文简洁汇报实际修改、检查结果和未完成的证据工作，并给出可打开的文件链接。
