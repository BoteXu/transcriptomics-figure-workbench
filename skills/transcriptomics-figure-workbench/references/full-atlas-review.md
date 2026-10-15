# Full atlas: display finishing and actual self-review

Version 0.3.0 provides **400 reviewed display exports**, not 400 distinct methods: 260 stable main IDs, 32 auxiliary panels, 88 saved alternatives, 8 QC/DE panels and 12 redesigned/new examples. There are 274 single exports and 126 complete composition arrangements. Original historical images, tables, IDs, upstream attributions and browser opinion keys are retained.

## What changed

The bundled `assets/studio/publication-svg.js` finishes frozen local SVGs: light title hierarchy, dark body labels, compact provenance, external guide lanes and bounded outer whitespace. It rejects active/external SVG content. It does not fit models, recalculate tests, enrichments, embeddings, clustering or intervals. Source-coordinate primitives are fingerprinted. Selected semantic color changes and explicit layout moves remain in each receipt.

Specific repairs include matrix label layering over gutter links (M04), separated tracks (R22), a reorganized multi-view dashboard (R24), contrast correction (R02), tighter bounds (T02), controlled guide placement, and exact paired/forest redraws from their frozen source tables. The three public-coordinate protein previews reuse their original rendered pixels in a tighter frame. They are not new molecular renders. Palette cards preserve exact declared hex values, attribution and C02's documented RGB conflict.

Complete combinations retain independent units, color keys, source tables and physical panel scale. They do not infer shared scientific axes. The extreme nine-panel horizontal composition exceeded a Chromium texture boundary; bounded tiles now join at exact pixel positions without rescaling. This was found by inspecting the actual exported image, not a successful export receipt.

## Reuse

In offline Figure Studio, load one selected SVG and use **整理版式**. Compare original and current previews; download the SVG and unreviewed record. Unsupported diagrams may need a specific layout patch or a fresh redraw. Do not silently use a generic finisher as scientific provenance. FigureSpec source/parameter bindings remain separate.

For reproducible repository exports, `tools/prepare_full_figure_review.py` binds selected public SVG/table/metadata hashes. `tools/finish_public_vectors.mjs` and `tools/compose_public_vectors.mjs` use an already provisioned Playwright browser, block external requests and write fresh output directories. They never install dependencies. Set `FIGURE_PLAYWRIGHT_MODULE` or use an existing Playwright package. The tile join uses an explicitly selected existing Python/Pillow runtime through `FIGURE_IMAGE_PYTHON`. Serial memory admission remains the host's responsibility.

`tools/publish_reviewed_atlas.py` consumes an actual separately prepared inspection ledger, checks the exact final PNG/export hashes, copies the selected exports and emits portable records. It cannot establish that a human or agent really inspected an image; the inspection statement must be truthful. No auto-approval from successful rendering is allowed.

## Acceptance boundaries

- Every final PNG was individually opened for self-review; the final ledger binds the inspected image and associated SVG/PDF hashes. This is one agent's self-review, not independent peer review.
- Browser text bounds/overlap flags are advisory. A mathematical subscript can overlap bounding boxes without a perceptual collision; manual dispositions are retained.
- PNG exports declare 300 DPI. Browser cropping rounds CSS boundaries, so dimensions can differ from vector-page dimensions by up to one CSS pixel plus one raster pixel. No data geometry is rescaled to hide this.
- PDF checks cover readable one-page structure and page dimensions. They do not claim pixel-by-pixel PDF inspection, font availability on every computer, paper proofs or journal acceptance.
- Dense and extreme-wide layouts retain a large physical canvas. Shrinking the entire canvas to a journal column is not an accepted final-size layout. Select fewer panels or redesign for the target width and inspect again.
- All non-structure examples are software/display fixtures, not biological findings. The three protein images originate from a public structure. File integrity and attractive appearance do not establish scientific validity.
