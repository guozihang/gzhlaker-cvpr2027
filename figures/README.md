# FastVCL 论文图片与占位素材

2026-10-17 按用户“先生成占位，后面调整”的要求制作。这些图表达拟议思路和版式，**不代表算法已经完成或实验已经验证**。

每张图交付：`.svg` 可编辑矢量源、`.pdf` 论文用矢量图、`.png` 快速预览。统一蓝色表示对应点、绿色表示轨迹/局部搜索域、橙色表示干扰点或间隙。

| 图 | PDF | SVG 编辑源 | PNG 预览 | 当前用途 |
|---|---|---|---|---|
| Fig. 1 | [PDF](fig_1_teaser.pdf) | [SVG](fig_1_teaser.svg) | [PNG](fig_1_teaser.png) | 稠密计算域与局部精化的概念对照（补充材料） |
| Fig. 2 | [PDF](fig_2_framework.pdf) | [SVG](fig_2_framework.svg) | [PNG](fig_2_framework.png) | 主文唯一框架图：特征、稀疏对应、轨迹/Tube、局部对齐，以及一个共享 `seltive model` 的锚点过滤与片段融合两处接入 |
| Fig. 3 | [PDF](fig_3_sparse_tracks.pdf) | [SVG](fig_3_sparse_tracks.svg) | [PNG](fig_3_sparse_tracks.png) | 锚点、间隙、有限 Tube 原理示意（补充材料） |
| Fig. 4 | [PDF](fig_4_tradeoff.pdf) | [SVG](fig_4_tradeoff.svg) | [PNG](fig_4_tradeoff.png) | 精度—延迟空结果图，无数据点或曲线（补充材料） |

## 重生成与修改

在论文根目录执行：

```bash
python3 scripts/generate_paper_placeholders.py
```

仅生成当前论文框架图：

```bash
python3 scripts/generate_framework.py
```

框架图与 `sec/3_method.tex` 对应：上排四个分区展示核心计算链，底部蓝色虚线表示完整分辨率归一化特征及有效性掩码直接进入 Tube 相似度计算。局部路径图对应论文拟议的零下界 DP；所有矩阵、坐标和区间均为示意。总生成脚本会调用这一专用脚本，不会恢复旧的文字流程占位图。

2026-10-19 第四轮改为**一个共享模型、两处有方向的接入**：下排中间是唯一的 `seltive model`，左侧是接入点①锚点判定（A0→A1，RANSAC 之前），右侧是接入点②片段判定（C0→Y，候选片段之后）；原视频帧与索引映射作为共享的额外输入从下方进入模型，橙色双向箭头表示“提问/判定”。图中明确写出预算 $B$、缓存、弃用/失败不改动该证据项。旧的“只核验最终候选”箭头已删除。该图仍是拟议设计示意，不能当作历史锚点级 JEV 路由或任何已实现结果的说明；帧映射、选择策略、模型后端及阈值仍需落实。第二轮/第三轮图注中的 post-only 描述已被第四轮取代。2026-10-20 第五轮只把预算符号从 $K$ 改为 $B$，框架结构与两个接入点不变。

依赖 Python 3 标准库与 `rsvg-convert`。脚本不读取实验数据，也不生成随机指标；Fig1/3 的坐标为人工定义的说明性几何。建议修改脚本后重生成；如果直接编辑 SVG，应同时保存修改来源并重新导出，避免下次运行脚本覆盖手工修改。

导出单张修改后的 SVG：

```bash
rsvg-convert --format pdf --output figures/fig_2_framework.pdf figures/fig_2_framework.svg
rsvg-convert --format png --output figures/fig_2_framework.png figures/fig_2_framework.svg
```

## 初稿插入

优先使用 PDF，并按跨栏宽度放置。四张图当前都带有英文的示意/待测标记，适合内部初稿；最终稿需依照定型方法和实测结果逐张替换。

LaTeX 片段见 [placeholders.tex](placeholders.tex)。**第三轮压页后，`main.tex` 只保留 Fig. 2（跨栏框架图，正文 Figure 1）；Fig. 1/3/4 已迁入 `supplementary.tex`（Fig. 1/2/3；注意补充材料中的编号）。图注以各入口文件中的 figure 环境为准。实际页码见最新 `README_BUILD.md`。** `placeholders.tex` 仅保留为独立预览片段，不再作为正文入口。

建议英文图注（已写进 LaTeX 片段）：

1. **Conceptual comparison of matching domains.** Dense comparison examines a broad frame-pair domain, whereas the proposed sparse-to-tube design uses temporal proposals to restrict fine-resolution alignment. The geometry is illustrative and does not represent a measured baseline or experimental output.
2. **FastVCL framework (proposed method).** Fixed ISC descriptors are normalized, sampled and matched by tiled mutual Top-K. Coordinate-deduplicated anchors undergo RANSAC, dual-axis support checks and gap splitting to define finite tubes. Full-resolution descriptors are reused for in-tube similarities. Proposed zero-floored local DP, backtrace, trimming, scoring and dual-axis de-duplication yield candidate intervals. One shared seltive model is queried at two budgeted insertion points: before fitting, to remove doubtful anchors (A0 to A1), and after extraction, to decide whether fragments are one continuous copy (C0 to Y). Both use original A/B frames through a verified index map, abstain on uncertainty or failure, and keep the core evidence unchanged when no action is taken. Backend, frame map and thresholds remain to be validated and are outside the core evaluated results in this draft. Matrices and trajectories are schematic.
3. **Illustration of anchor-supported refinement.** Sparse correspondences suggest separated support intervals, which define finite tube regions for local alignment. All coordinates are schematic; this figure is not a qualitative benchmark result.
4. **Placeholder for the accuracy–latency comparison.** No measurements are shown. Operating points will be populated from verified runs using a frozen evaluation and timing protocol.

## 后续替换

- Fig1：方法定型后核对每个框、箭头和术语。
- Fig2：上排按 `sec/3_method.tex` 与 `evidence/method_spec.md` 绘制；下排是一个共享 `seltive model` 的两处拟议接入（锚点过滤、片段融合）。以后方法定型或变更时同步修改方法说明、`scripts/generate_framework.py`、图注和图文件。
- Fig3：可以继续作为原理图；若改作真实案例，必须使用真实 pair、预测与 GT，记录样本选择规则和生成命令。有区间 GT 不等于有逐帧对应真值。
- Fig4：用真实结果绘图脚本替换；先明确横轴是 mean 还是 P50，以及同口径配置。无数据时保留空图。
- 占位图的源文件和真实实验图的源数据分开存档；真实图交付 run ID、输入 hash、脚本和输出文件。

## 预览

![Fig. 1](fig_1_teaser.png)

![Fig. 2](fig_2_framework.png)

![Fig. 3](fig_3_sparse_tracks.png)

![Fig. 4](fig_4_tradeoff.png)

## 第二轮排版修订（2026-10-18）

Fig. 4 使用 560×330 原生画布，提高单栏印刷时轴标签与占位说明的字号；仍无数据点、数值刻度或拟合曲线。Fig. 1/3 试排单栏后文字过小，已恢复跨栏。后续压页应重排原生布局或迁移到补充材料，不应直接继续缩小整图。

## 第三轮迁移（2026-10-18）

为把正文压到 fallback 模板的 8 页（参考文献另起第 9 页），Fig. 1、Fig. 3、Fig. 4 与效率/消融表
迁入补充材料；正文只保留跨栏框架图。所有图仍是示意/空结果，没有新增数据点或真实样本。补充材料
中的图号为 Fig. 1（域对照）、Fig. 2（锚点/Tube）、Fig. 3（空 trade-off 平面），与正文引用按文字
说明区分，不使用跨文档 `\ref`。

## 第四轮框架图修订（2026-10-19）

按第四轮方案把下排从“候选后置核验”改为“一个共享模型、两处有向接入”：中间是唯一的
`seltive model`，左边是 RANSAC 之前的锚点判定（$A_0\to A_1$），右边是候选片段之后的融合判定
（$C_0\to Y$）；原视频帧与索引映射作为共享额外输入从下方进入模型。图中保留预算 $B$、缓存、
弃权/失败不改证据的说明。旧的“只核验最终候选”箭头已删除。该图仍为拟议设计，不含任何实测
数据；正文因新增方法与 E6 增至 12 页（参考文献在第 11–12 页），详见 `README_BUILD.md`。
