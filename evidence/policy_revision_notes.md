# 2026-11-08：按 Overleaf 新 title / abstract 统一论文

基准提交：00ded7723b12ec811f65d76c0e184e952d1f83df（Update on Overleaf）。

## 固定内容

主文 title 命令与整个 sec/0_abstract.tex 均与基准提交完全一致，摘要末尾原本没有
换行，也保持不变。校验结果见 [audit](policy_revision_audit.json)。

## 本轮修改

- Introduction / Related Work 改为输入视频对的计算分配问题，并补充动态路由文献。
- Method 统一为前置 policy → 二选一分支。主分支为可训练编码器、可学习相似度和
  2D detector；加速分支为直接相似度、anchor、RANSAC 和有界端点检查。
- 补全低成本预览、离线分支偏好监督、成本项、训练划分和阈值选择。这些是拟议设计，
  不代表旧代码已经实现。
- 训练可离线执行两分支生成监督；推理只执行选定分支。耗时包含 policy、解码、
  特征和分支条件耗时；删除固定 stride 就是次二次复杂度的错误表述。
- 实验表改为主对比、路由对照、组件消融。正文保留 8 行历史诊断，补充材料保留全部
  25 行，并按 CSV 核对数值。历史 DP / tube 数据不作为当前加速分支结果。
- 重绘框架图、重写补充材料，同步 LLM Usage Statement 和构建说明。

## 证据边界

检查到的本地 FastVCL 仍位于 7c049599813de29b37adf94d07beccfd0b366a00，其旧路由与
验证模块不等同于本轮前置双分支 policy。没有发现新版训练权重或基准结果。本轮没有
训练模型或运行 VCSL/VCDB 实验。

主分支具体 backbone、交互层、detector 容量、训练参数和权重待实现与验证；补充材料
预览网络尺寸和几何参数是标明的初始设计。保留的摘要声称已有 competitive accuracy
和 significant speedup，正文明确说明现有记录尚不能证实。需要真实实验结果，不能
以旧表或估算时间填充。

历史表是工作簿转录，并非逐行完成预测和配置核验的审计；显示时补齐小数位不改变数值。

## 新增文献核对来源

- BlockDrop 用策略选择残差块、权衡计算和识别质量：
  [作者论文](https://arxiv.org/abs/1711.08393)。
- SkipNet 用门控网络动态跳层：
  [作者论文](https://arxiv.org/abs/1711.09485)。
- RANSAC 基础引用：
  [SRI 出版记录](https://www.sri.com/publication/artificial-intelligence-pubs/random-sample-consensus-a-paradigm-for-model-fitting-with-applications-to-image-analysis-and-automated-cartography-2/)。
- GIoU 框回归损失：
  [CVPR 2019 原论文](https://openaccess.thecvf.com/content_CVPR_2019/html/Rezatofighi_Generalized_Intersection_Over_Union_A_Metric_and_a_Loss_for_CVPR_2019_paper.html)。

同时核对 [TransVCL](https://arxiv.org/abs/2211.13090) 的特征增强、相似度和定位结构，
以及 [VCSL 官方仓库](https://github.com/alipay/VCSL) 的版本和评价背景。没有把其他
协议下的公开性能值填入本轮对比表。
