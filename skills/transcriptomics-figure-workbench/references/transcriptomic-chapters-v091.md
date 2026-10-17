# Transcriptomic analysis chapters and executable drawing recipes

## Scope

The chapter catalogue contains **58 implemented drawing recipes**: 28 bulk and 30 single-cell chapters. The 25 coherent study figures are a small companion demonstration, not a complete analysis workbench. Each chapter includes an executable FigureSpec, exact fictional TSV and actual exports in `assets/chapter-gallery`. All examples are illustrative frozen results. No analysis backend was executed to create them.

Discover the actual catalogue with `workbench.py chapters --assay bulk` or `--assay single_cell`. Search by question or method using `--search`. The generated JSON is authoritative for IDs, required result roles, specific QC/interpretation limits and source links. These chapters reuse consolidated forms and typed complementary panels; they are not 58 new chart types.

### Bulk coverage

Design and independent units; read QC; alignment and gene-body coverage; filtering sensitivity; normalization/RLE and mean-variance diagnostics; PCA with supplied ellipses, marginal proportions and variance profile; full-distribution DE; factorial interactions; model residual/dispersion checks; gene programs and selected uncertainty; ORA themes and supporting genes; complete GSEA; multicontrast pathway comparison; explicit gene-term membership; multiple full GSEA tracks; GSVA/ssGSEA summaries; WGCNA and preservation; TF footprints; mixture deconvolution; splicing and junctions; transcript usage; longitudinal trends; independent replication; conditional outcome association; PPI evidence; perturbation-signature connectivity; noncoding RNA hypotheses; fusion/transcript evidence.

### Single-cell coverage

Donor/capture design; barcode rank; cell QC; ambient/doublet diagnostics; integration and biology preservation; HVG/PC support; cluster resolution and donor support; annotation atlas with marker evidence; lineage subclusters; marker specificity; donor composition; donor-aware differential abundance; donor pseudobulk; celltype-by-contrast DE; celltype pathways and gene support; state/stress/cycle scores; hdWGCNA; trajectories and branch trends; velocity and phase diagnostics; communication and LR support; ligand-target evidence; regulons; inferred CNV; VDJ/clonotypes; celltype RNA processing; Perturb-seq; independent cohort transfer; spatial context; paired RNA-ATAC.

Conditional assays require their own data. A transcriptome alone does not supply VDJ calls, measured spatial coordinates, unspliced counts, paired ATAC or sequence-level fusion evidence. The plotting recipe remains available and illustrated; an actual project's result table must truthfully identify its source and assay.

## Prefer information-rich extensions

- PCA: supplied dispersion/reference ellipses, exact within-group marginal proportions and explained variance. Declare whether an ellipse describes dispersion, a reference region or uncertainty of a mean. Three observations are a minimum display condition, not statistical adequacy.
- DE/MA: full point scope, stacked marginal gene counts, restrained selected labels, consistent effect/FDR thresholds. No dark candidate overlay.
- Annotation: labelled subpopulations + annotation-block marker means/fractions + representative feature maps on identical coordinates/scales; expand by lineage as actual results support.
- ORA: linked GeneRatio, hit count, FDR and theme grouping with exact gene support. A single lollipop remains an optional compact view.
- GSEA: full ES, exact hit rugs, rank metric and declared leading edge; aligned multitrack alternatives and NES comparisons preserve their distinct units. ORA direction is never invented from a term name.
- Communication/modules/regulation: retain exact selected edges and corresponding matrix/effect support. Do not drop edges or choose a prettier graph at the expense of completeness.

Choose the extra channels that answer the question. Information-rich does not mean adding unrelated decorations or forcing every chapter onto a single paper page. Use complete companion views and a smaller selected main composition.

## Export and run a recipe

```text
python scripts/workbench.py chapters --search enrichment
python scripts/workbench.py chapter-template --entry bulk.ora --output selected-ora-template
python scripts/workbench.py plan --spec selected-ora-template/example.spec.json --output selected-ora.plan.json
python scripts/workbench.py render --plan selected-ora.plan.json --output selected-ora-render
```

The exported template is an executable synthetic example. Replace it with explicitly selected, reviewed frozen project results and a new source hash, provenance, figure ID and output directory before research use. It is not an analysis script. Large analysis remains on the user's existing server route.

### Multiple contrasts, celltypes and cohorts

`book-plan` and `book-render` preserve multiple result specifications for the same chapter under explicit scope identities. This removes the old one-result-per-role limitation.

```json
{
  "schema_version": 1,
  "assay": "single_cell",
  "title": "Selected donor-response figure book",
  "chapters": ["single_cell.pseudobulk", "single_cell.pathways"],
  "results": [
    {
      "id": "MyeloidContrastA",
      "chapter": "single_cell.pseudobulk",
      "scope": {
        "contrast": "Treated versus Control",
        "cell_type": "Myeloid",
        "cohort": "Declared cohort",
        "independent_unit": "Donor",
        "denominator": "Complete tested genes and declared donors"
      },
      "spec": "selected-result.spec.json",
      "frozen_results": true,
      "upstream_qc": "reviewed"
    }
  ]
}
```

Add separate result IDs for other celltypes, contrasts and cohorts. Safe IDs are bounded to letters, digits, underscore and hyphen. Ambiguous duplicate chapter/scope, changed bindings, inconsistent identity colours, invalid scientific units or unreviewed project QC are rejected. A maximum of 500 explicitly selected result specifications is supported; no private folder scanning occurs.

Use `chapters: "all"` to prepare full coverage. Every chapter has `plot_capability: IMPLEMENTED_WITH_EXECUTABLE_EXAMPLE`. `project_input_state: INPUT_REQUIRED` refers only to a project's missing frozen table, never an unimplemented drawing method. Export that chapter's runnable example to review its available drawing. Do not fabricate project results to fill a book.

## Data and layout contracts

The shared chapter renderer accepts an explicit `panels` list with stable IDs and `kind` from curve, points, interval, matrix, bubble, embedding, network, stack, bars and vector. Each record declares `panel_id`. Every declared panel and every table panel must match. Orders follow supplied records. No rows or edges are silently truncated.

Curves need unique series/x coordinates and any supplied bounds. Intervals require their definition and valid lower/estimate/upper. Matrices require a complete unique selected grid and explicit colour limits; missing is never filled with zero. Bubble sizes require a [0,1] fraction and denominator. Networks require complete explicit edges, weights and consistent frozen coordinates. Embeddings retain one position per object and explicit label anchors. Stacks require nonnegative additive values and a denominator. Velocity uses supplied vectors and an explicit scale.

Automatic columns use the actual selected panel count; custom `columns` from 1 to 4 reflow the same chapter without discarding panels. The linked enrichment view supports 1 or 2 columns. Single figures and compositions have independent physical size/readability checks. The default chapter reading sheet uses 297 mm; the richer study views use their own explicit width. A large reading sheet does not imply a two-column manuscript main figure is accepted. Use the layout planner to compose selected exports, preserving their guides and then review the actual pages.

## Sources and adoption decisions

The drawing code here is original. The following author and community sources informed design choices; packages retain their own authorship and licenses. No third-party analysis scripts, model weights or private results are redistributed.

| Source | Adopted idea | Deliberate limit |
|---|---|---|
| [scRNAtoolVis jjDotPlot](https://junjunlab.github.io/scRNAtoolVis-manual/jjdotplot.html) | Explicit marker/group order and annotation blocks | No marker inference or reselection for a nicer pattern |
| [scRNAtoolVis jjVolcano](https://junjunlab.github.io/scRNAtoolVis-manual/jjvolcano.html) | Celltype/contrast-aware comparison | Cells are not treated as independent donors |
| [scplotter gallery](https://pwwang.github.io/scplotter/) | Complementary annotation, communication and repertoire views | Frozen selected results only; native packages were not run here |
| [GseaVis basic usage](https://junjunlab.github.io/gseavis-manual/basic-usage.html) | Aligned multi-pathway tracks, gene support and result annotations | Exact supplied curves, ranks and summaries required |
| [YuLab knowledge-mining toolkit](https://yulab-smu.top/clusterProfiler-book/) | Link enrichment summaries to gene evidence and compare explicit contrasts | ORA, NES, probability, counts and membership retain different meanings |
| [hdWGCNA network visualization](https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html) | Module-scale evidence plus readable fixed network | No arbitrary edge downsampling or new UMAP/layout fit |
| [ComplexHeatmap annotation book](https://jokergoo.github.io/ComplexHeatmap-reference/book/heatmap-annotations.html) | Explicit grouping and aligned annotation tracks | No new clustering, hidden row selection or scale transformation |
| [DESeq2 vignette](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html) | Separate design, diagnostics, effects and uncertainty | No local model execution; illustrative numbers are not backend acceptance |
| [Single-cell best practices](https://www.sc-best-practices.org/) | Assay-aware chapters and independent-unit boundaries | Catalogue completeness is not scientific validity |

Actually reviewed source pages were checked on 2026-10-17. Blogs and package manuals are discovery material; numerical/scientific claims still require the original method and source results. Visual self-review, file validation, runtime rendering and scientific acceptance remain separate.
