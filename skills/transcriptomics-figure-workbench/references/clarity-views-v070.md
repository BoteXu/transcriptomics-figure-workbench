# Readable dense figures and additional views

Use fixed alias `clarity`, with `view`, `contract` and `options`. These independently implemented displays accept frozen tables. They do not run SHAP, DABEST, dcurves, segmentation, registration, model evaluation or ranking. [Actual examples](../assets/clarity-gallery/index.html) include editable exports and complete FigureSpecs.

## Choose the comparison

| View | Frozen fields | Intended use and important limit |
|---|---|---|
| `profiles` | `group, x, y` | Fine lines and small markers retain every vertex; direct terminal labels. Monotonic x, explicit reversed or forward x limits, no baseline shifts or smoothing. |
| `effects` | `record_type, panel, row, value`; summary `lower, upper, p, count_text`; instance `effect_id` | Two aligned panels, all instance values, separate supplied summary/interval and count/raw-p lanes. Instance jitter only separates marks within a row. No pooling or density estimation. |
| `contribution` | `unit_id, class, feature, contribution, feature_value` | One complete selected class per export, all declared features and instances. Colour means supplied feature value, not significance. Hash-based row jitter is not a beeswarm density or scientific coordinate. |
| `shares` | `class, feature, value` | Complete rectangular share matrix with one scale and readable numbers. Does not derive shares from contribution points or renormalize them. |
| `membership` | `record_type`; member `member_id, effect`; term `term_id, label, block, ratio, padj, count`; link `member_id, term_id` | Crossing ribbons replaced by a binary matrix, member effect strip and term statistics. Grey means no declared link in this selected complete input, not biological absence. Counts/ratios/FDR are supplied. |
| `pixels` / `mode: slices` | `view, u, v, intensity, label_id` | Three complete regular physical grids with categorical overlays. Labels have an explicit key; background is 0. `label` from the old E41 fixture is renamed `label_id` in the typed input, without changing values. |
| `pixels` / `mode: registration` | `u, v, fixed, registered` | Compact 2 × 2 fixed/registered/checkerboard/difference display. Shared intensity range, separate signed difference range, exact pixel centres. Subtraction and checkerboard selection are display operations; no registration or performance estimation. |
| `estimation` | `record_type`; observation `unit_id, group, value`; one summary `value, lower, upper`; density `x, density` | Independent observations next to a supplied effect interval and density. The two axes have separate declared scales. No bootstrap, KDE, tests or new effect estimation. This is not an axis-aligned native Gardner–Altman implementation. |
| `decision` | `series, x, value` | Stored threshold probability/net-benefit curves with two explicitly declared supplied baseline strategies. No benefit calculation, threshold selection or smoothing. Population, outcome, horizon and benefit unit must be declared upstream. |
| `precision_recall` | `series, x, value` | Stored recall/precision vertices, each in [0, 1]. Define positive class, evaluation set, prevalence and threshold convention upstream. No AP/AUC calculation or claim of clinical utility. |
| `rank_stability` | `feature, cohort, status, rank, lower_rank, upper_rank` | Complete feature × cohort grid. `reported` rows need supplied rank and span; `unassessed` rows must leave them empty. Explicit NA, fixed feature order, no new ranking or stability statistic. Rank spans are not automatically confidence intervals. |

These are ten selectable modes, including two arrangements of physical pixels. Fifteen actual examples contain eleven redesign/detail exports and four additional task views. Variants, classes, modes and scientific algorithms are not interchangeable counts.

## Exact options and runnable examples

Every mode requires nonempty `title` and `subtitle`. Use the following exact additional fields; unknown keys are rejected. See each example's `inputs/<ID>.spec.json` for full values and a populated unit/source contract.

| Mode | Additional option keys | Example |
|---|---|---|
| profiles | `group_order, x_limits, y_limits, x_label, y_label` | CLR01 |
| effects | `row_order, panel_order, panel_labels, limits, interval_definition, count_definition` | CLR02 |
| contribution | `class_label, feature_order, value_limits, effect_limits, effect_label, value_label` | CLR03–CLR07 |
| shares | `class_order, feature_order, share_limits, denominator` | CLR08 |
| membership | `member_order, term_order, effect_limits, denominator` | CLR09 |
| pixels | `mode, view_order, label_names, intensity_limits, difference_limits, tile_pixels, coordinate_labels, orientation_definition` | CLR10–CLR11 |
| estimation | `group_order, value_limits, effect_limits, value_label, effect_label, interval_definition` | EXT01 |
| decision | `series_order, reference_series, x_limits, y_limits, x_label, y_label, evaluation_definition` | EXT02 |
| precision_recall | `series_order, x_limits, y_limits, x_label, y_label, evaluation_definition` | EXT03 |
| rank_stability | `feature_order, cohort_order, rank_limits, interval_definition` | EXT04 |

Orders must cover all identities in the selected table. Preserve the original table and record selection before splitting a dashboard into separate exports. Five R11 class tables together preserve all 6,650 original contribution rows; CLR08 preserves all 45 original shares. Colour and jitter do not authorize a scientific interpretation. Physical image grids must remain complete; no filtering pixels to improve appearance.

Curve views require increasing stored x positions. This dedicated PR mode requires strictly increasing recall; retain repeated-recall vertical segments through the existing `figure_core.plot_curve` PR route rather than deleting vertices.

Publication examples declare 178 mm width and block essential font sizes below 7.5 pt. Font measurement, actual individual visual review and scientific interpretation have separate records. A nominal screen width does not establish a calibrated paper proof. Original wide dashboards and their warnings remain available.

## Source and attribution ledger

Reviewed on 2026-10-16. Text and authored examples below informed channel selection and layout. No upstream code, data, reference screenshots, model weights or fonts were copied into the package. The implementation is original; no native backend execution is claimed.

- [SHAP authors: beeswarm documentation](https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/plots/beeswarm.html): read per-instance contribution, feature-value colour, ordering and custom-colour sections. Adopt separate value/effect channels and complete class exports; do not recompute SHAP or its default ordering. This implementation uses deterministic row jitter, not SHAP's density stacking.
- [DABEST authors: basics](https://acclab.github.io/DABEST-python/tutorials/01-basics.html): read independent observation/effect distribution separation and the upstream interval workflow. Adopt the separation; accept the density and interval as frozen input. No DABEST code or bootstrap inference is reproduced.
- [Daniel D. Sjoberg and dcurves contributors: decision curve tutorial](https://www.danieldsjoberg.com/dcurves/articles/dca.html): read binary-outcome strategy comparisons and baseline definitions. Adopt explicit supplied baselines and readable guide lanes. Native smoothing and benefit calculation are not run.
- [scikit-learn contributors: Precision–Recall example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html): read the distinction between the displayed curve and computed average precision. Adopt separate recall/precision axes; stored vertices only, without an AP label.
- [Nilearn contributors: plotting guide](https://nilearn.github.io/stable/plotting/index.html): read multi-view/tiled arrangements and overlay guidance. Adopt explicit physical coordinates and separate intensity/label guides. The demonstration grids are procedural and are not anatomical scans.

Fine profiles, the binary membership reflow and rank-span facets are independently designed from the existing frozen-channel contracts. These sources are references, not an assertion that any one author's style is optimal for every dataset.
