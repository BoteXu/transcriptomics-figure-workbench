---
name: transcriptomics-figure-workbench
description: Design, render and improve scientific figures for multi-omics, computational biology and computer modelling from frozen results. Choose complete, attractive forms by question and available channels, preserve values and identities, adapt single and multi-panel layouts, and inspect actual exports. Includes bulk/single-cell studies, networks, spatial data, structures, modelling and coordinated views.
---

# Scientific Figure Workbench

Turn selected, reviewed results into readable scientific figures. The original
name and calls remain compatible. Methods, domains, examples and layouts are
separate dimensions; different colours or datasets do not create new methods.
Preserve classic alternatives, historical IDs and private/customized profiles.

## 1. Establish the question and frozen result

- Obtain the selected table or coordinates, source version/hash, contrast,
  complete denominator, independent biological unit, units, missingness,
  selection rule and uncertainty/density definitions. Review upstream QC.
- Match the question and supplied channels to the form. A normal request needs
  a convincing main figure and complementary evidence, rather than a bare
  scatter or an indiscriminate catalogue dump.
- Keep statistics, coordinates, intervals, memberships, ordering and units
  fixed. Do not refit an embedding, FDR, enrichment, density, model, clustering
  or uncertainty to make a richer image. Missing analysis remains missing.
- Follow the host's computation and server rules. This skill does not authorize
  installation, local analysis, remote submission or private-data upload.
  Keep private profiles and project results outside the distributable package.

## 2. Load only the route needed

Commands below use `python scripts/workbench.py` from the installed skill root.
In the source repository prepend `skills/transcriptomics-figure-workbench/` to
`scripts/`. Discovery and preflight use the standard library.

| Request | Entry | Read when needed |
|---|---|---|
| Single form or cross-domain choice | `visual-library --search`, `forms`, `catalog`, `describe` | [Coverage](references/visual-library-coverage.md), [selection rules](references/comprehensive-selection.md) |
| Design using actual columns | `design --brief … --output …` | [DesignBrief](references/design-workflow-v050.md); candidates still need exact renderer mapping |
| Routine bulk / single-cell | `choose`, `study-plan`, `study-render` | [Defaults](references/publication-defaults-v096.md), [actual examples](assets/routine-gallery/index.html) |
| Alternative PCA, volcano, GSEA, raincloud or subgroup marker composition | Existing renderer's `presentation`, `mode` or `composition` | [Five families: exact calls and selection](references/transcriptomic-alternatives-v0140.md), [28 frozen examples](assets/transcriptomic-alternatives/index.html) |
| Full per-analysis package | `analysis-library`, `analysis-suite`, `analysis-render` | [58-chapter companions](references/analysis-companion-coverage-v100.md), [input protocol](references/analysis-companion-protocol-v100.md) |
| Package-specific plots / GSEA | `methods`, `method`, `method-spec` | [Package contracts](references/package-method-entries.md); native software and frozen-result rendering are separate |
| Workbench result/QC/source handoff | `handoff-plan` then normal `render` | [Exact handoff contract](references/connected-workflows-v0120.md#handoff) |
| Shared-identity interactive inspection | `linked-views` | [Coordinated views and examples](references/connected-workflows-v0120.md#linked-views) |
| Alternative linked displays and readable exports | `linked-views`, per-view `kind` | [Scatter, labels and supplied intervals](references/readable-choices-v0130.md) |
| Arbitrary assembly | `layout-plan`, `layout-export`, `layout-inspect` | [Flexible board](references/forms-v080.md#adapt-layout-at-use-time), [responsive layout](references/responsive-layout-v081.md) |
| Legacy, radar, 3D or animation | `visual-template --entry <ID> --output <fresh-directory>` | [42 upgrades and 3D](references/historical-and-3d-methods.md), [scale examples](assets/method-scale-gallery/index.html) |

The [complete visual library](assets/visual-library/index.html) spans the package;
the analysis library covers transcriptomics questions within it. Keep H01–H42,
D01 scatter3D, D02 volume, D03 trajectory, original Python/R calls, 260 stable
source IDs and attributed palettes. Group close forms under a parent while
preserving different scientific meanings and inputs. The [preserved detailed
guide](references/routing-guide-v0110.md) retains specialist routes and historical
review scope; open only the relevant sections.

## 3. Prefer richer compatible defaults

| Evidence | Preferred form when required channels are supplied |
|---|---|
| PCA | Stored coordinates, explained variance, defined supplied ellipses and marginal counts; complete sample/group/project guides |
| Differential expression | Complete tested universe, volcano/MA distributions, thresholds, aligned effect table and supplied intervals; keep nonsignificant genes |
| Expression / QC | Supplied raincloud geometry with every observation and independent-unit counts; classic box/violin remain alternatives |
| GSEA / enrichment | ES, hits, ranked metric, leading edge, NES/FDR, gene-set version and universe; complementary membership/redundancy and cross-contrast views |
| Single-cell annotation | Shared embeddings, per-subgroup location, multiple markers, specificity/fraction summaries and donor-aware composition/effects |
| WGCNA / networks | Input/sample QC, selected-power diagnostics, supplied hierarchy/TOM, module–trait and membership evidence, hubs, function and validation |
| Cross-omics / modelling | Explicit shared objects, matched scales and independent units; complementary effects, contributions, uncertainty, validation and coordinated views |

Preference depends on real channels. NES alone cannot supply an ES curve or CI.
For these five families, choose the compatible evidence/facet, landscape,
card/aligned, oriented raincloud or marker strip/card alternative described in
the [selection guide](references/transcriptomic-alternatives-v0140.md). Use the
actual example specs; preserve complete denominators and shared marker scales.
Cells, spots, frames, libraries and sample labels do not establish biological
replication. Keep one named category mapping throughout a project; do not cycle
indistinguishable identity colours.

Whole-study requests include every declared applicable frozen result and its
complementary views. An overview is insufficient for an analysis. Demonstrate
missing project sections only with clearly separated synthetic fixtures; never
use simulations to fill missing project evidence.

## 4. Render and adapt to actual content

1. Export a compatible template to a fresh directory. Edit FigureSpec using
   exact `describe` parameters and actual source metadata.
2. Run `plan --spec … --output …` or `handoff-plan`. These check contracts,
   hashes and bindings; they are not analysis or scientific acceptance.
3. Run `render --plan … --output …` in the existing authorized environment.
   Output is `RENDERED_UNREVIEWED` until actual images are inspected.
4. Adapt singles and compositions to counts, long labels and physical width.
   Use supported rows/columns, spans, cameras, pagination and reading pages;
   reject unsupported/conflicting settings. Do not truncate data to match an
   example or shrink text until it becomes unreadable.
5. Keep full guides, units and complete selected content. Near-identical
   heatmaps are extensions, not automatically separate main panels.

Use colour together with stable shapes or named/textual cues. Keep keyboard
focus distinct from selection. For linked inspection, use full object labels
only for a small explicit scope; interval views require supplied bounds and
their meaning. Redraw exports at the requested size rather than cloning a
narrow-screen panel. See [readable alternatives](references/readable-choices-v0130.md).

For 3D expose occlusion with companion projections. Volumes need a complete
uniform grid, units and explicit transfer functions. Trajectories need stable
atom identities, supplied bonds, alignment/PBC provenance and physical times;
playback fps is separate. Keep cameras/limits fixed across frames. Do not infer
bonds, conformers, MD or segmentation while styling.

## 5. Inspect actual exports and deliver

Inspect every changed single figure and composition at its intended final size.
Check complementarity, hierarchy, balance, whitespace, units, denominators,
clipping, overlap, legends, numerical lanes, contrast and identity. Inspect
small/large content and requested layouts. A contact sheet, font measurement,
successful process or hash cannot approve aesthetics. Revise failures and
inspect replacement pixels.

Use `review --bundle` for integrity and a separate visual decision with actual
checks, notes and matching width/artifact scope. Bind review to exact output
hashes. Changed input, code, size, layout or output bytes invalidate the
corresponding old review. Self-review is not independent review or manuscript
acceptance. See [review and delivery](references/workbench-v030.md).

Deliver the preferred preview, editable PDF/SVG, exact TSV, FigureSpec, sources
and receipts. Linked views include offline HTML, scope and input hash. Report
engineering, actual visual review and scientific acceptance separately. See
[content preservation](references/content-preservation.md) for upgrades.
