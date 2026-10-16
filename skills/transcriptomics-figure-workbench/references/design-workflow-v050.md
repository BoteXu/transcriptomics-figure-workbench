# Question-led design and target-size review

## DesignBrief v1

`workbench.py design --brief brief.json --output new-design.json` uses only the standard library. Input is one selected local TSV (at most 5 MiB / 20,000 rows / 250 fields) with its exact SHA256. The output is a source-bound, non-executable recommendation; it neither creates a FigureSpec nor verifies statistical values.

Exact top-level fields:

```json
{
  "schema_version": 1,
  "question": "Which supplied pathway scores differ across the displayed conditions?",
  "structure": "matrix",
  "input": {"path": "scores.tsv", "sha256": "REPLACE_WITH_ACTUAL_SHA256"},
  "roles": {"row": "pathway", "column": "sample", "value": "score", "row_group": "programme", "column_group": "condition"},
  "context": {
    "frozen_results": true,
    "independent_unit": "One independent donor per named sample; declared in the source receipt",
    "denominator": "All selected donor samples; no count denominator for these scores",
    "uncertainty": "No interval supplied; descriptive score display only",
    "upstream_qc": "reviewed",
    "selection": "Prespecified pathways; all selected rows retained",
    "missingness": "Complete selected grid; no imputation"
  },
  "target": {"width_mm": 178, "minimum_text_pt": 7, "medium": "paper"}
}
```

Structures: `differential_expression`, `enrichment`, `effects`, `matrix`, `embedding`, `network`, `overlap`, `paired`, `profiles`, `survival`, `uncertainty`. Current additions: `curves`, `score_comparison`, `associations`, `contributions`, `imaging`, `estimation`, `model_evaluation`, `rank_stability` (nineteen structures total). Every mapped role names an actual selected field. Read `figure_workbench/design.py` for the exact candidate-role list. A `HOLD` has explicit blocking reasons and no preferred design. The QC field is a caller declaration; it is not independently verified by the planner. Candidate compatibility is necessary, not sufficient: renderer contracts still check real values, full grids, test status, scales and identities.

Prefer the attractive compatible candidate, review the actual example, then construct the exact FigureSpec parameters shown by `describe`. Guidance labels such as `editorial / forest` must be translated to that renderer's documented `kind` or options, not blindly copied into parameters. Existing `method-spec` remains the fixed package-binding route. Source changes invalidate saved execution plans.

## New frozen display alternatives

All use `renderer: publication_plus`, `parameters: {view, contract, options}`. `contract` requires the same complete source/unit/denominator/value/uncertainty/synthetic definition as the editorial renderer. Contract and provenance synthetic flags must match.

| View | Required table fields | Exact options besides `title`, `subtitle` |
|---|---|---|
| `halfeye` | `record_type,label`; `density` rows: `x,density`; `summary` rows: `estimate,lower,upper,inner_lower,inner_upper` | `order,interval_definition,reference,x_label` |
| `split_matrix` | `row,column,value,row_group,column_group` | `row_order,column_order,limits,value_label` |
| `profile` | `record_type` equal to `profile`, `category,series,value,area` | `category_order,series_order,area_max,area_label,value_limits,value_label` |

Half-eye accepts 1–12 named distributions, increasing supplied coordinates, nonnegative density and exactly one nested interval summary per label. A common density-height factor preserves relative supplied heights; there is no KDE or normalisation to unit area. Interval probability/type comes from the caller. The synthetic example's illustrative inner/outer bounds are not claimed to be 50%/95% intervals.

Split matrix accepts a complete selected grid up to 40 rows × 24 columns, consistent contiguous supplied groups, exact display order and a signed colour range containing every value. It adds gaps and aligned category strips without clustering, scaling, filling missing values or selecting significant cells.

Profile accepts at most 40 categories × 4 series. All category/series cells must be present; every value fits the declared common range, and point area uses one positive common maximum. It displays the exact same R02 values in an aligned linear alternative without spline fitting or smoothing. The old radial source remains available.

The five examples and complete reusable FigureSpecs are in [the portable gallery](../assets/design-gallery/index.html). VIS04 and VIS05 reuse existing package renderers to improve a bar chart and a low-discrimination embedding; these do not add new algorithms.

## Physical-size gate

New FigureSpec export fields:

```json
"export": {
  "raster_dpi": 300,
  "tiff": false,
  "target_width_mm": 178,
  "minimum_text_pt": 7,
  "readability_policy": "block"
}
```

Widths must be finite 40–1000 mm and thresholds 5–30 pt. Choose the appropriate threshold for the intended publisher/medium. `block` requires an explicit width; if any essential declared text is smaller after scaling to that width, rendering raises `PRINT_SIZE_HOLD` before committing a final bundle. Reflow or redesign instead of merely increasing DPI. `warn` preserves legacy rendering and records the metric. Increasing DPI cannot fix physical text size.

The metric excludes explicit software badges and figure-level provenance footers. It measures declared Matplotlib font sizes, not glyph extents, contrast, occlusion or actual paper output. Export receipts retain the target and measurements. It does not silently change canvas, text, data or panel count.

## Target-bound visual record

The six checks remain `labels_readable`, `units_and_denominators_visible`, `guides_clear`, `no_clipping`, `color_roles_consistent`, `final_size_inspected`. Record only checks actually performed. Target-width exports additionally require:

```json
{"scope":"individual_at_target_width","width_mm":178,"artifacts":["png"]}
```

Pass this via `review --inspection inspection.json` with the checklist, notes, decision and a new output path. `width_mm` must match the export target. A contact overview, mismatched width, stale bundle or incomplete checks cannot be accepted. Notes identify a screen layout, vector review or actual paper proof; do not imply all three. Historical exports without an explicit target retain their historical review contract.

## Reference search and adoption

The following primary sources were consulted for design principles in this update:

- [ggdist slab/interval guide](https://mjskay.github.io/ggdist/articles/slabinterval.html): combine supplied distribution profiles and intervals with explicit interval semantics.
- [ComplexHeatmap split guide](https://jokergoo.github.io/ComplexHeatmap-reference/book/a-single-heatmap.html#heatmap-split): aligned row/column slices and annotations. This renderer uses supplied memberships, not the guide's optional clustering methods.
- [ComplexUpset examples](https://krassowski.github.io/complex-upset/articles/Examples_Python.html): aligned intersection displays and explicit denominator/annotation choices. Existing UpSet remains the implementation route.
- [GseaVis author manual](https://junjunlab.github.io/gseavis-manual/basic-usage.html#new-style-graphic): compact enrichment strata and direct annotations; existing 25 package examples remain preferred for GSEA.

These are independently implemented display ideas. No external figures or third-party code were redistributed, and no native R package runtime validation is claimed. The current search did not yield a newly readable WeChat article; no unread tutorial is presented as integrated code.
