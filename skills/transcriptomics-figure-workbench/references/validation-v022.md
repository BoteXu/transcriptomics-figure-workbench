# Validation v0.2.2 — flexible matrix inputs

Scope: input normalization and final-size label geometry for matrix-style
renderers. This is software and rendering validation, not biological result
validation.

Verified with the repository's configured Python environment:

- `tests/check_matrix_flexibility.py`: long and wide tables, renamed fields,
  explicit row/column orders, aliases, row annotations, masked missing cells,
  and long row names; PASS.
- `tests/check_increment_runtime.py`: 52 existing frozen examples, theme
  replacement, geometry replay, identifier round-trip and negative contracts;
  PASS.
- `tests/check_linked_runtime.py`: 14 linked-display examples and negative
  contracts; PASS.
- `tests/check_package.py`: 244 preserved source examples, 15 color cards,
  100 Python renderers and 1,387 catalog assets; PASS.
- `tests/check_color_cards.py`: 15 card contracts, including continuous-color
  preservation under font-only replacement; PASS.

The new matrix layer accepts explicit long or wide inputs and records the
resolved field names, row/column IDs, aliases, display orders, dimensions and
missing-cell policy in the figure specification. It retains input order when
no order is given. It does not infer clustering, calculate associations or
replace absent cells with zero. The shipped reference PNG/PDF/SVG/TSV bytes
were not regenerated or rewritten for this increment.
