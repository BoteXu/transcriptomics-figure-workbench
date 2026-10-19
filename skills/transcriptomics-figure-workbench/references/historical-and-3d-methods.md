# 42 个历史配方的当前入口与三维／轨迹方法

[逐张查看实际示例](../assets/method-upgrade-gallery/index.html) · [综合绘图库](../assets/visual-library/index.html) · [逐张审阅记录](../assets/method-upgrade-gallery/visual-review.json) · [本轮修订及验收范围](method-upgrade-validation.md)

## 本轮实际交付与边界

上一轮42个迁移入口与三种新增方法的 **93 份单图、45 份完整组装页**保持原文件。本轮另提供[45种方法的实际数据量与布局检查](method-scale-validation.md)：**135份不同冻结输入、180张单图、45张完整布局对照页**，逐张检查并绑定最终图片哈希。`Scale_H01_...` 到 `Scale_H42_...` 及 `Scale_D01_...` 到 `Scale_D03_...` 是新模板编号；相同方法的档位／布局没有重复计为新方法。

所有示例均为明确标记的公开软件绘图测试数据。历史输入逐字节保留，三维新数据是作者构造的坐标／规则网格／帧序列。没有组学推断、模型训练、拓扑推测、分子动力学、体分割或真实生物学效应验证。绘图实现、数值编码检查、作者逐图屏幕自检、独立审美评审和真实科学验收分别记录。

每份当前单图有相对路径 FigureSpec、准确 TSV、PNG／SVG／PDF。轨迹另有真实 GIF、无联网请求的 HTML 播放页与帧时间 JSON。组装页提供实际 SVG／PNG 及可编辑 `layout.request.json`，保留两份完整源图、独立图例、坐标和标签。旧图、原编号、雷达、三维曲面和经典函数调用继续保留。

## 直接调用

以下命令从 skill 的 `scripts` 目录运行；输出目录必须是新目录。

```text
python workbench.py visual-template --entry H02_forest --output example-forest
python workbench.py plan --spec example-forest/example.spec.json --output example-forest/plan.json
python workbench.py render --plan example-forest/plan.json --output example-forest-export

python workbench.py visual-template --entry D01_Scatter3D --output example-3d
python workbench.py visual-template --entry D02_Volume_Custom --output example-volume
python workbench.py visual-template --entry D03_Trajectory --output example-frames

python workbench.py visual-template --entry Scale_H02_forest_Medium --output example-scale-forest
python workbench.py visual-template --entry Scale_D02_Volume_Custom --output example-camera-volume
```

`visual-template` 复制真实模板与输入，不执行推断。新数据须更新输入哈希、单位、来源、参数和图号，再生成新计划、渲染、逐张检查。默认与 `_Custom` 使用相同冻结输入；`_Small` 是明确独立的数据量示例。命令、文件及图片存在不自动授予科学或美观验收。

## 自定义布局与完整组装

- 三维／轨迹单图支持 `columns`、`rows`、`width`、`panel_height`；行数不够容纳全部面板时拒绝请求，不截断数据。相机、投影、切片、关键帧也是显式参数。
- 历史配方沿用各自的 `size`、顺序和标签参数；FigureSpec 的 `layout.width_inches`、`layout.height_inches` 调整物理版面。阅读策略可能扩大最终画布以容纳全部标签，实际尺寸写入导出记录，不假装严格等于请求尺寸。
- 密集活动矩阵提供150行全标签长页和紧凑全数值页；后者明确 `row_label_mode='none'`。没有删掉行或值。列显示别名逐一声明，原始ID仍在 TSV。
- 组装示例为每种方法比较同一输入的两幅完整单图；不同布局收在同一方法内。`columns`、`canvas_width_pt`、`packing`、`gap_pt`、`padding_pt` 可改。使用 `workbench.py layout-plan --request <layout.request.json> --output <fresh-plan.json>`，再 `layout-export --plan <fresh-plan.json> --output <fresh-directory>`；编辑请求或源图后重建计划。
- 字号测量不是美观性认可。每份最终 PNG 单独审阅，绑定 SHA256；换布局、标题、数据量或投稿尺寸后须重新检查。组合页支持原像素查看，宽／长页不可直接缩成期刊单栏并沿用审阅。

## 新增三维方法的输入契约

|入口|准确输入|实际实现与可调项|
|---|---|---|
|`figure_three_dimensional.plot_scatter3d`|`object_id, group, x, y, z`；唯一对象、有限数值、明确轴标签和坐标单位|1–8个明确仰角／方位角、正交投影、正交三维相机、完整对象与组计数、按物理范围设置箱体比例|
|`figure_three_dimensional.plot_volume_rendering`|`x, y, z, value`；完整均匀规则体素，明确单位、值域、透明度参考距离和传递结点|六个轴向方向及1–4个给定正交相机；有限预算的前向射线合成，物理步长修正透明度，三线性图像采样；中央切片与传递曲线。缺失体素拒绝，不补零；不是MIP、分割或交互三维网格|
|`figure_three_dimensional.plot_molecular_trajectory`|atom行：`frame_id,time,atom_id,element,chain,x,y,z`；bond行：`source_id,target_id`；2–240帧，元素C/N/O/S/H/P，严格递增时间|固定相机／全帧范围、选定关键帧、真实GIF、离线滑块和播放按钮。1–30 fps是展示速度；物理时间来自原表。键必须明确，所有帧原子身份一致，不拟合／对齐／重成像|

轨迹例子是虚构链，不冒充已识别蛋白。真实结构继续使用已有结构查看器核对链、残基、单位、拓扑和上游处理。所有大型计算保持已有服务器流程。

## 保留与改进的明确选项

经典调用默认保留。当前迁移与数据量示例按审阅选择：森林图 `presentation='table'`；状态及径向图 `numeric_guides=True`；多分类贡献／嵌入图谱／活动矩阵 `presentation='reading'`，同时保留 `classic`；跨组学视图的实际对象连线支持行列变化；等高线对比描边并保留边缘数字；训练诊断 `presentation='balanced'`；活动矩阵90度列名、完整行标签、独立模块条带和密度数值尺度。位点边界符号和给定参考始终保留。原值、分母、坐标和统计量不变。

## 参考及采用范围

代码为本项目独立实现，未复制第三方脚本或再分发模型／权重。采用 [Matplotlib 三维轴文档](https://matplotlib.org/stable/api/toolkits/mplot3d/axes3d.html)中明确相机和轴控制方式；依据 [Matplotlib 动画文档](https://matplotlib.org/stable/users/explain/animations/animations.html)把静态关键帧与动画导出分别验证。体值的颜色和透明度分别声明，参考 [Kitware 的体绘制说明](https://www.kitware.com/new-in-paraview-5-9-volume-rendering-with-a-separate-opacity-array/)中的通道区分；本项目实现有限轴向与给定正交相机合成，没有集成ParaView／VTK后端。

## 42 项保留映射

下表由冻结基线与已导出示例核对；每行另有 `_Custom` 和 `_Composition` 示例。原编号仍指向原历史归档，当前调用使用新增稳定ID。

|原编号|当前ID|当前绘图函数|
|---|---|---|
|`E40`|`H01_branch_tree`|`figure_biomni_views.plot_branch_tree`|
|`P19a`|`H02_forest`|`figure_core.plot_forest`|
|`P08`|`H03_volcano`|`figure_core.plot_volcano`|
|`P12a`|`H04_heatmap`|`figure_core.plot_heatmap`|
|`AUX_paired`|`H05_paired`|`figure_extensions.plot_paired`|
|`P14`|`H06_effect_matrix`|`figure_extensions.plot_effect_matrix`|
|`P33`|`H07_xy_points`|`figure_general.plot_xy_points`|
|`P34`|`H08_grouped_estimates`|`figure_general.plot_grouped_estimates`|
|`P36`|`H09_confusion_counts`|`figure_general.plot_confusion_counts`|
|`E35`|`H10_split_metric_matrix`|`figure_linked_evidence.plot_split_metric_matrix`|
|`E36`|`H11_hierarchy_tracks`|`figure_linked_evidence.plot_hierarchy_tracks`|
|`E37`|`H12_radial_hierarchy`|`figure_linked_evidence.plot_radial_hierarchy`|
|`AUX_c37_terms`|`H13_stacked_values`|`figure_linked_evidence.plot_stacked_values`|
|`E01`|`H14_enrichment_grid`|`figure_method_extensions.plot_enrichment_grid`|
|`E06a`|`H15_term_key`|`figure_method_extensions.plot_term_key`|
|`E19`|`H16_bivariate_tiles`|`figure_method_extensions.plot_bivariate_tiles`|
|`P21a`|`H17_cohort_intervals`|`figure_multimodal.plot_cohort_intervals`|
|`P18`|`H18_association_matrix`|`figure_multimodal.plot_association_matrix`|
|`P27`|`H19_calibration_counts`|`figure_multimodal.plot_calibration_counts`|
|`M01`|`H20_cross_effects`|`figure_multiomics_views.plot_cross_effects`|
|`M04`|`H21_aligned_views`|`figure_multiomics_views.plot_aligned_views`|
|`M08`|`H22_genomic_links`|`figure_multiomics_views.plot_genomic_links`|
|`E29`|`H23_locus_tracks`|`figure_multiscale.plot_locus_tracks`|
|`E32`|`H24_uncertainty_fan`|`figure_multiscale.plot_uncertainty_fan`|
|`N01`|`H25_typed_network`|`figure_network_extensions.plot_typed_network`|
|`N07`|`H26_multistate_matrix`|`figure_network_extensions.plot_multistate_matrix`|
|`N08`|`H27_running_enrichment`|`figure_network_extensions.plot_running_enrichment`|
|`N11`|`H28_contour_field`|`figure_network_extensions.plot_contour_field`|
|`R24`|`H29_process_dashboard`|`figure_process_dashboard.plot_process_dashboard`|
|`P26a`|`H30_publication_curve`|`figure_publication.plot_publication_curve`|
|`P16a`|`H31_aligned_matrix`|`figure_publication.plot_aligned_matrix`|
|`R07`|`H32_mantel_matrix`|`figure_reference.plot_mantel_matrix`|
|`R10`|`H33_contribution_swarm`|`figure_reference.plot_contribution_swarm`|
|`R18`|`H34_pca_reference`|`figure_reference.plot_pca_reference`|
|`R03`|`H35_state_dashboard`|`figure_reference.plot_state_dashboard`|
|`R11`|`H36_multiclass_contributions`|`figure_reference.plot_multiclass_contributions`|
|`R04`|`H37_embedding_atlas`|`figure_reference.plot_embedding_atlas`|
|`R14`|`H38_training_dashboard`|`figure_reference.plot_training_dashboard`|
|`R15`|`H39_activity_dashboard`|`figure_reference.plot_activity_dashboard`|
|`R16`|`H40_effect_distribution_forest`|`figure_reference.plot_effect_distribution_forest`|
|`R20`|`H41_facet_bubble_matrix`|`figure_reference.plot_facet_bubble_matrix`|
|`P10`|`H42_volcano_marginal`|`figure_styles.plot_volcano_marginal`|
