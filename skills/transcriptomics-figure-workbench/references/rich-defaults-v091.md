# Richer defaults for ordinary requests

The v0.9 study demonstration chose bare PCA and volcano displays even though
more useful extensions existed. Passing layout and file checks did not resolve
that presentation failure. v0.9.1 changes both actual examples and preference.

| Role | Preferred compatible presentation | Required scientific channels |
|---|---|---|
| Bulk PCA | Samples, explicit dispersion ellipses, marginal within-group proportions, supplied scree profile | Frozen scores, reviewed ellipse definition/geometry, complete checked bin counts and variance percentages |
| DE | Selected-label volcano plus stacked effect/FDR marginal distributions and count/percentage key | Same complete DE results, exact bin edges/counts, explicit unchanged thresholds |
| MA | Mean-effect scatter plus stacked marginal counts | Frozen means, effects, tested statuses and exact histogram summaries |
| Single-cell annotation | Identity embedding and ordered, grouped marker specificity | Reviewed annotations/label anchors, complete means/detection fractions |
| Per-subgroup markers | One scope per page: highlight plus multiple marker maps and all-identity specificity | Explicit focus/marker assignment, every cell, exact shared coordinates, common expression units/limits |
| Single-cell main | A coherent identity/evidence page, with donor response and composition as separate companions | Annotation evidence on the main page; donor denominators and independently supplied donor DE on their own pages |
| QC | Complete observations alongside sample summaries, with explicit group colours | Exact observations, metric units and sample-group mapping |
| Effect intervals | Aligned points/intervals and exact numerical columns | Frozen estimates and supplied uncertainty bounds |
| Batch coverage | Same-coordinate facets with complete background and batch counts | Fixed coordinates and explicit batch labels |

A simple display remains available when extra channels are absent or a user
asks for simplicity. Record that reason. Extra axes alone do not establish good
design: inspect their information value, balance, scale, colour meaning and
labels in the actual export. The study planner now exposes these presentation
decisions, and the question-led design planner ranks compatible richer options
ahead of a generic scatter or volcano.

## Scientific and implementation boundaries

- A dispersion/coverage ellipse is not a confidence interval for a mean or a
  test of group separation. The fictional fixture supplies reference geometry;
  no covariance estimate or inferential confidence region was fitted.
- Marginal bins are exact supplied display counts, checked against the complete
  points. No smoothing or KDE is introduced inside the renderer.
- Representative marker maps retain every supplied cell, unchanged coordinates
  and one expression scale. Marker identity/annotation is not inferred.
- Plausible marker names in the demonstration label fictional expression. They
  are not real experimental measurements or validation of an annotation.
- Drawing jitter is deterministic, horizontal and display-only. Sample summaries
  describe plotted observations; they are not donor-level statistical tests.
- Per-subgroup feature-map rows grow with the number of selected markers.
  `ncols` / `nrows` and physical dimensions reflow the same template; incomplete
  rows are centred and a narrow column gets vertically separated guides.

The crowded earlier candidate atlas was rejected after user review. See
[the explicit acceptance revision](editorial-acceptance-v091.md) and the actual
[per-subgroup pages](../assets/subgroup-gallery/index.html). Historical screen
records do not make that rejected arrangement a current preferred design.

## Sources actually consulted

The implementation is original, drawing on the already reviewed community
ledger and these author references. No third-party code was copied or executed:

- [Matplotlib ellipse example](https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html): ellipse geometry and explicit statistical meaning.
- [Seaborn joint-plot reference](https://seaborn.pydata.org/generated/seaborn.jointplot.html): separate main/marginal views and shared axes.
- [scCustomize analysis plotting](https://samuel-marsh.github.io/scCustomize/articles/Gene_Expression_Plotting.html): representative feature maps, deliberate point order and shared presentation.
- [ComplexHeatmap annotations](https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html): explicit annotation blocks and reserved guide regions.

Screen self-review, font measurement, independently reviewed biological
validity and calibrated paper proofs remain distinct. Recheck changed exports.
