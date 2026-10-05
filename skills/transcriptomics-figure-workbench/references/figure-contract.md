# Scientific figure contract

## Required before rendering

Record source path/checksum, input unit, annotation version, comparison, independent unit, inclusion/exclusion rules, displayed denominator, numeric scale, upstream model, FDR family and interval meaning. Required caller metadata keys: source,palette,input_unit,experimental_unit,contrast,denominator,model,limits,filtering,uncertainty,interpretation_limit,synthetic. Text fields must be nonempty. API v2 computes input_hash from the exact UTF-8 TSV bytes; never supply it manually. For file-backed results pass source_file and preferably expected_source_sha256; the receipt separately records the upstream file hash. A table hash identifies the table, not the unprovided upstream file or validity of a model. Keep missing different from zero; a threshold-filtered gene is not a negative result. Display only estimable comparisons.

- RNA-seq count, estimated count, log-normalized expression, VST and row-z-score are distinct. Label exactly. Do not average transformed values and call the result raw expression.
- A cell/spot/metacell/technical run is not automatically an independent subject. Show sample-level summaries alongside dense cell views. Do not draw distribution densities from two animal observations.
- Heatmap row z-scores compare within a gene, not abundance across genes; constant rows need explicit handling. Preserve intended sample order and label hierarchical clustering if used.
- Dot area represents detection fraction only if the denominator is explicit. State whether color is mean across all cells, positive cells only, or a scaled statistic.
- UMAP shows an embedding, not measured tissue space or a calibrated intercluster distance. Use one embedding for split views; disclose any downsampling and keep numeric summaries on all eligible cells.
- Separate classification color, continuous expression color, signed effect color and evidence level. Same hue can appear in separate semantic namespaces only with unambiguous legends.
- Point intervals require actual supplied bounds, not invented error bars. A supplied interval must contain its estimate; do not mix SD, SE, bootstrap and confidence intervals without labeling.
- Multi-cohort forest: same effect units/contrast within panel. Missing estimates listed separately; do not invent a zero row.
- Declare forest effect_scale: difference/log_ratio uses null=0; ratio uses positive estimates/bounds, log axis and null=1. AUC difference intervals must come from the upstream matched evaluation; marginal AUC intervals do not define a valid difference interval.
- Paired panels require a complete one-to-one subject×condition table and explicit condition order. Record excluded incomplete pairs separately. Repeated technical measurements need upstream aggregation before using this adapter.
- Networks: log edge-selection rule, edge weight, direction source and layout seed. Use fixed positions across comparisons. Correlation edges must not acquire regulatory arrowheads.
- ROC/PR: consume OOF or held-out scores/curves from the approved analysis. Do not train, flip score direction for a higher AUC, smooth curves into better performance, or calculate CI from repeated-CV rows as independent patients.
- Trajectory, velocity, splice tracks, spatial maps and multiome overlays require their corresponding data and validated upstream outputs. Unavailable means unavailable, not an invitation to fabricate.

## Style defaults (override with user style)

White background, charcoal labels, restrained grid. Use mid/deep categories and enough separation at final size. Keep zero-expression background light and positive expression sequential; signed effects diverge around zero. Preserve all group legends. Do not claim a palette colorblind-safe without checking it.

Start single/double-column figure widths around 85/180 mm; confirm journal requirements. Start text at 8–10 pt at final dimensions. Use line widths consistently. Direct-label a handful of focal genes; use an appendix for long lists. Avoid alluvial/3D/radial alternatives unless they clarify the specific relationship.

## Export/review

API v2 writes SVG/PDF/300dpi PNG, exact TSV, JSON and session info into one per-figure directory. Both languages use SHA256 for plotted input, outputs and renderer scripts. Supplied upstream expected SHA256 is verified before rendering. Existing v1 flat files and v2 bundles are refused. Figure adapters stamp their input table and plotting semantics; export rejects a different table. Native-object plots need their own reviewed adapter and provenance export; calling stamp alone is not proof that an arbitrary figure matches a table.

The exporter uses an exclusive figure-id lock and a staging directory on the destination filesystem, then renames the complete bundle. Caught failures remove only the exporter's own temporary files and release its lock; rerunning the same id is possible after failure. A process crash/power loss can leave an uncommitted staging directory or lock: inspect ownership before any cleanup. Do not claim atomic multi-directory publication. For patched figures, new output ids preserve the previous version.

Check: row counts, values and units; observed sample n; legend/axis consistency; all intended categories present; cutoff disclosure; no clipping at full and reduced size; missing vs zero; color/grayscale readability; source link; uncertainty; all captions. Plotting failures must not receive completion status. New outputs remain RENDERED_UNREVIEWED; save a separate visual-review record with the reviewed PNG/PDF hash. Do not silently edit a receipt or promote a software demo to a scientific result.

For source-only requests do not create dummy research plots. Synthetic fixtures are allowed for software tests but carry DEMO/SYNTHETIC in titles and captions and must stay outside scientific results.
