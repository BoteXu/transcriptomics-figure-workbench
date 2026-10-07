# v0.2.4 rendering and preservation validation

This release retains the 244 v0.2.3 sources byte-for-byte and adds 14 standalone
result modes and two explicit compositions. The catalog has 260 stable sources,
72 drawing families, 26 composition entries, 15 color cards, three native public
protein examples and one supporting-table entry. Forty-two actual compositions
retain their individual tables, panels and hash bindings; all have horizontal
and vertical alternatives. The 108 Python functions and 28 historical R
counterparts are separate inventories, not a claim of scientific algorithms or
complete R parity.

Runtime, scientific-channel invariants, layout checks and manual visual review
are distinct. The full function inventory is exercised by
tests/audit_plot_library.py using bounded synthetic fixtures. It checks immutable
inputs, quantitative geometry, exact matrix/annotation centers and both page
orientations. The audit retains advisory warnings instead of calling the whole
library aesthetically or scientifically validated.

The independent flow test checks seven stages, both flow orientations, zero
amounts, shuffled paths and node/band quantity conservation. The matrix checks
use independently ordered cell identities and area/color values, exact
annotation and activity-track centers, and explicit shared-axis PDF alignment.
The five Biomni-view tests compare glyph heights, transformed contact values,
actual branch lengths, original pixels, checkerboards and signed differences.
The nine analysis-result checks compare arc widths to counts, PIPs to heights,
calibration support to counts, curves and matrix arrays to inputs, and waterfall
levels/bars to an independent cumulative sum. TSV replay and invalid inputs are
tested separately. Calibration and trajectories also accept more models/series
than their old example-specific limits.

Palette/typography replacement preserves coordinates and quantitative geometry.
Annotation categories use registered project colors. Default signed heatmaps
receive the signed project scale. A regression removes duplicate heatmap titles
before placing the title above annotation tracks. New splice transcript rows
receive physical space per row; junction lanes are explicitly supplied.
Dense matrix column and training run labels retain their supplied rotation and
font sizes while the canvas grows from measured label extents. Five focused
guide regressions reject tick/title overlaps, require immutable input and
unchanged quantitative geometry, and check repeated optimization does not grow
the canvas indefinitely. Updated historical previews are saved separately.

Saved previews use C06/Arial; portable tests use an explicitly available font
where configured. Software tests do not establish inference, original-reference
pixel equivalence, all possible label densities, clinical validity or upstream
Biomni/analysis-engine runtime. Formal use requires reviewed input semantics and
actual final-size export inspection. Private profiles, user reference pictures,
research data and Biomni runtime receipts remain outside the public package.
