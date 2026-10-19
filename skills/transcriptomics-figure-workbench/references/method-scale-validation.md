# 45 种方法的数据量、布局与实际图像检查

## 实际范围

42 个历史配方和三种新增三维方法，共 45 种方法。每种实际生成三档不同冻结输入、小／中／大三个单图，以及与大档使用同一完整输入的自定义单图；另组装两幅完整 SVG 作布局对照。合计 **135 份不同冻结输入、180 张单图、45 张对照页**。数据量和布局变体不会增加方法数。

本次逐张检查 225 张最终 PNG；每张记录绑定准确图像 SHA256，长页面另按原尺寸分段看图。动画的四份实际 GIF／离线 HTML 也检查了首、中、末帧、时间标签、拖动及播放暂停，全部 6／12／24／24 帧解码，无外部请求。见 [图片检查记录](../assets/method-scale-gallery/visual-review.json) 和 [动画检查记录](../assets/method-scale-gallery/animation-review.json)。这是作者逐图屏幕自检，独立审美评审与真实科学验收均未建立。

## 数据量的含义

Small／Medium／Large 是同一种示例内的相对档位，具体范围如下；不是对任意大数据的性能保证。部分历史冻结树最多五叶，未外推为大规模系统树能力。带 `display` 的复制对象仅用于绘图拥挤测试，不是独立样本或新科学结果。三档输入均有不同哈希；自定义布局与大档逐字节同表。

|方法 / 当前调用前缀|数据量维度|小 → 中 → 大|自定义实际画布（英寸）|
|---|---|---|---|
|已有分支长度树 / `Scale_H01_branch_tree`|tree leaves|2 → 4 → 5|9.75 × 3.65|
|效应区间森林图 / `Scale_H02_forest`|label|2 → 6 → 18|14.25 × 7.70|
|火山图 / `Scale_H03_volcano`|gene effects|140 → 280 → 420|11.75 × 5.16|
|矩阵热图 / `Scale_H04_heatmap`|features × samples|[4, 3] → [8, 6] → [12, 8]|9.75 × 5.54|
|配对观测轨迹 / `Scale_H05_paired`|paired display units|16 → 32 → 48|14.25 × 5.16|
|效应与不确定性矩阵 / `Scale_H06_effect_matrix`|feature|2 → 6 → 18|11.75 × 9.20|
|独立单位散点 / `Scale_H07_xy_points`|points|18 → 33 → 48|9.75 × 5.16|
|分组估计区间 / `Scale_H08_grouped_estimates`|category|2 → 4 → 12|14.25 × 7.14|
|给定混淆计数 / `Scale_H09_confusion_counts`|classes|2 → 3 → 6|11.75 × 8.74|
|双指标三角矩阵 / `Scale_H10_split_metric_matrix`|row_id|2 → 4 → 12|9.75 × 6.00|
|已有层次树与轨道 / `Scale_H11_hierarchy_tracks`|tree leaves|6 → 11 → 16|14.25 × 6.10|
|已有环形层次树 / `Scale_H12_radial_hierarchy`|tree leaves|6 → 11 → 16|11.75 × 8.50|
|同单位可加量堆积 / `Scale_H13_stacked_values`|object_id|3 → 8 → 24|9.75 × 9.05|
|已有富集结果点阵 / `Scale_H14_enrichment_grid`|terms × result columns|[6, 2] → [12, 4] → [18, 6]|14.25 × 7.06|
|条目索引表 / `Scale_H15_term_key`|term_id|2 → 6 → 18|10.50 × 8.40|
|双量值色块矩阵 / `Scale_H16_bivariate_tiles`|matrix rows × columns|[3, 3] → [6, 6] → [8, 9]|11.63 × 5.90|
|队列估计区间 / `Scale_H17_cohort_intervals`|feature|2 → 5 → 15|14.25 × 9.13|
|关联结果矩阵 / `Scale_H18_association_matrix`|features × modalities|[3, 2] → [5, 3] → [7, 4]|11.75 × 5.66|
|已有校准结果与人数 / `Scale_H19_calibration_counts`|supplied calibration bins per model|2 → 4 → 5|9.75 × 6.30|
|跨组学配对效应 / `Scale_H20_cross_effects`|cross-view feature effects|27 → 52 → 76|14.25 × 6.10|
|同对象对齐视图 / `Scale_H21_aligned_views`|objects × coordinate views|[12, 3] → [24, 3] → [36, 3]|9.00 × 11.30|
|基因组候选连接 / `Scale_H22_genomic_links`|physical track records|33 → 63 → 93|9.75 × 6.90|
|局部位点结果轨道 / `Scale_H23_locus_tracks`|supplied variants|9 → 19 → 27|14.25 × 7.40|
|给定多层不确定区间 / `Scale_H24_uncertainty_fan`|stored x vertices per group/coverage|4 → 8 → 11|11.75 × 5.70|
|类型互作网络 / `Scale_H25_typed_network`|nodes and all supplied selected-subgraph edges|[10, 4] → [19, 13] → [28, 27]|9.75 × 6.70|
|多事件状态矩阵 / `Scale_H26_multistate_matrix`|matrix rows × columns|[3, 4] → [6, 8] → [8, 12]|14.25 × 6.70|
|已有富集运行曲线 / `Scale_H27_running_enrichment`|stored curve vertices|100 → 200 → 300|11.75 × 6.70|
|给定等值场 / `Scale_H28_contour_field`|supplied rectangular field grid|[14, 11] → [27, 22] → [40, 32]|9.75 × 6.70|
|流程与结果组合 / `Scale_H29_process_dashboard`|stored schematic vertices and supplied surface samples|1622 → 2510 → 6074|11.75 × 20.14|
|已有 ROC 与 PR 曲线 / `Scale_H30_publication_curve`|stored curve vertices per model|4 → 6 → 8|11.75 × 12.05|
|带对齐注释的矩阵 / `Scale_H31_aligned_matrix`|features × samples|[4, 3] → [8, 6] → [12, 8]|9.75 × 5.94|
|已有 Mantel 结果矩阵 / `Scale_H32_mantel_matrix`|variables × supplied specimen sets|[5, 4] → [10, 4] → [14, 4]|14.25 × 11.58|
|给定贡献点分布 / `Scale_H33_contribution_swarm`|features × complete contribution units|[7, 67] → [13, 134] → [19, 200]|11.75 × 7.51|
|已有 PCA 坐标与区间 / `Scale_H34_pca_reference`|stored points; all reference contours retained|120 → 240 → 360|9.75 × 6.50|
|状态结果组合 / `Scale_H35_state_dashboard`|states and stored embedding points|[12, 536] → [20, 1068] → [28, 1600]|14.25 × 10.22|
|分类贡献分解 / `Scale_H36_multiclass_contributions`|classes with complete contribution and share channels|2 → 4 → 5|9.81 × 17.49|
|已有嵌入坐标多视图 / `Scale_H37_embedding_atlas`|atlas categories × main identities|[24, 4] → [47, 8] → [70, 16]|9.75 × 12.13|
|已有训练曲线组合 / `Scale_H38_training_dashboard`|stored epochs × diagnostic runs|[41, 10] → [80, 19] → [120, 28]|14.25 × 8.88|
|已有活性结果组合 / `Scale_H39_activity_dashboard`|matrix rows × columns|[50, 15] → [100, 30] → [150, 44]|11.75 × 29.30|
|给定分布与效应区间 / `Scale_H40_effect_distribution_forest`|outcomes × complete effect panels|[9, 2] → [18, 2] → [26, 2]|9.75 × 10.19|
|分面气泡矩阵 / `Scale_H41_facet_bubble_matrix`|features × windows per complete facet|[3, 3] → [6, 6] → [8, 8]|14.25 × 11.19|
|火山图与边际分布 / `Scale_H42_volcano_marginal`|gene effects|140 → 280 → 420|11.75 × 7.96|
|三维散点与正交投影 / `Scale_D01_Scatter3D`|stored XYZ objects|48 → 96 → 144|14.00 × 8.70|
|体渲染与给定传递函数 / `Scale_D02_Volume`|uniform grid with identical physical extent|[8, 8, 8] → [16, 16, 16] → [24, 24, 24]|11.50 × 16.28|
|分子轨迹动画与逐帧查看 / `Scale_D03_Trajectory`|complete atom frames|[6, 24] → [12, 24] → [24, 24]|14.50 × 6.80|

实际画布包含标题与脚注；长页需要原尺寸阅读。对照页保留原 SVG 字体和整幅内容，宽度／行高变化刻意可见，它不是建议直接缩到期刊单栏的组图。真实论文排版需选择互补内容并按目标物理尺寸再次检查。

## 已落实的修正

- 森林和队列效应：物理行高、区间、零线与数值区分别对齐；类别较多的估计图改用横向点区间，经典柱图仍可选。
- 双指标和关联矩阵：单独的注释带、清楚的三角方向、独立色标、精确匹配 n 与缺失格，防止编码混淆。
- 观测单位说明：长图例标题自动换行，保留完整文字和每组 n，避免旧入口在不同字体环境下超出画布。
- 富集：完整运行曲线、全部命中和完整排序指标；80 个 hit 不因曲线档位减少而删去，不补造 NES／FDR。
- 多视图：连线绑定实际对象与实际坐标轴，单列和多列重排后仍接到相同身份；共享坐标不等于共享科学量尺。
- 等高线：白色对比描边及边缘完整数字，修复边缘裁切。
- 流程结果页：完整示意图与三曲面、三矩阵和两组计数分开阅读；身份标签覆盖穿越的装饰线，支持两列／三列。
- 多分类贡献、状态及嵌入图谱：完整阅读版与经典总览分开；密集环形编号交替半径并加引导线，70 项图例不省略。
- 活动矩阵：150 行全部标签的长页、原始列名映射、独立模块条带和五个密度轮廓；密度共用数值范围，明确纵轴。
- 气泡分面：默认物理高度随行分面和特征数增长，稀疏数据不沿用空大的画布。
- 火山／PCA：保留边缘轨道、计数、比例、阈值和给定轮廓的定义；常规 bulk 请求继续优先完整专用扩展，基础兼容函数保留。

## 三维新增与扩展

- 三维散点：48／96／144 个给定 XYZ 对象；自定义三个相机加三个正交投影，显式 3 列 × 2 行，检查遮挡与单位。
- 体绘制：8³／16³／24³ 个体素，物理范围一致。有限预算的正交相机射线前向合成；三线性采样只用于图像生成，按物理采样距离修正透明度。自定义两相机、两轴向观察、三中央切片和传递函数，共八面板。不是分割、拟合或新体数据。
- 分子轨迹：同一 24 原子、23 条明确键，6／12／24 帧；自定义六关键帧与另一固定相机，GIF 和 HTML 都保留所有 24 帧，物理时间为 0–11.5 ps。没有 MD、拓扑推断、对齐或重成像。

## 调用与复现

从 skill 的 `scripts` 目录执行：

```text
python workbench.py visual-template --entry Scale_H40_effect_distribution_forest_Medium --output effect-example
python workbench.py plan --spec effect-example/example.spec.json --output effect-example/plan.json
python workbench.py render --plan effect-example/plan.json --output effect-export

python workbench.py visual-template --entry Scale_D01_Scatter3D_Custom --output scatter-example
python workbench.py visual-template --entry Scale_D02_Volume_Custom --output volume-example
python workbench.py visual-template --entry Scale_D03_Trajectory_Custom --output trajectory-example
```

所有输出路径选新目录。每份模板记录相对输入、输入哈希、来源、主题、参数与导出设置；修改输入后更新哈希并重做计划。自定义单图使用对应方法的 `size` 或 `width/panel_height/columns/rows`，跨图组装使用 `layout.request.json`。参数不足以容纳全部内容时拒绝，而不静默删图。

## 保留和验收边界

上一轮 93 张单图、45 张组装页、原 42 个历史编号、雷达和三维曲面保留原文件。综合库按父族合并近似画法，当前 21 份图库的 2247 条来源引用对应 1697 个条目：1239 个当前、458 个历史；86 个父族和 90 个原基础画法仍保留。

测试分别检查输入／计划契约、冻结值及坐标、实际渲染、布局、离线播放和图片检查绑定。脚本通过不能替代看图；同样，当前合成图看过不保证新数据、新标签、新颜色或期刊缩放后仍美观。所有示例标记为合成软件材料，不是生物学证据。
