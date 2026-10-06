# v0.2.2 validation scope

This increment addresses matrix input and label geometry. It does not replace
or regenerate the 244 archived source previews, the 40 saved compositions,
the 15 color cards, or the three public coordinate examples.

The shared matrix input layer accepts reviewed long tables and explicit wide
tables. It preserves identifier strings, validates complete row/column
orders, keeps row annotations separate from value columns, and records a
masked-missing policy only when the caller asks for it. Heatmap, dot,
confusion, aligned, polished, annotated, effect, association, activity,
palette-panel and multistate matrix routes derive labels and canvas geometry
from the supplied dimensions; row names are retained by default and long
names can be wrapped. Composite dashboards still keep their declared number
of semantic panels, while their internal matrix IDs are checked from input.

The new `tests/check_matrix_flexibility.py` covers a rectangular wide table,
renamed fields, explicit row/column reordering, aliases, long row labels,
row annotations, dot/confusion label flexibility, missing-cell rejection and
explicit masking. The existing
52-case incremental suite, 14 linked-display cases, color-card contracts and
package-preservation checks also pass. These are software and rendering
checks; they do not calculate clusters, correlations, enrichment, WGCNA
modules or any biological result.

The installed public files were synchronized to v0.2.2 after backing up the
previous installed copy. The private `references/lps-profile.md` remains
outside the public package and was preserved byte-for-byte.
