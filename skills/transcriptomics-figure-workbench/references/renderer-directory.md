# Executable renderer directory

Generated from shipped Python source. Function, alias, family and example counts are separate.

Discovery does not import plotting dependencies. Source availability is not runtime or scientific acceptance.

| Callable | Fixed aliases | Table entry | Required parameters |
|---|---|---|---|
| figure_analysis_results.plot_splice_tracks | splice_tracks | yes | sample_order, transcript_order, region, coordinate_definition, coverage_definition, junction_definition |
| figure_analysis_results.plot_variant_posteriors | variant_posteriors | yes | signal_order, region, coordinate_definition, posterior_definition |
| figure_analysis_results.plot_contribution_waterfall | contribution_waterfall | yes | component_order, baseline, total, quantity_definition, contribution_definition |
| figure_annotation_views.plot_annotation_evidence | canonical ID | yes | mode, title, expression_label, detection_definition, expression_limits, marker_order |
| figure_biomni_views.plot_sequence_logo | sequence_logo | yes | position_order, alphabet, symbol_slots, height_definition, height_unit |
| figure_biomni_views.plot_contact_tracks | contact_tracks | yes | bin_order, track_order, region_definition, coordinate_unit, value_definition, value_limits, track_unit |
| figure_biomni_views.plot_branch_tree | branch_tree | yes | root_id, leaf_order, branch_unit, tree_definition |
| figure_biomni_views.plot_slice_overlay | slice_overlay | yes | view_order, axis_labels, label_slots, intensity_limits, registration_definition, orientation_definition |
| figure_biomni_views.plot_registration_check | registration_check | yes | intensity_limits, difference_limits, tile_pixels, coordinate_labels, registration_definition |
| figure_chapter_views.plot_transcriptomic_chapter | canonical ID | yes | panels, title, scope_note |
| figure_clarity_views.plot_clarity_views | clarity | yes | view, contract, options |
| figure_coexpression_evidence.plot_coexpression_evidence | canonical ID | yes | mode, title, context, definition |
| figure_core.plot_embedding | embedding | yes | palette |
| figure_core.plot_samples | canonical ID | yes | palette, y_label |
| figure_core.plot_forest | canonical ID | yes | x_label, interval_label, effect_scale |
| figure_core.plot_volcano | volcano | yes | none |
| figure_core.plot_dot | dot_matrix | yes | value_label, value_semantics, denominator_label |
| figure_core.plot_heatmap | heatmap | yes | value_label |
| figure_core.plot_qc | canonical ID | yes | y_label |
| figure_core.plot_composition | composition | yes | palette |
| figure_core.plot_curve | canonical ID | yes | none |
| figure_editorial.plot_editorial | editorial | yes | kind, contract |
| figure_enrichment_story.plot_enrichment_story | canonical ID | yes | mode, title, background_definition, gene_set_version, selection_definition, support_contrast, tested_size |
| figure_expanded_grammar.plot_mosaic_counts | mosaic_counts | yes | contract |
| figure_expanded_grammar.plot_waffle_counts | waffle_counts | yes | contract, unit_label |
| figure_expanded_grammar.plot_horizon_series | horizon_series | yes | contract, band_width, x_label, y_label |
| figure_expanded_grammar.plot_connected_scatter | connected_scatter | yes | contract, x_label, y_label |
| figure_expanded_grammar.plot_mirrored_bars | mirrored_bars | yes | contract, unit_label, left_group, right_group |
| figure_expanded_grammar.plot_genomic_rainfall | genomic_rainfall | yes | contract, assembly, gap_definition |
| figure_extensions.plot_paired | paired | yes | palette, condition_order, y_label |
| figure_extensions.plot_effect_matrix | effect_matrix | yes | effect_label, effect_scale |
| figure_extensions.plot_annotated_heatmap | canonical ID | yes | value_label, group_palette, block_palette, scale_type |
| figure_extensions.plot_score_comparison | canonical ID | yes | score_label, condition_labels |
| figure_general.plot_xy_points | xy_points | yes | palette, x_label, y_label, unit_label |
| figure_general.plot_grouped_estimates | grouped_estimates | yes | palette, y_label, interval_label |
| figure_general.plot_binned_distribution | canonical ID | yes | palette, x_label, denominator_label |
| figure_general.plot_confusion_counts | canonical ID | yes | unit_label |
| figure_general.plot_density_ridges | density_ridges | yes | palette, x_label, density_label |
| figure_gsea.plot_gsea_tracks | gsea_tracks | yes | contract, curve_order, ranked_universe, metric_label, contrast, gene_set_version |
| figure_gsea.plot_gsea_nes | gsea_nes | yes | contract, pathway_order, contrast_order, nes_limits |
| figure_gsea.plot_gsea_leading_edge | gsea_leading_edge | yes | contract, pathway_order, gene_order, value_label, value_limits |
| figure_gsea.plot_ora_terms | ora_terms | yes | contract, term_order, background_definition |
| figure_integrated_views.plot_integrated_view | canonical ID | yes | mode, title |
| figure_lineage_views.plot_lineage_view | canonical ID | yes | mode, title, definition |
| figure_linked_evidence.plot_membership_ribbons | membership_ribbons | yes | member_order, term_order, block_slots, effect_limits, significance_limits, ratio_max, ratio_definition |
| figure_linked_evidence.plot_split_metric_matrix | split_metric_matrix | yes | row_order, column_order, row_slots, association_limits, significance_limits, association_definition, probability_definition |
| figure_linked_evidence.plot_hierarchy_tracks | hierarchy_tracks | yes | leaf_order, height_definition |
| figure_linked_evidence.plot_radial_hierarchy | radial_hierarchy | yes | leaf_order, height_definition, metric_limits, metric_definition, outer_definition, area_definition |
| figure_linked_evidence.plot_stacked_values | stacked_values | yes | object_order, segment_order, value_definition, additivity_definition |
| figure_method_extensions.plot_enrichment_grid | enrichment_grid | yes | significance_limits, ratio_max, block_slots, column_order, term_order |
| figure_method_extensions.plot_term_effect_circle | term_effect_circle | yes | term_order, effect_limits, zscore_limits, significance_max, zscore_definition, effect_label |
| figure_method_extensions.plot_term_key | term_key | yes | none |
| figure_method_extensions.plot_two_set_overlap | two_set_overlap | yes | set_columns, unit_label |
| figure_method_extensions.plot_gene_term_chord | gene_term_chord | yes | gene_order, term_order, effect_limits, effect_label |
| figure_method_extensions.plot_distribution_result | distribution | yes | mode, x_label, y_label |
| figure_method_extensions.plot_balance | balance | yes | stage_order, threshold, metric_definition |
| figure_method_extensions.plot_agreement | agreement | yes | bias, loa, unit_label, difference_definition |
| figure_method_extensions.plot_survival_result | survival | yes | time_label, risk_convention, interval_definition |
| figure_method_extensions.plot_swimmer | swimmer | yes | time_label, event_shapes, object_order |
| figure_method_extensions.plot_specification_curve | specification_curve | yes | spec_order, decision_order, effect_scale, interval_definition |
| figure_method_extensions.plot_vector_field | vector_field | yes | arrow_scale, vector_definition, coordinate_definition |
| figure_method_extensions.plot_bivariate_tiles | bivariate_tiles | yes | x_breaks, y_breaks, x_label, y_label |
| figure_multimodal.plot_cohort_intervals | canonical ID | yes | palette, effect_scale, effect_label, interval_label |
| figure_multimodal.plot_association_matrix | canonical ID | yes | value_label, method_label |
| figure_multimodal.plot_calibration_counts | calibration_counts | yes | palette, interval_label, evaluation_label |
| figure_multimodal.plot_interval_tracks | canonical ID | yes | palette, assembly, chromosome, region, value_label |
| figure_multimodal.plot_frozen_dynamics | frozen_dynamics | yes | palette, time_label, value_label, unit_label, interval_label |
| figure_multimodal.plot_residue_confidence | canonical ID | yes | sequence_label |
| figure_multiomics_views.plot_cross_effects | cross_effects | yes | x_label, y_label, comparison_definition |
| figure_multiomics_views.plot_aligned_views | aligned_views | yes | view_order, coordinate_definition |
| figure_multiomics_views.plot_loading_projection | loading_projection | yes | x_label, y_label, projection_definition |
| figure_multiomics_views.plot_mass_spectrum | mass_spectrum | yes | spectrum_order, mass_definition, intensity_definition, normalization_definition |
| figure_multiomics_views.plot_genomic_links | genomic_links | yes | track_order, region, assembly, chromosome, coordinate_definition, value_definition, link_definition |
| figure_multiomics_views.plot_pathway_overlay | pathway_overlay | yes | node_limits, node_value_definition, edge_definition |
| figure_multiomics_views.plot_diagnostic_panel | model_diagnostic | yes | mode, model_definition, reference_definition |
| figure_multiscale.plot_ternary_composition | ternary | yes | components, denominator_definition |
| figure_multiscale.plot_genome_overview | genome_overview | yes | chromosome_order, chromosome_lengths, segment_slots, assembly, coordinate_definition, thresholds |
| figure_multiscale.plot_locus_tracks | locus_tracks | yes | position_limits, chromosome, assembly, coordinate_definition, ld_reference, ld_definition, recombination_unit |
| figure_multiscale.plot_funnel_result | funnel | yes | reference_estimate, effect_definition, precision_definition, guide_definition |
| figure_multiscale.plot_hierarchy_partition | hierarchy_area | yes | root_id, quantity_definition |
| figure_multiscale.plot_uncertainty_fan | uncertainty_fan | yes | coverage_order, interval_definition, x_label, y_label |
| figure_multiscale.plot_spatial_overlay | spatial_overlay | yes | mode, pixel_size, physical_unit, background_definition |
| figure_network_extensions.plot_typed_network | typed_network | yes | edge_label, node_area_label, relation_semantics |
| figure_network_extensions.plot_weighted_chord | weighted_chord | yes | weight_label, order |
| figure_network_extensions.plot_alluvial | alluvial | yes | stage_columns, weight_label |
| figure_network_extensions.plot_upset | upset | yes | set_columns, unit_label |
| figure_network_extensions.plot_multistate_matrix | multistate_matrix | yes | state_order, state_slots |
| figure_network_extensions.plot_running_enrichment | running_enrichment | yes | curve_groups, rank_label |
| figure_network_extensions.plot_rank_bump | rank_bump | yes | stage_order |
| figure_network_extensions.plot_hex_density | canonical ID | yes | x_label, y_label, unit_label |
| figure_network_extensions.plot_contour_field | canonical ID | yes | value_label, limits, levels, x_label, y_label |
| figure_package_styles.plot_package_style | package_style | yes | view, contract, options |
| figure_palette_applications.plot_palette_plate | canonical ID | yes | palette_name, panel_specs |
| figure_palette_applications.plot_palette_panel | canonical ID | yes | palette_name, panel_spec |
| figure_polish.plot_polished_matrix | polished_matrix | yes | value_label, limits, signed |
| figure_polish.plot_recorded_evidence | canonical ID | yes | none |
| figure_polish.plot_availability_counts | canonical ID | yes | none |
| figure_process_dashboard.plot_process_dashboard | canonical ID | yes | palette, surface_order, bar_group_order, stage_order, geometry_label, count_label |
| figure_publication.plot_publication_curve | frozen_curve | yes | palette, curve_type, labels |
| figure_publication.plot_aligned_matrix | annotated_matrix | yes | value_label, limits |
| figure_publication.plot_publication_forest | forest | yes | palette, x_label, interval_label, effect_scale |
| figure_publication.plot_feature_facets | feature_facets | yes | value_label, limits |
| figure_publication.plot_raincloud | raincloud | yes | palette, y_label, unit_label |
| figure_publication_plus.plot_publication_plus | publication_plus | yes | view, contract, options |
| figure_qc_de.plot_frozen_qc_de | qc_de | yes | mode, contract |
| figure_reference.plot_annular_profile | canonical ID | yes | palette, value_label, area_label, value_max |
| figure_reference.plot_ellipse_correlation | canonical ID | yes | labels |
| figure_reference.plot_signed_network | canonical ID | yes | none |
| figure_reference.plot_mantel_matrix | canonical ID | yes | labels, specimen_order, p_type, pearson_p_type |
| figure_reference.plot_parallel_trials | canonical ID | yes | axis_order, axis_ranges, score_label, score_limits |
| figure_reference.plot_contribution_swarm | canonical ID | yes | feature_order, contribution_label, limits |
| figure_reference.plot_group_beeswarm | canonical ID | yes | palette, group_order, value_label, summary_label, limits |
| figure_reference.plot_joint_reference | canonical ID | yes | palette, x_label, y_label, limits |
| figure_reference.plot_pca_reference | canonical ID | yes | palette, group_order, axis_labels, limits, ellipse_label |
| figure_reference.plot_state_dashboard | canonical ID | yes | palette, family_order, condition_order, mean_label, program_label |
| figure_reference.plot_multiclass_contributions | canonical ID | yes | palette, class_order, feature_orders, limits |
| figure_reference.plot_embedding_atlas | canonical ID | yes | palette, stack_palette, atlas_order, main_order, marker_label, count_label, fraction_label, radial_count_max |
| figure_reference.plot_training_dashboard | canonical ID | yes | palette, selected_epoch, selection_label, loss_label, heat_label, gradient_label |
| figure_reference.plot_activity_dashboard | canonical ID | yes | palette, row_order, column_order, value_label, bar_label, line_label |
| figure_reference.plot_effect_distribution_forest | canonical ID | yes | row_order, panel_order, panel_labels, limits, interval_label, count_label, p_type |
| figure_reference.plot_facet_bubble_matrix | canonical ID | yes | row_facets, column_facets, feature_order, window_order, value_label |
| figure_reference.plot_strip_effects | canonical ID | yes | palette, panel_order, contrast_order, eligibility_label |
| figure_reference.plot_aligned_tracks | canonical ID | yes | palette, category_order, track_order, matrix_order, block_order, matrix_labels, matrix_limits, count_label |
| figure_reference.plot_surface_grid | canonical ID | yes | axis_labels, value_label, limits |
| figure_refined_views.plot_refined_views | refined | yes | view, contract, options |
| figure_study_overview.plot_transcriptomic_overview | canonical ID | yes | assay, contrast, independent_unit, denominator |
| figure_styles.plot_volcano_editorial | canonical ID | yes | none |
| figure_styles.plot_volcano_marginal | volcano_marginal | yes | none |
| figure_styles.plot_enrichment_lollipop | canonical ID | yes | score_type, denominator_label, count_label |
| figure_styles.plot_composition_panels | canonical ID | yes | palette, unit_label |
| figure_styles.plot_sample_distribution | canonical ID | yes | palette, y_label |
| figure_wgcna_views.plot_wgcna_view | canonical ID | yes | mode, title, context |

## figure_analysis_results.plot_splice_tracks

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| sample_order | true | — |
| transcript_order | true | — |
| region | true | — |
| coordinate_definition | true | — |
| coverage_definition | true | — |
| junction_definition | true | — |
| width_per_count | false | 0.045 |
| title | false | "" |

## figure_analysis_results.plot_variant_posteriors

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| signal_order | true | — |
| region | true | — |
| coordinate_definition | true | — |
| posterior_definition | true | — |
| label_ids | false | null |
| title | false | "" |

## figure_analysis_results.plot_contribution_waterfall

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| component_order | true | — |
| baseline | true | — |
| total | true | — |
| quantity_definition | true | — |
| contribution_definition | true | — |
| title | false | "" |

## figure_annotation_views.plot_annotation_evidence

Separate annotation atlas and per-subgroup multi-marker reading pages.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| expression_label | true | — |
| detection_definition | true | — |
| expression_limits | true | — |
| marker_order | true | — |
| focus_group | false | null |
| group_order | false | null |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 3.25 |
| panel_height | false | 3.15 |
| composition | false | "auto" |

## figure_biomni_views.plot_sequence_logo

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| position_order | true | — |
| alphabet | true | — |
| symbol_slots | true | — |
| height_definition | true | — |
| height_unit | true | — |
| position_label | false | "Supplied position" |
| title | false | "" |

## figure_biomni_views.plot_contact_tracks

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| bin_order | true | — |
| track_order | true | — |
| region_definition | true | — |
| coordinate_unit | true | — |
| value_definition | true | — |
| value_limits | true | — |
| track_unit | true | — |
| title | false | "" |

## figure_biomni_views.plot_branch_tree

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| root_id | true | — |
| leaf_order | true | — |
| branch_unit | true | — |
| tree_definition | true | — |
| title | false | "" |

## figure_biomni_views.plot_slice_overlay

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| view_order | true | — |
| axis_labels | true | — |
| label_slots | true | — |
| intensity_limits | true | — |
| registration_definition | true | — |
| orientation_definition | true | — |
| arrangement | false | "horizontal" |
| title | false | "" |

## figure_biomni_views.plot_registration_check

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| intensity_limits | true | — |
| difference_limits | true | — |
| tile_pixels | true | — |
| coordinate_labels | true | — |
| registration_definition | true | — |
| arrangement | false | "horizontal" |
| title | false | "" |

## figure_chapter_views.plot_transcriptomic_chapter

Draw a complete, explicitly selected analysis chapter with adaptive packing.

| Parameter | Required | Default |
|---|---|---|
| panels | true | — |
| title | true | — |
| scope_note | true | — |
| columns | false | "auto" |
| rows | false | null |
| presentation | false | "classic" |

## figure_clarity_views.plot_clarity_views

Fine profiles, readable dense panels, imaging and supplied evaluation views.

| Parameter | Required | Default |
|---|---|---|
| view | true | — |
| contract | true | — |
| options | true | — |

## figure_coexpression_evidence.plot_coexpression_evidence

Coexpression, pathway/regulon and donor-level companions with exact result semantics.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| context | true | — |
| definition | true | — |
| module_order | false | null |
| columns | false | "auto" |
| value_label | false | "Oriented module eigengene" |
| value_limits | false | null |
| label_genes | false | [] |
| edge_semantics | false | null |
| directed | false | false |
| cloud_shapes | false | null |

## figure_core.plot_embedding

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| axis_prefix | false | "UMAP" |

## figure_core.plot_samples

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| y_label | true | — |

## figure_core.plot_forest

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| x_label | true | — |
| interval_label | true | — |
| effect_scale | true | — |

## figure_core.plot_volcano

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| alpha | false | 0.05 |
| fc | false | 1 |

## figure_core.plot_dot

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| value_semantics | true | — |
| denominator_label | true | — |
| row_field | false | "feature" |
| column_field | false | "group" |
| fraction_field | false | "fraction" |
| value_field | false | "value" |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| row_label_wrap | false | null |
| column_label_wrap | false | null |
| label_rotation | false | null |
| figsize | false | null |
| continuous_colors | false | null |
| row_counts | false | null |
| count_label | false | null |

## figure_core.plot_heatmap

Draw a signed/sequential heatmap from a long or wide matrix.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| center | false | 0 |
| scale_type | false | "signed" |
| row_field | false | "feature" |
| column_field | false | "sample" |
| value_field | false | "value" |
| value_columns | false | null |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| missing | false | "error" |
| figsize | false | null |
| cell_width | false | 0.44 |
| cell_height | false | 0.27 |
| label_rotation | false | 45 |
| show_labels | false | true |
| row_label_mode | false | "all" |
| column_label_mode | false | "all" |
| row_label_wrap | false | null |
| column_label_wrap | false | null |
| label_fontsize | false | null |
| title | false | "" |
| row_annotations | false | null |
| column_annotations | false | null |
| annotation_palettes | false | null |
| continuous_colors | false | null |

## figure_core.plot_qc

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| y_label | true | — |
| metric_field | false | null |
| metric_labels | false | null |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 3.3 |
| panel_height | false | 3.5 |

## figure_core.plot_composition

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| y_label | false | "Fraction of included cells" |
| mode | false | "stacked" |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 3.5 |
| panel_height | false | 2.6 |

## figure_core.plot_curve

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| kind | false | "ROC" |
| palette | false | null |
| mode | false | "auto" |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 3.8 |
| panel_height | false | 3.6 |
| prevalence | false | null |
| interval_label | false | null |
| interpolation | false | "linear" |

## figure_editorial.plot_editorial

Six rebuilt frozen-result modes. Candidate aesthetics require actual review.

| Parameter | Required | Default |
|---|---|---|
| kind | true | — |
| contract | true | — |
| options | false | null |

## figure_enrichment_story.plot_enrichment_story

Linked ORA/GSEA and complete selected gene support on aligned term rows.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| background_definition | true | — |
| gene_set_version | true | — |
| selection_definition | true | — |
| support_contrast | true | — |
| tested_size | true | — |
| query_size | false | null |
| nes_limits | false | [-3, 3] |
| gene_effect_limits | false | [-3, 3] |
| columns | false | "auto" |
| presentation | false | "auto" |

## figure_expanded_grammar.plot_mosaic_counts

Area mosaic: group width is total count; within-group height is count fraction.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| category_order | false | null |
| group_order | false | null |
| title | false | "Composition and sample size" |

## figure_expanded_grammar.plot_waffle_counts

One square per declared count unit; no rounding or percentage apportionment.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| unit_label | true | — |
| columns | false | 10 |
| category_order | false | null |
| title | false | "Exact count composition" |

## figure_expanded_grammar.plot_horizon_series

Fold signed magnitude into explicit bands; preserve a full linear reference panel.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| band_width | true | — |
| bands | false | 3 |
| series_order | false | null |
| x_label | true | — |
| y_label | true | — |
| title | false | "Signed time-course overview" |

## figure_expanded_grammar.plot_connected_scatter

Two supplied measurements linked in explicit step order, with start/end labels.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| x_label | true | — |
| y_label | true | — |
| series_order | false | null |
| title | false | "Joint response over time" |

## figure_expanded_grammar.plot_mirrored_bars

Compare two nonnegative profiles around a common zero with exact numeric labels.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| unit_label | true | — |
| left_group | true | — |
| right_group | true | — |
| category_order | false | null |
| title | false | "Two-group profile" |

## figure_expanded_grammar.plot_genomic_rainfall

Supplied genomic positions and precomputed positive gaps on a shared log scale.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| assembly | true | — |
| gap_definition | true | — |
| chromosome_order | false | null |
| title | false | "Genomic event spacing" |

## figure_extensions.plot_paired

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| condition_order | true | — |
| y_label | true | — |

## figure_extensions.plot_effect_matrix

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| effect_label | true | — |
| effect_scale | true | — |
| evidence_cap | false | 6 |
| row_field | false | "feature" |
| column_field | false | "contrast" |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| cell_width | false | 1.1 |
| cell_height | false | 0.4 |

## figure_extensions.plot_annotated_heatmap

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| group_palette | true | — |
| block_palette | true | — |
| scale_type | true | — |
| column_annotation_label | false | "Column group" |
| row_annotation_label | false | "Feature block" |
| row_field | false | "feature" |
| column_field | false | "sample" |
| value_field | false | "value" |
| column_annotation_field | false | "sample_group" |
| row_annotation_field | false | "feature_block" |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| cell_width | false | 0.45 |
| cell_height | false | 0.3 |
| row_label_wrap | false | null |
| column_label_wrap | false | null |
| merge_annotation_legends | false | false |
| continuous_colors | false | null |
| title | false | "" |
| presentation | false | "classic" |
| matrix_semantics | false | null |

## figure_extensions.plot_score_comparison

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| score_label | true | — |
| condition_labels | true | — |

## figure_general.plot_xy_points

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| x_label | true | — |
| y_label | true | — |
| unit_label | true | — |
| connect_order | false | false |
| label_points | false | false |

## figure_general.plot_grouped_estimates

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| y_label | true | — |
| interval_label | true | — |

## figure_general.plot_binned_distribution

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| x_label | true | — |
| denominator_label | true | — |

## figure_general.plot_confusion_counts

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| unit_label | true | — |
| label_order | false | null |
| label_aliases | false | null |
| label_wrap | false | null |
| figsize | false | null |

## figure_general.plot_density_ridges

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| x_label | true | — |
| density_label | true | — |
| amplitude | false | 0.8 |
| height_scale | false | null |
| title | false | "" |

## figure_gsea.plot_gsea_tracks

GSEA classic/overlay/facets: exact running ES, hit rugs, rank metric and supplied NES/FDR.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| curve_order | true | — |
| ranked_universe | true | — |
| metric_label | true | — |
| contrast | true | — |
| gene_set_version | true | — |
| mode | false | "classic" |
| title | false | "Gene set enrichment" |
| show_leading_edge | false | true |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 4.2 |
| panel_height | false | 3.6 |

## figure_gsea.plot_gsea_nes

Signed NES dot matrix; explicit not_tested cells and supplied FDR outlines.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| pathway_order | true | — |
| contrast_order | true | — |
| nes_limits | true | — |
| alpha | false | 0.05 |
| size_max | false | 200 |
| title | false | "Pathway enrichment across contrasts" |

## figure_gsea.plot_gsea_leading_edge

Explicit complete gene/set membership map; missing membership is not inferred.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| pathway_order | true | — |
| gene_order | true | — |
| value_label | true | — |
| value_limits | true | — |
| title | false | "Leading-edge membership and effect" |

## figure_gsea.plot_ora_terms

ORA bubble/lollipop with exact numerator/denominator, no GSEA/ORA conflation.

| Parameter | Required | Default |
|---|---|---|
| contract | true | — |
| term_order | true | — |
| background_definition | true | — |
| mode | false | "bubble" |
| ratio_max | false | 1 |
| significance_max | false | 8 |
| title | false | "Selected over-representation results" |

## figure_integrated_views.plot_integrated_view

Prefer a compatible information-rich view; all extra scientific channels are supplied.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| axis_labels | false | null |
| ellipse_definition | false | null |
| labels | false | [] |
| alpha | false | 0.05 |
| fc | false | 1 |
| feature_columns | false | "auto" |
| cloud_shapes | false | null |
| observation_unit | false | null |
| presentation | false | "auto" |
| group_counts | false | null |
| expression_limits | false | null |
| identity_by_cell | false | null |
| identity_order | false | null |

## figure_lineage_views.plot_lineage_view

Show actual lineage/flow identities, quantities and coordinate meanings.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| definition | true | — |
| level_order | false | null |
| root_id | false | null |
| value_limits | false | [0, 1] |
| columns | false | "auto" |

## figure_linked_evidence.plot_membership_ribbons

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| member_order | true | — |
| term_order | true | — |
| block_slots | true | — |
| effect_limits | true | — |
| significance_limits | true | — |
| ratio_max | true | — |
| ratio_definition | true | — |
| title | false | "" |

## figure_linked_evidence.plot_split_metric_matrix

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| row_order | true | — |
| column_order | true | — |
| row_slots | true | — |
| association_limits | true | — |
| significance_limits | true | — |
| association_definition | true | — |
| probability_definition | true | — |
| title | false | "" |

## figure_linked_evidence.plot_hierarchy_tracks

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| leaf_order | true | — |
| height_definition | true | — |
| title | false | "" |

## figure_linked_evidence.plot_radial_hierarchy

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| leaf_order | true | — |
| height_definition | true | — |
| metric_limits | true | — |
| metric_definition | true | — |
| outer_definition | true | — |
| area_definition | true | — |
| label_ids | false | [] |
| title | false | "" |

## figure_linked_evidence.plot_stacked_values

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| object_order | true | — |
| segment_order | true | — |
| value_definition | true | — |
| additivity_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_enrichment_grid

Full term x group/cell-class grid; tested absence and untested are distinct.

| Parameter | Required | Default |
|---|---|---|
| significance_limits | true | — |
| ratio_max | true | — |
| block_slots | true | — |
| column_order | true | — |
| term_order | true | — |
| title | false | "" |

## figure_method_extensions.plot_term_effect_circle

Inner p-height/z-score colour; outer individual gene-effect positions.

| Parameter | Required | Default |
|---|---|---|
| term_order | true | — |
| effect_limits | true | — |
| zscore_limits | true | — |
| significance_max | true | — |
| zscore_definition | true | — |
| effect_label | true | — |
| title | false | "" |

## figure_method_extensions.plot_term_key

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| title | false | "" |

## figure_method_extensions.plot_two_set_overlap

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| set_columns | true | — |
| unit_label | true | — |
| title | false | "" |

## figure_method_extensions.plot_gene_term_chord

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| gene_order | true | — |
| term_order | true | — |
| effect_limits | true | — |
| effect_label | true | — |
| title | false | "" |

## figure_method_extensions.plot_distribution_result

One curve/point engine for frozen ECDF steps or matched QQ coordinates.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| x_label | true | — |
| y_label | true | — |
| title | false | "" |
| reference_distribution | false | null |

## figure_method_extensions.plot_balance

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| stage_order | true | — |
| threshold | true | — |
| metric_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_agreement

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| bias | true | — |
| loa | true | — |
| unit_label | true | — |
| difference_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_survival_result

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| time_label | true | — |
| risk_convention | true | — |
| interval_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_swimmer

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| time_label | true | — |
| event_shapes | true | — |
| object_order | true | — |
| title | false | "" |

## figure_method_extensions.plot_specification_curve

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| spec_order | true | — |
| decision_order | true | — |
| effect_scale | true | — |
| interval_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_vector_field

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| arrow_scale | true | — |
| vector_definition | true | — |
| coordinate_definition | true | — |
| title | false | "" |

## figure_method_extensions.plot_bivariate_tiles

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| x_breaks | true | — |
| y_breaks | true | — |
| x_label | true | — |
| y_label | true | — |
| title | false | "" |

## figure_multimodal.plot_cohort_intervals

Complete cohort x feature grid, comparable contrast/effect units, no pooling.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| effect_scale | true | — |
| effect_label | true | — |
| interval_label | true | — |
| title | false | "" |

## figure_multimodal.plot_association_matrix

Frozen signed correlation with supplied FDR marks; missing entries hatch.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| method_label | true | — |
| alpha | false | 0.05 |
| title | false | "" |
| row_field | false | "feature" |
| column_field | false | "modality" |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| cell_width | false | 0.7 |
| cell_height | false | 0.36 |
| label_rotation | false | 25 |

## figure_multimodal.plot_calibration_counts

Frozen reliability curve + actual bin counts; no rebinning or calibration fit.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| interval_label | true | — |
| evaluation_label | true | — |
| title | false | "" |

## figure_multimodal.plot_interval_tracks

Prebinned disjoint intervals only, no BAM/bigWig parsing or invented genes.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| assembly | true | — |
| chromosome | true | — |
| region | true | — |
| value_label | true | — |
| coordinate_system | false | "zero_based_half_open" |
| title | false | "" |

## figure_multimodal.plot_frozen_dynamics

Supplied trajectory summaries/bounds, no smoothing, block averaging or simulation.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| time_label | true | — |
| value_label | true | — |
| unit_label | true | — |
| interval_label | true | — |
| title | false | "" |

## figure_multimodal.plot_residue_confidence

Supplied per-residue pLDDT: predicted local confidence, not flexibility/affinity.

| Parameter | Required | Default |
|---|---|---|
| sequence_label | true | — |
| title | false | "" |

## figure_multiomics_views.plot_cross_effects

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| x_label | true | — |
| y_label | true | — |
| comparison_definition | true | — |
| alpha | false | 0.05 |
| label_ids | false | [] |
| title | false | "" |

## figure_multiomics_views.plot_aligned_views

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| view_order | true | — |
| coordinate_definition | true | — |
| draw_links | false | true |
| title | false | "" |

## figure_multiomics_views.plot_loading_projection

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| x_label | true | — |
| y_label | true | — |
| projection_definition | true | — |
| title | false | "" |

## figure_multiomics_views.plot_mass_spectrum

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| spectrum_order | true | — |
| mass_definition | true | — |
| intensity_definition | true | — |
| normalization_definition | true | — |
| mirror | false | false |
| label_peak_ids | false | [] |
| title | false | "" |

## figure_multiomics_views.plot_genomic_links

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| track_order | true | — |
| region | true | — |
| assembly | true | — |
| chromosome | true | — |
| coordinate_definition | true | — |
| value_definition | true | — |
| link_definition | true | — |
| title | false | "" |

## figure_multiomics_views.plot_pathway_overlay

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| node_limits | true | — |
| node_value_definition | true | — |
| edge_definition | true | — |
| title | false | "" |

## figure_multiomics_views.plot_diagnostic_panel

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| model_definition | true | — |
| reference_definition | true | — |
| cook_area_scale | false | 180 |
| title | false | "" |

## figure_multiscale.plot_ternary_composition

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| components | true | — |
| denominator_definition | true | — |
| title | false | "" |

## figure_multiscale.plot_genome_overview

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| chromosome_order | true | — |
| chromosome_lengths | true | — |
| segment_slots | true | — |
| assembly | true | — |
| coordinate_definition | true | — |
| thresholds | true | — |
| title | false | "" |

## figure_multiscale.plot_locus_tracks

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| position_limits | true | — |
| chromosome | true | — |
| assembly | true | — |
| coordinate_definition | true | — |
| ld_reference | true | — |
| ld_definition | true | — |
| recombination_unit | true | — |
| title | false | "" |

## figure_multiscale.plot_funnel_result

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| reference_estimate | true | — |
| effect_definition | true | — |
| precision_definition | true | — |
| guide_definition | true | — |
| title | false | "" |

## figure_multiscale.plot_hierarchy_partition

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| root_id | true | — |
| quantity_definition | true | — |
| title | false | "" |

## figure_multiscale.plot_uncertainty_fan

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| coverage_order | true | — |
| interval_definition | true | — |
| x_label | true | — |
| y_label | true | — |
| title | false | "" |

## figure_multiscale.plot_spatial_overlay

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| pixel_size | true | — |
| physical_unit | true | — |
| background_definition | true | — |
| value_limits | false | null |
| value_label | false | "Supplied value" |
| title | false | "" |

## figure_network_extensions.plot_typed_network

Explicit node XY/labels/types/groups/areas + edges/endpoints/weights/signs.

| Parameter | Required | Default |
|---|---|---|
| edge_label | true | — |
| node_area_label | true | — |
| relation_semantics | true | — |
| directed | false | false |
| shape_map | false | null |
| title | false | "" |
| size | false | [8.5, 6.2] |

## figure_network_extensions.plot_weighted_chord

Nonnegative quantitative relationships: widths carry the supplied weights.

| Parameter | Required | Default |
|---|---|---|
| weight_label | true | — |
| order | true | — |
| title | false | "" |

## figure_network_extensions.plot_alluvial

Conserved path bands, with left-to-right or top-to-bottom stage direction.

| Parameter | Required | Default |
|---|---|---|
| stage_columns | true | — |
| weight_label | true | — |
| title | false | "" |
| orientation | false | "horizontal" |
| stage_orders | false | null |
| path_order | false | null |
| gap_fraction | false | 0.045 |
| path_field | false | "path_id" |
| weight_field | false | "weight" |
| category_aliases | false | null |
| stage_aliases | false | null |
| color_stage | false | null |

## figure_network_extensions.plot_upset

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| set_columns | true | — |
| unit_label | true | — |
| title | false | "" |

## figure_network_extensions.plot_multistate_matrix

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| state_order | true | — |
| state_slots | true | — |
| title | false | "" |
| row_field | false | "row" |
| column_field | false | "column" |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |

## figure_network_extensions.plot_running_enrichment

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| curve_groups | true | — |
| rank_label | true | — |
| title | false | "" |

## figure_network_extensions.plot_rank_bump

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| stage_order | true | — |
| title | false | "" |

## figure_network_extensions.plot_hex_density

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| x_label | true | — |
| y_label | true | — |
| unit_label | true | — |
| gridsize | false | 24 |
| title | false | "" |

## figure_network_extensions.plot_contour_field

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| limits | true | — |
| levels | true | — |
| x_label | true | — |
| y_label | true | — |
| title | false | "" |

## figure_package_styles.plot_package_style

Fourteen reference-informed package display grammars; frozen tables and explicit method context.

| Parameter | Required | Default |
|---|---|---|
| view | true | — |
| contract | true | — |
| options | true | — |

## figure_palette_applications.plot_palette_plate

C01–C07 original application examples. panel_specs records exact mappings.

| Parameter | Required | Default |
|---|---|---|
| palette_name | true | — |
| panel_specs | true | — |
| size | false | null |
| font_family | false | "DejaVu Sans" |
| layout | false | "plate" |
| ncols | false | "auto" |
| nrows | false | null |

## figure_palette_applications.plot_palette_panel

One reusable scientific panel. No palette poster or automatic composition.

| Parameter | Required | Default |
|---|---|---|
| palette_name | true | — |
| panel_spec | true | — |
| size | false | [6.7, 5.1] |
| font_family | false | "Arial" |

## figure_polish.plot_polished_matrix

All values/order retained; layout matrix, blocks or transpose; exact alias mapping.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| limits | true | — |
| signed | true | — |
| row_aliases | false | null |
| column_aliases | false | null |
| row_blocks | false | null |
| column_blocks | false | null |
| layout | false | "matrix" |
| width_mm | false | 180 |
| font_size | false | 8.5 |
| title | false | "" |
| note | false | "" |
| sign_marks | false | true |
| row_field | false | "feature" |
| column_field | false | "sample" |
| value_field | false | "value" |
| value_columns | false | null |
| row_order | false | null |
| column_order | false | null |
| missing | false | "error" |
| label_rotation | false | null |
| row_label_wrap | false | null |
| column_label_wrap | false | null |

## figure_polish.plot_recorded_evidence

Preserve zero, N/A and overlapping report-unit denominators; no risk estimates.

| Parameter | Required | Default |
|---|---|---|
| row_aliases | false | null |
| layout | false | "aligned" |
| width_mm | false | 180 |
| font_size | false | 8.5 |
| title | false | "Recorded evidence" |
| note | false | "" |

## figure_polish.plot_availability_counts

Two frozen counts and exact absence arithmetic; keep all literature zeroes explicit.

| Parameter | Required | Default |
|---|---|---|
| row_aliases | false | null |
| title | false | "Record availability" |
| width_mm | false | 180 |

## figure_process_dashboard.plot_process_dashboard

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| surface_order | true | — |
| bar_group_order | true | — |
| stage_order | true | — |
| geometry_label | true | — |
| count_label | true | — |
| size | false | [12, 9] |

## figure_publication.plot_publication_curve

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| curve_type | true | — |
| labels | true | — |
| title | false | "" |
| prevalence | false | null |

## figure_publication.plot_aligned_matrix

Publication matrix accepting either a long or an explicit wide table.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| limits | true | — |
| signed | false | true |
| center | false | 0 |
| geometry | false | "tile" |
| block_palette | false | null |
| count_label | false | "Supplied count" |
| title | false | "" |
| continuous_colors | false | null |
| row_field | false | "feature" |
| column_field | false | "sample" |
| value_field | false | "value" |
| value_columns | false | null |
| row_order | false | null |
| column_order | false | null |
| row_aliases | false | null |
| column_aliases | false | null |
| row_block_field | false | "feature_block" |
| row_count_field | false | "row_count" |
| missing | false | "error" |
| figsize | false | null |
| cell_width | false | 0.44 |
| cell_height | false | 0.27 |
| label_rotation | false | 35 |
| row_label_wrap | false | null |
| column_label_wrap | false | null |
| label_fontsize | false | 9 |

## figure_publication.plot_publication_forest

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| x_label | true | — |
| interval_label | true | — |
| effect_scale | true | — |
| title | false | "" |
| compact | false | true |
| decimals | false | 2 |

## figure_publication.plot_feature_facets

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| value_label | true | — |
| limits | true | — |
| title | false | "" |
| ncols | false | "auto" |
| point_size | false | null |
| continuous_colors | false | null |
| nrows | false | null |
| panel_width | false | 2.8 |
| panel_height | false | null |
| presentation | false | "classic" |

## figure_publication.plot_raincloud

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| y_label | true | — |
| unit_label | true | — |
| title | false | "" |
| density_min_n | false | 20 |

## figure_publication_plus.plot_publication_plus

Frozen half-eye, split annotated matrix and aligned profile alternatives.

| Parameter | Required | Default |
|---|---|---|
| view | true | — |
| contract | true | — |
| options | true | — |

## figure_qc_de.plot_frozen_qc_de

Render eight bounded QC/DE modes from reviewed summaries; preserve exact input and project theme.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| contract | true | — |
| order | false | null |
| marker_map | false | null |
| title | false | "" |

## figure_reference.plot_annular_profile

R01/R02. Area profile and bubble ring; area in pt^2 per original unit.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| value_label | true | — |
| area_label | true | — |
| value_max | true | — |
| area_scale | false | 0.045 |
| connect_categories | false | false |
| curve_mode | false | "vertices" |
| size | false | [8, 7] |
| font_size | false | 9 |
| label_layout | false | "auto" |

## figure_reference.plot_ellipse_correlation

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| labels | true | — |
| cmap_name | false | "ellipse_yellow_purple" |
| size | false | [7, 7] |

## figure_reference.plot_signed_network

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette_name | false | "network_teal_red" |
| node_color | false | "#45B0C8" |
| size | false | [7, 7] |
| view | false | "auto" |

## figure_reference.plot_mantel_matrix

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| labels | true | — |
| specimen_order | true | — |
| p_type | true | — |
| pearson_p_type | true | — |
| size | false | [9, 7] |

## figure_reference.plot_parallel_trials

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| axis_order | true | — |
| axis_ranges | true | — |
| score_label | true | — |
| score_limits | true | — |
| size | false | [10, 5] |

## figure_reference.plot_contribution_swarm

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| feature_order | true | — |
| contribution_label | true | — |
| limits | true | — |
| cmap_name | false | "shap_teal_red" |
| size | false | [8, 8] |

## figure_reference.plot_group_beeswarm

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| group_order | true | — |
| value_label | true | — |
| summary_label | true | — |
| limits | true | — |
| size | false | [9, 5] |

## figure_reference.plot_joint_reference

R08/R12/R13. Marginals, fits/bands and box summaries are supplied, never fitted.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| x_label | true | — |
| y_label | true | — |
| limits | true | — |
| marginal_mode | false | "density" |
| identity | false | false |
| residual_label | false | null |
| size | false | [8, 7] |

## figure_reference.plot_pca_reference

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| group_order | true | — |
| axis_labels | true | — |
| limits | true | — |
| ellipse_label | true | — |
| spider | false | false |
| landscape | false | false |
| size | false | [8, 6] |

## figure_reference.plot_state_dashboard

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| family_order | true | — |
| condition_order | true | — |
| mean_label | true | — |
| program_label | true | — |
| size | false | [9, 9] |

## figure_reference.plot_multiclass_contributions

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| class_order | true | — |
| feature_orders | true | — |
| limits | true | — |
| size | false | [12, 9] |

## figure_reference.plot_embedding_atlas

R04 all three subfigures. Supplied tree segments are drawn, not clustered.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| stack_palette | true | — |
| atlas_order | true | — |
| main_order | true | — |
| marker_label | true | — |
| count_label | true | — |
| fraction_label | true | — |
| radial_count_max | true | — |
| size | false | [10, 15] |

## figure_reference.plot_training_dashboard

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| selected_epoch | true | — |
| selection_label | true | — |
| loss_label | true | — |
| heat_label | true | — |
| gradient_label | true | — |
| size | false | [10, 6] |

## figure_reference.plot_activity_dashboard

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| row_order | true | — |
| column_order | true | — |
| value_label | true | — |
| bar_label | true | — |
| line_label | true | — |
| size | false | [10, 7] |
| row_aliases | false | null |
| column_aliases | false | null |
| row_label_wrap | false | 18 |
| column_label_wrap | false | 13 |
| row_label_mode | false | "all" |

## figure_reference.plot_effect_distribution_forest

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| row_order | true | — |
| panel_order | true | — |
| panel_labels | true | — |
| limits | true | — |
| interval_label | true | — |
| count_label | true | — |
| p_type | true | — |
| size | false | [12, 9] |

## figure_reference.plot_facet_bubble_matrix

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| row_facets | true | — |
| column_facets | true | — |
| feature_order | true | — |
| window_order | true | — |
| value_label | true | — |
| size | false | [10, 8] |

## figure_reference.plot_strip_effects

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| panel_order | true | — |
| contrast_order | true | — |
| up_color | false | "#FF6A3D" |
| down_color | false | "#7CCD14" |
| eligibility_label | true | — |
| alpha | false | 0.05 |
| fc | false | 1 |
| size | false | [10, 5] |

## figure_reference.plot_aligned_tracks

R22. Domain-neutral aligned bar tracks and multiple matrix strips.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| category_order | true | — |
| track_order | true | — |
| matrix_order | true | — |
| block_order | true | — |
| matrix_labels | true | — |
| matrix_limits | true | — |
| count_label | true | — |
| size | false | [12, 7] |

## figure_reference.plot_surface_grid

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| axis_labels | true | — |
| value_label | true | — |
| limits | true | — |
| view | false | [32, -132] |
| size | false | [9, 6] |
| projection | false | "surface" |
| center | false | null |

## figure_refined_views.plot_refined_views

Compact GSEA, supplied nested ribbon, score shifts and association matrices.

| Parameter | Required | Default |
|---|---|---|
| view | true | — |
| contract | true | — |
| options | true | — |

## figure_study_overview.plot_transcriptomic_overview

A coherent main figure; complete companion results remain independently exported.

| Parameter | Required | Default |
|---|---|---|
| assay | true | — |
| contrast | true | — |
| independent_unit | true | — |
| denominator | true | — |
| matrix_label | false | "Row z-score" |
| panels | false | null |
| labels | false | [] |
| alpha | false | 0.05 |
| fc | false | 1 |
| embedding_axes | false | null |
| panel_titles | false | null |
| presentation | false | "basic" |
| ellipse_definition | false | null |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 3.9 |
| panel_height | false | 3.6 |

## figure_styles.plot_volcano_editorial

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| labels | false | [] |
| alpha | false | 0.05 |
| fc | false | 1 |

## figure_styles.plot_volcano_marginal

Circular-point volcano with count histograms of the same displayed genes.

| Parameter | Required | Default |
|---|---|---|
| labels | false | [] |
| alpha | false | 0.05 |
| fc | false | 1 |
| x_bins | false | 42 |
| y_bins | false | 36 |

## figure_styles.plot_enrichment_lollipop

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| score_type | true | — |
| denominator_label | true | — |
| count_label | true | — |

## figure_styles.plot_composition_panels

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| unit_label | true | — |
| y_max | false | null |
| ncols | false | "auto" |
| nrows | false | null |
| panel_width | false | 2.8 |
| panel_height | false | 2.9 |
| cloud_shapes | false | null |
| celltype_palette | false | null |

## figure_styles.plot_sample_distribution

See the fixed implementation and its input contract.

| Parameter | Required | Default |
|---|---|---|
| palette | true | — |
| y_label | true | — |

## figure_wgcna_views.plot_wgcna_view

Dedicated network diagnostics, identities and result meanings; adaptive facets.

| Parameter | Required | Default |
|---|---|---|
| mode | true | — |
| title | true | — |
| context | true | — |
| leaf_order | false | null |
| module_order | false | null |
| selected_power | false | null |
| fit_reference | false | null |
| probability_kind | false | "adjusted" |
| coefficient_semantics | false | "signed" |
| matrix_definition | false | "TOM" |
| track_labels | false | ["Dynamic modules", "Merged modules"] |
| columns | false | "auto" |
| preservation_guides | false | null |
| label_genes | false | [] |
| value_limits | false | [-3, 3] |
| diagnostics | false | "standard" |
| merge_reference | false | null |
