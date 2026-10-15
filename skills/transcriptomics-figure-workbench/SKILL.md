---
name: transcriptomics-figure-workbench
description: Select, render, restyle, compare and audit scientific figures from frozen result tables. Use a source-derived renderer catalog, shared project themes, offline SVG previews, standalone panels and traceable compositions. Preserve supplied statistics, units, identities and geometry rather than rerunning analysis.
---

# Scientific Figure Workbench

Choose visual encoding by the data structure and intended comparison. Keep source values, independent units, denominators, missingness and supplied uncertainty explicit. Browse without requiring a dataset; formal drawing needs the selected table and provenance.

## Choose the work mode

- **Discover a figure:** use `scripts/workbench.py catalog --search <term>` and `describe <renderer>`. These commands do not import plotting stacks. The generated [renderer directory](references/renderer-directory.md) lists current signatures and counts; functions, fixed aliases and drawing families are different dimensions. Inspect a specific implementation's input contract before choosing it.
- **Render frozen results:** read [the unified workflow](references/workbench-v030.md). Select one FigureSpec, prepare a source-bound plan and render into a new output directory. `plan` is preflight only; actual files and receipt hashes establish completion. Table-specific semantic checks still run in the selected renderer.
- **Refine appearance:** preserve the selected category map and continuous-scale roles. Use one project theme, a named typography profile and a new figure ID. Compare quantitative geometry, then inspect actual final-size exports. Read [aesthetic controls](references/aesthetic-controls.md) for detailed legacy controls.
- **Use the rebuilt design or additional drawing modes:** read [the aesthetic rebuild](references/aesthetic-rebuild.md) and inspect its 12 actual examples. Six redesigned modes and six supplemental entries are implemented. The repository additionally supplies 400 individually inspected final exports with exact PNG hashes; see [full-atlas review](references/full-atlas-review.md). Text geometry checks do not replace visual review; retain separate source/uncertainty definitions and do not infer scientific analyses from the figures.
- **Explore interactively:** generate offline Figure Studio with `workbench.py studio`. Load a selected SVG and optional FigureSpec for text previews, before/after comparison and redraw settings. The publication-layout button uses the bundled inert-SVG finisher; its export remains unreviewed until actually inspected. An explicitly supplied gallery exposes all 260 historical source IDs. No service, private upload or automatic data cache is used. Previews remain unreviewed; unknown data/parameters are never inferred.
- **Compose panels:** retain each independent panel and its table. Use [combination contracts](references/combinations-router.md) and the existing hash-verified `compose_panels` implementation for final assembly. Studio's draggable board exports a layout draft only. Shared scientific axes and common guides need explicit identity/scale bindings.
- **Review delivery:** use `workbench.py review` for exact file checks, then record only visual checks actually performed. Changed exports invalidate prior visual acceptance. File integrity, visual quality and scientific validity are separate.

## Package and method entries

Use `workbench.py methods` and `method <entry>` for 25 fixed package/method bindings. Read [package/method routes](references/package-method-entries.md) for dedicated GSEA classic/overlay/facets, NES and leading-edge views, ORA bubble/lollipop and result bindings for enrichment, GSVA, DE, single-cell, WGCNA, communication, activity and survival packages. Native package analysis stays on the existing analysis host. Input/export summaries alone cannot reconstruct genuine ES curves.

## Select specialist input contracts as needed

The preserved [v0.2.5 routing map](references/legacy-routing-v025.md) provides the complete conditional route map. Read only the relevant reference:

- General data shape and visual meaning: [data-expression-router](references/data-expression-router.md).
- Matrices, labels, missing cells and ordering: [matrix-input](references/matrix-input.md).
- QC/DE frozen summaries: [qc-de-article-review](references/qc-de-article-review.md).
- Distribution, paired changes, effects, curves and useful combinations: [publication layouts](references/publication-layouts.md).
- Genomic, multiomic, spatial, model and computational-biology results: [analysis modules](references/analysis-modules-router.md), [multiomics views](references/course-visualization-router.md), [Biomni views](references/biomni-visualization-router.md).
- Networks, memberships and aligned tracks: [network expansion](references/network-expansion.md), [linked evidence](references/wgcna-visualization-router.md), [alignment](references/alignment-and-flow.md).
- Genuine protein coordinates: [protein visualization](references/protein-visualization.md); use an installed specialist viewer and declared chains/residues. A schematic is not an atomic model.

## Appearance and scientific invariants

Establish one selected palette, stable identity-to-color slots, font hierarchy and semantic continuous scales per project. The [15 color cards](references/reference-palette-guide.md) retain attribution and the documented C02 printed-value conflict. Do not cycle colors when capacity is insufficient. Apply an explicit replacement card through the existing theme tool, then inspect all comparable panels. Native/R automatic replacement remains limited to its actually tested adapters.

Paper, compact, presentation and large-print profiles adjust typography. SVG Studio text previews preserve other geometry; final redraw can change text extents and needs export inspection. Some legacy internal colors have no semantic adapter: retain or explicitly review them rather than guess their meaning.

Use supplied results and stored coordinates. Do not refit tests, FDR, models, embedding, clustering, enrichment or uncertainty for aesthetics. Unknown is not zero; a cell, spot or technical repeat is not automatically an independent subject. Legacy descriptive display operations retain their documented limits and host execution restrictions.

Follow the host's memory, computation and server rules. This skill does not authorize local scientific analysis, installation, remote dispatch or private uploads. Use the existing server route for scientific computation and large rendering. Keep private project profiles, original references, inputs and plans outside the distributable skill.

## Export and acceptance

New FigureSpec renders produce atomic bundles with PDF, SVG, 300/600-DPI PNG, optional TIFF, exact plotted TSV, provenance and environment versions. Saved plans bind exact source, data and settings. No overwriting existing figure bundles or automatic retry of an ambiguous operation.

Review actual outputs at final size for labels, units, guides, clipping, category/color semantics and readability. Preserve failure versions. Record the exact bundle hash and inspection scope separately from mechanical checks. Synthetic examples are labeled and never presented as scientific results.

Retain historical Python/R calls, all 260 stable previews, 42 actual compositions, auxiliary panels, 15 cards and original browser opinion keys. Follow [content preservation](references/content-preservation.md). Newly unified callable entries do not become new scientific methods. Current validation is in [v0.3 acceptance](references/validation-v030.md); earlier receipts retain their own scope.
