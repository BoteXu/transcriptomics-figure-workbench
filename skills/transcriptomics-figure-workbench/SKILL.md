---
name: transcriptomics-figure-workbench
description: Design, render and improve publication figures from frozen scientific result tables. Prefer polished examples that match the research question, preserve statistical channels and identity, check the intended physical size and record artifact-bound visual review. Includes omics, enrichment, effects, networks, distributions and traceable multi-panel figures.
---

# Scientific Figure Workbench

## Start with the comparison and a polished example

Identify the comparison the reader should see, the supplied data shape and the intended use (paper, slide or screen). **Prioritize attractive, restrained examples with readable labels and clear visual hierarchy.** Use the [five current design alternatives](assets/design-gallery/index.html) and [25 package examples](assets/package-gallery/index.html) before searching the historical catalog. Offer one preferred design and at most two useful alternatives. A different palette or repeated layout is not a new scientific method.

| Intended comparison | Preferred display | Required distinction |
|---|---|---|
| Differential expression | Selected-label volcano; short declared feature set as point/interval forest | Effect, adjusted probability and uncertainty are separate channels |
| Enrichment across contrasts | Aligned NES dot matrix; term lollipop for ORA | NES differs from ES; size differs from significance; missing tests remain explicit |
| A genuine enrichment curve | ES + hit barcode + rank metric; facets for many pathways | Requires supplied full curve and ranked universe, not only an enrichment summary |
| A matrix with known groups | Split annotated heatmap; expression dot matrix when fractions matter | Fixed order/groups, units, colour range, fraction denominator and missingness |
| Distribution and uncertainty | Supplied half-eye + intervals, or a point/interval forest | A density requires supplied coordinates; no new KDE, intervals or tests for styling |
| Paired observations | Sparse paired points/lines | Only connect the same independently identified unit |
| Stored embedding | Restrained category palette and explicit label anchors | Preserve coordinates; a cell is not an independent donor |
| Dense graph or many memberships | Adjacency / membership matrix; aligned UpSet | Preserve edge and intersection definitions; do not prune to make a nicer network |
| Profiles with many categories | Aligned linear small multiples | Prefer to overlapping radial fills for precise comparison; retain a radial alternative when requested |
| Multiple panels | Few balanced panels with independent exports | Check the actual page width; provide a component reading view for oversized layouts |

Respect a user-selected design. These defaults guide choices when no design was specified; scientific compatibility is mandatory. Do not manufacture missing channels or change selection thresholds for appearance.

## Workflow

### 1. Establish the frozen input and scope

For formal drawing, obtain one selected table, source version/hash, biological independent unit, denominator, contrast, missingness, selection and uncertainty definitions. Upstream QC must already be reviewed. If these are unresolved, prepare a design proposal and mark the dependency; do not present a final research figure as accepted. Browsing examples requires no private data.

Follow the host's memory, computation and server rules. This skill does not authorize local research analysis, package installation, remote dispatch or upload. Keep private profiles, inputs, drafts and plans outside the distributable skill.

### 2. Prepare a question-led design

Use `scripts/workbench.py design --brief <DesignBrief.json> --output <new-plan.json>` for a source-bound recommendation. Read [the design workflow and schemas](references/design-workflow-v050.md). This standard-library step checks the selected TSV, explicit semantic roles and context; it returns `HOLD` or compatible candidates. It does not certify numerical/biological validity, create a FigureSpec or run inference.

Use `catalog --search`, `describe <renderer>`, `methods` or `method <entry>` for exact callable contracts. [The generated directory](references/renderer-directory.md) comes from shipped source; discovery imports no plotting dependencies. Design view names are guidance until mapped to that renderer's exact parameters.

### 3. Bind and render the selected design

Prepare a complete FigureSpec and a fresh `plan`; `plan` is preflight only. For new publication work declare `export.target_width_mm`, `minimum_text_pt` and `readability_policy: block`. The policy checks essential text at that physical width before writing a final bundle. A font-size measurement cannot certify appearance.

Use `render --plan` into a fresh directory. Source, table, settings and renderer identities must still match. Actual outputs and receipts establish completion. A blocked size gate means reflow, fewer selected panels with explicit selection, a larger target, or a component reading edition; do not silently shrink or discard data. Preserve failed versions and never overwrite existing bundles.

### 4. Improve appearance without changing the results

Use one project theme and consistent category-to-colour slots. Prefer restrained teal/coral/slate accents, dark text, fine neutral guides, direct labels and a dedicated guide lane when they suit the selected data. Use a sequential ramp for nonnegative magnitudes and a declared centred diverging ramp for signed effects. Avoid encoding many identities with nearly indistinguishable shades. Palette capacity must cover all identities; do not cycle colours.

Keep supplied statistics, coordinates, intervals, ordering, membership and units fixed. Do not refit FDR, embedding, clustering, enrichment, density or confidence limits for aesthetics. Reuse existing renderers and change presentation in a new version. Use `restyle` for allowed appearance fields; compare quantitative geometry and input hashes. Legacy colours with unknown semantics need an explicit mapping review.

For source SVG finishing, use Studio's inert-SVG finisher and explicit source-bound patches. It preserves graphical primitives while allowing text spacing, consistent colours and bounded decorative-opacity changes. Its output is unreviewed until actually inspected. No external SVG content is fetched.

### 5. Inspect all exports in scope

Separate three records: file/encoding checks, visual inspection, and scientific interpretation. Screen every selected figure; enlarge dense or flagged figures and inspect all changed outputs individually. A contact sheet can find broad problems but cannot establish small-label or final-size acceptance. Keep the actual inspection scope and PNG hash; do not copy old review claims onto changed bytes.

At intended size inspect hierarchy, labels/units, legends, clipping, overlap, category/scale meaning, point/line contrast and panel balance. Use the offline [review browser template](assets/studio/review-browser.html) through the repository's generated review gallery for original/revised comparisons, native pixel zoom and component reading. Do not infer shared axes merely from aligned panels.

### 6. Record and deliver

`review --bundle` checks file hashes. A visual decision needs the six actual checks and notes. For target-width bundles, `--inspection` must identify the inspected artifact types, individual scope and matching width; contact overviews cannot become acceptance. Source/export changes invalidate the corresponding bound record. A self-review is not an independent second review or paper proof.

Deliver a preferred preview, editable PDF/SVG, exact plotted TSV, FigureSpec and receipts. State material limitations and what was actually inspected. Keep `RENDERED_UNREVIEWED`, `FILES_VERIFIED`, `MEASUREMENT_PASS`, visual acceptance and scientific acceptance distinct.

## Specialist routes and compatibility

- Package views and GSEA contracts: [package/method entries](references/package-method-entries.md), [package styles](references/package-styles-v040.md).
- New half-eye, split matrix and linear profile contracts: [design workflow](references/design-workflow-v050.md).
- Matrix ordering/missingness: [matrix input](references/matrix-input.md); QC/DE: [frozen summaries](references/qc-de-article-review.md).
- Genomics, multiomics, spatial and model results: [analysis modules](references/analysis-modules-router.md), [multiomics](references/course-visualization-router.md), [Biomni views](references/biomni-visualization-router.md).
- Networks, memberships and tracks: [network expansion](references/network-expansion.md), [linked evidence](references/wgcna-visualization-router.md), [alignment](references/alignment-and-flow.md).
- Composition: [combination contracts](references/combinations-router.md). Final hash-verified assembly uses `compose_panels`; Studio's draggable board is a draft.
- Protein coordinates: [protein visualization](references/protein-visualization.md). Reuse a specialist viewer; a schematic is not an atomic model.
- Legacy controls: [routing map](references/legacy-routing-v025.md), [aesthetic controls](references/aesthetic-controls.md), [unified commands](references/workbench-v030.md).

Retain the original Python/R calls, 260 stable source IDs, historical images and opinion keys, 42 compositions, auxiliary panels and attributed colour cards. Preserve customized/private profiles during upgrades. See [content preservation](references/content-preservation.md), [v0.5 review scope](references/validation-v050.md), [v0.4 acceptance](references/validation-v040.md) and [v0.3 acceptance](references/validation-v030.md). Historical validation keeps its original scope.
