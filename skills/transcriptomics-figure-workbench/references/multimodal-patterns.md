# Frozen tables for computational biology and multi-omics

New module: scripts/figure_multimodal.py (Python only). Uses existing matplotlib/pandas/numpy and API v2 export_figure; no extra packages. Existing R/Python functions and commands remain compatible. Read [figure-contract.md](figure-contract.md) first.

| Question | Adapter / exact table columns | Required semantics and limits |
|---|---|---|
| Effect consistency across cohorts | plot_cohort_intervals: feature,cohort,estimate,lower,upper | palette, effect_scale, effect_label, interval_label. Same contrast/units; complete unique grid, max16 features/6 cohorts. Ratio uses log axis/null1. No pooling or invented intervals; list unavailable estimates separately. |
| Multi-omics association | plot_association_matrix: feature,modality,status,value,q,n | value_label, method_label; optional alpha. Frozen correlation [-1,1], FDR[0,1], matched independent-unit integer n>=3. Explicit full grid max24x12. status='unavailable' requires value/q/n missing and is hatched. No FDR calculation/imputation; dots mean supplied q<=alpha. |
| Probability calibration and support | plot_calibration_counts: model,bin_left,bin_right,predicted,estimate,lower,upper,n | palette, interval_label, evaluation_label. Frozen sorted disjoint bins; probabilities/bounds[0,1], integer n>0. Counts use actual bin edges, within each model. No ECE/CI computation/rebinning or fitting. Pair with frozen ROC/PR and prevalence. |
| Genome-locus signal | plot_interval_tracks: track,start,end,value | palette, assembly, chromosome, region=(start,end), value_label; coordinate_system='zero_based_half_open'. Prebinned sorted disjoint integer intervals wholly inside region. Comparable units/common y limits. Unprovided intervals remain gaps. No BAM/bigWig/GTF/Hi-C parser; use official pyGenomeTracks for those in an existing environment. |
| Computational dynamics | plot_frozen_dynamics: series,time,estimate,lower,upper | palette,time_label,value_label,unit_label,interval_label. Sorted unique time per series, comparable units, supplied bounds; no smoothing/statistics/simulation. Frames are autocorrelated; separate independent starts/repeats unless frozen upstream aggregation is defined. Caption RMSD alignment/reference and equilibration. |
| Local structure confidence | plot_residue_confidence: residue,plddt | sequence_label with chain/isoform/version; sorted unique integer 1-based residues, pLDDT0-100. Residue gaps stay disconnected. Neither experimental B-factor, dynamics, affinity nor interdomain orientation. No PAE/3D renderer. |

All adapters accept title. Export the exact original input table; aliases on tick labels must have an explicit saved ID mapping. The Python theme decorator avoids global rcParams changes.

Example (metadata requirements remain in figure-contract.md):

    from figure_multimodal import plot_cohort_intervals
    from figure_core import export_figure
    fig = plot_cohort_intervals(table, palette, effect_scale='log_ratio',
        effect_label='log2 fold change', interval_label='Upstream 95% CI')
    export_figure(fig, table, new_output_root, 'cohort_effects_v2', meta,
        source_file=source_path, expected_source_sha256=source_hash)

## Reuse existing implementations

- Complex heatmaps: plot_annotated_heatmap / plot_aligned_matrix provide frozen order, annotation strips and numeric scales. For actual dendrograms, assay-specific matrices, OncoPrint and advanced legend packing use ComplexHeatmap official APIs. Never invent a tree or recluster each compared panel.
- Single-cell composition/state: plot_composition_panels uses complete sample-resolved counts; plot_feature_facets preserves stored coordinates and common expression limits. Pair cell views with animal/donor summaries. No new differential abundance/state inference.
- Pathway/regulation: frozen ORA/NES lollipop and effect/FDR matrices. Prefer sender×receiver/regulator×target matrices for dense edges. Networks need frozen positions, signed weights, selection universe, direction evidence and isolated-node handling. Correlation gets no regulatory arrowheads. No new network-layout or inference adapter.
- Generalization: compatible frozen cohort metrics with intervals and existing ROC/PR. Record split units, cohort/model/protocol IDs, prevalence, assay shift, confidence method and unavailable cohorts. Fold repeats are not independent subjects; never tune on test sets or invert scores for prettier AUC.
- Structure/docking: route real 3D coordinates to structure-viewer/PyMOL. PAE needs residue-pair matrix/chain boundaries/Å units; contacts need distance definition. Computational docking scores are not measured affinity. Apply fgf18-screening-visualization's R1/R2 and independent-start rules only when that project is selected.

## Representative validation

python scripts/multimodal_test.py NEW_OUTPUT_DIRECTORY creates six labeled synthetic template bundles, a same-table synthetic before/after heatmap and a PDF gallery. Inputs are deterministic software fixtures, not simulated scientific results. review_exports.py checks actual output hashes, SVG text/path structure, PDF fonts/page text and renders PDF pages for pixel inspection. Visual review is separately recorded; file checks do not confer scientific approval.

Read [visual-system.md](visual-system.md) for theme/layout decisions, [visual-sources-20261002.md](visual-sources-20261002.md) for primary references and rights, and [validation-20261002.md](validation-20261002.md) for actual tested coverage and limits.
