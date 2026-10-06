# v0.2.3 validation scope

This incremental release follows the v0.2.2 matrix-input audit. It removes the
remaining fixed display caps found during a route-by-route scan: the activity
dashboard now labels every supplied column, the training dashboard derives
epoch ticks from the supplied data and displays every run label, and cohort
intervals scale to all supplied features and cohorts.

The changes remain rendering-only. They preserve source identifiers, use
explicit caller ordering, wrap long labels, and derive canvas dimensions from
the supplied data. They do not calculate cohorts, intervals, training losses,
or any biological result.

Validation includes `tests/check_matrix_flexibility.py`, package structure and
catalog checks, the 15 color-card contracts, linked/replay checks, the 52-case
incremental replay suite, Python compilation, and manual long-label rendering
inspection. The public installed copy is synchronized to v0.2.3 while the
private local profile remains excluded from the release archive.
