# Frozen-table visual polish

Implemented additive Python route: `scripts/figure_polish.py`. Import existing `figure_core.export_figure` for API-v2 bundles. Existing APIs and six multimodal families are unchanged.

Choose layout from data semantics, not a universal card style:

| Renderer | Frozen schema | Useful layout / limits |
|---|---|---|
| `plot_polished_matrix` | `feature,sample,value`: complete unique finite grid | `matrix` for contrasts; `blocks` for contiguous sample/time groups; `transpose` only after final-size review. Explicit `value_label`, `limits`, `signed` required; all values must fit. |
| `plot_recorded_evidence` | reversible union from `recorded_evidence_table(therapy,comedication)` | `aligned` shares labels; `table` prioritizes exact counts; `split` needs more vertical space. No risk/CI calculation. |
| `plot_availability_counts` | `display_cluster,reports,any_therapy_rows,nonempty_literature_reference` | Absolute report counts, exact availability numerator/n and explicit literature counts, including zero. Availability is not assigned duration. |

Matrix optional arguments: `row_aliases`, `column_aliases` map exact IDs to unique display labels; `row_blocks`, `column_blocks` cover every ID and must be contiguous in supplied order. No clustering/reordering. `layout`, `width_mm=180`, `font_size=8.5`, `title`, `note`, `sign_marks=True`. Negative-only minus glyphs supplement the signed color scale; they are not significance marks. Export exact alias maps beside the bundle when abbreviating. Do not use ordinal probe aliases without the map. Scales are sequential for magnitudes, zero-centered for signed effects; background detection P is not stronger expression. Heatmap cells remain vector polygons.

Evidence therapy columns: `cluster,denominator,single_complete_nonnegative_pair,missing_multiple_invalid_or_negative_dates,no_linked_therapy`; integer categories exhaust n. Medication columns: `cluster,comedication,denominator,any_role,suspect_role,status`; complete cluster/drug grid, matched n, `0 <= suspect <= any <= n`. `recorded_field_count` permits explicit zero. `index_drug_not_comedication` and `unavailable` require missing counts, rendered N/A and ? with hatching; never coerce to zero. `table_kind` is reserved by the reversible union. Keep source drug/phenotype/full scientific captions in provenance; display labels may shorten them with exact mapping. Reports are not patients; overlapping cluster memberships cannot become a pooled denominator.

```python
from figure_polish import plot_polished_matrix
fig = plot_polished_matrix(frozen, value_label='Stored log2 difference',
    limits=(-2, 2), signed=True, column_blocks=original_groups,
    row_aliases=exact_probe_aliases, title='Reviewed frozen contrasts')
# Supply the complete figure-contract metadata to existing export_figure.
```

Physical margins reserve space for titles, groups, tick labels, colorbar and notes. Width 150-240 mm and font 8-11 pt are guarded starting geometries, not guarantees for arbitrary labels. Match final publication width before accepting a figure. Long labels, many groups and translated captions still require inspection. Do not shorten scientific boundaries out of the deliverable: link full original captions while keeping on-panel notes concise. Test all eligible rows/counts/order and zero/missing semantics, not just visual style.

Design provenance (2026-10-02): [ComplexHeatmap official annotations](https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html), [scIB original paper](https://www.nature.com/articles/s41592-021-01336-8) Fig. 2, [Rougier et al., Ten Simple Rules for Better Figures](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833). Borrow hierarchy, alignment and scientific encoding; do not substitute publisher images for generated results. scIB Fig. 2 pixels and publisher CC BY 4.0 were checked in the prior source audit; the official annotations chapter was checked as documentation. This round copies no paper artwork/code. Article image rights do not follow software rights.

Run `python scripts/polish_test.py NEW_DIRECTORY` for explicitly synthetic fixtures. See [validation-polish-20261002.md](validation-polish-20261002.md) for actual scope/limits. This is a renderer-only route, not an analysis or clinical review.
