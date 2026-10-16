# Data-dependent layout and fresh visual review

## Single figures

FigureSpec accepts an optional `layout` object. Studio exposes physical canvas width/height and facet rows/columns when exporting a redraw configuration. The actual renderer must support the requested arrangement: a layout field must never be silently ignored.

```json
"layout": {
  "columns": 3,
  "panel_width_inches": 4.2,
  "panel_height_inches": 3.8
}
```

Native GSEA facets, stored-feature facets, sample-composition facets and palette plates derive rows from the complete selected panel count. With `columns: "auto"` and explicit `rows`, columns are derived instead. Explicit insufficient capacity is rejected. GSEA facets retain a complete ES curve, hit rug, rank metric and supplied NES/FDR for every pathway. The package and refined GSEA routes use the same dynamic facet implementation.

Heatmaps derive dimensions from their actual row/column identities; label wrapping and cell size remain renderer parameters. GSEA NES/leading-edge matrices, package heatmaps/dot matrices and editorial matrices no longer enforce the removed small example-grid limits. Input completeness, explicit missingness, effect units, colour limits and supplied uncertainty remain required.

`width_inches` and `height_inches` work through the common render path. `size_policy: "grow"` (default) allows additional space for real guides and records the actual size. Use `size_policy: "block"` when an exact requested canvas must be respected; an unreadable fit is rejected. `wrap_labels` retains full tick text with line breaks. Native `axis_groups` may reflow explicitly declared complete axes groups, including colour bars/insets. All axes must be covered exactly once. Figures with unowned figure-level annotations must use complete source SVG panels rather than guessed annotation ownership.

Automatic point size for stored-feature facets depends on the actual point count. Automatic facet height respects the stored coordinate aspect. Sample-composition facets default to a common zero-based range covering every supplied fraction; `y_max: 1` explicitly retains a 100% range. The denominator still includes all supplied cell types. These are presentation rules, not new biological analyses.

Method roles are still meaningful: paired displays require complete pairs, a single-pathway classic GSEA view has one pathway, and scientific axes/colour bars are not independent panels. Palette capacity, explicit input/resource budgets and backend-specific scientific contracts remain enforced. For a historical dashboard with a fixed semantic arrangement, render complete supported components and assemble the requested layout; do not imply that every legacy signature accepts arbitrary arguments.

## Compositions

`layout-plan` / `layout-export` support count-driven grid layout, unequal columns, explicit spans/positions and row-based pagination. Explicit positions are reserved before automatic placement, including positions declared later in the request.

For mixed tall/wide complete panels, set `packing: "masonry"`. Heights follow each full SVG's aspect ratio. `packing_order: "tall_first"` balances columns; `"input"` retains insertion placement. `label_order: "reading"` assigns automatic panel letters in reading order; explicit labels are retained. Masonry does not combine with fixed rows, spans, row heights or row-based pagination; these use grid packing. A rejected combination must be corrected explicitly.

Masonry is useful for exploration and mixed aspect ratios. A strict aligned scientific comparison may need grid rows, common physical axis sizes and explicit coordinate alignment instead. Source SVGs, scales, legends and exact tables remain separate and intact.

## Inspect after every layout change

1. Confirm every selected identity, point/curve, interval and required guide is retained.
2. Render the actual output. Inspect full figures and each composition page; enlarge dense labels.
3. Check title hierarchy, label readability, collisions/clipping, guide placement, panel balance, aspect ratio and excess blank space. Improve and rerender failures.
4. Bind screen review to the final SVG/PNG hashes. Check the final physical size separately when selected. No old review transfers across changed bytes.

For a native export use the existing `review` workflow. For complete SVG layouts, `layout-inspect --bundle <folder> --record <review.json>` checks the exact current receipt, output files and source hashes against an explicitly performed screen-review record. An inspection command does not itself establish visual approval.

## Actual recheck scope

The public `examples/responsive-v081` fixtures contain 14 single-figure exports: four matrix/long-label layouts, 1/5/7 feature facets, 2/5/9 pathway GSEA facets, 2/7/13 composition facets and a 41-row forest. Four composition configurations produce six pages: one panel, four mixed panels with natural heights, an asymmetric arrangement and eleven complete panels across three pages.

All 20 complete images were actually viewed on screen after the relevant repairs. Screen images may be resized; this is not exhaustive native-pixel review, calibrated paper proof or independent scientific validation. The v0.8 gallery's 458 earlier screen reviews retain their exact earlier scope; this recheck does not pretend that every one of the 124 callables was executed across every possible data volume.

Changed historical renderer sources are retained byte for byte as non-executable text in `source-archive-v080`, with their original hashes. Old receipts identify those old sources; they do not validate a changed current renderer. Current source identities invalidate old execution plans.
