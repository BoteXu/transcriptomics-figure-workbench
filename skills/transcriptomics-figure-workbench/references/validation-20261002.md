# Validation and explicit limits: 2026-10-02 upgrade

## New implemented coverage

Six original Python-only frozen-table adapters in scripts/figure_multimodal.py; no new R equivalent is claimed. Shared Arial theme uses installed font, Okabe-Ito category colors, redundant shape/line encoding, explicit zero/ratio references and signed-value labels. Existing R/Python modules/signatures are unchanged.

The synthetic driver renders six new-family bundles plus same-input old/new heatmaps. It checks20 rejection cases, input immutability, global theme restoration, exact output/input SHA256, supplied point geometry, residue gaps and shared track limits. No scientific inference, training, simulation or project data rewrite.

Existing Python regression_test.py:18 refusal cases plus ratio reference, input/upstream hash checks, failed-export retry, preserving previous outputs and Unicode path/font passed. Existing R smoke_test.R:17 synthetic figures×6 files,9 refusal checks and output hashes passed. R4.4.2 issued historical LC_* C.UTF-8 startup warnings but exited0; no global locale or permissions changed.

## Actual export and visual review

Eight final bundles checked: exact TSV/hash, actual SVG XML text/path/image structure, actual one-page PDFs with embedded fonts/text and no text outside page bounds. Heatmap bodies may be embedded raster images inside SVG/PDF while labels stay vector; not all data marks are promised editable.

Six new layouts reviewed as actual PDF-page pixel contact sheet, original-PNG grayscale contact and actual SVG browser contact; before/after matrix and attributed gallery cover also viewed. Separate hash-linked visual_review.json records final scope. New exporter receipts remain RENDERED_UNREVIEWED and synthetic=true; software visual QA does not grant scientific validity.

MuPDF's SVG renderer initially mishandled CSS transparency, hatching, dashes and fonts. Its previews are marked limited and not used for acceptance. Actual SVG byte content was reviewed in installed Edge headless with a new isolated profile; no existing session/credentials read, no security flags/permissions changed. The first external-image HTML wrapper failed resource loading, then was corrected to inline the actual exported SVG bytes. Grayscale inspection found ambiguity of association sign; signed numeric labels were added. A final matrix preview showed its long sensitivity label touching the synthetic footer; an explicit display alias (saved in the receipt) fixed it without changing source IDs or values. Numeric label ink now chooses dark/white by relative luminance rather than a magnitude cutoff.

Final synthetic test directory is under the authorized task workspace: upgrade_20261002/release. Eight-page publication_gallery_v2.pdf includes source citations, six templates and identical-input before/after. Earlier tests_v1/v2/v3/tests_final/verified and intermediate galleries remain isolated and are not final acceptance evidence. Most example widths are double-column (~180mm); no single-column print/long-label/maximum-cardinality acceptance is claimed.

## Guidance-only / untested here

- Advanced native ComplexHeatmap objects, dendrograms/OncoPrint, complex networks and inferred regulatory edges.
- Raw BAM/bigWig/GTF/Hi-C adapters; genomic template accepts prebinned numeric disjoint intervals only.
- PAE/contact matrices, 3D structure/docking visualization adapters and new simulation outputs.
- New R equivalents, real multi-omics biological validation, arbitrary huge datasets/Chinese labels, validated CVD simulation and full journal-specific print checks.

Project-specific scientific profiles and exclusions stay private. Frozen-table plotting does not authorize upstream analysis.

## Recoverability and dependencies

Pre-upgrade backups, installation manifests and unchanged-file hashes were checked locally. Private output and installation paths are not required by the distributable skill.

Development used existing Python/R environments; no analysis packages were installed or upgraded. Core frozen-table adapters require matplotlib/pandas/numpy. PDF/gray review helpers additionally use PyMuPDF/Pillow. Font fallback and native objects need checks in each target environment.

Sources and permissions: [visual-sources-20261002.md](visual-sources-20261002.md). Schemas: [multimodal-patterns.md](multimodal-patterns.md). Historical validation is retained in [validation.md](validation.md).
