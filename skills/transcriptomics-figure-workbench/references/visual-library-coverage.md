# 综合绘图库：方法保留与覆盖范围

由实际目录和渲染器登记表生成。索引存在、代码存在、后端运行和视觉验收分别记录。

## 计数

- source_records: 1884
- actual_entries: 1334
- method_families: 83
- preserved_base_forms: 90
- historical_examples: 458
- galleries: 19
- removed_assets: 0
- registered_renderers: 133
- renderers_with_examples: 132
- delegating_wrappers: 1
- unaccounted_renderers: 0

90 个基础画法完整保留；相近画法作为83个父族中的具名扩展。19份目录含重叠来源，1884不是独立绘图方法数。

## 渲染器对照

|登记入口|现有 FigureSpec|历史／参考例|状态|
|---|---:|---:|---|
|`figure_analysis_evidence.plot_analysis_evidence`|425|0|CURRENT_SPEC|
|`figure_analysis_results.plot_splice_tracks`|2|1|CURRENT_SPEC|
|`figure_analysis_results.plot_variant_posteriors`|1|1|CURRENT_SPEC|
|`figure_analysis_results.plot_contribution_waterfall`|1|1|CURRENT_SPEC|
|`figure_annotation_views.plot_annotation_evidence`|34|0|CURRENT_SPEC|
|`figure_biomni_views.plot_sequence_logo`|1|1|CURRENT_SPEC|
|`figure_biomni_views.plot_contact_tracks`|1|1|CURRENT_SPEC|
|`figure_biomni_views.plot_branch_tree`|0|1|HISTORICAL_RECIPE|
|`figure_biomni_views.plot_slice_overlay`|1|3|CURRENT_SPEC|
|`figure_biomni_views.plot_registration_check`|1|3|CURRENT_SPEC|
|`figure_chapter_views.plot_transcriptomic_chapter`|89|0|CURRENT_SPEC|
|`figure_clarity_views.plot_clarity_views`|19|15|CURRENT_SPEC|
|`figure_coexpression_evidence.plot_coexpression_evidence`|27|0|CURRENT_SPEC|
|`figure_core.plot_embedding`|1|2|CURRENT_SPEC|
|`figure_core.plot_samples`|1|1|CURRENT_SPEC|
|`figure_core.plot_forest`|0|2|HISTORICAL_RECIPE|
|`figure_core.plot_volcano`|0|1|HISTORICAL_RECIPE|
|`figure_core.plot_dot`|2|2|CURRENT_SPEC|
|`figure_core.plot_heatmap`|0|5|HISTORICAL_RECIPE|
|`figure_core.plot_qc`|1|1|CURRENT_SPEC|
|`figure_core.plot_composition`|2|2|CURRENT_SPEC|
|`figure_core.plot_curve`|5|3|CURRENT_SPEC|
|`figure_editorial.plot_editorial`|7|9|CURRENT_SPEC|
|`figure_enrichment_story.plot_enrichment_story`|30|0|CURRENT_SPEC|
|`figure_expanded_grammar.plot_mosaic_counts`|2|1|CURRENT_SPEC|
|`figure_expanded_grammar.plot_waffle_counts`|2|1|CURRENT_SPEC|
|`figure_expanded_grammar.plot_horizon_series`|2|1|CURRENT_SPEC|
|`figure_expanded_grammar.plot_connected_scatter`|2|1|CURRENT_SPEC|
|`figure_expanded_grammar.plot_mirrored_bars`|2|1|CURRENT_SPEC|
|`figure_expanded_grammar.plot_genomic_rainfall`|2|1|CURRENT_SPEC|
|`figure_extensions.plot_paired`|0|1|HISTORICAL_RECIPE|
|`figure_extensions.plot_effect_matrix`|0|1|HISTORICAL_RECIPE|
|`figure_extensions.plot_annotated_heatmap`|6|1|CURRENT_SPEC|
|`figure_extensions.plot_score_comparison`|1|1|CURRENT_SPEC|
|`figure_general.plot_xy_points`|0|5|HISTORICAL_RECIPE|
|`figure_general.plot_grouped_estimates`|0|1|HISTORICAL_RECIPE|
|`figure_general.plot_binned_distribution`|1|1|CURRENT_SPEC|
|`figure_general.plot_confusion_counts`|0|1|HISTORICAL_RECIPE|
|`figure_general.plot_density_ridges`|1|2|CURRENT_SPEC|
|`figure_gsea.plot_gsea_tracks`|4|4|CURRENT_SPEC|
|`figure_gsea.plot_gsea_nes`|1|1|CURRENT_SPEC|
|`figure_gsea.plot_gsea_leading_edge`|1|1|CURRENT_SPEC|
|`figure_gsea.plot_ora_terms`|2|2|CURRENT_SPEC|
|`figure_integrated_views.plot_integrated_view`|35|0|CURRENT_SPEC|
|`figure_lineage_views.plot_lineage_view`|6|0|CURRENT_SPEC|
|`figure_linked_evidence.plot_membership_ribbons`|1|1|CURRENT_SPEC|
|`figure_linked_evidence.plot_split_metric_matrix`|0|1|HISTORICAL_RECIPE|
|`figure_linked_evidence.plot_hierarchy_tracks`|0|1|HISTORICAL_RECIPE|
|`figure_linked_evidence.plot_radial_hierarchy`|0|1|HISTORICAL_RECIPE|
|`figure_linked_evidence.plot_stacked_values`|0|2|HISTORICAL_RECIPE|
|`figure_method_extensions.plot_enrichment_grid`|0|1|HISTORICAL_RECIPE|
|`figure_method_extensions.plot_term_effect_circle`|1|4|CURRENT_SPEC|
|`figure_method_extensions.plot_term_key`|0|4|HISTORICAL_RECIPE|
|`figure_method_extensions.plot_two_set_overlap`|1|2|CURRENT_SPEC|
|`figure_method_extensions.plot_gene_term_chord`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_distribution_result`|2|2|CURRENT_SPEC|
|`figure_method_extensions.plot_balance`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_agreement`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_survival_result`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_swimmer`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_specification_curve`|1|1|CURRENT_SPEC|
|`figure_method_extensions.plot_vector_field`|2|1|CURRENT_SPEC|
|`figure_method_extensions.plot_bivariate_tiles`|0|1|HISTORICAL_RECIPE|
|`figure_multimodal.plot_cohort_intervals`|0|2|HISTORICAL_RECIPE|
|`figure_multimodal.plot_association_matrix`|0|1|HISTORICAL_RECIPE|
|`figure_multimodal.plot_calibration_counts`|0|2|HISTORICAL_RECIPE|
|`figure_multimodal.plot_interval_tracks`|1|1|CURRENT_SPEC|
|`figure_multimodal.plot_frozen_dynamics`|1|4|CURRENT_SPEC|
|`figure_multimodal.plot_residue_confidence`|1|1|CURRENT_SPEC|
|`figure_multiomics_views.plot_cross_effects`|0|1|HISTORICAL_RECIPE|
|`figure_multiomics_views.plot_aligned_views`|0|1|HISTORICAL_RECIPE|
|`figure_multiomics_views.plot_loading_projection`|1|1|CURRENT_SPEC|
|`figure_multiomics_views.plot_mass_spectrum`|1|1|CURRENT_SPEC|
|`figure_multiomics_views.plot_genomic_links`|0|1|HISTORICAL_RECIPE|
|`figure_multiomics_views.plot_pathway_overlay`|1|1|CURRENT_SPEC|
|`figure_multiomics_views.plot_diagnostic_panel`|5|4|CURRENT_SPEC|
|`figure_multiscale.plot_ternary_composition`|1|1|CURRENT_SPEC|
|`figure_multiscale.plot_genome_overview`|1|1|CURRENT_SPEC|
|`figure_multiscale.plot_locus_tracks`|0|1|HISTORICAL_RECIPE|
|`figure_multiscale.plot_funnel_result`|1|1|CURRENT_SPEC|
|`figure_multiscale.plot_hierarchy_partition`|1|1|CURRENT_SPEC|
|`figure_multiscale.plot_uncertainty_fan`|0|1|HISTORICAL_RECIPE|
|`figure_multiscale.plot_spatial_overlay`|1|2|CURRENT_SPEC|
|`figure_network_extensions.plot_typed_network`|0|8|HISTORICAL_RECIPE|
|`figure_network_extensions.plot_weighted_chord`|1|1|CURRENT_SPEC|
|`figure_network_extensions.plot_alluvial`|2|1|CURRENT_SPEC|
|`figure_network_extensions.plot_upset`|2|2|CURRENT_SPEC|
|`figure_network_extensions.plot_multistate_matrix`|0|2|HISTORICAL_RECIPE|
|`figure_network_extensions.plot_running_enrichment`|0|1|HISTORICAL_RECIPE|
|`figure_network_extensions.plot_rank_bump`|1|1|CURRENT_SPEC|
|`figure_network_extensions.plot_hex_density`|1|2|CURRENT_SPEC|
|`figure_network_extensions.plot_contour_field`|0|1|HISTORICAL_RECIPE|
|`figure_package_styles.plot_package_style`|27|27|CURRENT_SPEC|
|`figure_palette_applications.plot_palette_plate`|7|54|CURRENT_SPEC|
|`figure_palette_applications.plot_palette_panel`|0|0|DELEGATING_WRAPPER|
|`figure_polish.plot_polished_matrix`|1|3|CURRENT_SPEC|
|`figure_polish.plot_recorded_evidence`|1|3|CURRENT_SPEC|
|`figure_polish.plot_availability_counts`|1|1|CURRENT_SPEC|
|`figure_process_dashboard.plot_process_dashboard`|0|1|HISTORICAL_RECIPE|
|`figure_publication.plot_publication_curve`|0|2|HISTORICAL_RECIPE|
|`figure_publication.plot_aligned_matrix`|0|7|HISTORICAL_RECIPE|
|`figure_publication.plot_publication_forest`|1|5|CURRENT_SPEC|
|`figure_publication.plot_feature_facets`|4|3|CURRENT_SPEC|
|`figure_publication.plot_raincloud`|1|3|CURRENT_SPEC|
|`figure_publication_plus.plot_publication_plus`|3|3|CURRENT_SPEC|
|`figure_qc_de.plot_frozen_qc_de`|3|8|CURRENT_SPEC|
|`figure_reference.plot_annular_profile`|1|2|CURRENT_SPEC|
|`figure_reference.plot_ellipse_correlation`|1|1|CURRENT_SPEC|
|`figure_reference.plot_signed_network`|2|1|CURRENT_SPEC|
|`figure_reference.plot_mantel_matrix`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_parallel_trials`|1|1|CURRENT_SPEC|
|`figure_reference.plot_contribution_swarm`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_group_beeswarm`|1|1|CURRENT_SPEC|
|`figure_reference.plot_joint_reference`|1|3|CURRENT_SPEC|
|`figure_reference.plot_pca_reference`|0|2|HISTORICAL_RECIPE|
|`figure_reference.plot_state_dashboard`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_multiclass_contributions`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_embedding_atlas`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_training_dashboard`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_activity_dashboard`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_effect_distribution_forest`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_facet_bubble_matrix`|0|1|HISTORICAL_RECIPE|
|`figure_reference.plot_strip_effects`|1|1|CURRENT_SPEC|
|`figure_reference.plot_aligned_tracks`|1|1|CURRENT_SPEC|
|`figure_reference.plot_surface_grid`|2|1|CURRENT_SPEC|
|`figure_refined_views.plot_refined_views`|15|5|CURRENT_SPEC|
|`figure_study_overview.plot_transcriptomic_overview`|2|0|CURRENT_SPEC|
|`figure_styles.plot_volcano_editorial`|1|1|CURRENT_SPEC|
|`figure_styles.plot_volcano_marginal`|0|1|HISTORICAL_RECIPE|
|`figure_styles.plot_enrichment_lollipop`|1|2|CURRENT_SPEC|
|`figure_styles.plot_composition_panels`|5|1|CURRENT_SPEC|
|`figure_styles.plot_sample_distribution`|1|2|CURRENT_SPEC|
|`figure_wgcna_views.plot_wgcna_view`|32|0|CURRENT_SPEC|

## 全面性的边界

这份清单核对的是现有实现，不代表所有科学可视化方法已经穷尽。三维曲面有实际原始网格、二维映射及三维视角实例；不据此宣称已提供三维散点、体渲染、分子轨迹动画或交互三维网格。雷达保留原始剖面及历史示例；大于四条剖面需分面。

多组学索引含跨层关系、基因组轨道、变异后验、剪接、质谱和通路叠加；建模含ROC、PR、校准、决策、生存、残差、贡献与敏感性。结构固定参考与可运行数值图分别标记。原生软件包算法没有因绘图入口而被实现或重新验证。

历史版本完整导出沿用既有公开 v0.8.0 归档链接，便携安装提供离线预览；当前 FigureSpec、输入和导出直接使用随包本地文件。
