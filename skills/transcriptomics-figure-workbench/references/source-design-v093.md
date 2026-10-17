# 原图参考到代码与实际示例 · v0.9.3

90个合并图型均有实际查看过的原图或作者示例参考。新增34条来源，连同上一版8条图形记录共42条；一条来源可能包含数幅图。优先近两年的研究图，必要时采用更早且解释清楚的作者示例。相关组件、尺度或反面例子的借鉴不冒充同图型原图。

本轮96个单图视图、261个三档数据量变体、48个完整面板布局共405份最终PNG已经逐张自检。单图中的87种原生图型、7个同型扩展、2个固定参考图，加上组图布局构成90个基础条目。没有增加90套算法。保留已有优点的画法也重新出图检查，不为凑数量改写。

[当前完整单图与可运行配置](../assets/source-gallery/index.html) · [精确验收边界](validation-v093.md) · [90项机器可读映射](source-design-v093.json)

## 使用顺序

先判断研究问题、独立单位和现有结果字段，再选图型与一个必要扩展；随后明确顺序、尺度、颜色语义和物理布局。原生示例目录中的 `example.spec.json` 可以经统一 `plan`、`render` 接口复现。三档数据量示例和48种布局在仓库 `examples/source-v093/`，其参数及输入同样可检查。

对密集带符号网络优先矩阵，明确遮罩未报告单元；小网络保留圆形扩展。二维完整网格优先于遮挡的三维曲面。组成分面对比保留统一100%分母；ROC/PR可用分面和供应区间，示例供应界限不是置信区间。径向图不替代精确的线性效应比较。单图或组图换数据、标签、尺寸、行列后重新审图。

## 每种图的实现与实例

| 基础图型 | 已查看来源编号 | 实际实现 | 完整示例 |
|---|---|---|---|
| 热图 · `heatmap` | [nicheformer](#nicheformer), [total-rna](#total-rna), [compass-survival](#compass-survival), [gbp2-network](#gbp2-network), [droplet-hic](#droplet-hic), [retina-rna-atac](#retina-rna-atac) | [figure_polish.plot_polished_matrix](../scripts/figure_polish.py) | [打开](../assets/source-gallery/heatmap/heatmap.svg) |
| 点阵与气泡矩阵 · `dot-matrix` | [skin-atlas](#skin-atlas), [total-rna](#total-rna), [cortical-grn](#cortical-grn) | [figure_core.plot_dot](../scripts/figure_core.py) | [打开](../assets/source-gallery/dot-matrix/dot-matrix.svg) |
| 效应与区间森林图 · `forest` | [gbp2-network](#gbp2-network), [wilke-uncertainty](#wilke-uncertainty) | [figure_publication.plot_publication_forest](../scripts/figure_publication.py) | [打开](../assets/source-gallery/forest/forest.svg) |
| 火山图 · `volcano` | [nicheformer](#nicheformer) | [figure_styles.plot_volcano_editorial](../scripts/figure_styles.py) | [打开](../assets/source-gallery/volcano/volcano.svg) |
| GSEA 富集曲线 · `gsea` | [gbp2-network](#gbp2-network) | [refined](../scripts/figure_refined_views.py) | [打开](../assets/source-gallery/gsea/gsea.svg) |
| 富集结果点线图 · `enrichment-summary` | [total-rna](#total-rna), [gbp2-network](#gbp2-network) | [figure_styles.plot_enrichment_lollipop](../scripts/figure_styles.py) | [打开](../assets/source-gallery/enrichment-summary/enrichment-summary.svg) |
| 通路环形效应图 · `term-circle` | [circular-bars](#circular-bars) | [figure_method_extensions.plot_term_effect_circle](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/term-circle/term-circle.svg) |
| 配对观测图 · `paired` | [wilke-associations](#wilke-associations) | [editorial](../scripts/figure_editorial.py) | [打开](../assets/source-gallery/paired/paired.svg) |
| 观测与区间图 · `point-interval` | [compass-benchmark](#compass-benchmark), [cytometric-gating](#cytometric-gating), [wilke-distributions](#wilke-distributions), [wilke-uncertainty](#wilke-uncertainty) | [figure_styles.plot_sample_distribution](../scripts/figure_styles.py) | [打开](../assets/source-gallery/point-interval/point-interval.svg) |
| 雨云与半眼分布 · `raincloud` | [wilke-distributions](#wilke-distributions) | [figure_publication.plot_raincloud](../scripts/figure_publication.py) | [打开](../assets/source-gallery/raincloud/raincloud.svg) |
| 箱线图 · `box` | [droplet-hic](#droplet-hic), [cytometric-gating](#cytometric-gating), [wilke-distributions](#wilke-distributions) | [figure_core.plot_qc](../scripts/figure_core.py) | [打开](../assets/source-gallery/box/box.svg) |
| 小提琴图 · `violin` | [total-rna](#total-rna), [droplet-hic](#droplet-hic), [wilke-distributions](#wilke-distributions) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/violin/violin.svg) |
| 嵌入与主成分散点 · `embedding` | [skin-atlas](#skin-atlas), [total-rna](#total-rna), [bonsai](#bonsai) | [figure_core.plot_embedding](../scripts/figure_core.py) | [打开](../assets/source-gallery/embedding/embedding.svg) |
| 特征着色嵌入图 · `feature-embedding` | [total-rna](#total-rna), [bonsai](#bonsai), [retina-rna-atac](#retina-rna-atac) | [figure_publication.plot_feature_facets](../scripts/figure_publication.py) | [打开](../assets/source-gallery/feature-embedding/feature-embedding.svg) |
| 散点与给定趋势 · `scatter` | [nuclear-space](#nuclear-space), [total-rna](#total-rna), [finemap-calibration](#finemap-calibration), [cytometric-gating](#cytometric-gating), [wilke-distributions](#wilke-distributions) | [figure_core.plot_samples](../scripts/figure_core.py) | [打开](../assets/source-gallery/scatter/scatter.svg) |
| 曲线与给定区间带 · `ribbon` | [compass-survival](#compass-survival), [wilke-uncertainty](#wilke-uncertainty), [wilke-time](#wilke-time) | [figure_multimodal.plot_frozen_dynamics](../scripts/figure_multimodal.py) | [打开](../assets/source-gallery/ribbon/ribbon.svg) |
| 有序曲线与剖面 · `profile` | [nicheformer](#nicheformer), [total-rna](#total-rna), [droplet-hic](#droplet-hic), [wilke-time](#wilke-time) | [clarity](../scripts/figure_clarity_views.py) | [打开](../assets/source-gallery/profile/profile.svg) |
| 分组柱状图 · `bars` | [compass-benchmark](#compass-benchmark), [cortical-grn](#cortical-grn), [wilke-proportions](#wilke-proportions) | [figure_polish.plot_availability_counts](../scripts/figure_polish.py) | [打开](../assets/source-gallery/bars/bars.svg) |
| 堆叠与组成柱状图 · `stacked` | [gbp2-network](#gbp2-network), [cortical-grn](#cortical-grn), [wilke-proportions](#wilke-proportions) | [figure_core.plot_composition](../scripts/figure_core.py) | [打开](../assets/source-gallery/stacked/stacked.svg) |
| 环形组成图 · `donut` | [apobec-rainfall](#apobec-rainfall), [wilke-proportions](#wilke-proportions) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/donut/donut.svg) |
| 直方图与频数轮廓 · `histogram` | [wilke-ecdf](#wilke-ecdf) | [figure_general.plot_binned_distribution](../scripts/figure_general.py) | [打开](../assets/source-gallery/histogram/histogram.svg) |
| 山脊分布图 · `ridges` | [wilke-distributions](#wilke-distributions) | [figure_general.plot_density_ridges](../scripts/figure_general.py) | [打开](../assets/source-gallery/ridges/ridges.svg) |
| ROC 曲线 · `roc` | [sklearn-roc](#sklearn-roc) | [figure_core.plot_curve](../scripts/figure_core.py) | [打开](../assets/source-gallery/roc/roc.svg) |
| 精确率与召回曲线 · `precision-recall` | [sklearn-pr](#sklearn-pr) | [figure_core.plot_curve](../scripts/figure_core.py) | [打开](../assets/source-gallery/precision-recall/precision-recall.svg) |
| 校准曲线与样本支持 · `calibration` | [finemap-calibration](#finemap-calibration), [sklearn-roc](#sklearn-roc) | [figure_core.plot_curve](../scripts/figure_core.py) | [打开](../assets/source-gallery/calibration/calibration.svg) |
| 关系网络 · `network` | [ms2crossion](#ms2crossion) | [figure_reference.plot_signed_network](../scripts/figure_reference.py) | [打开](../assets/source-gallery/network/network.svg) |
| 弦图 · `chord` | [circlize](#circlize) | [figure_network_extensions.plot_weighted_chord](../scripts/figure_network_extensions.py) | [打开](../assets/source-gallery/chord/chord.svg) |
| 成员连线与带状图 · `membership-links` | [wilke-nested](#wilke-nested) | [figure_linked_evidence.plot_membership_ribbons](../scripts/figure_linked_evidence.py) | [打开](../assets/source-gallery/membership-links/membership-links.svg) |
| 流向与桑基图 · `flow` | [wilke-nested](#wilke-nested) | [figure_network_extensions.plot_alluvial](../scripts/figure_network_extensions.py) | [打开](../assets/source-gallery/flow/flow.svg) |
| 集合交集图 · `upset` | [complex-upset](#complex-upset) | [figure_network_extensions.plot_upset](../scripts/figure_network_extensions.py) | [打开](../assets/source-gallery/upset/upset.svg) |
| 双集合重叠图 · `venn` | [gbp2-network](#gbp2-network), [complex-upset](#complex-upset) | [figure_method_extensions.plot_two_set_overlap](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/venn/venn.svg) |
| 相关矩阵 · `correlation` | [nuclear-space](#nuclear-space), [retina-rna-atac](#retina-rna-atac), [wilke-associations](#wilke-associations) | [figure_reference.plot_ellipse_correlation](../scripts/figure_reference.py) | [打开](../assets/source-gallery/correlation/correlation.svg) |
| 联合散点与边际分布 · `joint` | [ms2crossion](#ms2crossion) | [figure_reference.plot_joint_reference](../scripts/figure_reference.py) | [打开](../assets/source-gallery/joint/joint.svg) |
| 排名轨迹与范围 · `rank` | [wilke-time](#wilke-time), [wilke-associations](#wilke-associations) | [figure_network_extensions.plot_rank_bump](../scripts/figure_network_extensions.py) | [打开](../assets/source-gallery/rank/rank.svg) |
| 门控散点 · `gating` | [cytometric-gating](#cytometric-gating) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/gating/gating.svg) |
| 环带剖面图 · `annular` | [circular-bars](#circular-bars) | [figure_reference.plot_annular_profile](../scripts/figure_reference.py) | [打开](../assets/source-gallery/annular/annular.svg) |
| 贡献蜂群图 · `contribution` | [shap-beeswarm](#shap-beeswarm) | [clarity](../scripts/figure_clarity_views.py) | [打开](../assets/source-gallery/contribution/contribution.svg) |
| 效应分布与区间 · `effect-distribution` | [wilke-uncertainty](#wilke-uncertainty) | [clarity](../scripts/figure_clarity_views.py) | [打开](../assets/source-gallery/effect-distribution/effect-distribution.svg) |
| 配准空间图 · `spatial` | [nuclear-space](#nuclear-space), [nicheformer](#nicheformer), [gbp2-network](#gbp2-network) | [figure_multiscale.plot_spatial_overlay](../scripts/figure_multiscale.py) | [打开](../assets/source-gallery/spatial/spatial.svg) |
| 切片叠加 · `slice` | [nuclear-space](#nuclear-space), [wilke-panels](#wilke-panels) | [figure_biomni_views.plot_slice_overlay](../scripts/figure_biomni_views.py) | [打开](../assets/source-gallery/slice/slice.svg) |
| 配准检查 · `registration` | [wilke-panels](#wilke-panels) | [figure_biomni_views.plot_registration_check](../scripts/figure_biomni_views.py) | [打开](../assets/source-gallery/registration/registration.svg) |
| 层次与分支树 · `hierarchy` | [gbp2-network](#gbp2-network), [bonsai](#bonsai), [wilke-nested](#wilke-nested) | [figure_multiscale.plot_hierarchy_partition](../scripts/figure_multiscale.py) | [打开](../assets/source-gallery/hierarchy/hierarchy.svg) |
| 坐标与基因组轨道 · `interval-tracks` | [nuclear-space](#nuclear-space), [droplet-hic](#droplet-hic), [migraine-finemap](#migraine-finemap), [retina-rna-atac](#retina-rna-atac) | [figure_multimodal.plot_interval_tracks](../scripts/figure_multimodal.py) | [打开](../assets/source-gallery/interval-tracks/interval-tracks.svg) |
| 二维密度与等高场 · `field` | [temporal-fields](#temporal-fields) | [figure_network_extensions.plot_hex_density](../scripts/figure_network_extensions.py) | [打开](../assets/source-gallery/field/field.svg) |
| 事件状态矩阵 · `state-matrix` | [compass-benchmark](#compass-benchmark), [wilke-panels](#wilke-panels) | [figure_polish.plot_recorded_evidence](../scripts/figure_polish.py) | [打开](../assets/source-gallery/state-matrix/state-matrix.svg) |
| 双条件分数与差值 · `scores` | [wilke-associations](#wilke-associations) | [figure_extensions.plot_score_comparison](../scripts/figure_extensions.py) | [打开](../assets/source-gallery/scores/scores.svg) |
| 参考配色 · `palettes` | [skin-atlas](#skin-atlas), [wilke-panels](#wilke-panels) | [fixed reference or complete-SVG layout](https://github.com/BoteXu/transcriptomics-figure-workbench/blob/main/tools/package_source_audit.py) | [打开](../assets/source-gallery/palettes/palettes.svg) |
| 分子结构展示 · `structures` | [ms2crossion](#ms2crossion), [wilke-panels](#wilke-panels) | [fixed reference or complete-SVG layout](https://github.com/BoteXu/transcriptomics-figure-workbench/blob/main/tools/package_source_audit.py) | [打开](../assets/source-gallery/structures/structures.svg) |
| 决策曲线 · `decision` | [wilke-panels](#wilke-panels) | [clarity](../scripts/figure_clarity_views.py) | [打开](../assets/source-gallery/decision/decision.svg) |
| 生存曲线与风险人数 · `survival` | [compass-survival](#compass-survival) | [figure_method_extensions.plot_survival_result](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/survival/survival.svg) |
| 地图数值展示 · `maps` | [wilke-maps](#wilke-maps) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/maps/maps.svg) |
| 地理连线 · `geographic-links` | [wilke-maps](#wilke-maps) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/geographic-links/geographic-links.svg) |
| 雷达剖面 · `radar` | [compass-survival](#compass-survival), [circular-bars](#circular-bars) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/radar/radar.svg) |
| 对象示意图 · `object-schematic` | [compass-benchmark](#compass-benchmark), [ms2crossion](#ms2crossion), [wilke-panels](#wilke-panels) | [figure_palette_applications.plot_palette_plate](../scripts/figure_palette_applications.py) | [打开](../assets/source-gallery/object-schematic/object-schematic.svg) |
| MA 图 · `ma` | [wilke-associations](#wilke-associations) | [figure_qc_de.plot_frozen_qc_de](../scripts/figure_qc_de.py) | [打开](../assets/source-gallery/ma/ma.svg) |
| 径向效应图 · `radial-effects` | [circular-bars](#circular-bars) | [figure_qc_de.plot_frozen_qc_de](../scripts/figure_qc_de.py) | [打开](../assets/source-gallery/radial-effects/radial-effects.svg) |
| 效应排序图 · `ranked-effects` | [wilke-associations](#wilke-associations) | [figure_qc_de.plot_frozen_qc_de](../scripts/figure_qc_de.py) | [打开](../assets/source-gallery/ranked-effects/ranked-effects.svg) |
| 马赛克图 · `mosaic` | [wilke-nested](#wilke-nested) | [mosaic_counts](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/mosaic/mosaic.svg) |
| 计数方格 · `waffle` | [wilke-uncertainty](#wilke-uncertainty) | [waffle_counts](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/waffle/waffle.svg) |
| 地平线剖面 · `horizon` | [wilke-time](#wilke-time) | [horizon_series](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/horizon/horizon.svg) |
| 有序连线散点 · `connected-scatter` | [wilke-time](#wilke-time) | [connected_scatter](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/connected-scatter/connected-scatter.svg) |
| 镜像柱图 · `mirrored-bars` | [compass-benchmark](#compass-benchmark) | [mirrored_bars](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/mirrored-bars/mirrored-bars.svg) |
| 基因组降雨图 · `rainfall` | [apobec-rainfall](#apobec-rainfall) | [genomic_rainfall](../scripts/figure_expanded_grammar.py) | [打开](../assets/source-gallery/rainfall/rainfall.svg) |
| 多面板拼版 · `composition` | [skin-atlas](#skin-atlas), [nuclear-space](#nuclear-space), [nicheformer](#nicheformer), [total-rna](#total-rna), [finemap-calibration](#finemap-calibration), [compass-benchmark](#compass-benchmark), [compass-survival](#compass-survival), [gbp2-network](#gbp2-network), [cortical-grn](#cortical-grn), [wilke-proportions](#wilke-proportions), [wilke-panels](#wilke-panels) | [fixed reference or complete-SVG layout](../scripts/figure_workbench/layout.py) | [组图实例](https://github.com/BoteXu/transcriptomics-figure-workbench/tree/main/examples/source-v093/layout) |
| 分位数对照图 · `qq` | [wilke-ecdf](#wilke-ecdf) | [figure_method_extensions.plot_distribution_result](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/qq/qq.svg) |
| 残差诊断散点 · `residual-diagnostics` | [wilke-ecdf](#wilke-ecdf) | [figure_multiomics_views.plot_diagnostic_panel](../scripts/figure_multiomics_views.py) | [打开](../assets/source-gallery/residual-diagnostics/residual-diagnostics.svg) |
| 复合图与仪表板 · `dashboards` | [bonsai](#bonsai), [wilke-panels](#wilke-panels) | [figure_styles.plot_composition_panels](../scripts/figure_styles.py) | [打开](../assets/source-gallery/dashboards/dashboards.svg) |
| Residue confidence · `residue-confidence` | [fold-confidence](#fold-confidence) | [figure_multimodal.plot_residue_confidence](../scripts/figure_multimodal.py) | [打开](../assets/source-gallery/residue-confidence/residue-confidence.svg) |
| Parallel trials · `reference-parallel-trials` | [wilke-time](#wilke-time) | [figure_reference.plot_parallel_trials](../scripts/figure_reference.py) | [打开](../assets/source-gallery/reference-parallel-trials/reference-parallel-trials.svg) |
| Group beeswarm · `reference-group-beeswarm` | [wilke-distributions](#wilke-distributions) | [figure_reference.plot_group_beeswarm](../scripts/figure_reference.py) | [打开](../assets/source-gallery/reference-group-beeswarm/reference-group-beeswarm.svg) |
| Strip effects · `reference-strip-effects` | [cortical-grn](#cortical-grn) | [figure_reference.plot_strip_effects](../scripts/figure_reference.py) | [打开](../assets/source-gallery/reference-strip-effects/reference-strip-effects.svg) |
| Aligned tracks · `reference-aligned-tracks` | [retina-rna-atac](#retina-rna-atac), [wilke-panels](#wilke-panels) | [figure_reference.plot_aligned_tracks](../scripts/figure_reference.py) | [打开](../assets/source-gallery/reference-aligned-tracks/reference-aligned-tracks.svg) |
| Surface grid · `reference-surface-grid` | [temporal-fields](#temporal-fields) | [figure_reference.plot_surface_grid](../scripts/figure_reference.py) | [打开](../assets/source-gallery/reference-surface-grid/reference-surface-grid.svg) |
| Distribution ecdf · `distribution-ecdf` | [wilke-ecdf](#wilke-ecdf) | [figure_method_extensions.plot_distribution_result](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/distribution-ecdf/distribution-ecdf.svg) |
| Covariate balance · `covariate-balance` | [cobalt-love](#cobalt-love) | [figure_method_extensions.plot_balance](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/covariate-balance/covariate-balance.svg) |
| Bland altman supplied · `bland-altman-supplied` | [statsmodels-agreement](#statsmodels-agreement) | [figure_method_extensions.plot_agreement](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/bland-altman-supplied/bland-altman-supplied.svg) |
| Swimmer followup · `swimmer-followup` | [apobec-rainfall](#apobec-rainfall), [swimplot](#swimplot) | [figure_method_extensions.plot_swimmer](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/swimmer-followup/swimmer-followup.svg) |
| Specification curve · `specification-curve` | [specification-original](#specification-original) | [figure_method_extensions.plot_specification_curve](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/specification-curve/specification-curve.svg) |
| Supplied vector field · `supplied-vector-field` | [temporal-fields](#temporal-fields) | [figure_method_extensions.plot_vector_field](../scripts/figure_method_extensions.py) | [打开](../assets/source-gallery/supplied-vector-field/supplied-vector-field.svg) |
| Ternary composition · `ternary-composition` | [mpltern-axes](#mpltern-axes) | [figure_multiscale.plot_ternary_composition](../scripts/figure_multiscale.py) | [打开](../assets/source-gallery/ternary-composition/ternary-composition.svg) |
| Genome association overview · `genome-association-overview` | [migraine-finemap](#migraine-finemap) | [figure_multiscale.plot_genome_overview](../scripts/figure_multiscale.py) | [打开](../assets/source-gallery/genome-association-overview/genome-association-overview.svg) |
| Funnel supplied results · `funnel-supplied-results` | [wilke-uncertainty](#wilke-uncertainty) | [figure_multiscale.plot_funnel_result](../scripts/figure_multiscale.py) | [打开](../assets/source-gallery/funnel-supplied-results/funnel-supplied-results.svg) |
| Feature correlation projection · `feature-correlation-projection` | [wilke-associations](#wilke-associations) | [figure_multiomics_views.plot_loading_projection](../scripts/figure_multiomics_views.py) | [打开](../assets/source-gallery/feature-correlation-projection/feature-correlation-projection.svg) |
| Mass spectrum mirror · `mass-spectrum-mirror` | [ms2crossion](#ms2crossion) | [figure_multiomics_views.plot_mass_spectrum](../scripts/figure_multiomics_views.py) | [打开](../assets/source-gallery/mass-spectrum-mirror/mass-spectrum-mirror.svg) |
| Pathway quantity overlay · `pathway-quantity-overlay` | [pathview-original](#pathview-original) | [figure_multiomics_views.plot_pathway_overlay](../scripts/figure_multiomics_views.py) | [打开](../assets/source-gallery/pathway-quantity-overlay/pathway-quantity-overlay.svg) |
| Coverage, splice junctions and isoforms · `splice-tracks` | [ggtranscript-junction](#ggtranscript-junction) | [figure_analysis_results.plot_splice_tracks](../scripts/figure_analysis_results.py) | [打开](../assets/source-gallery/splice-tracks/splice-tracks.svg) |
| Variant posteriors across supplied signals · `variant-posteriors` | [migraine-finemap](#migraine-finemap) | [figure_analysis_results.plot_variant_posteriors](../scripts/figure_analysis_results.py) | [打开](../assets/source-gallery/variant-posteriors/variant-posteriors.svg) |
| Complete signed contributions to one score · `contribution-waterfall` | [shap-waterfall](#shap-waterfall) | [figure_analysis_results.plot_contribution_waterfall](../scripts/figure_analysis_results.py) | [打开](../assets/source-gallery/contribution-waterfall/contribution-waterfall.svg) |
| Position-wise sequence logo · `sequence-logo` | [logomaker](#logomaker) | [figure_biomni_views.plot_sequence_logo](../scripts/figure_biomni_views.py) | [打开](../assets/source-gallery/sequence-logo/sequence-logo.svg) |
| Physical contact bins and aligned signal tracks · `contact-tracks` | [droplet-hic](#droplet-hic) | [figure_biomni_views.plot_contact_tracks](../scripts/figure_biomni_views.py) | [打开](../assets/source-gallery/contact-tracks/contact-tracks.svg) |

## 来源、采用和舍弃

<a id="skin-atlas"></a>

### Human skin fibroblast single-cell and spatial atlas

[原始来源](https://www.nature.com/articles/s41590-025-02267-8/figures/1)

- 采用：One primary embedding, persistent identity colours, marker blocks labelled by identity, wide cross-population evidence lane.
- 舍弃或边界：Do not reproduce tiny marker labels or put every subgroup feature map in the overview. Split detailed reading pages.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="nuclear-space"></a>

### Cell-type-specific nuclear compartments from spatial multi-omics

[原始来源](https://www.nature.com/articles/s41586-025-08838-x/figures/2)

- 采用：Overview to explicitly selected region to orthogonal quantitative support; align physical coordinate tracks and retain modality-specific units.
- 舍弃或边界：No invented image evidence or inferred registration. A cell count is not a biological replicate count. Dense image and track detail needs a separate page.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="nicheformer"></a>

### Nicheformer single-cell and spatial omics foundation model

[原始来源](https://www.nature.com/articles/s41592-025-02814-z/figures/3)

- 采用：Rows follow a question; relate attention summaries to spatial context and selected effects. Align related matrices and make their separate ranges explicit.
- 舍弃或边界：Avoid neon identity colours and repeated panels with no additional question. The paper's red/blue gene classes must not be mistaken for up/down regulation.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="total-rna"></a>

### Scalable single-cell total RNA sequencing

[原始来源](https://www.nature.com/articles/s41587-026-03068-6/figures/3)

- 采用：Named continuous ordering, stable state colours, selected-gene facets and enrichment summary with explicit member support.
- 舍弃或边界：Do not compare per-gene 0–1 values as absolute expression. No LOWESS or new scoring is fitted for styling. Reject crowded gene-program labels and significance-star piles.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="finemap-calibration"></a>

### Genome-wide fine-mapping calibration

[原始来源](https://www.nature.com/articles/s41588-026-02549-3/figures/2)

- 采用：Equal x/y ranges and a visible identity reference; rows indicate scenarios and columns comparison families.
- 舍弃或边界：Avoid red/green-only contrasts and repeated small legends. Do not label these PIP calibration simulations as clinical-risk calibration.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="compass-benchmark"></a>

### COMPASS clinical-cohort evaluation

[原始来源](https://www.nature.com/articles/s41591-026-04502-7/figures/2)

- 采用：Keep cohort design visible beside held-out evaluation. Encode opposing transfer counts around a common baseline and identify comparator/reference results.
- 舍弃或边界：Do not default to dozens of narrow bars with vertical method names, rainbow cohort annotations or plots that confuse patient, cohort and training-seed replication.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="compass-survival"></a>

### COMPASS survival and tumour-immune profiles

[原始来源](https://www.nature.com/articles/s41591-026-04502-7/figures/5)

- 采用：Show survival uncertainty and effect intervals, preserve state labels across profiles, and group concepts by biological role.
- 舍弃或边界：Do not copy dense 16-axis radar layouts or rainbow continuous scales. Supply risk counts when available and check group labels against actual data. Polygon area is not an effect size.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="gbp2-network"></a>

### GBP2 module, enrichment and spatial evidence

[原始来源](https://www.nature.com/articles/s41467-025-67690-9/figures/1)

- 采用：Relate supplied module identities to module-trait estimates, enrichment and independent candidate support. Use the correct HR null and preserve the full source scope.
- 舍弃或边界：The crowded nine-part page and tiny spatial legends are unsuitable defaults. Retain full GSEA running score, hit positions and ranked metric when supplied; an enrichment curve alone is insufficient. One section is not replicated tissue evidence.
- 审阅范围：Original figure and caption; related components require contextual interpretation
- 代码与图片：No image or code copied; independently authored implementation

<a id="bonsai"></a>

### Bonsai / Nature Biotechnology

[原始来源](https://www.nature.com/articles/s41587-026-03220-2/figures/3)

- 采用：Whole-tree overview linked to a named local focus; persistent identity colours.
- 舍弃或边界：Do not refit a hyperbolic embedding or imply original tree coordinates.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="droplet-hic"></a>

### Droplet Hi-C / Nature Biotechnology

[原始来源](https://www.nature.com/articles/s41587-024-02447-1/figures/2)

- 采用：Physical coordinate alignment across contact, insulation and gene tracks; separate units.
- 舍弃或边界：Tiny enrichment labels and crowded ten-panel pages. Online 2024; 2025 issue is not a 2025 publication date.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="migraine-finemap"></a>

### Migraine fine mapping / Nature Communications

[原始来源](https://www.nature.com/articles/s41467-025-64880-3/figures/2)

- 采用：Full-width locus context above aligned source-specific posterior tracks on a common physical x axis.
- 舍弃或边界：Do not derive a causal posterior or new credible set from a drawing.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="cytometric-gating"></a>

### Automated cytometric gating / Nature Communications

[原始来源](https://www.nature.com/articles/s41467-025-56622-2/figures/4)

- 采用：Stored gates over full density and common comparison axes; show observations beside summaries.
- 舍弃或边界：Overpacked comparison pages and long tiny tilted labels; no gating engine called.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="ms2crossion"></a>

### MS2DeepScore cross-ion / Nature Communications

[原始来源](https://www.nature.com/articles/s41467-026-69083-y/figures/3)

- 采用：Network overview with readable local detail; mirror spectra around zero with explicit spectrum identity.
- 舍弃或边界：Do not copy the study edge threshold, infer peak matches or use tiny linked structures.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="retina-rna-atac"></a>

### Human retina RNA and ATAC / Nature Genetics

[原始来源](https://www.nature.com/articles/s41588-025-02454-1/figures/5)

- 采用：Block identities and physically aligned coverage, peaks and genes.
- 舍弃或边界：Overcompressed labels and rainbow dendrogram decoration. DOI year recorded; publication date not inferred.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="cortical-grn"></a>

### Cortical cell-fate regulatory networks / Nature

[原始来源](https://www.nature.com/articles/s41586-025-09997-7/figures/5)

- 采用：Aligned marker-fraction/mean matrix and identity-count sidebars; separate species and culture conditions.
- 舍弃或边界：Repeated tiny UMAPs and an overpacked ten-panel page; cells do not replace donors.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="temporal-fields"></a>

### Temporal tissue dynamics / Nature

[原始来源](https://www.nature.com/articles/s41586-025-09876-1/figures/2)

- 采用：Common scenario coordinates and visible vector heads; distinguish stable and unstable symbols.
- 舍弃或边界：No inferred streamlines, nullclines or fitted dynamics. Viewed publisher 685-pixel original preview; fine print not assessed.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="apobec-rainfall"></a>

### APOBEC3 mutagenesis / Nature Genetics / Extended Data 3

[原始来源](https://www.nature.com/articles/s41588-025-02187-1/figures/8)

- 采用：Shared genomic position, log inter-event distance, restrained background events, distinct event classes.
- 舍弃或边界：Do not infer clusters from appearance or carry mutation distances across chromosomes; whole figure is too dense for reuse.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="circular-bars"></a>

### Tobias Stadler / circular bar example

[原始来源](https://r-graph-gallery.com/web-circular-barplot-with-R-and-ggplot2.html)

- 采用：Keep a central hole, restrained colour, direct external labels and explicit secondary quantity.
- 舍弃或边界：Prefer aligned linear effects for precise comparisons; do not make radial area represent an unlabelled statistic.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="wilke-distributions"></a>

### Claus O. Wilke / Boxplots and violins

[原始来源](https://clauswilke.com/dataviz/boxplots-violins.html)

- 采用：Retain individual observations; categorical displacement changes no measurement; shared density x scale.
- 舍弃或边界：Do not estimate a new density or distribution from a polished contour.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-ecdf"></a>

### Claus O. Wilke / ECDF and quantile comparisons

[原始来源](https://clauswilke.com/dataviz/ecdf-qq.html)

- 采用：Related density and ECDF share a horizontal range; QQ uses an identity reference and complete tails.
- 舍弃或边界：A reference line does not establish normality; no automatic tail clipping.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-uncertainty"></a>

### Claus O. Wilke / Uncertainty displays

[原始来源](https://clauswilke.com/dataviz/visualizing-uncertainty.html)

- 采用：Nested intervals have an explicit hierarchy; retain estimates, reference values and exact count cells.
- 舍弃或边界：Do not fabricate intervals or a density; funnel usage borrows interval hierarchy, not a same-chart exemplar.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-proportions"></a>

### Claus O. Wilke / Proportion comparisons

[原始来源](https://clauswilke.com/dataviz/visualizing-proportions.html)

- 采用：Small multiples share a 0–100% scale with a pale full denominator.
- 舍弃或边界：Author-labelled bad stacked-middle-category example is a rejection example, not a recommendation.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-time"></a>

### Claus O. Wilke / Time series and connected scatter

[原始来源](https://clauswilke.com/dataviz/time-series.html)

- 采用：Name line endpoints directly; sparse milestones retain a traceable order.
- 舍弃或边界：Do not smooth stored vertices or treat an arbitrary order as time; parallel/horizon borrowing is related label design only.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-nested"></a>

### Claus O. Wilke / Nested proportions

[原始来源](https://clauswilke.com/dataviz/nested-proportions.html)

- 采用：Mosaic width retains denominators; conserved bands and ordered labelled nodes reduce lookup.
- 舍弃或边界：Author-labelled ugly parallel-sets plot is rejected. Do not inflate small or zero paths.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-associations"></a>

### Claus O. Wilke / Associations

[原始来源](https://clauswilke.com/dataviz/visualizing-associations.html)

- 采用：Explicit signed colour/area scales; direct slope endpoints; fixed comparison axes.
- 舍弃或边界：A projection is not causal evidence. MA borrowing concerns precise Cartesian comparisons, not a same-chart example.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-maps"></a>

### Claus O. Wilke / Geospatial displays

[原始来源](https://clauswilke.com/dataviz/geospatial-data.html)

- 采用：A restrained ordered scale and clearly declared coordinate/projection context.
- 舍弃或边界：Avoid aspect distortion; raw longitude/latitude links are not geodesics.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="wilke-panels"></a>

### Claus O. Wilke / Multi-panel figures

[原始来源](https://clauswilke.com/dataviz/multi-panel-figures.html)

- 采用：Weighted panel spans follow the question; persistent colours and one clear reading order; retain full standalone reading views.
- 舍弃或边界：Do not infer a shared cohort, axis or legend from mere adjacency. These are related layout references, not identical chart exemplars.
- 审阅范围：same_chart_or_component
- 代码与图片：Book CC BY-NC-ND: link and describe principles only; no image/code redistribution or adaptation. Workbench code independently authored.

<a id="logomaker"></a>

### Ammar Tareen and Justin B. Kinney / Logomaker examples

[原始来源](https://logomaker.readthedocs.io/en/latest/examples.html)

- 采用：Separate probability, bits and signed enrichment; explicit zero reference and highlighted supplied positions.
- 舍弃或边界：Do not replace a supplied height definition with information content or enable signed heights without an explicit contract.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="shap-beeswarm"></a>

### SHAP authors / beeswarm example

[原始来源](https://shap.readthedocs.io/en/stable/example_notebooks/api_examples/plots/beeswarm.html)

- 采用：Complete individual signed contributions, zero reference and separate supplied feature-value scale.
- 舍弃或边界：Do not silently sum unnamed features, refit a model or calculate attribution.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="shap-waterfall"></a>

### SHAP authors / waterfall example

[原始来源](https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/plots/waterfall.html)

- 采用：Exact signed component labels and explicit baseline-to-total accounting.
- 舍弃或边界：No new SHAP calculation, feature ranking or unlabelled residual term.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="complex-upset"></a>

### Michał Krassowski / ComplexUpset examples

[原始来源](https://krassowski.github.io/complex-upset/articles/Examples_R.html)

- 采用：Align exact intersection counts, binary membership and inclusive set totals; separate rows with faint bands.
- 舍弃或边界：Do not imply Venn circle areas are proportional; do not discard all-zero objects.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="cobalt-love"></a>

### Noah Greifer / cobalt Love plot

[原始来源](https://ngreifer.r-universe.dev/cobalt/doc/love.plot.html)

- 采用：Complete covariate names, declared thresholds, redundant shapes for adjustment stage and shared x scale.
- 舍弃或边界：Do not connect unrelated covariates as a continuous measurement, or declare balance from threshold alone.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="swimplot"></a>

### Jessica Weiss / Creating swimmer plots with ease

[原始来源](https://mirror.metanet.ch/cran/web/packages/swimplot/vignettes/Introduction.to.swimplot.html)

- 采用：Individual follow-up rows, explicit event symbols and complete guides; stratification can replace a dense page.
- 舍弃或边界：No manufactured response duration, treatment segments or ongoing arrows; source uses example data.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="circlize"></a>

### Zuguang Gu / advanced chord diagram labels and gaps

[原始来源](https://jokergoo.github.io/circlize_book/book/advanced-usage-of-chorddiagram.html)

- 采用：Separate sectors with controlled gaps, allow label room and retain an explicit weight key.
- 舍弃或边界：Do not infer direction or causality from ribbons; avoid red/green-only identity distinction.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="sklearn-pr"></a>

### scikit-learn authors / precision-recall examples

[原始来源](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

- 采用：Explicit staircase vertices, positive-class definition and a separately declared prevalence baseline.
- 舍弃或边界：Fold AP mean plus standard deviation is not a confidence interval. No AUC or curve fitting is performed.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="sklearn-roc"></a>

### scikit-learn authors / multiclass ROC examples

[原始来源](https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html)

- 采用：Unit-square comparison axes, chance/identity guide and redundant model line styles.
- 舍弃或边界：Do not invent AUC, micro/macro averaging or uncertainty. Calibration borrows axis design, not the same statistic.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="statsmodels-agreement"></a>

### statsmodels authors / mean-difference plot

[原始来源](https://www.statsmodels.org/stable/generated/statsmodels.graphics.agreement.mean_diff_plot.html)

- 采用：Separate labelled bias and agreement-limit guides over complete observations.
- 舍弃或边界：Agreement limits are not confidence intervals of the mean. Retain supplied bounds without estimation.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="mpltern-axes"></a>

### Yuji Ikeda / mpltern three coloured axes

[原始来源](https://mpltern.readthedocs.io/en/stable/gallery/axis_and_tick/98.colored_axes.html)

- 采用：Readable 0 to 1 ticks on all three component axes and faint guides.
- 舍弃或边界：Do not infer a trajectory from unrelated example points; avoid strong coloured grids.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="ggtranscript-junction"></a>

### Dylan Zhang and collaborators / ggtranscript junction example

[原始来源](https://github.com/dzhang32/ggtranscript)

- 采用：Shared physical coordinates, named transcript lanes and supplied junction counts.
- 舍弃或边界：Do not shorten gaps without declaring a transformed axis or infer strand/isoform abundance.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="specification-original"></a>

### Simonsohn et al. / specification curve original Figure 2

[原始来源](https://www.nature.com/articles/s41562-020-0912-z/figures/2)

- 采用：Strict alignment of effect positions and declared model-decision cells.
- 舍弃或边界：Reject significance-coloured backgrounds and unreadable hundreds of labels. Viewed publisher original; screenshot edge truncation limits fine-print review.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation

<a id="fold-confidence"></a>

### Severe deviation in protein fold prediction / Scientific Reports Figure 1

[原始来源](https://www.nature.com/articles/s41598-025-89516-w/figures/1)

- 采用：Explicit 0 to 100 local confidence scale and separate structural comparisons.
- 舍弃或边界：This source shows structure colouring and PAE, not an identical residue-profile chart. Local confidence is not domain-orientation or binding evidence.
- 审阅范围：related_confidence_scale_and_structure_comparison
- 代码与图片：No image or code copied; original implementation

<a id="pathview-original"></a>

### Weijun Luo and Cory Brouwer / Pathview Figure 1

[原始来源](https://pmc.ncbi.nlm.nih.gov/articles/PMC3702256/)

- 采用：Keep physical map identity, a separate quantitative key and explicit edge meanings.
- 舍弃或边界：Reject unreadable tiny nodes and red/green-only contrast. A coloured abundance map does not establish flux or activation.
- 审阅范围：same_chart_or_component
- 代码与图片：No image or code copied; original implementation
