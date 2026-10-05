# A reusable visual system with semantic flexibility

Use scripts/figure_multimodal.py's THEME, CATEGORY, SIGNED, themed and axis as an additive Python theme, not global rcParams overrides. Use compatible explicit fonts, final-size type and project palette in R; existing R functions are unchanged.

- Start at180mm double-column or85mm single-column width and8-10pt text at final dimensions. The new examples target double-column; single-column must be rerendered and inspected, not blindly reduced. Give interval rows/long labels extra height; do not mechanically equalize all panels.
- White background, charcoal labels, restrained reference grid, consistent stroke weights and clear data-first hierarchy. Short display labels need exact source-ID mapping; no hidden relabeling of groups.
- CATEGORY uses Okabe-Ito hues, with markers/line types for redundant encoding. Signed effect/correlation uses blue-ivory-vermillion around a stated zero; nonnegative magnitude needs a sequential map. Category identity, effect and evidence are different scales.
- Use common limits on comparable panels, preserve extreme values and disclose transformations. Missing remains missing; neither clipped values nor synthetic error bars are acceptable.
- Prefer direct labels for a few focal features, small multiples for many categories and a table for long lists. Networks require interpretable edge evidence and fixed coordinates; hairball/chord/radar decoration is not a default quantitative design.
- Put panel letters outside data, align comparable axes, share semantic legends and leave room for captions. Caption unit, denominator, independent n, uncertainty, model/contrast, exclusions and interpretation boundary.
- View PNG plus actual PDF at final size; parse actual SVG text/vector elements and inspect a rasterization when available. Check clipping/legend collisions and grayscale readability. Palette pedigree alone does not establish every plot is accessible. This release includes grayscale previews, not a full validated color-vision-deficiency simulation.
- Never use a schematic/AI image as a measured or computed quantitative result. Synthetic fixtures must be conspicuously labeled and isolated from scientific releases.

Reference principles and source rights: [visual-sources-20261002.md](visual-sources-20261002.md). Practical table adapters: [multimodal-patterns.md](multimodal-patterns.md).
