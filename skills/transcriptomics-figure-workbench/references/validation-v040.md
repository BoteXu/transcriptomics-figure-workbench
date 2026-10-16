# v0.4 package display acceptance

All 25 fixed method entries have a new PNG/PDF/SVG example, exact source TSV, complete FigureSpec and output receipt. Eight GSEA/ORA examples are redesigned and seventeen previously unillustrated entries are completed. One callable renderer supplies fourteen display grammars (121 Python plot functions and 79 fixed aliases overall).

Each exact final PNG was visually inspected for layout, labels, legends, colour semantics and readability; changed images were re-inspected and unchanged image bytes hash-matched. Per-image notes and SHA256 values are in [self-review](../assets/package-gallery/self-review.json). This is subjective self-review, not user aesthetic approval.

Acceptance checks exact frozen cells and coordinates, dot areas, complete grids, GSEA channels, survival/risk alignment, single-page PDFs and 300-DPI PNGs. Malformed scientific display inputs are rejected. Studio browser checks exercise image selection and export/spec links for all 25 entries. CI repeats contracts on Windows/macOS/Linux and actual rendering on Linux. CI success is recorded by the workflow, not inferred from this document.

Native scientific engines were not installed or executed, no real dataset was analysed and no private data was uploaded. Synthetic rendering success is separate from native package runtime validation, biological inference and suitability for future inputs. Historical v0.3 reviews retain their own scope and files.

See [design/source ledger](package-styles-v040.md) and [package/method input contracts](package-method-entries.md).
