# Coherent bulk and single-cell figure sets

Start with a question and explicit frozen outputs. The host checks the design,
independent unit, contrast, denominators and upstream QC before choosing views.
This skill draws supplied results; it does not normalize expression, fit DE,
infer embeddings or annotations, calculate enrichment, or certify the analysis.

## Expected outputs

| Section | Bulk RNA-seq | Single-cell RNA-seq |
|---|---|---|
| Main figure | Sample architecture, DE, a prespecified expression program and pathway context | Cell identity, marker specificity, donor composition and one declared donor-pseudobulk contrast |
| QC | Sample expression distributions, library totals, supplied PCA and complete sample correlation | Detected genes, total UMIs and mitochondrial percentage by sample; cells per donor; supplied batch embedding |
| Expression | Annotated heatmap with fixed sample and feature order; effect intervals | Cell-type embedding, marker mean/fraction dot matrix, shared-scale feature maps; optional annotated matrix |
| Difference | Effect and FDR volcano, supplied effect intervals and MA | Donor-level pseudobulk volcano, intervals, MA and supplied expression matrix for each explicitly selected annotation |
| Composition | Only when relevant frozen proportions exist | One donor per descriptive composition unit; retain complete cell-type counts and denominators |
| Pathways | ORA ratio, overlap-count area and FDR; full GSEA curve, hit rugs and rank metric | The same views, tied to the declared donor contrast and annotation |

Main figures and companions answer different reading needs. Do not stack all
diagnostics into one small manuscript page. Keep the complete single figures;
use a reading edition or pagination for dense tables and many panels. Do not
discard observations, genes, pathways, uncertainty or missingness for appearance.

The main-figure renderer is a presentation mode for existing forms, not a new
analysis method. Its mixed table contains `record_type=embedding,de,matrix,
enrichment` for bulk or `embedding,marker_dot,composition,de` for single-cell.
Panel order, rows, columns and physical panel size are configurable. Complete
categorical matrices grow their own row; unrelated panels do not become tall
merely because a neighbouring matrix has more labels. Every selected channel
must exist. Colour keys, point-area keys and label lanes remain part of the panel.

## Explicit manifest

A `StudyFigureManifest` has exactly these fields:

```json
{
  "schema_version": 1,
  "assay": "bulk",
  "title": "Selected frozen study results",
  "contrast": "Treatment versus control",
  "independent_unit": "Donor; one independent biological unit per subject",
  "denominator": "The declared tested genes and selected samples",
  "frozen_results": true,
  "upstream_qc": "reviewed",
  "results": [
    {"role": "differential_expression", "spec": "DE/DE.spec.json"},
    {"role": "differential_heatmap", "spec": "Expression/Expression.spec.json"},
    {"role": "enrichment_summary", "spec": "Pathways/Pathways.spec.json"}
  ]
}
```

Each `spec` is an ordinary FigureSpec, relative to this manifest. It binds exact
TSV bytes, renderer source, parameters, provenance, theme and export size. The
example above supports the differential and pathway request; it is deliberately
incomplete for a full article figure set. The planner lists every missing role
and blocks missing required results. Optional results are `NOT_SUPPLIED`.

```text
python scripts/workbench.py study-plan --manifest results/study.json --request "展示差异和通路" --output plans/figures.json
python scripts/workbench.py study-render --plan plans/figures.json --output figures/revision-1
```

“画质控图” selects QC. “展示差异和通路” selects difference and pathways.
“做一套文章组图” selects the complete assay-specific sections. The host must
resolve requests outside the documented vocabulary, clarify the intended
comparison, and prepare an overview FigureSpec when a main figure is required.
The planner does not automatically invent an overview from unrelated files.

QC-only drawing can inspect an unresolved upstream QC state. Downstream views
require declared reviewed QC. A cell-only independent unit blocks differential
inference routing. The declarations themselves remain subject to scientific
review; free text is not proof of an adequate donor model.

Rendering is serial and uses a fresh output directory. A failure saves a partial
receipt. Never automatically retry an unknown analysis or overwrite earlier
figures. A rendered set remains `RENDERED_REVIEW_REQUIRED` until actual review.

## Acceptance

1. Check exact inputs, units, selection, missingness and scientific channels.
2. Run the ordinary request and inspect the resulting selection and omissions.
3. Inspect every final single figure and all composition pages, including dense
   labels and the intended physical width. Check the main figure's reading order,
   complementary information, balance, guides, contrast and complete labels.
4. Reflow or choose a better extension when a view fails; do not shrink text,
   hide data, omit labels or add decorative channels to obtain a pass.
5. Record output hashes, inspected file types, width, actual scope and unresolved
   limits. File integrity, font measurement, self-review and scientific validity
   are separate decisions. Changed exports need a new bound visual review.

The supplied fictional fixture has twelve donors, nine hundred nested cells and
1,200 fictional genes. These are frozen software-test channels, with no fitted
DE, inferred embedding or calculated enrichment. The selected myeloid donor
contrast has separate scope-specific specifications. Reused illustrative values
are disclosed; they are not independent validation or biomedical evidence.
