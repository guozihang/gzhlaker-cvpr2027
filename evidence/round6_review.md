# FastVCL 第六轮执行记录

日期：2026-10-25。执行入口：[第六轮论文优化执行计划](../FastVCL_CVPR2027_第六轮论文优化执行计划.md)。
本轮完成了论文侧的 P0-1–P0-5、官方 2027 模板迁移、LLM Usage Statement、框架图的语义区分、
两份 PDF 的重建与页面核验，以及 evidence 的同步。**没有**修改原型、执行数据集推理、调用视觉
模型、运行 GPU kernel 或产生任何基准结果；主表全部数值仍为 pending。

## 1. 本轮改了什么

| 项目 | 本轮处理 | 验收状态 |
|---|---|---|
| P0-1 Conn 连接判定 | 把“提议路径”的局部 DP 与“证明连接”的 Conn 分开。Conn 只在合法左支持节点播种，不允许任何格点重启，回溯必须同时满足左支持起点和右支持终点；只检验唯一最高分路径，失败即拒绝，并明确首版不枚举所有可行路径；复用路径执行同样的端点、区域、步集和质量检查 | 参考实现与正文、补充一致；计划中的两个反例均拒绝 |
| P0-2 覆盖率与计算量 | 覆盖率改为端点区间上的 $\min(d_A/s_A,d_B/s_B)$，跳过索引会降低覆盖率；路径节点、DP 访问、前驱计算、相似度计算和失败/复用分别计数；不再用路径长度自证覆盖 | 参考实现与正文一致；小网格枚举核对通过 |
| P0-3 几何与合并范围 | 边界映射按方向分别比较：A$\to$B 残差对 $\kappa_B$，B$\to$A 残差对 $\kappa_A$，拒绝合并阈值；阈值/逆斜率必须有限，退化映射不可用；零 gap 仅当两轴均为零才合法。合并只处理原始 $\mathcal C_0$ 的不相交二元组，按冻结顺序、消费两个成员、不新增边、不再做集合级复核；重建失败保留两成员 | 不对称阈值反例拒绝；三片段链只产生一次合并；共享成员不重复消费 |
| P0-4 预算上界 | 引入实际逻辑问题数 $q_A,q_F$，给出 $q_A\le\lfloor2B/3\rfloor$、$q_A+q_F\le B$、$N_{\rm paired}\le3q_A+5q_F\le5B$、$N_{\rm slots}\le6q_A+10q_F\le10B$；固定分配 $3B_A+5B_F$ 只是特例，$B=12$ 全转移为 60 对位置/120 帧槽而非 44；E6-F 的 Conn-only 行改为 0 个模型问题并另列检查边上限 | 正文、补充、参考实现与表格一致 |
| P0-5 模板与声明 | 迁移官方 CVPR 2027 author kit v1；移除 review header 中的 Paper ID；加入 LLM Usage Statement；正文于第 8 页结束，未缩字体、未改页边距 | 归档 SHA-256 与官方链接一致；`cvpr.sty`/`.bst` 与 kit 逐字节一致；正文 8 页 |
| 框架图 | 重新生成 Fig. 2：核心框标注“proposal paths, zero restart”，融合框标注“Conn: separate two-end certification”和“pairwise merge · no model call”，无障碍描述同步 | 图与正文规则一致，无截断 |
| Evidence | 更新 claims、implementation status、missing evidence、manifest、selective-model spec、experiment plan、contract/method spec 的轮次状态；新增 round-six 检查与快照 | 顶部为当前状态，旧轮次日期保留 |

## 2. 实际执行的检查

| 检查 | 结果 | 产物 |
|---|---|---|
| 第六轮参考语义检查 | **35/35** 通过：Conn 反例/端点/复用、区间覆盖、按轴阈值、零 gap、链式与共享成员合并、预算转移包络、正文/补充规则存在性 | [round6_math_checks.json](round6_math_checks.json) |
| 论文标量检查 | 7 组通过 | [round6_paper_math_checks.json](round6_paper_math_checks.json) |
| evaluator parity | 211 cases，0 mismatch，macro/sentinel/accounting 通过 | [round6_evaluator_parity.json](round6_evaluator_parity.json) |
| contract probes | 8 个既有原型行为全部复现 | [round6_contract_probes.json](round6_contract_probes.json) |
| 原型单测（只读重跑） | 646 tests，OK，10 CUDA skip，43.101 s | [round6_prototype_tests.log](round6_prototype_tests.log) |
| 主文 PDF | 编译 exit 0；10 页；正文结束于第 8 页；参考文献第 8–9 页；LLM 声明第 10 页；无 overfull/undefined | `main.pdf` |
| 补充 PDF | 编译 exit 0；12 页；无 overfull/undefined | `supplementary.pdf` |
| 视觉核验 | 主文第 1/4/8/9/10 页，补充第 8/10/12 页；表格、框架图、算法、声明无截断 | 本轮会话 |
| 模板核验 | 官方 ZIP SHA-256 `7271bdbb…c43121`；`cvpr.sty` `1cd7f434…4286b4`；`ieeenat_fullname.bst` `e38e6166…acfc`，均与本仓库一致 | [round6_source_snapshot.json](round6_source_snapshot.json) |
| 链接/空白/JSON | 文档本地链接存在；JSON 可解析；`git diff --check` 通过 | 本轮 |

上述检查都是语义、公式、文本或只读代码检查，不是数据集、模型或 GPU 结果。原型测试通过只说明
既有实现没有回归，不证明任何拟议规则在真实数据上有效；第六轮的修复目前只存在于论文侧参考实现。

## 3. 资产核验与阻塞

- **数据字节口径**：同一次统计中，12,254 个 `.npy` 的 `stat().st_size` 合计为
  **4,388,241,152 字节**，`stat().st_blocks*512` 合计为 **4,418,396,160 字节**。前者是逻辑
  文件大小，后者是分配块占用；两者差异解释第五轮资产记录与 manifest 的数值差，不构成特征内容
  变化的证据。val 41,798 对、test 54,630 对。
- **原视频**：数据根目录仍为 0 个 `.mp4/.mkv/.avi/.webm/.mov`，没有可信的
  feature-index $\to$ frame 映射，不能构造原帧证据板或执行 E6。
- **视觉后端**：本轮未重新审计全局缓存；沿用第五轮结论——没有已验证的 Visual Jev/VideoJev
  权重、API 凭据或可运行后端。接口仍是 proposed。
- **原型**：HEAD `fdc3362b2418b316e16d6dfd68435e40c1b1afb8`，跟踪文件工作树干净；本轮没有修改
  原型。zero-floor core、distinct support、zero margin、strongest-competitor margin、fusion
  selector 和 `Conn` 仍未实现；W6-1、W6-2 未启动。
- **预算**：全量 val+test 96,428 对，单个 augmented 配置的算术逻辑问题上界仍为 1,157,136；
  这不是实际调用、token、费用或耗时估计。

因此第六轮计划中的停止条件仍成立：无可信帧映射/后端，视觉分支维持 proposed；无独立标签与审计，
不认证 1% 风险；无 core/STB 实现与真实小试，E1 的 novelty gate 仍为空。

## 4. 页面与结构状态

- 主文 10 页：正文（含两张表）结束于第 8 页；参考文献从第 8 页底部开始并延续到第 9 页；
  LLM Usage Statement 独占第 10 页。八页正文限制**已满足**。
- 补充 12 页：新增第六轮更新说明；§14 决策规范、预算/风险表、E6 矩阵与整合算法保留。
- 与第五轮相比，正文从约 8.5 页压缩到 8 页以内，主要来自 experiments 小节的合并与压缩；
  没有通过缩字体、改页边距或隐藏 TODO 达标。
- 若要继续加正文，必须等量删减，否则会把结论推入第 9 页。

## 5. 未完成与下一步

1. **W6-1 实现**：把 zero-floor DP、distinct 双轴支持、zero margin、competitor margin、
   fusion selector 和 Conn 作为显式变体加入原型，并在相同输入上与 legacy 对照；本轮只在
   `scripts/round6_reference.py` 提供论文侧参考语义。
2. **W6-2 小试**：在冻结开发子集上先跑 20 对冒烟，再跑约 200 对 E1/E3，记录失败账本和耗时；
   在此之前不把任何 STB/核心对照写成结果。
3. **原帧与后端**：取得与 ISC 特征匹配的原视频或 frame manifest，核对至少三个视频的首/中/末
   映射；冻结一个可运行后端并做真实输入 smoke。
4. **动作与审计**：标注真实的 anchor/fusion 机会，冻结阈值，独立 audit；不足时保留 shadow，
   不认证 1%。
5. **正式运行与成稿**：全量 val/test、外部基线、计时子集；只有真实结果才能替换主表占位符。

## 6. 复现命令

```bash
# PDF
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs main.tex
TECTONIC_CACHE_DIR=.home/Library/Caches/TectonicProject.Tectonic tectonic --only-cached --keep-logs supplementary.tex

# 第六轮语义与论文标量检查
cd scripts && python3 -B check_round6_semantics.py --output ../evidence/round6_math_checks.json
cd .. && python3 scripts/check_paper_semantics.py --output evidence/round6_paper_math_checks.json

# 只读 parity / contract / 原型测试
PY=/Users/gzhlaker/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_evaluator_parity.py --output evidence/round6_evaluator_parity.json
PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/check_contract_semantics.py --output evidence/round6_contract_probes.json
cd ../FastVCL && PYTHONDONTWRITEBYTECODE=1 "$PY" -B -m unittest discover -s tests -t .
```

本轮没有修改 `../FastVCL` 的任何文件；它的 HEAD 和工作树与快照一致。
