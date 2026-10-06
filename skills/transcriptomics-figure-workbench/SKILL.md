---
name: transcriptomics-figure-workbench
description: Select, draw, restyle and export scientific figures by data structure and intended expression. Preserve distributions, volcanoes, forests, associations, marker views and useful combinations; support project-wide palette and typography, independent panels and computational-biology figures. Use frozen results rather than rerunning scientific analysis.
---

# Transcriptomics Figure Workbench

Serve the scientific question: identify what kind of data suits a figure and what it can express, then choose a clear visual encoding. Do not classify primarily by species, field or the original paper topic. Browsing a catalog does not require a real dataset; formal plotting requires the source and its semantics.

This is an additive workbench. Retain useful existing renderers, aesthetic variants, combined layouts and stable IDs. A feature retained in code but absent from the visible catalog is incomplete delivery. Check [content-preservation.md](references/content-preservation.md) before presenting an updated gallery.

## Choose an input and expression route

- Default gallery: [drawing-methods.md](references/drawing-methods.md), authoritative contracts in references/drawing-methods.json. The primary directory has 68 drawing families and 24 composition entries; each has exactly one primary preview plus meaningful modes. The 244 source IDs remain reachable through source archives and old deep links. Fifteen color cards, three native structure examples and one supporting table are separate library entries. Color, axis scale, labels, repeated facets and additional optional tracks do not create new drawing types. The old 45 broad G navigation groups remain compatibility routes only. See [consolidation-audit.md](references/consolidation-audit.md).
- Linked relationships and modules: [wgcna-visualization-router.md](references/wgcna-visualization-router.md). Membership curves, split-metric cells, rectangular/radial supplied trees and additive stacks declare exact frozen relationships and units. K37–K40 save both independent panels and compositions; K38/K40 are modes of the same module-results entry. No enrichment, WGCNA, network fitting or docking is executed.
- Reference fidelity: [reference-visual-language.md](references/reference-visual-language.md). Audit marks, encodings, guide meanings, alignment, layer hierarchy and composite relationships against the actual reference. State approximations and unavailable original inputs; a similar chart name or color does not establish fidelity.
- Additional relationships and pathway-facing views: [network-expansion.md](references/network-expansion.md). Nine original static adapters add typed networks, weighted ribbons, alluvials, UpSet, multiple-event matrices, supplied enrichment stacks, given ranks, hex counts and supplied contour fields. Do not rerun their upstream analyses.
- Combination input compatibility and the first 20 K examples: [combinations-router.md](references/combinations-router.md); the next 16 are in [extended-combinations.md](references/extended-combinations.md). Keep both standalone components and all 40 compositions; extend when the data relationship adds information.
- New frozen result structures: [methods-extension-router.md](references/methods-extension-router.md). Enrichment grids and member rings, ECDF/QQ, balance, agreement, survival/follow-up, specifications, supplied vectors, ternary, global/local position, effect precision, hierarchy area, nested intervals and model diagnostics each declare exact input and encoded quantities.
- Multiomics and course-derived routes: [course-visualization-router.md](references/course-visualization-router.md). Matched effects, view/factor variance, signed loadings, matched sample views, feature correlation circles, registered spatial overlays, supplied spectra/chromatograms, genomic links and pathway overlays retain modality/object/unit boundaries. Reuse matrix/curve/composition engines instead of inventing a method per scenario.
- Input shape → intended expression → required fields → interpretation boundary: [data-expression-router.md](references/data-expression-router.md).
- Flexible matrix input and output geometry: [matrix-input.md](references/matrix-input.md). Heatmaps, dot/confusion views, aligned/polished/annotated/effect/association matrices, activity and palette-panel matrices accept explicit IDs, orders/aliases, full row-name display with label-aware margins/wrapping, and an explicit masked-missing policy. They do not infer clustering or convert absent cells to zero; fixed composite dashboards retain only their declared panel semantics.
- Existing basic/refined forms: [aesthetic-controls.md](references/aesthetic-controls.md), [aesthetic-upgrades.md](references/aesthetic-upgrades.md), [publication-layouts.md](references/publication-layouts.md), [expanded-patterns.md](references/expanded-patterns.md), [visual-polish.md](references/visual-polish.md). Keep rainclouds, marginal stacked volcanoes, publication forests, feature facets and all earlier variants discoverable.
- Supplied references R01–R25: [reference-patterns-20261005.md](references/reference-patterns-20261005.md), exact contracts in references/reference-patterns.json. figure_reference.py adds 19 frozen-table functions; figure_process_dashboard.py adds one process composite.
- Independent applications T01–T43: references/panel-patterns.json and [project-style.md](references/project-style.md). These are 43 reviewable panels covering 21 structures, not 43 algorithms. A palette poster is not the default figure layout.
- Protein coordinates: [protein-visualization.md](references/protein-visualization.md). Use actual PDB/mmCIF and explicit model/assembly/chain/residue selections in the installed structure viewer or existing PyMOL. A schematic silhouette is not an atomic structure.
- Earlier specialist routes: [catalog.md](references/catalog.md), [code-recipes.md](references/code-recipes.md), [multimodal-patterns.md](references/multimodal-patterns.md). Preserve all 42 historical scenario routes and their DOC/CONDITIONAL limits. Keep private project context outside this package; the optional contract is [lps-profile.md](references/lps-profile.md). Public paper-derived guidance is [tls-hnscc-visuals.md](references/tls-hnscc-visuals.md).

## One editable appearance configuration per project

Establish one selected base color card, a stable group-to-color dictionary and one font family/size hierarchy in project_theme.json. All comparable panels read this file. Preview C06/Arial is an example, not a selection for a real research project.

Read [reference-palette-guide.md](references/reference-palette-guide.md) and references/reference-palettes.json: seven supplied cards explicitly titled 科研配色方案 plus eight attributed Tol/ColorBrewer cards. Ordinary plot colors remain appearance references. Preserve C02's printed Hex/RGB conflict. Label independently designed continuous extensions separately from original card colors.

Use project_theme.render_panel for single panels; render_project_panels.py reads one frozen-table manifest and one theme. set_project_theme.py saves a replacement card/font to a new file; re-render the same manifest in a fresh directory. Identity slots stay fixed across subsets and reordered rows. Never cycle colors when category capacity is inadequate.

Continuous colors have separate sequential/signed roles, limits and centers. The same metric keeps the same range across comparable panels; different units need their own range. Font/color replacement cannot change coordinates, data-encoded point areas, matrix order, cutoffs, values or intervals.

Existing R/Python calls remain compatible. render_with_theme maps explicit category arguments and reference semantic roles; unknown internal legacy/native colors need a declared adapter. Do not claim every R/native backend has been tested for automatic replacement. The 43-panel route and 52 new standalone frozen-table examples have actual replacement and geometry checks; native labels need backend-specific font support. render_frozen_table.py supplies 43 fixed adapters and preserves string identities separately from numeric fields.

## Independent panels and useful combinations

Keep individual panels editable and available. Also keep: categorical embedding + marker matrix/feature facets; volcano + stacked marginal counts; forest + numbers; scatter + marginal distributions/fit/residuals; heatmap + hierarchy/counts/annotations; contribution facets + supplied shares; training curves + runs + diagnostics; process schematic + structure/supplied surfaces/counts.

Compose when panels share meaningful identities, scales or complementary questions. Each panel retains its own table and guide. compose_panels.compose_bundles arranges hash-verified single-page bundles in an explicit layout and checks common theme; it does not infer alignments or merge legends. Both separate and combined forms belong in the catalog.

All40 saved composition layouts and component bindings are in references/combination-recipes.json. compose_catalog_examples.py rebuilds the reviewed gallery sources by explicit IDs or --all. render_saved_components.py redraws the32 registered auxiliary panels from exact shipped tables, separately from the244 source previews. Use one project theme when redrawing components; compose newly exported bundles only after data, font and theme checks.

Reserve distinct space for data, legends, colorbars and annotations. Legends must not cover points, bars, curves or uncertainty bands. Use an outer guide lane or separate legend region; long labels may need wider canvas or faceting. panel_layout_audit.py checks guide/canvas and guide/data-region bounding boxes. Inspect actual exports for titles, annotations, colorbars and contrast too. Repeat after replacing fonts/sizes.

## Scientific invariants and export

Read [figure-contract.md](references/figure-contract.md) for formal figure work and [visual-system.md](references/visual-system.md) for final-size design. Establish units, comparison, denominator, exclusions, uncertainty definition and source version. Missing input blocks only that panel; unknown is not zero. Cells, spots and frames are not automatically independent subjects.

Use provided statistics and stored coordinates. No silent model fitting, tests, selection, imputation, clustering, enrichment or trajectory reconstruction for aesthetics. Existing descriptive raw-point summaries are documented; they are not formal inference. Preserve negative findings, original cutoffs and all eligible rows.

figure_core API v2 exports PDF/SVG/300dpi PNG, exact TSV, provenance JSON and session; it checks stamped input/hashes and rejects caller-written input_hash and overwrite. Native structures retain their own render receipts. Synthetic examples, software checks and visual acceptance do not establish scientific truth.

Large computation/downloads stay in the separately authorized shared server workflow. Figure work does not authorize installations, training, simulation, uploads or jobs. Review external code before execution; preserve attribution/license. User reference images remain private and outside the installable skill.

## Validation and complete delivery

Inventory: 100 Python plot functions, including all 95 previous functions and five new linked-display functions. The 28 historical R counterparts remain. Preserve all 244 stable previews, 40 actual compositions, 32 auxiliary panels, 15 pure color cards and three public atomic-coordinate examples. The primary directory has 92 drawing/composition entries; function, source, preset, composition and library counts are different dimensions.

Current scope: [validation-v022.md](references/validation-v022.md). Previous scope: [validation-v021.md](references/validation-v021.md), [validation-v020.md](references/validation-v020.md). Earlier checks: [validation-reference-20261005.md](references/validation-reference-20261005.md), [validation.md](references/validation.md), [validation-20261002.md](references/validation-20261002.md), [validation-polish-20261002.md](references/validation-polish-20261002.md), [validation-increments-20261005.md](references/validation-increments-20261005.md). External skill increments: [external-increments-20261005.md](references/external-increments-20261005.md).

Run checks proportional to changed behavior. Smoke/regression, reference_validation.py, review_exports.py and build_gallery.py retain their roles. Inspect actual PDF/raster exports at intended size, fix clipping/occlusion and keep failed versions. Record exact reviewed hashes; software tests are not visual acceptance.

Deliver the complete visible catalog, standalone/combined previews, requested exports, exact rows, shared appearance settings, captions and a separate review record. Do not show only newly added graphs. Check coverage against the baseline and every supplied reference before calling the update complete.
