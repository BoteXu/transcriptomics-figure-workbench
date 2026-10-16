# Existing forms, consolidated extensions — v0.8

Start with [the consolidated gallery](../assets/forms-gallery/index.html). It contains 90 base entries, including one composition entry and two reference entries. These are navigation groups, not a count of scientific methods. All 458 existing exports remain addressable: 332 standalone images and 126 compositions. This release adds no independent chart type.

## Choose a form, then an extension

- Heatmap: one entry, with grouping gaps, transpose, supplied tree, annotations, side summaries, cell values and two-metric displays nested below it. Thirty-six source examples retain their own scales and units.
- GSEA: one entry, with classic three tracks, overlay, aligned facets and a continuous rank strip. Preserve supplied ES, NES, FDR, hit locations, leading-edge meaning and the ranked universe.
- Forest: one entry, with linear/log axes, grouping and numeric columns. A ratio and a difference are not interchangeable because the layouts resemble each other.
- Repeated bars, curves, donuts, gates and palettes: different datasets or colours are examples of an extension, not independent entries.
- Composition: balanced, horizontal and vertical layouts share one entry. Dense dashboards have a single separate entry with named source examples.

The source list is collapsed by default. A legacy ID, such as `PKG22` or `T30`, opens its exact example within the shared form. Existing Python functions and aliases are preserved.

```
python scripts/workbench.py forms --search heatmap
python scripts/workbench.py form heatmap
python scripts/workbench.py form PKG22
```

`form-catalog.json` is the maintained mapping. Each form has `variants`; each variant has `example_ids` and a preferred example. `extensions` stores the exact source-bound examples for compatibility. These fields describe presentation. Original FigureSpec and renderer contracts still govern execution.

## Same-form finishing

Studio's **同图型美化** accepts a selected inert SVG. It standardizes text hierarchy, quiet framing and spacing while checking that graphical primitives are retained. The 458 shipped revisions also include explicit complete-panel reflows for R04/R11/R16/R24, the visible geographic frame repair for T02, and smaller nonquantitative identity markers for T35. The latter does not alter any of its 1,080 stored curve vertices.

The finisher preserves quantitative colours and sizes whose semantics cannot safely be inferred. It does not recompute clustering, density, inference, enrichment, FDR or embedding. Unsupported structures can fail closed; a rendered preview remains unreviewed. Styling cannot repair an incorrect input or scientific model.

Literal label-retention checks cover all 332 standalone sources, including NES/FDR, units, denominators and interpretation notes. Compositions embed the revised source components with scientific captions intact. The component hashes identify which revision was assembled.

## Adapt layout at use time

Examples do not fix the number of rows, columns, genes, samples, pathways or groups. Inspect the actual input and supported renderer parameters; do not silently select a fixed top-N, trim categories or manufacture missing cells to match an example. Historical dashboards are frozen reference compositions, not a promise that their original renderer accepts arbitrary input. Use complete dynamic components and the flexible compositor when the requested arrangement differs.

Studio's board supports any selected column count up to its resource bound, automatic columns, unequal column weights, panel row/column spans, explicit positions, preferred panel height and a row limit for pagination. Select local SVG files to produce a hash-bound layout request; a thumbnail-only reference board remains a draft. Save the request beside its selected source files.

```
python scripts/workbench.py layout-plan --request layout-request.json --output selected.plan.json
python scripts/workbench.py layout-export --plan selected.plan.json --output fresh-layout
```

The standard-library exporter produces actual vector SVG pages and a source-bound receipt. It does not require a local scientific stack. PDF/raster export remains a separate rendering step; the repository's two actual layout demonstrations include rendered SVG/PDF/PNG pages. `examples/layout-v080` demonstrates a large panel spanning two rows and two columns, and seven panels automatically paginated across two pages. These are arrangements of existing forms, not new chart types.

Request fields: `canvas_width_pt`, optional `canvas_height_pt`, `columns` (integer or `auto`), optional `rows`, `column_weights`, `row_heights_pt`, `gap_pt`, `padding_pt`, `max_rows_per_page`, and `panels`. A panel supplies `id`, relative `svg`, optional exact `sha256`, `label`, `row_span`, `column_span`, optional zero-based `row`/`column`/`page`, optional `height_pt` and an exact plotted `table`. A fixed height can make text too small; target-size review remains required. Overlap, insufficient capacity, changed sources and active/external SVG content are rejected. A separately exported legend can be placed as its own panel; source-internal legend movement needs its renderer's supported controls.

## Inspection and delivery

All current images have a bound screen-review record. Every complete image was viewed separately framed in a bounded sheet; selected dense figures were enlarged further. This is screen inspection, not calibrated paper proof, exhaustive native-pixel text inspection, independent second review or scientific acceptance. Target 178 mm remains **unassessed** for the new library; earlier size warnings remain in the archived records.

Use the full library's offline browser for original/current comparison, native-pixel zoom and exact SVG/PDF/table/receipt links. The installable skill contains compact public preview pixels; editable full bundles are available in the release. For manuscript use, select the final physical width, reflow dense panels and inspect the actual final export.

Upstream attribution, exact tables and historical renderers remain intact. Private profiles are outside the distributable package and must be preserved when installing an update.
