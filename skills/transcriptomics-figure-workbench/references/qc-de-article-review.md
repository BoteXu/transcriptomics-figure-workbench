# 转录组 QC / DE 绘图增量与代码审查

来源：[用户指定文章](https://mp.weixin.qq.com/s/Sb80ORHTXlLZdGkEDcyFpw)。2026-10-14 用户在聊天中提供完整脚本。本次依据该脚本审查；浏览器未成功读取网页正文，未声称完成网页与粘贴代码逐字比对。原脚本无随附可再分发许可，未复制原脚本、分析器或文章图片。新增渲染实现独立编写，原算法与软件归属不变。

## 可复用内容与实际入口

新入口 `figure_qc_de.plot_frozen_qc_de(data, theme, mode=..., contract=...)` 提供八个冻结表模式。它不做输入矩阵清洗、自动 log、填补、PCA、聚类、相关、回归、差异检验、FDR 或置信区间估计。每个模式接受至多 5000 条已审核摘要；大矩阵、原始表达与上游计算继续在服务器。

| 原脚本功能 | 本项目入口 / 输入 | 处理决定 |
|---|---|---|
| 校正前后样本箱线图 | 新 `sample_boxstats`；sample_id/project/q1/median/q3/whislo/whishi/n | 保留完整样本顺序、项目颜色、表达尺度、须线与离群点显示声明；不静默删除数据 |
| 项目色、表型形状 PCA | 新 `pca_scores`；已算坐标、方差解释标签、明确形状字典、可选已算椭圆 | 不重算 PCA、协方差或质心；不循环颜色/形状 |
| Volcano | `figure_styles.plot_volcano_editorial` | 保留原调整值、效应和明确边界；零 P 值显示需明确策略 |
| MA | 新 `ma`；feature_id/average/effect/status | 平均表达单位与对比必须说明，不把任意差值改称 log2FC |
| DEG 计数 | 新 `deg_counts`；up/down/other/untested 的完整计数 | 未检验与未显著分开，明确全集与选择阈值 |
| P 值分布 | 新 `pvalue_hist`；已算连续覆盖 [0,1] 的 bins 与整数计数 | 不因美观重算 P；不把缺失 P 作为 1 |
| Top-DEG 热图 | `figure_core.plot_heatmap` 的显式顺序、注释与 `missing=mask` | 上游提供已选基因、已算 Z 分数与树；不填零或重新聚类 |
| Top-gene 分布 | `figure_core.plot_samples` / `figure_publication.plot_raincloud` | 显示独立单位及固定数值；小 n 不默认画平滑密度；选择性图不是独立验证 |
| DEG 环形比例 | 新 `deg_donut` | 包含未检验分类；全零仅显示无数据文本，不绘造假扇区 |
| 效应森林图 | `figure_core.plot_forest` / `figure_publication.plot_publication_forest` | 只用真实 lower/upper；不从缺失 SE 画零宽区间，不统一用 1.96 替代原模型区间 |
| 全基因效应排名 | 新 `ranked_effects`；已算唯一 rank/effect/status | 不重新选基因、算优先级或重排结果；保留 rank 定义 |
| 环形签名 | 新 `radial_effects`；明确 <=40 特征及给定顺序 | 柱长为原效应绝对值、色为方向；无额外基线偏移、百分位截断或未说明透明度编码 |
| 联合火山及边际 | 已有 `figure_styles.plot_volcano_marginal` | 相同变量的所有组使用相同 bin 边界，密集图的汇总在服务器冻结 |
| 样本相关矩阵 | 已有矩阵/注释/树布局 | 输入已算相关矩阵、完整 ID 及同一上下界，不重新选择高变基因或拟合相关 |
| 综合主图 | 已有 `compose_panels.compose_bundles` | 先保留各独立面板再按显式布局组合；比较坐标必须单独声明 |

这八个模式复用既有箱线、散点、柱、极坐标和组成编码，不新增八种图形家族。原有 260 个稳定示例、42 个组合及全部旧入口保留。新增模式的可审查预览单独列在 [增量示例目录](../../../examples/qc-de/index.html)，不替换旧图册。

## 新入口契约

所有模式的 `contract` 都需非空 `source_definition`, `independent_unit`, `denominator`。主题使用同一个 `project_theme.json`；项目颜色身份不能随子集/行序变化。字体由该主题选择，不能宣称 Times New Roman 在每台机器都存在。

- `sample_boxstats`：完整 `order`；声明 `expression_scale`, `whisker_definition`, `outlier_display`。n 为每个箱的特征数，不是独立样本数。
- `pca_scores`：`record_type=sample` 行含 sample_id/project/phenotype/x/y。可选 `record_type=ellipse` 行含 project/x/y/width/height/angle/coverage。声明 `axis_x`, `axis_y`, `pca_basis`, `feature_selection`, `ellipse_definition`, `x_limits`, `y_limits`；明确 `marker_map`。几何和来源必须来自服务器结果。按样本云协方差和卡方分位构造的椭圆应称数据分布椭圆，不能直接称均值的 95% 置信区间。
- `ma`：feature_id/average/effect/status；声明 `average_definition`, `effect_definition`, `status_definition`, `feature_selection`。
- `ranked_effects`：feature_id/rank/effect/status；声明 `rank_definition` 及上述效应/分类/选择语义。
- `radial_effects`：feature_id/effect/status 和完整显式 `order`；声明原全集与截取规则，不暗示选中子集是全部差异。
- `deg_counts` / `deg_donut`：status/count，四类 up/down/other/untested 都须出现，即使为零；声明 `status_definition`, `count_unit`。
- `pvalue_hist`：left/right/count，非重叠且连续覆盖 [0,1]；声明 `pvalue_definition`, `bin_boundary_definition`，分母交代未检验/缺失项。

用既有 `figure_core.export_figure` 导出 PDF/SVG/PNG、精确 TSV、参数、主题和来源记录。对提交需要的 TIFF 可在服务器从冻结结果的同一 figure 导出并保存独立来源/校验记录；本轮未改变核心导出格式或声称 TIFF 已验收。

## 原代码中需要修正的分析与解释问题

1. 脚本读取 pre 与 norm 矩阵，**没有执行批次校正**。标题应由真实处理回执决定；不能因箱线图相近或 PCA 混合而认定校正成功。
2. 前后分别筛选高变基因和拟合 PCA，轴方向及基底可能不同。需共享冻结投影或明确各自拟合，不能把坐标位移直接解释成校正效果。
3. 仅凭数值范围自动 log2 并平移非正数据，可能改变尺度及效应含义。由测量协议和既有处理记录决定，不纳入绘图。
4. 中位数填补、重复标识平均、低方差过滤属于分析决定；需 QC/统计方案和真实服务器记录，不能当作绘图清洗。
5. 普通逐基因 OLS 不等同于 limma 的经验贝叶斯检验，也不适用于直接把原始 RNA counts 当连续同方差量处理。
6. 用项目字段作协变量需元数据佐证。样本名解析、每组两个样本与设计满秩均不能证明独立重复、足够功效或模型假设成立。
7. 将无效 P 统一改为 1 或把无穷值改为 0 隐藏检验失败。应保留失败/未检验状态。
8. 样本散布椭圆与均值置信椭圆不同；原公式是分布几何，默认“95% confidence”表述不准确。
9. 缺失 SE 填 0 产生伪精确区间；小样本统一 1.96 也不保留原 t 模型区间。本项目要求原区间。
10. 热图行 Z 分数填零会把缺失/不可估计值误画成均值；重新聚类改变排序。本项目要求已审核尺度、掩膜和树。
11. 各类别单独调用相同 bins 数会得到不同边界；边际图应使用共同明确边界。
12. 颜色/形状循环、按出现顺序分配身份会造成跨面板冲突；需全项目固定映射并拒绝容量不足。
13. Top-gene 图和签名轮的筛选/截断需显式说明；无显著基因时，不能换成其他基因仍标“Top DEG”。
14. 柱长、透明度、点面积和裁切后的显著性均需单独图例；本轮环形图只保留清楚的绝对效应和方向。
15. 字体回退、输出覆盖及部分导出失败需要真实记录；“SCI 级”或图形美观不能替代统计和科学验收。

## 验证状态

检查记录见 [validation-v025.md](validation-v025.md)。仅对合成冻结摘要做渲染和拒绝路径检查，不验证原脚本的 OLS、批次校正或科学结论。未复制文章的私有/付费附件。
