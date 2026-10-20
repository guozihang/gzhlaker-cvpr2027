# FastVCL 第五轮执行记录

日期：2026-10-20。执行入口：[第五轮论文优化方案](../FastVCL_CVPR2027_第五轮论文优化方案.md)。本轮完成了论文与方法规范的 P0-1–P0-5、P1 表格拆分和 evidence 同步，重建并视觉核验了两份 PDF，记录了资产与实验阻塞。**没有**执行数据集推理、视觉模型、GPU 或付费调用；论文仍不含任何正式结果。

## 1. 本轮改了什么

| 项目 | 本轮处理 | 验收状态 |
|---|---|---|
| P0-1 引言因果判断 | 删除“更多 ISC 比较不能解决”的绝对判断；改为检验视觉决策是否提供几何/便宜规则之外的信息；`reversible` 改为 `abstaining`，明确 on 模式单项失败只保证该项回退，只有 off/shadow 要求整体等于 core | 完成 |
| P0-2 margin 竞争对象 | 式 `eq:margin` 改为排除当前匹配后的最强竞争者；记录 competitor pool 的跨 plan 合并与去重；单侧缺失标 missing，选择器用中性秩 0.5；`K` 拆为 `K_nn`（邻居数）和 `B`（问题预算） | 完成 |
| P0-3 融合规则 | 补齐几何边、同 A 不同 B 排除、分组轮转选择器、归一化 gap/边界映射误差排序、固定 $R_e$ 与 $L_cW_c$ 的 Conn、单轮不传递、成员消费、端点和分数重算；加入 mechanism accounting（机会数、合法边覆盖率、Conn 通过率、询问/执行动作） | 完成规范；未实现代码 |
| P0-4 预算/重试/连接成本 | 锚点证据最多 3 对/6 帧，融合证据最多 5 对/10 帧；$B_A=\lfloor2B/3\rfloor$，未用 A 额度只能转 F；缓存命中也计问题；重试默认关闭，启用时最坏 $B+R$；连接工作逐 cell 计费；伪代码从主流程删除 C0 先验输入，改为 A0→A1→tracks/tubes→C0→Y | 完成 |
| P0-5 风险分母 | 分开真锚点删除率（全 A0 与受询真锚点两个口径）、删除动作错误率、错误融合率、覆盖率/弃权率、最终全评估效果；给出零错误精确上界及 150/299/300 的数值；明确有效分母、相关性、分组区间和零宽 bootstrap 限制 | 完成 |
| P1 表格与文档 | 主表拆为固定特征 core 表与 augmented 表；augmented 行不再与 core 混排；同步 claims/status/spec/manifest 等 evidence 文档 | 完成同步 |
| 页面重组 | 摘要、引言、相关工作、Method、Experiments、Conclusion 重写；validity mask、算法、风险表、融合细则移入补充材料 | 部分：正文约 8.5 页，8 页目标未完全达到 |

## 2. 实际执行的检查

| 检查 | 结果 | 产物 |
|---|---|---|
| 本轮参考语义检查 | 18/18 通过；覆盖最强竞争者 margin、缺失/并列、selector 轮转、融合边五种非法情形、Conn 路径、风险上界、预算计数、TeX 规则存在性 | [round5_math_checks.json](round5_math_checks.json) |
| 旧论文标量检查 | 7 组通过 | [round5_paper_math_checks.json](round5_paper_math_checks.json) |
| evaluator parity | 211 cases，0 mismatch，macro/sentinel/accounting 通过 | [round5_evaluator_parity.json](round5_evaluator_parity.json) |
| contract probes | 8 个既有行为全部复现，包括原型 DP 与拟议规则的差异 | [round5_contract_probes.json](round5_contract_probes.json) |
| 原型单测（只读重跑） | 646 tests，OK，10 CUDA skip，45.369 s | [round5_prototype_tests.log](round5_prototype_tests.log) |
| 论文主 PDF | 编译 exit 0；10 页；正文约 8.5 页，参考文献从第 9 页开始 | `main.pdf` |
| 补充 PDF | 编译 exit 0；12 页；无 overfull/undefined 警告 | `supplementary.pdf` |
| 视觉核验 | 主文第 8–9 页、补充第 8/10/12 页；表格、算法、公式无截断 | 本轮会话 |
| 链接/空白/JSON | 文档本地链接存在；JSON 可解析；`git diff --check` 通过 | 本轮 |

上述检查都是语义、公式或只读代码检查，不是数据集、模型或基准结果。原型测试通过只说明既有实现没有回归，不证明论文拟议的新规则有效。

## 3. 资产核验与阻塞

详细字段见 [round5_assets.json](round5_assets.json) 和 [round5_source_snapshot.json](round5_source_snapshot.json)。

- **数据**：`/Users/gzhlaker/Downloads/VCSL` 存在，12,254 个 ISC 特征文件，4,418,396,160 字节；val 41,798 对、test 54,630 对。元数据哈希与本轮记录一致。
- **原视频**：在数据根目录下检索 `.mp4/.mkv/.avi/.webm/.mov`，结果为 **0**。因此没有可信的 feature-index → frame 映射，不能构造 A/B 原帧证据板。
- **视觉后端**：未发现 Visual Jev/VideoJev/Qwen 等已验证权重；Hugging Face 缓存 22 MB、13 个文件，不构成可用后端；无 API 凭据验证，主运行时无 torch。
- **硬件**：Apple M2 arm64，无 CUDA GPU；`nvidia-smi` 不存在。
- **原型**：HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，工作树干净；本轮只读重跑 646 项测试，未实现 zero-floor、competitor margin、fusion selector 或 Conn。
- **预算**：按历史 41,798 + 54,630 对、每对 12 个逻辑问题，单个 augmented 配置的算术上限是 1,157,136 个问题；这不是执行量或 GPU 小时估计。

因此触发方案中的停止条件：**无可信原帧映射** → 保留双阶段 proposed 描述，不做猜测式取帧；**无足够标签或独立审计** → 保持 shadow，不认证 1% 风险；**无有效融合机会** → 只报告规范与计数模板。W5-2、W5-3、W5-4 均未启动。

## 4. 页面与结构状态

- 主文 10 页：摘要/引言/相关工作约 2 页，Method 约 3.5 页，Experiments 约 3 页，Conclusion 与参考文献从第 9 页开始。正文约 **8.5 页**，低于上一轮的约 10 页，但**未达到 8 页工作目标**。
- 补充 12 页：新增 notation/validity、diagnostics/augmented 表、完整的 §14 决策规范、预算表、风险台账、E6 表和整合算法。
- 剩余可裁剪项（按优先级）：把 timing 小节移入补充；把 action risk 的详细台账再压缩为 3–4 行；把 E6 行描述移入补充矩阵。再次裁剪会削弱主文的实验契约，因此本轮未继续。

## 5. 未完成与下一步

1. **实现**：把 zero-floor DP、distinct support、zero margin、competitor margin、fusion selector 和 Conn 作为显式变体加入原型，并在相同输入上与 legacy 对照；本轮只在 `scripts/round5_reference.py` 提供了论文侧参考语义。
2. **真实数据链**：取得与 ISC 特征版本匹配的原视频或作者提供的 frame manifest，验证至少 3 个视频的首/中/末 feature-index → frame；在此之前不做视觉调用。
3. **后端**：确定一个可运行的 Visual Jev/VideoJev 4B 后端，冻结权重、prompt、选项顺序和证据板；没有权重时不把接口当模型。
4. **E1/E3**：先跑 core 一致性和 simple sparse-to-band 对照；否则 RQ1 的 novelty gate 仍为空。
5. **E6-A/F shadow**：在真实标签和机会池上统计删除/融合机会、Conn 通过率和动作风险；达到门槛后才进入 on 模式。
6. **页面**：若必须严格 8 页，按 §4 的裁剪项继续，并在裁剪后重新做视觉核验。

## 6. 复现命令

```bash
# PDF
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex

# 本轮语义与旧检查
cd scripts && python3 -B check_round5_semantics.py --output ../evidence/round5_math_checks.json
cd .. && python3 scripts/check_paper_semantics.py --output evidence/round5_paper_math_checks.json

PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py --output evidence/round5_evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py --output evidence/round5_contract_probes.json

# 原型只读测试
cd ../FastVCL
PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .
```

本轮没有修改 `../FastVCL` 的任何文件；它的 HEAD 和工作树与快照一致。
