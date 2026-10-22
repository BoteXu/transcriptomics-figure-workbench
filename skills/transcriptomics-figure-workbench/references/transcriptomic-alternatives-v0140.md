# Five complete transcriptomic figure families

These are optional compositions of existing frozen results, not new analysis
algorithms. Select by the question and supplied channels. Preserve every classic
form; a new colour, layout or input size is not a new method.

## Actual calls and examples

The [rendered examples](../assets/transcriptomic-alternatives/index.html) include
28 reading pages, exact FigureSpecs, untouched source tables or explicitly
declared complete selections, PNG, editable SVG and PDF. They use fictional
public fixtures; no private research, fitted densities or biological claims.

| Family | Existing entry | Optional parameter | Useful information |
|---|---|---|---|
| PCA | `figure_integrated_views.plot_integrated_view`, `mode="pca"` | `presentation="evidence"` | Coordinates, named colour/shape groups, supplied reference contours, checked marginal proportions, sample support and complete supplied variance profile |
| PCA | same | `presentation="facets"` | One highlighted identity per panel, all others grey, identical quantitative limits; `ncols`, `nrows`, `panel_width`, `panel_height` |
| Volcano | same, `mode="volcano"` | `presentation="evidence"` | Every tested gene, checked stacked marginals, exact threshold/count denominator, selected-gene numeric register |
| Volcano | same | `presentation="landscape"` | Evidence view plus full tested-universe ranked effect strip, preserving every nonsignificant gene |
| GSEA | `figure_gsea.plot_gsea_tracks` | `mode="cards"` | Each pathway has ES, hits, leading-edge emphasis, ranked metric, NES/FDR and set size; flexible `ncols`, `nrows`, panel dimensions |
| GSEA | same | `mode="aligned"` | Aligned complete running scores and hit lanes, one shared ranked metric, per-pathway summaries |
| Expression | `figure_chapter_views.plot_transcriptomic_chapter` | `presentation="raincloud_horizontal"` or `"raincloud_vertical"` | Supplied half-cloud, every observation, empirical box/median, count unit and group n; `columns` and `rows` |
| Per-subgroup markers | `figure_annotation_views.plot_annotation_evidence`, `mode="subgroup"` | `composition="strips"` | Location and complete specificity summary, then one marker map and all-identity mean/fraction comparison per row |
| Per-subgroup markers | same | `composition="paired_cards"` | Multiple marker cards across adaptable rows/columns; shared complete coordinates, expression limits and comparison groups |

The APIs retain all required scientific parameters. Change only the documented
presentation parameters in a compatible FigureSpec. `describe --renderer ...`
shows the current full signature; the example's `figure.spec.json` is the
complete reproducible call, including source hash, units, theme and metadata.

```sh
python scripts/workbench.py plan --spec assets/transcriptomic-alternatives/PCA_evidence/figure.spec.json --output outputs/pca-plan.json
python scripts/workbench.py render --plan outputs/pca-plan.json --output outputs/pca
python scripts/workbench.py plan --spec assets/transcriptomic-alternatives/GSEA_cards/figure.spec.json --output outputs/gsea-plan.json
python scripts/workbench.py render --plan outputs/gsea-plan.json --output outputs/gsea
python scripts/workbench.py plan --spec assets/transcriptomic-alternatives/Subgroup_01_paired_cards/figure.spec.json --output outputs/markers-plan.json
python scripts/workbench.py render --plan outputs/markers-plan.json --output outputs/markers
```

Commands run from the installed skill root, in an existing authorized rendering
environment. In the repository prepend `skills/transcriptomics-figure-workbench/`
to script and asset paths. A fresh output path preserves old exports.

## Selection rules and scientific boundaries

- Prefer PCA evidence for a compact main page when the complete marginal bins
  and variance profile exist. Facets are useful for overlap, identity tracing
  and larger scopes. Reference contours without a supplied coverage level are
  explicitly labelled as such; never call them 95% confidence intervals.
  Small/medium/large examples keep original coordinates and fixed contours.
  Axis variance belongs to the supplied original PCA, not a newly selected fit.
- Prefer volcano evidence for a readable comparison and landscape when the
  distribution of all effects matters. The selected numeric register is a
  labelled subset, never the denominator. Do not recalculate FDR or counts from
  only the visible labels. Both complete stacked marginal counts are verified.
- Prefer GSEA cards for independent pathway reading; aligned lanes for
  comparisons on the same ranked universe. The complete ES, exact hit ranks,
  shared rank metric, supplied leading-edge flags, NES, FDR, set definition and
  contrast must exist. `show_leading_edge=False` turns emphasis off. Full gene
  identities remain in the TSV; a count or bold rug does not replace them.
- A raincloud requires supplied cloud geometry, matching raw range and n,
  every raw observation and an explicit count unit. The narrow box summarizes
  empirical quartiles/median and 1.5 IQR whiskers; it is not a confidence
  interval. Dots remain visible at small n. Cell count is not donor replication.
- Marker strips favour direct cross-identity comparison; paired cards favour
  compact review of several markers. Every marker map retains every cell and
  the same coordinates/limits. Detection fractions and mean expression are
  supplied channels. The five subgroup pairs and 2/4/8-marker examples expose
  off-target expression instead of hiding other identities. `_demoB` channels
  in the eight-marker display fixture are synthetic layout channels.

Unsupported row/column combinations raise an error. A larger reading page is
not automatically suitable for a journal column: reflow complete cards or use
multiple pages, then inspect the requested final physical size. No font-size
measurement or successful process proves aesthetics or scientific validity.

## Sources, adopted principles and limits

The SciSpace search was used for method discovery. It returned older
foundations as well as recent papers, and duplicate Raincloud versions; it is
not a systematic search or a claim that all references are from 2024–2026.
Author repositories checked 2026-10-22:

- [GseaVis, JunJunLab](https://github.com/junjunlab/GseaVis): complete GSEA
  tracks, pathway-specific styling and readable summaries; adopted as design
  principles for original frozen-table cards/aligned lanes.
- [RainCloudPlots](https://github.com/RainCloudPlots/RainCloudPlots): raw
  observations beside distributions and compact summaries; original code here
  draws already supplied cloud geometry and supports both orientations.
- [scCustomize, Samuel Marsh](https://github.com/samuel-marsh/scCustomize):
  careful feature/identity presentation; original per-subgroup compositions
  here retain shared scales and complete comparison identities.

No external source code, article pixels, datasets, weights or native package
executables were copied or bundled in this increment. External packages retain
their own licenses and attribution. The implementation does not claim that the
native software ran or that one composition is always scientifically superior.

## Acceptance

Each changed single/composition and custom-layout page needs actual screen
inspection after rendering. Record the exact source revision, image hashes,
defects and repaired rerenders. Keep `RENDERED_UNREVIEWED`, screen self-review,
final-size print proof, independent review and scientific acceptance distinct.
The gallery review ledger records the completed scope; it cannot approve
different user data, longer labels or a smaller output width automatically.
