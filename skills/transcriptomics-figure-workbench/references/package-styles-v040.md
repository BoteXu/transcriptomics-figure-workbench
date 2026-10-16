# Package figures v0.4: reference-informed redesign

This release gives **all 25 registered package/method entries an actual new example**. Eight GSEA/ORA examples are redesigned and seventeen previously unillustrated entries now have PNG/PDF/SVG, frozen source TSV, complete FigureSpec and output receipts. These are 25 bindings using 14 display grammars, not 25 new scientific methods. Original v0.3 examples and their reviews remain intact.

## Visual decisions

| Family | Design applied | Scientific channels preserved |
|---|---|---|
| GSEA | Compact ES / hit / ranking strata; coloured summaries; declared gene labels; classic, overlay and facets | Complete supplied rank axis, ES versus NES, hit identity, leading-edge flags, FDR |
| NES / ORA | Ordered horizontal structure, restrained continuous ramps, separate size and colour guides | Set size versus query count, query denominator, background, missing tests |
| Ridges | Clear baselines, common display-height factor, readable labels | Supplied density grid, no KDE or smoothing of real inputs |
| cnet / emap / WGCNA / CellChat | Method-specific fixed topology examples, explicit node labels, unobtrusive edges, separate legends | Nodes, coordinates, weights, edge definition and direction; no layout inference |
| GSVA / decoupleR / PROGENy | Sample annotation strips, fixed order and zero-centred scales | Original score units; no rescaling or clustering |
| DESeq2 / MSstats / limma | Light guides, selected labels, compact effect table, aligned intervals | Existing effects, probabilities and intervals; no model fitting |
| Seurat / Scanpy | Marker identity strip, separated fraction/mean guides; dense stored coordinate examples | Means/fractions and cell identities; no embedding or donor-level inference |
| Survival / ROC | Aligned risk table, supplied confidence bands and censor marks; separate curve legend | Original step/threshold coordinates, time units and supplied uncertainty |

The original `package_editorial` categorical palette uses restrained teal, coral, slate, lavender and gold. It is not claimed to be extracted from an article. Its category slots are explicit; continuous diverging and sequential ramps remain separate. Enlarging type, changing geometry or replacing colour mappings requires a new export and review.

## Reference ledger (accessed 2026-10-16)

| Source and attribution | Access actually achieved | Adopted principle |
|---|---|---|
| [GseaVis author manual: basic usage](https://junjunlab.github.io/gseavis-manual/basic-usage.html#new-style-graphic), JunJunLab | Manual content and actual example visually inspected in browser | Compact stacked GSEA, explicit gene labels and legible annotations |
| [scCustomize: gene expression plotting](https://samuel-marsh.github.io/scCustomize/articles/Gene_Expression_Plotting.html#clustered-dotplots), Samuel Marsh | Actual clustered-dotplot example visually inspected in browser | Identity strip, structured marker matrix and separate channels; supplied order used here |
| [survminer author example](https://rpkgs.datanovia.com/survminer/tools/README-ggplot2-more-customized-survival-plot-1.png), survminer authors | Actual example image visually inspected in browser | Restrained step curves, interval bands and aligned risk table |
| [enrichplot author book](https://yulab-smu.top/biomedical-knowledge-mining-book/enrichplot-gsea.html), Guangchuang Yu and contributors | Documentation read | Preserve genuine running ES, hits, distributions and leading-edge scope |
| [Seurat DotPlot reference](https://satijalab.org/seurat/reference/dotplot), Satija Lab | Documentation read | Dot area = fraction, colour = declared expression channel |
| [CellChat](https://github.com/jinworks/CellChat), Jin and collaborators | Public repository description consulted; no native engine executed | Distinguish predicted sender/receiver weights from measured causal signals |
| [EnhancedVolcano](https://bioconductor.org/packages/release/bioc/html/EnhancedVolcano.html), package authors | Public package description consulted; no figure copied | Selected labels and transparent effect/probability semantics |

Search included Chinese public tutorials and WeChat entry points. No newly retrieved WeChat full article or code is claimed: accessible author sources supplied the actual visual references. Unread excerpts are not accepted as reviewed figure evidence. No third-party screenshots, article text, code, gene sets, assets or native software were redistributed; this release contains original display implementations and original synthetic fixtures. Package names and upstream algorithms retain their attribution and licences.

## Reproduce or replace a fixture

Open [the new gallery](../assets/package-gallery/index.html), select a method and inspect its source TSV and `.spec.json`. To use actual results, replace the selected table and the provenance/independent-unit/uncertainty definitions, retain canonical column semantics, choose explicit orders, limits and category slots, then run:

```sh
python scripts/workbench.py method-spec --entry Seurat.DotPlot --template selected-context.json --output selected.spec.json
python scripts/workbench.py plan --spec selected.spec.json --output selected.plan.json
python scripts/workbench.py render --plan selected.plan.json --output fresh-output
```

Set `renderer` to `package_style`; `parameters` contains `contract` and `options`. The method fixes its `view` and any arrangement constraints. The bundled complete specs are runnable templates. Legacy templates using their existing renderer keep the old route. Neither route reads native RDS/h5ad objects or installs analysis packages. Upstream analysis/export remains on the existing analysis host.

Local review checks input/output hashes, actual stored coordinates, text geometry and final artifacts. Visual inspection is subjective and scoped to these exact synthetic exports. It does not establish native package execution, scientific correctness, general aesthetics across future data, or user preference.
