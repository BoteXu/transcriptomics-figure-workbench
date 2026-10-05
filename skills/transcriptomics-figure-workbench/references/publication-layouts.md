# Reference-led publication layouts

Use when a user asks for polished, coherent figures rather than isolated color changes. Five original table-based families in `figure_publication.R` and `.py` extend, not replace, the existing marginal volcano and provenance/export contract. No third-party code or copyrighted figure is bundled.

## What to learn from the supplied examples

- Aligned module heatmap, module strip, gene-count bar, composition stack: one row identity and order across panels. Side values must be supplied and named; gene counts, enrichment overlaps and cell proportions are not interchangeable. Display a dendrogram only when an actual upstream tree/linkage and its metric exist. Do not add a fake tree or silently recluster.
- Orange/purple square and circle matrices: offer `geometry='tile'` or `'bubble'` with identical input, order and color limits. Bubble area is **constant** in this adapter, not a second statistic. Use the separate core dot adapter when area must encode detection. A row z-score is not an expression fold change; scaling is upstream and recorded, never automatic.
- Single-cell atlas composite: reuse one stored embedding and one cell set for identity/feature panels; add an independently sourced marker matrix. Do not recreate separation, crop rare cells, redraw cluster contours as boundaries, or substitute smoothed density for measured expression. Zero-value background is light grey; positive values use a readable sequential palette, not a rainbow by default.
- Multi-model ROC: compact square axes, thin unsmoothed steps, grey chance diagonal, concise model/AUC legend below or beside the plot. AUC supplied from the frozen evaluation, not recalculated by the renderer. PR uses pre-step for increasing recall or post-step for decreasing recall; ROC uses nondecreasing FPR and post-step. Verify step area against supplied non-interpolated AP; reversing row order requires changing the step convention. No direction flipping or performance-driven color/order selection.
- Radial abundance plot: optional supplementary presentation of a small fixed feature list only when it clarifies paired profiles. Both conditions need the same explicitly named transform/scale and missing-vs-zero rules. Connecting unrelated genes does not make them a pathway; log2FC should be a separate signed band or external mark, not a fabricated common radial unit. Retain a linear matrix/dot companion. Current implementation status: design-only, not an executed radial renderer.

## Default design choices for this requested redesign

White/ivory background; charcoal text; references/outlines `#B8BEC5` rather than black; orange `#E98B2A`, purple `#7562A5`, teal `#2D9C95`, blue `#4B88B5`. Signed matrix: purple → ivory → orange with exact explicit center and limits. These are user-selected colors, **not a claim of tested color-blind accessibility**; add labels/line styles. Constant-area matrix bubbles must have a color key, not a spurious size legend.

Compact titles describe the question. Put model details, evidence caveats and interval definitions in the gallery/caption, while retaining short essential labels on the image. Shorten labels only through a recorded mapping; no unnamed categories. Long uncertain cell labels may use stable cluster IDs with a full companion table. At publication scale inspect title/legend separation, axis labels, tiny cells and dense panels. A larger blank canvas does not fix unresolved hierarchy.

## Renderer contracts

Source/import core before the R module; Python module imports the core. All functions return stamped figures and use the core immutable bundle exporter.

1. `plot_publication_curve`: model,x,y complete finite [0,1] curves in frozen threshold order; `curve_type` ROC/PR, `labels` includes supplied AUC/AP values, PR `prevalence` required. Steps are explicit; function checks the expected x direction. It does not fit/evaluate a model.
2. `plot_aligned_matrix`: feature,sample,value complete finite unique grid, explicitly named `value_label`, `limits`, `center`, `signed`; optional feature_block and row_count must be constant per feature, row_count nonnegative integer. `block_palette` required for block strip. Count bar uses supplied counts and true zero baseline, with a caller-specified `count_label`. All rows/panels share frozen first-occurrence order. No scaling, missing filling, thresholding or clustering.
3. `plot_publication_forest`: label,group,estimate,lower,upper; finite ordered bounds containing estimate, palette per group and `effect_scale` declared. Adds subtle group spacing and supplied numeric estimates. Range, IQR and CI remain caller-specified, never auto-labelled as CI.
4. `plot_feature_facets`: cell_id,x,y,feature,value; complete cell×feature grid and exactly matching coordinates across features. Nonnegative values, one global explicit [0,max] color range, original points, no smoothing. Point order is zero background then positive in original order and recorded. Use separate calls for independently meaningful gene scales and state their limits. Python rasterizes dense point layers; text remains vector.
5. `plot_raincloud`: sample_id,group,value; `unit_label` mandatory and unique observation IDs. Half KDE + narrow Tukey box + **all** raw points; no new p-values. Only groups with n>=20 and >=5 distinct values get a cloud, n>=5 a box; smaller groups show points. This is a conservative template display rule, not statistical sufficiency. Python uses Scott bandwidth, R nrd0; disclose differing bandwidths and do not claim pixel-equivalent densities. Both restrict display to observed min/max and normalize width within group, so cloud width does not encode sample size. Raw n remains visible. Cells/captures are not automatically independent animals. Prefer raincloud for distributions, not ROC, correlation, forest estimates or six seed-overlap observations. Zero-inflated RNA requires visible zero points and a separate detection-rate plot; KDE is descriptive, not a measurement model.

## R and Python examples

```r
source(file.path(skill_dir,'scripts','figure_core.R'))
source(file.path(skill_dir,'scripts','figure_publication.R'))
p <- plot_aligned_matrix(tab, value_label='Supplied row z-score',
    limits=c(-2,2), center=0, signed=TRUE, geometry='tile',
    count_label='Module genes', block_palette=module_palette)
# Existing values outside limits are rejected, not silently saturated.
# Use export_figure(p, tab, new_output, new_id, real_meta).
```

```python
from figure_publication import plot_publication_curve, plot_aligned_matrix
fig = plot_publication_curve(curves, palette, curve_type='ROC',
    labels=frozen_labels, title='LPS classification')
fig = plot_aligned_matrix(table, value_label='Raw-positive cells (%)',
    limits=(0,100), signed=False, geometry='bubble')
```

## Official examples and code checked 2026-10-01

| Source | What was adopted | Status |
|---|---|---|
| [ComplexHeatmap linked panels](https://jokergoo.github.io/ComplexHeatmap-reference/book/a-list-of-heatmaps.html), [bar annotations](https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html#barplot_annotation) | row alignment, actual side summaries, separate legends | official docs/code checked; local adapters newly authored |
| [Seurat visualization vignette](https://satijalab.org/seurat/articles/visualization_vignette) | feature/identity/marker panel information hierarchy | official docs/code checked; no reanalysis or source data copied |
| [scCustomize analysis plots](https://samuel-marsh.github.io/scCustomize/articles/Gene_Expression_Plotting.html) | meaningful expression palettes and panel clarity | official docs checked; optional native package not executed |
| [sklearn display examples](https://scikit-learn.org/stable/auto_examples/miscellaneous/plot_display_object_visualization.html) | separate data/statistics from display objects | official docs/code checked; frozen curves only |

User attachments were visually inspected in the chat, not treated as source statistics. The supplied `.dat` begins with GIF89a: file extension alone does not identify code or analytical data. It is a visual reference, not a basis for inference. Upstream website PNG links were located, but code/document review is not labelled as a screenshot inspection. Current software tests and actual result QA belong in validation.md; do not claim a reference package was executed merely because these independent adapters pass.
