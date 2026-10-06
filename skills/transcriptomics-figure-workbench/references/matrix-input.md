# Flexible matrix input

Matrix figures use the same data contract regardless of whether the source is
an expression matrix, an association table, an enrichment grid, a loading
table, or another reviewed result. The renderer receives a rectangular set of
row IDs, column IDs, and numeric cell values; it does not calculate the matrix.

The shared Python input layer accepts either of these forms:

```text
long:  row_id | column_id | value
wide:  row_id | value_column_1 | value_column_2 | ...
```

For a wide table, pass `row_field` and, when the table contains annotations,
an explicit `value_columns` list. This prevents count, group, batch, or other
metadata columns from being mistaken for matrix values. For a long table, pass
`row_field`, `column_field`, and `value_field` when the source names differ
from the defaults (`feature`, `sample`, `value`).

`row_order` and `column_order` are optional display orders. If omitted, the
first appearance in the input is retained. If supplied, each order must
contain every ID exactly once; rows or columns are never silently dropped and
no clustering is inferred for presentation. `row_aliases` and
`column_aliases` change only display labels and must cover every ID with unique
nonempty text.

Complete grids remain the default contract. If a cell is genuinely absent,
use `missing='mask'` to show it as an absent/masked cell and preserve the
absence in the figure specification. Missing values are not converted to
zero. An incomplete table with the default `missing='error'` is rejected so a
plot cannot imply a measured zero or a complete comparison.

The heatmap, annotated/aligned/polished matrix, effect matrix, association
matrix and multistate matrix routes all derive canvas size from the declared
number of rows and columns. Row names are shown in full by default; long names can be wrapped
with `row_label_wrap`, and the canvas margin grows with the longest displayed
name. `figsize`, cell-size and label-size controls are available where labels
need more room. Labels can be hidden only with an explicit `*_label_mode` or
`show_labels=False`, and that choice is stored in the figure specification.
Matrix dimensions, identifiers, order and missing-cell policy are recorded in
the exported figure specification and can be replayed from the same table.
