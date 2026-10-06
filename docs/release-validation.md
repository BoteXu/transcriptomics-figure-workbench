# Release validation and declared limits

Version 0.1.0 is a cleaned publication copy of the locally developed skill. Private scientific result profiles, local paths and runtime receipts were replaced with generic guidance; plotting source code and stable example identities were preserved.

The completed [publication-check.json](publication-check.json) records the actual checks: 50 navigation groups, all 168 stable previews, 15 cards, 68 Python plot functions, 47 unchanged script files, 909 linked catalog assets, skill-creator structure, 17 synthetic core bundles with 9 rejection cases, and an actual R05 CLI render from the public inputs. All 168 preview PNGs retained their exact bytes. All 204 pages across 181 sanitized PDF files retained identical rendered page pixels. The 24-page overview links all 168 IDs. This scope does not establish scientific validity.

The public gallery was also opened in a browser: the K07 composite image loaded, search returned the raincloud-related entries, and all 15 color-card options were visible. The original private-reference pane remains empty in the public data. Browser note export/import and every platform/font/native renderer were not newly exhaustively tested for this release.

Historical checks remain documented separately in the skill references. Current publication checks do not rerun the full R suite, every native renderer, every external package object or all statistical methods. All development previews are demonstrations; actual research inputs require their own source/design and visual review.

Core requirements are deliberately small. Pillow/PyMuPDF are optional review/composition dependencies; PyMuPDF's license remains separate. Fonts and native renderers are not distributed. The release smoke environment is one local Windows/Python environment, not proof of cross-platform or minimum-version acceptance.

Run `python tests/check_package.py` from the repository root for dependency-free structural and privacy checks. To exercise the plotting backend, use `python skills/transcriptomics-figure-workbench/scripts/smoke_test.py NEW_OUTPUT_DIRECTORY` in a prepared environment. That driver produces synthetic examples, not research results.

The downloadable skill ZIP includes only the installable skill, license/attribution and version information. The repository additionally contains the full public gallery and overview; user reference images and private runtime receipts are excluded.

## Subsequent release

This document preserves the v0.1.0 history. Previous v0.2.0 scope is [release-validation-v020.md](release-validation-v020.md); v0.2.1 scope is [release-validation-v021.md](release-validation-v021.md). Current checks are documented in [release-validation-v022.md](release-validation-v022.md).
