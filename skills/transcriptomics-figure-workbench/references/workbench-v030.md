# Unified figure workflow

The `workbench.py` entry separates discovery, preflight, drawing, appearance and review. Catalog discovery and input preflight use the standard library. Plotting dependencies load only for the selected render. Existing direct Python/R calls and `render_frozen_table.py` remain compatible.

## Discover and select

```sh
python scripts/workbench.py catalog --search raincloud
python scripts/workbench.py describe forest
```

The generated [renderer directory](renderer-directory.md) accounts for every Python plot function and its actual parameters. Canonical names and fixed aliases identify the same implementations. Function counts, visual families, source examples and compositions are separate dimensions. Source implementation does not prove current dependency runtime or scientific validity. Some legacy renderers retain internal colors without semantic replacement; their original appearance limits still apply.

## One selected FigureSpec

FigureSpec schema 1 has these fields:

| Field | Meaning |
|---|---|
| `schema_version` | `1`; unknown fields fail |
| `figure_id` | Stable safe ID; use a new ID for changed output |
| `renderer` | Fixed alias or catalog canonical ID |
| `input` | One local TSV `path`; optional SHA256, explicit numeric fields and bounded row/byte budgets |
| `parameters` | Required and optional drawing parameters from `describe` |
| `theme` | Existing complete project theme, including fixed category slots and semantic continuous scales |
| `provenance` | Source, input/experimental unit, contrast, denominator, model, limits, filtering, uncertainty, interpretation limit and explicit synthetic flag |
| `appearance` | Optional paper/compact/presentation/large-print typography, selected font and bounded size overrides |
| `export` | Optional `raster_dpi: 300` or `600`; `tiff: true` adds TIFF |

Numeric columns are parsed separately from identifier strings. Declare additional dynamic numeric fields when a canonical legacy callable uses columns that cannot be derived statically. String identities such as `001` remain strings. Preflight checks configuration, selected input bounds and source bindings; the chosen renderer still validates its specific row semantics before export.

Migrate a known saved style without modifying any source files:

```sh
python scripts/workbench.py migrate --input input.tsv --style style.json --meta context.json --theme project_theme.json --id F01 --output figure.spec.json
```

The selected saved style must match its registered callable. Incomplete provenance or a saved input hash mismatch blocks migration. Keep private specifications and project themes outside the installed skill.

## Preflight and render

```sh
python scripts/workbench.py plan --spec figure.spec.json --output figure.plan.json
python scripts/workbench.py render --plan figure.plan.json --output figures
```

Or explicitly draw directly from a selected spec:

```sh
python scripts/workbench.py render --spec figure.spec.json --output figures
```

Saved plans bind exact data, configuration and source versions. Changed bindings require a new preflight. Plans are private preparation records; they are not scheduler submissions. A completed render contains SVG, PDF, PNG, the exact plotted TSV, JSON provenance and environment versions; optional TIFF and raster DPI are verified separately. New bundles publish only after the complete export succeeds. Existing output and cooperative export locks are preserved. No automatic dependency installation, network request, model fitting or scientific inference occurs.

## Restyle and compare

The four profiles change typography rather than data encodings. The same project category map and continuous-scale roles remain. An explicit replacement card is made with the existing theme tool and reviewed across the whole project.

```sh
python scripts/workbench.py restyle --spec figure.spec.json --appearance appearance.json --id F01_v2 --output figure-v2.spec.json
```

Restyling produces a new spec. Re-render, compare actual exports and inspect the final size. The export receipt includes a quantitative geometry fingerprint so frozen-input style regression can be checked separately from visual quality.

## Offline Figure Studio

```sh
python scripts/workbench.py studio --output figure-studio.html
```

Open the generated HTML in a browser. Add `--gallery` with an explicitly selected repository gallery directory to include all historical examples; `--demo-svg` can embed one bounded synthetic figure. The installable package includes the Studio builder and assets, rather than downloading a gallery automatically.

Studio supports searchable callable/parameter discovery, complete stable-ID source browsing when supplied, local SVG import, font/size previews, before/after comparison, redraw settings, a draggable composition draft and export settings. It runs offline without starting a service. Imported SVG is bounded, parsed and checked for scripts, event handlers, active elements, processing instructions and external resources. Previews run inside script-disabled sandboxed frames. No private inputs are cached or uploaded. Loading a file is explicitly selected by the user.

The SVG editor changes text appearance only and checks other geometry. It does not infer unknown renderer settings or replace quantitative colors. Preset sizes and 300/600 DPI choices enter redraw settings; the SVG preview applies only font family and the separate text-scale control. Browser font availability, metrics and layout can differ from final export. Without a FigureSpec, export produces appearance settings only. Save downloaded specs beside the original spec so relative source paths retain their meaning.

Composition boards arrange complete preview panels and export a `LAYOUT_DRAFT`. Use the existing hash-verified [composition route](combinations-router.md) for final PDF/vector assembly. Preview arrangement is not final composition, a shared legend or shared scientific axes.

## Separate file, visual and scientific acceptance

```sh
python scripts/workbench.py review --bundle figures/F01
python scripts/workbench.py review --bundle figures/F01 --decision accepted --checks visual-checks.json --notes "Actual inspection scope and limitations" --output F01.visual-review.json
python scripts/workbench.py review --bundle figures/F01 --record F01.visual-review.json
```

The six explicit checks are `labels_readable`, `units_and_denominators_visible`, `guides_clear`, `no_clipping`, `color_roles_consistent`, `final_size_inspected`. Only record checks actually performed. The decision binds receipt bytes and exact exported files; changed or missing output makes it stale. Software verification is not visual inspection; neither establishes biological or statistical validity. A script that exercises acceptance behavior must label injected check values as a software fixture.
