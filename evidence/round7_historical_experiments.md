# 第七轮：无 JEV 历史实验转录

来源：`VCL指标调研 (1).xlsx`，Sheet1；数值单位为百分数。
全部为用户提供的历史记录，尚未逐行核对预测、运行配置及评估日志。
下表不代表本次重新运行实验。时间为原表记法，尚不能统一解释为定位耗时。

| Excel 行 | 变体 | R (%) | P (%) | F1 (%) | 原表耗时 |
|---|---|---:|---:|---:|---|
| 12 | DP 基线 CPU | 14.36 | 93.94 | 24.91 | 57m15s |
| 13 | DP 基线 GPU | 14.36 | 93.94 | 24.91 | 32m37s |
| 15 | 无DP（argmax） | 16.53 | 85.11 | 27.68 | 30m21s |
| 16 | non-tube | 7.19 | 94.26 | 13.35 | 32m31s |
| 17 | non-tube-fully（直接 track→segment） | 13.69 | 94.05 | 23.90 | 29m24s |
| 18 | min_cosine=0.6 | 15.83 | 93.77 | 27.09 | 31m59s |
| 19 | min_cosine=0.55 | 16.18 | 93.70 | 27.59 | 31m14s |
| 20 | min_cosine=0.50 | 16.38 | 93.70 | 27.89 | 33m19s |
| 21 | sparse.stride=2 | 25.96 | 89.04 | 40.20 | 33m43s |
| 22 | sparse.stride=1 | 31.15 | 86.33 | 45.79 | 40m32s |
| 23 | min_inliers=3 | 21.97 | 89.93 | 35.31 | 32m49s |
| 24 | min_inliers=2 | 24.07 | 89.13 | 37.90 | 33m32s |
| 25 | min/max / slope=0.25 /4.0 | 14.40 | 93.86 | 24.97 | 31m38s |
| 26 | ransac.min_a_span=2.0 | 14.36 | 93.94 | 24.92 | 31m41s |
| 27 | sparse.topk=3 | 14.74 | 91.20 | 25.38 | 33m55s |
| 29 | tube + DP / stride2 + inliers3 | 29.65 | 87.07 | 44.24 | 40m32s |
| 30 | tube + DP / stride1 + inliers2 | 31.33 | 86.03 | 45.93 | 41m18s |
| 31 | tube + DP / stride1 + inliers2 + min_cosine=0.6 | 31.48 | 86.06 | 46.09 | 43m18s |
| 32 | non-tube / stride1 + inliers2 + min_cosine=0.6 | 37.05 | 80.82 | 50.81 | 37m32s |
| 33 | tube + argmax？ / stride1 + inliers2 + min_cosine=0.6 | 56.23 | 63.58 | 59.68 | 37m50s |
| 34 | tube + argmax？ / stride1 + inliers2 + min_cosine=0.6 | 58.07 | 61.81 | 59.88 | 9m3s |
| 35 | tube + argmax？ / stride1 + inliers2 + min_cosine=0.6 / +slope=0.25 /4.0 | 60.31 | 61.15 | 60.73 | 8m44s |
| 36 | tube + argmax / stride1 + inliers2 + min_cosine=0.5 / + topk=3 +slope=0.25 /4.0 | 60.73 | 59.39 | 60.05 | 56m31s |
| 37 | tube + argmax / stride1 + inliers2 + min_cosine=0.5 / + topk=3 +slope=0.25 /4.0 | 60.73 | 59.39 | 60.05 | 9m33s |
| 38 | non-tube-fully / stride1 + inliers2 + min_cosine=0.5 / + topk=3 +slope=0.25 /4.0 | 36.48 | 66.90 | 47.21 | 53m15s |

完整参数、原始单元格与异常标记分别见 CSV 和 JSON。
F1 保留原表值；不以四舍五入后的 P/R 重算值覆盖它。
