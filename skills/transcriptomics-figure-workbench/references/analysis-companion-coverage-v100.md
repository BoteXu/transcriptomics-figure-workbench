# 逐分析的完整配套问题与实际示例

本表从可执行配方生成，核心专用主图保留在统一分析目录；此处逐项列出补充的 QC、支持、解释和验证。不同数据量和行列是同一画法的布局扩展，不计作新分析。

[统一目录](../assets/analysis-library/index.html) · [全部配套示例](../assets/companion-gallery/index.html) · [选择、输入与验收](analysis-companion-protocol-v100.md)

WGCNA 与 hdWGCNA 的完整路线继续保留，见 [网络章节](analysis-library-v097.md)。本次其余 56 章各有单项配套页、完整组合及扩展数据的一列阅读版；六个章节另有三列宽版。所有材料为明确虚构的冻结绘图输入，不是新完成的组学分析。

## 设计与独立样本 · `bulk.design`

核心输入：`sample_covariates`、`library_counts`。

方法/解释限制：Review design rank, pairing and confounding; technical libraries do not increase biological n.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_design_01](../assets/companion-gallery/index.html#B_design_01)|Biological units and library contributions|qc|fraction · Fraction of declared denominator|
|[B_design_02](../assets/companion-gallery/index.html#B_design_02)|Covariates across independent donors|qc|matrix · Declared design code|
|[B_design_03](../assets/companion-gallery/index.html#B_design_03)|Group balance within batches|qc|fraction · Fraction of declared denominator|
|[B_design_04](../assets/companion-gallery/index.html#B_design_04)|Missing covariate audit|qc|matrix · Explicit missing indicator|
|[B_design_05](../assets/companion-gallery/index.html#B_design_05)|Prespecified design sensitivity|validation|effects · STAT1 log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_design_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_design_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#B_design_ThreeColumns)。

## 测序读段质控 · `bulk.reads`

核心输入：`base_quality`、`read_classes`。

方法/解释限制：Complete base positions and all read classes; no silent removal of failed libraries.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_reads_01](../assets/companion-gallery/index.html#B_reads_01)|Base-quality profiles by read|qc|profile · Read position (nt) / Phred quality|
|[B_reads_02](../assets/companion-gallery/index.html#B_reads_02)|Adapter content across read positions|qc|profile · Read position (nt) / Adapter fraction|
|[B_reads_03](../assets/companion-gallery/index.html#B_reads_03)|Frozen read-length distribution|qc|bins · Read length (nt) / Supplied count|
|[B_reads_04](../assets/companion-gallery/index.html#B_reads_04)|Base composition across cycles|qc|profile · Read position (nt) / Base fraction|
|[B_reads_05](../assets/companion-gallery/index.html#B_reads_05)|Duplication and unique-fragment classes|qc|fraction · Fraction of declared denominator|
|[B_reads_06](../assets/companion-gallery/index.html#B_reads_06)|GC distributions against a frozen reference|qc|bins · GC fraction / Supplied count|
|[B_reads_07](../assets/companion-gallery/index.html#B_reads_07)|Read retention through declared processing|validation|fraction · Fraction of declared denominator|

[配套组合](../assets/companion-gallery/index.html#B_reads_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_reads_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 比对与覆盖 · `bulk.alignment`

核心输入：`alignment_classes`、`gene_body_coverage`。

方法/解释限制：Reference build, strandedness and assay must match; coverage is not expression.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_alignment_01](../assets/companion-gallery/index.html#B_alignment_01)|Complete mapping categories|qc|fraction · Fraction of declared denominator|
|[B_alignment_02](../assets/companion-gallery/index.html#B_alignment_02)|Gene-body coverage by library|qc|profile · Relative gene position / Normalized coverage|
|[B_alignment_03](../assets/companion-gallery/index.html#B_alignment_03)|Insert-size distributions|qc|bins · Insert length (bp) / Supplied count|
|[B_alignment_04](../assets/companion-gallery/index.html#B_alignment_04)|Strandedness evidence by library|qc|fraction · Fraction of declared denominator|
|[B_alignment_05](../assets/companion-gallery/index.html#B_alignment_05)|Feature-assignment classes|qc|fraction · Fraction of declared denominator|
|[B_alignment_06](../assets/companion-gallery/index.html#B_alignment_06)|Mapping-quality distributions|validation|bins · Mapping quality / Supplied count|

[配套组合](../assets/companion-gallery/index.html#B_alignment_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_alignment_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 基因检出与过滤 · `bulk.filtering`

核心输入：`threshold_profile`、`retained_feature_counts`。

方法/解释限制：Freeze tested universe and rule; do not choose thresholds for more discoveries.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_filtering_01](../assets/companion-gallery/index.html#B_filtering_01)|Mean expression and detection|qc|scatter · Supplied mean log count / Detection fraction|
|[B_filtering_02](../assets/companion-gallery/index.html#B_filtering_02)|Gene-retention sensitivity|qc|profile · Declared count threshold / Retained fraction|
|[B_filtering_03](../assets/companion-gallery/index.html#B_filtering_03)|Feature classes before and after filtering|qc|fraction · Fraction of declared denominator|
|[B_filtering_04](../assets/companion-gallery/index.html#B_filtering_04)|Effect stability across filter choices|validation|effects · Log2 fold change · supplied 95% interval|
|[B_filtering_05](../assets/companion-gallery/index.html#B_filtering_05)|Detection support across groups|qc|matrix · Detected donor fraction|

[配套组合](../assets/companion-gallery/index.html#B_filtering_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_filtering_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 标准化与均值方差 · `bulk.normalization`

核心输入：`rle_density`、`mean_variance`。

方法/解释限制：Declare RLE/reference and transformed scale; drawing never estimates density or normalization.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_normalization_01](../assets/companion-gallery/index.html#B_normalization_01)|Library-size distributions by condition|qc|raincloud · Condition / Library size (millions)|
|[B_normalization_02](../assets/companion-gallery/index.html#B_normalization_02)|Paired donor RLE medians before/after normalization|qc|paired · Repeated condition / Donor median relative log2 expression|
|[B_normalization_03](../assets/companion-gallery/index.html#B_normalization_03)|Donor RLE medians after normalization|qc|raincloud · Condition / Donor median relative log2 expression|
|[B_normalization_04](../assets/companion-gallery/index.html#B_normalization_04)|Mean–variance transformation diagnostics|qc|scatter · Supplied mean / Supplied variance|
|[B_normalization_05](../assets/companion-gallery/index.html#B_normalization_05)|Reference-feature normalization sensitivity|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_normalization_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_normalization_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 样本关系与批次 · `bulk.batch`

核心输入：`embedding`、`ellipse_geometry`、`marginal_counts`、`variance_profile`。

方法/解释限制：Ellipse meaning and all samples required; separation does not establish successful batch correction.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_batch_01](../assets/companion-gallery/index.html#B_batch_01)|Condition balance within each batch|qc|fraction · Fraction of declared denominator|
|[B_batch_02](../assets/companion-gallery/index.html#B_batch_02)|Complete covariate-associated variance|qc|matrix · Supplied variance fraction|
|[B_batch_03](../assets/companion-gallery/index.html#B_batch_03)|Donor RLE medians before/after batch adjustment|qc|paired · Repeated condition / Donor median relative log2 expression|
|[B_batch_04](../assets/companion-gallery/index.html#B_batch_04)|Interferon-program scores by batch|interpretation|raincloud · Batch / Supplied donor interferon score|
|[B_batch_05](../assets/companion-gallery/index.html#B_batch_05)|Biological-effect preservation across choices|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_batch_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_batch_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 差异表达 · `bulk.differential`

核心输入：`complete_de`、`effect`、`p_adj`、`marginal_counts`。

方法/解释限制：Freeze contrast, independent units and FDR family; no selected-gene-only volcano.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_differential_01](../assets/companion-gallery/index.html#B_differential_01)|Binned dispersion summaries and fitted trend|qc|profile · Supplied mean / Supplied dispersion|
|[B_differential_02](../assets/companion-gallery/index.html#B_differential_02)|Cook influence across fitted expression|qc|scatter · Supplied fitted log count / Supplied Cook distance|
|[B_differential_03](../assets/companion-gallery/index.html#B_differential_03)|Prespecified gene effects with uncertainty|interpretation|effects · Log2 fold change · supplied 95% interval|
|[B_differential_04](../assets/companion-gallery/index.html#B_differential_04)|STAT1 expression in independent donors|interpretation|raincloud · Condition / Supplied log2 normalized STAT1 expression|
|[B_differential_05](../assets/companion-gallery/index.html#B_differential_05)|Complete raw probability distribution|validation|bins · Raw P value / Genes per supplied bin|
|[B_differential_06](../assets/companion-gallery/index.html#B_differential_06)|Unshrunk versus shrunk effects|validation|scatter · Unshrunk log2 fold change / Shrunk log2 fold change|
|[B_differential_07](../assets/companion-gallery/index.html#B_differential_07)|Effect stability across prespecified models|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_differential_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_differential_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#B_differential_ThreeColumns)。

## 交互效应 · `bulk.interaction`

核心输入：`interaction_effects`、`model_predictions`。

方法/解释限制：Require a same-study factorial design and estimable interaction; separate cohorts cannot identify interaction.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_interaction_01](../assets/companion-gallery/index.html#B_interaction_01)|Independent support for factorial cells|qc|matrix · Independent donor count|
|[B_interaction_02](../assets/companion-gallery/index.html#B_interaction_02)|STAT1 condition-by-time predictions|interpretation|profile · Time (days) / Supplied log2 STAT1 expression|
|[B_interaction_03](../assets/companion-gallery/index.html#B_interaction_03)|Gene-wise interaction contrasts|interpretation|effects · Supplied log2 interaction contrast · interval|
|[B_interaction_04](../assets/companion-gallery/index.html#B_interaction_04)|STAT1 simple effects at prespecified times|interpretation|effects · STAT1 log2 response contrast · supplied 95% interval|
|[B_interaction_05](../assets/companion-gallery/index.html#B_interaction_05)|Interaction-model sensitivity|validation|effects · STAT1 log2 response contrast · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_interaction_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_interaction_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 模型诊断 · `bulk.model_qc`

核心输入：`residuals`、`dispersion_curve`、`influence`。

方法/解释限制：Use actual fitted-model residuals and influential observations; a model is not accepted by a pretty plot.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_model_qc_01](../assets/companion-gallery/index.html#B_model_qc_01)|Fitted values and residual structure|qc|scatter · Supplied fitted value / Supplied residual|
|[B_model_qc_02](../assets/companion-gallery/index.html#B_model_qc_02)|Quantile diagnostics with frozen reference|qc|scatter · Theoretical quantile / Observed residual quantile|
|[B_model_qc_03](../assets/companion-gallery/index.html#B_model_qc_03)|Residual distributions by batch|qc|raincloud · Batch / Supplied residual|
|[B_model_qc_04](../assets/companion-gallery/index.html#B_model_qc_04)|Leverage and observation influence|qc|scatter · Supplied leverage / Supplied Cook distance|
|[B_model_qc_05](../assets/companion-gallery/index.html#B_model_qc_05)|Prespecified diagnostic sensitivity|validation|effects · STAT1 log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_model_qc_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_model_qc_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 基因程序与效应 · `bulk.programs`

核心输入：`selected_expression`、`effect_intervals`。

方法/解释限制：Freeze selection and scale; interval level and denominator must be declared.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_programs_01](../assets/companion-gallery/index.html#B_programs_01)|Program membership and complete gene support|qc|matrix · Explicit membership|
|[B_programs_02](../assets/companion-gallery/index.html#B_programs_02)|Interferon-program distributions in independent donors|interpretation|raincloud · Condition / Supplied interferon-program score|
|[B_programs_03](../assets/companion-gallery/index.html#B_programs_03)|Program response estimates|interpretation|effects · Donor program-score difference · supplied 95% interval|
|[B_programs_04](../assets/companion-gallery/index.html#B_programs_04)|Interferon-program progression across measured time|extension|profile · Time (days) / Supplied interferon-program score|
|[B_programs_05](../assets/companion-gallery/index.html#B_programs_05)|Interferon response in independent cohorts|validation|effects · Donor program-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_programs_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_programs_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## ORA 功能富集 · `bulk.ora`

核心输入：`term_ratio`、`term_fdr`、`gene_term_membership`。

方法/解释限制：Actual tested background and mapping versions required; ORA does not establish activity direction.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_ora_01](../assets/companion-gallery/index.html#B_ora_01)|Selected queries and tested-universe coverage|qc|matrix · Supplied coverage fraction|
|[B_ora_02](../assets/companion-gallery/index.html#B_ora_02)|Prespecified enrichment effect estimates|interpretation|effects · Supplied log odds ratio · supplied interval|
|[B_ora_03](../assets/companion-gallery/index.html#B_ora_03)|Complete term–gene support|function|matrix · Explicit annotation membership|
|[B_ora_04](../assets/companion-gallery/index.html#B_ora_04)|Annotated and unannotated query genes|qc|fraction · Fraction of declared denominator|
|[B_ora_05](../assets/companion-gallery/index.html#B_ora_05)|Enrichment stability across backgrounds|validation|effects · Log enrichment odds ratio · supplied 95% interval|
|[B_ora_06](../assets/companion-gallery/index.html#B_ora_06)|Term overlap and redundancy context|function|matrix · Supplied overlap fraction|

[配套组合](../assets/companion-gallery/index.html#B_ora_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_ora_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## GSEA 完整证据 · `bulk.gsea`

核心输入：`complete_rank_curve`、`rank_metric`、`hit_ranks`、`leading_edge`、`NES`、`FDR`。

方法/解释限制：Full signed ranked universe, ties and gene-set version required; never reconstruct a curve from NES.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_gsea_01](../assets/companion-gallery/index.html#B_gsea_01)|Complete ranked-universe statistic|qc|profile · Supplied gene rank / Supplied ranking statistic|
|[B_gsea_02](../assets/companion-gallery/index.html#B_gsea_02)|Set coverage in the ranked universe|qc|fraction · Fraction of declared denominator|
|[B_gsea_03](../assets/companion-gallery/index.html#B_gsea_03)|Normalized enrichment across contrasts|interpretation|effects · Supplied NES · upstream interval|
|[B_gsea_04](../assets/companion-gallery/index.html#B_gsea_04)|Leading-edge membership across selected terms|function|matrix · Explicit leading-edge membership|
|[B_gsea_05](../assets/companion-gallery/index.html#B_gsea_05)|Enrichment concordance across rankings|validation|scatter · NES · primary ranking / NES · alternative ranking|
|[B_gsea_06](../assets/companion-gallery/index.html#B_gsea_06)|Leading-edge overlap across pathways|validation|matrix · Supplied overlap fraction|

[配套组合](../assets/companion-gallery/index.html#B_gsea_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_gsea_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#B_gsea_ThreeColumns)。

## 通路跨对比 · `bulk.pathway_contrasts`

核心输入：`NES_grid`、`FDR_grid`、`set_coverage`。

方法/解释限制：Keep not-tested distinct from nonsignificant; cross-contrast effect and FDR families must be explicit.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_pathway_contrasts_01](../assets/companion-gallery/index.html#B_pathway_contrasts_01)|Tested pathway scope across contrasts|qc|matrix · Explicit tested indicator|
|[B_pathway_contrasts_02](../assets/companion-gallery/index.html#B_pathway_contrasts_02)|Prespecified cross-contrast pathway effects|interpretation|effects · Supplied signed pathway effect · interval|
|[B_pathway_contrasts_03](../assets/companion-gallery/index.html#B_pathway_contrasts_03)|Shared and contrast-specific leading edges|function|matrix · Explicit membership|
|[B_pathway_contrasts_04](../assets/companion-gallery/index.html#B_pathway_contrasts_04)|Pathway concordance between contrasts|interpretation|scatter · NES · contrast A / NES · contrast B|
|[B_pathway_contrasts_05](../assets/companion-gallery/index.html#B_pathway_contrasts_05)|Pathway effects in an independent cohort|validation|effects · Signed pathway-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_pathway_contrasts_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_pathway_contrasts_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 通路支持基因 · `bulk.gene_support`

核心输入：`term_overlap`、`gene_term_membership`、`gene_effects`。

方法/解释限制：Absence of membership differs from missing annotation; selection and background must be frozen.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_gene_support_01](../assets/companion-gallery/index.html#B_gene_support_01)|Explicit pathway membership|qc|matrix · Annotation membership|
|[B_gene_support_02](../assets/companion-gallery/index.html#B_gene_support_02)|Supporting-gene effect estimates|interpretation|effects · Log2 fold change · supplied 95% interval|
|[B_gene_support_03](../assets/companion-gallery/index.html#B_gene_support_03)|STAT1 donor expression in the selected pathway|interpretation|raincloud · Condition / Supplied log2 STAT1 expression|
|[B_gene_support_04](../assets/companion-gallery/index.html#B_gene_support_04)|Gene effects across support contrasts|function|matrix · Supplied log2 fold change|
|[B_gene_support_05](../assets/companion-gallery/index.html#B_gene_support_05)|Supporting-gene replication effects|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_gene_support_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_gene_support_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 多通路 GSEA · `bulk.gsea_multitrack`

核心输入：`complete_curves`、`rank_metric`、`hits`、`leading_edge`、`NES`、`FDR`。

方法/解释限制：Every curve and rank is supplied; no invented ES curve, recomputed FDR or selected-rank truncation.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_gsea_multitrack_01](../assets/companion-gallery/index.html#B_gsea_multitrack_01)|Ranked-universe coverage per selected set|qc|fraction · Fraction of declared denominator|
|[B_gsea_multitrack_02](../assets/companion-gallery/index.html#B_gsea_multitrack_02)|Complete common ranking statistic|qc|profile · Supplied gene rank / Supplied ranking statistic|
|[B_gsea_multitrack_03](../assets/companion-gallery/index.html#B_gsea_multitrack_03)|Selected pathways on a common NES scale|interpretation|effects · Supplied NES · upstream interval|
|[B_gsea_multitrack_04](../assets/companion-gallery/index.html#B_gsea_multitrack_04)|Leading-edge support across the common gene scope|function|matrix · Explicit leading-edge membership|
|[B_gsea_multitrack_05](../assets/companion-gallery/index.html#B_gsea_multitrack_05)|Prespecified ranking sensitivity|validation|scatter · NES · ranking A / NES · ranking B|

[配套组合](../assets/companion-gallery/index.html#B_gsea_multitrack_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_gsea_multitrack_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## GSVA／基因集评分 · `bulk.gsva`

核心输入：`sample_scores`、`coverage`、`score_effects`。

方法/解释限制：GSVA/ssGSEA scale and subsequent donor-level model differ; do not interpret scores as absolute activity.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_gsva_01](../assets/companion-gallery/index.html#B_gsva_01)|Gene-set coverage in the measured universe|qc|fraction · Fraction of declared denominator|
|[B_gsva_02](../assets/companion-gallery/index.html#B_gsva_02)|Interferon-pathway scores in independent donors|interpretation|raincloud · Condition / Supplied interferon GSVA score|
|[B_gsva_03](../assets/companion-gallery/index.html#B_gsva_03)|Adjusted donor-level pathway effects|interpretation|effects · Donor GSVA-score difference · supplied 95% interval|
|[B_gsva_04](../assets/companion-gallery/index.html#B_gsva_04)|GSVA scores across independent donors|interpretation|matrix · Supplied GSVA score|
|[B_gsva_05](../assets/companion-gallery/index.html#B_gsva_05)|Interferon-pathway response across measured time|extension|profile · Time (days) / Supplied interferon GSVA score|
|[B_gsva_06](../assets/companion-gallery/index.html#B_gsva_06)|Independent-cohort pathway replication|validation|effects · Donor GSVA-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_gsva_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_gsva_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 转录因子活性 · `bulk.tf_activity`

核心输入：`TF_activity`、`TF_effects`、`targets`。

方法/解释限制：Record regulon/sign and coverage; inferred activity is not direct binding evidence.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_tf_activity_01](../assets/companion-gallery/index.html#B_tf_activity_01)|Regulon target coverage|qc|fraction · Fraction of declared denominator|
|[B_tf_activity_02](../assets/companion-gallery/index.html#B_tf_activity_02)|STAT1 activity in independent donors|interpretation|raincloud · Condition / Supplied STAT1 activity score|
|[B_tf_activity_03](../assets/companion-gallery/index.html#B_tf_activity_03)|Adjusted TF activity effects|interpretation|effects · Donor TF-activity score difference · supplied 95% interval|
|[B_tf_activity_04](../assets/companion-gallery/index.html#B_tf_activity_04)|Signed TF–target evidence|function|matrix · Supplied signed regulatory prior|
|[B_tf_activity_05](../assets/companion-gallery/index.html#B_tf_activity_05)|STAT1 activity and expression|interpretation|scatter · Centered log2 STAT1 expression / Supplied STAT1 activity score|
|[B_tf_activity_06](../assets/companion-gallery/index.html#B_tf_activity_06)|TF activity across independent cohorts|validation|effects · Donor TF-activity score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_tf_activity_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_tf_activity_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 细胞组成反卷积 · `bulk.deconvolution`

核心输入：`sample_fractions`、`fraction_effects`。

方法/解释限制：Declare reference and compositional denominator; model fractions are not measured cell counts.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_deconvolution_01](../assets/companion-gallery/index.html#B_deconvolution_01)|Reference coverage within cell identities|qc|fraction · Fraction of declared denominator|
|[B_deconvolution_02](../assets/companion-gallery/index.html#B_deconvolution_02)|Complete donor mixture estimates|interpretation|fraction · Fraction of declared denominator|
|[B_deconvolution_03](../assets/companion-gallery/index.html#B_deconvolution_03)|Donor-level compositional contrasts|interpretation|effects · ln(Treated fraction / Control fraction) · 95% interval|
|[B_deconvolution_04](../assets/companion-gallery/index.html#B_deconvolution_04)|Frozen observed and reconstructed expression|qc|scatter · Observed log expression / Reconstructed log expression|
|[B_deconvolution_05](../assets/companion-gallery/index.html#B_deconvolution_05)|Reference-choice sensitivity of mixture effects|validation|effects · ln(Treated fraction / Control fraction) · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_deconvolution_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_deconvolution_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 可变剪接 · `bulk.splicing`

核心输入：`junction_coverage`、`delta_PSI`、`isoform_usage`。

方法/解释限制：Freeze event coordinates/build and donor support; gene DE and splicing are distinct tests.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_splicing_01](../assets/companion-gallery/index.html#B_splicing_01)|Physical exon and junction support|qc|locus · Genomic position · declared reference build|
|[B_splicing_02](../assets/companion-gallery/index.html#B_splicing_02)|STAT1 illustrative exon-event PSI|interpretation|raincloud · Condition / Supplied event PSI|
|[B_splicing_03](../assets/companion-gallery/index.html#B_splicing_03)|Event-level differential splicing|interpretation|effects · Supplied delta PSI · interval|
|[B_splicing_04](../assets/companion-gallery/index.html#B_splicing_04)|Event coverage and missing donor support|qc|fraction · Fraction of declared denominator|
|[B_splicing_05](../assets/companion-gallery/index.html#B_splicing_05)|Splicing effects across event types|interpretation|matrix · Supplied delta PSI|
|[B_splicing_06](../assets/companion-gallery/index.html#B_splicing_06)|Splicing-event replication|validation|effects · Supplied delta PSI · interval|

[配套组合](../assets/companion-gallery/index.html#B_splicing_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_splicing_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 转录本使用 · `bulk.dtu`

核心输入：`transcript_fractions`、`usage_intervals`。

方法/解释限制：Require transcript-version mapping and parent-gene denominator; transcript fractions are compositional.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_dtu_01](../assets/companion-gallery/index.html#B_dtu_01)|Quantifiable transcript support|qc|fraction · Fraction of declared denominator|
|[B_dtu_02](../assets/companion-gallery/index.html#B_dtu_02)|Within-gene STAT1 transcript usage by donor|interpretation|fraction · Fraction of declared denominator|
|[B_dtu_03](../assets/companion-gallery/index.html#B_dtu_03)|Prespecified STAT1 transcript-usage changes|interpretation|effects · Supplied change in transcript fraction|
|[B_dtu_04](../assets/companion-gallery/index.html#B_dtu_04)|STAT1 transcript structure and junction support|function|locus · Genomic position · declared reference build|
|[B_dtu_05](../assets/companion-gallery/index.html#B_dtu_05)|Transcript and parent-gene effects|interpretation|matrix · Supplied channel-specific standardized effect|
|[B_dtu_06](../assets/companion-gallery/index.html#B_dtu_06)|Transcript-version sensitivity|validation|effects · Transcript-fraction change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_dtu_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_dtu_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 时间与纵向变化 · `bulk.timecourse`

核心输入：`time_predictions`、`effect_intervals`。

方法/解释限制：Repeated donors and time units required; supplied model curves only, no smoothing for appearance.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_timecourse_01](../assets/companion-gallery/index.html#B_timecourse_01)|Donor support across measured times|qc|matrix · Explicit observation present|
|[B_timecourse_02](../assets/companion-gallery/index.html#B_timecourse_02)|Paired STAT1 donor response at two time points|interpretation|paired · Repeated condition / Supplied log2 STAT1 expression|
|[B_timecourse_03](../assets/companion-gallery/index.html#B_timecourse_03)|STAT1 longitudinal predictions|interpretation|profile · Time (days) / Supplied log2 STAT1 expression|
|[B_timecourse_04](../assets/companion-gallery/index.html#B_timecourse_04)|Prespecified time-by-condition effects|interpretation|effects · Log2 expression change · supplied 95% interval|
|[B_timecourse_05](../assets/companion-gallery/index.html#B_timecourse_05)|Within-donor model sensitivity|validation|effects · Log2 expression change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_timecourse_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_timecourse_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 独立队列复现 · `bulk.replication`

核心输入：`cohort_effects`、`matched_features`。

方法/解释限制：Harmonize effect scale and biological context; prevent overlap and discovery-validation leakage.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_replication_01](../assets/companion-gallery/index.html#B_replication_01)|Shared versus unavailable feature coverage|qc|fraction · Fraction of declared denominator|
|[B_replication_02](../assets/companion-gallery/index.html#B_replication_02)|Effect concordance across independent cohorts|interpretation|scatter · Discovery effect / Replication effect|
|[B_replication_03](../assets/companion-gallery/index.html#B_replication_03)|STAT1 independent-cohort effects and uncertainty|interpretation|effects · Log2 fold change · supplied 95% interval|
|[B_replication_04](../assets/companion-gallery/index.html#B_replication_04)|Direction and magnitude by cohort|interpretation|matrix · Supplied log2 effect|
|[B_replication_05](../assets/companion-gallery/index.html#B_replication_05)|Leave-one-cohort sensitivity|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_replication_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_replication_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 生存与临床关联 · `bulk.survival`

核心输入：`survival_curves`、`risk_table`、`hazard_intervals`。

方法/解释限制：Clinical use requires endpoint/censoring/design review; association is not clinical prediction validation.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_survival_01](../assets/companion-gallery/index.html#B_survival_01)|Endpoint and censoring audit|qc|fraction · Fraction of declared denominator|
|[B_survival_02](../assets/companion-gallery/index.html#B_survival_02)|Frozen survival curves and confidence intervals|interpretation|profile · Follow-up time (months) / Survival probability|
|[B_survival_03](../assets/companion-gallery/index.html#B_survival_03)|People at risk over follow-up|qc|matrix · Supplied people at risk|
|[B_survival_04](../assets/companion-gallery/index.html#B_survival_04)|Adjusted outcome associations|interpretation|effects · Supplied hazard ratio · interval|
|[B_survival_05](../assets/companion-gallery/index.html#B_survival_05)|Proportional-hazards diagnostic residuals|qc|profile · Follow-up time (months) / Supplied scaled residual|
|[B_survival_06](../assets/companion-gallery/index.html#B_survival_06)|Calibration from a held-out cohort|validation|profile · Supplied predicted risk / Supplied observed risk|

[配套组合](../assets/companion-gallery/index.html#B_survival_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_survival_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 蛋白互作 PPI · `bulk.ppi`

核心输入：`fixed_nodes`、`fixed_edges`、`edge_weights`。

方法/解释限制：Record evidence class, full selected edges and species; graph proximity is not mechanism.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_ppi_01](../assets/companion-gallery/index.html#B_ppi_01)|Interaction evidence by source|qc|matrix · Supplied evidence score|
|[B_ppi_02](../assets/companion-gallery/index.html#B_ppi_02)|Protein mapping and coverage|qc|fraction · Fraction of declared denominator|
|[B_ppi_03](../assets/companion-gallery/index.html#B_ppi_03)|Complete selected interaction weights|interpretation|matrix · Supplied PPI weight|
|[B_ppi_04](../assets/companion-gallery/index.html#B_ppi_04)|Prespecified node-level response|interpretation|effects · Node-expression log2 fold change · supplied 95% interval|
|[B_ppi_05](../assets/companion-gallery/index.html#B_ppi_05)|Network evidence across independent sources|validation|effects · Node-expression log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_ppi_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_ppi_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 扰动签名匹配 · `bulk.connectivity`

核心输入：`connection_scores`、`signature_coverage`。

方法/解释限制：Preserve perturbation/dose/cell context; reversed signatures do not establish efficacy.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_connectivity_01](../assets/companion-gallery/index.html#B_connectivity_01)|Query-signature coverage|qc|fraction · Fraction of declared denominator|
|[B_connectivity_02](../assets/companion-gallery/index.html#B_connectivity_02)|Connection scores with supplied uncertainty|interpretation|effects · Supplied connection score · interval|
|[B_connectivity_03](../assets/companion-gallery/index.html#B_connectivity_03)|Context and dose specificity|interpretation|matrix · Supplied connection score|
|[B_connectivity_04](../assets/companion-gallery/index.html#B_connectivity_04)|Prespecified dose-response summaries|extension|profile · Dose (declared unit) / Supplied connection score|
|[B_connectivity_05](../assets/companion-gallery/index.html#B_connectivity_05)|Signature reversal in independent contexts|validation|effects · Connection-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_connectivity_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_connectivity_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 非编码 RNA · `bulk.noncoding`

核心输入：`RNA_effects`、`RNA_target_edges`。

方法/解释限制：Require RNA biotype and target-evidence provenance; coexpression is not a validated ceRNA mechanism.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_noncoding_01](../assets/companion-gallery/index.html#B_noncoding_01)|RNA-biotype annotation and mapping|qc|fraction · Fraction of declared denominator|
|[B_noncoding_02](../assets/companion-gallery/index.html#B_noncoding_02)|Prespecified noncoding RNA effects|interpretation|effects · Noncoding-RNA log2 fold change · supplied 95% interval|
|[B_noncoding_03](../assets/companion-gallery/index.html#B_noncoding_03)|RNA001 expression in independent donors|interpretation|raincloud · Condition / Supplied log2 RNA001 expression|
|[B_noncoding_04](../assets/companion-gallery/index.html#B_noncoding_04)|RNA–target evidence classes|function|matrix · Supplied evidence indicator|
|[B_noncoding_05](../assets/companion-gallery/index.html#B_noncoding_05)|Noncoding RNA response replication|validation|effects · Noncoding-RNA log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#B_noncoding_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_noncoding_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 融合与转录本结构 · `bulk.fusions`

核心输入：`breakpoint_support`、`coverage`、`validation_summary`。

方法/解释限制：Needs sequence-level evidence and artifact checks; a breakpoint call is not validated oncogenicity.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[B_fusions_01](../assets/companion-gallery/index.html#B_fusions_01)|Split-read and spanning-pair support|qc|matrix · Supporting reads|
|[B_fusions_02](../assets/companion-gallery/index.html#B_fusions_02)|Breakpoint-flanking transcript support|qc|locus · Genomic position · declared reference build|
|[B_fusions_03](../assets/companion-gallery/index.html#B_fusions_03)|Breakpoint read classes|qc|fraction · Fraction of declared denominator|
|[B_fusions_04](../assets/companion-gallery/index.html#B_fusions_04)|Artifact and orthogonal evidence|interpretation|matrix · Explicit evidence indicator|
|[B_fusions_05](../assets/companion-gallery/index.html#B_fusions_05)|Event support in independent libraries|validation|effects · Supplied log support ratio · interval|

[配套组合](../assets/companion-gallery/index.html#B_fusions_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#B_fusions_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 供体与单细胞设计 · `single_cell.design`

核心输入：`donor_covariates`、`capture_counts`。

方法/解释限制：Cells, captures and donors differ; record nested design and donor replication.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_design_01](../assets/companion-gallery/index.html#S_design_01)|Capture contribution within independent donors|qc|fraction · Fraction of declared denominator|
|[S_design_02](../assets/companion-gallery/index.html#S_design_02)|Donor, condition and capture design|qc|matrix · Declared design code|
|[S_design_03](../assets/companion-gallery/index.html#S_design_03)|Donor balance within annotated identities|qc|fraction · Fraction of declared denominator|
|[S_design_04](../assets/companion-gallery/index.html#S_design_04)|Replicate support across cell identities|qc|matrix · Supplied cell count|
|[S_design_05](../assets/companion-gallery/index.html#S_design_05)|Donor-level design sensitivity|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_design_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_design_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## Barcode 与检出 · `single_cell.barcode`

核心输入：`barcode_rank`、`droplet_classes`。

方法/解释限制：Need raw droplet totals and selected threshold; cell calling does not validate cell identity.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_barcode_01](../assets/companion-gallery/index.html#S_barcode_01)|Barcode rank across captures|qc|profile · Barcode rank / Supplied log UMI count|
|[S_barcode_02](../assets/companion-gallery/index.html#S_barcode_02)|Complete droplet-call categories|qc|fraction · Fraction of declared denominator|
|[S_barcode_03](../assets/companion-gallery/index.html#S_barcode_03)|UMI distributions by droplet class|qc|bins · UMI count / Supplied count|
|[S_barcode_04](../assets/companion-gallery/index.html#S_barcode_04)|Genes and UMIs in declared droplets|qc|scatter · Supplied log UMI count (log10) / Supplied log gene count (log10)|
|[S_barcode_05](../assets/companion-gallery/index.html#S_barcode_05)|Cell-call threshold sensitivity|validation|profile · Declared calling threshold / Retained fraction|

[配套组合](../assets/companion-gallery/index.html#S_barcode_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_barcode_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 单细胞质控 · `single_cell.qc`

核心输入：`cell_metrics`、`donor_labels`。

方法/解释限制：Retain metric units and actual thresholds; cells remain nested within donors.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_qc_01](../assets/companion-gallery/index.html#S_qc_01)|Independent-donor median detected genes|qc|raincloud · Condition / Supplied donor median genes|
|[S_qc_02](../assets/companion-gallery/index.html#S_qc_02)|Independent-donor mitochondrial summaries|qc|raincloud · Condition / Supplied donor median mitochondrial fraction|
|[S_qc_03](../assets/companion-gallery/index.html#S_qc_03)|Cell complexity and mitochondrial burden|qc|scatter · Supplied log UMI count / Mitochondrial fraction|
|[S_qc_04](../assets/companion-gallery/index.html#S_qc_04)|Cell-retention audit within each donor|qc|fraction · Fraction of declared denominator|
|[S_qc_05](../assets/companion-gallery/index.html#S_qc_05)|Retained cell support by donor and identity|qc|matrix · Supplied retained cells|
|[S_qc_06](../assets/companion-gallery/index.html#S_qc_06)|Donor-response sensitivity to QC rules|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_qc_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_qc_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 环境 RNA 与双细胞 · `single_cell.ambient_doublet`

核心输入：`doublet_scores`、`ambient_profile`、`donor_rates`。

方法/解释限制：Method scores and reviewed calls are separate; preserve flagged cells and removal rules.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_ambient_doublet_01](../assets/companion-gallery/index.html#S_ambient_doublet_01)|Donor-level ambient contamination summaries|qc|raincloud · Condition / Supplied donor ambient fraction|
|[S_ambient_doublet_02](../assets/companion-gallery/index.html#S_ambient_doublet_02)|Doublet score and droplet complexity|qc|scatter · Supplied log UMI count / Supplied doublet score|
|[S_ambient_doublet_03](../assets/companion-gallery/index.html#S_ambient_doublet_03)|Reviewed doublet calls by donor|qc|fraction · Fraction of declared denominator|
|[S_ambient_doublet_04](../assets/companion-gallery/index.html#S_ambient_doublet_04)|Ambient-profile marker support|qc|matrix · Supplied expression score|
|[S_ambient_doublet_05](../assets/companion-gallery/index.html#S_ambient_doublet_05)|Biological-response sensitivity to correction|validation|effects · Log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_ambient_doublet_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_ambient_doublet_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 整合与批次 · `single_cell.integration`

核心输入：`stored_embeddings`、`mixing_scores`、`biology_scores`。

方法/解释限制：Use frozen pre/post diagnostics and batch-donor mapping; good mixing can erase biology.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_integration_01](../assets/companion-gallery/index.html#S_integration_01)|Donor batch-mixing scores before/after integration|qc|paired · Repeated condition / Supplied donor median batch-mixing score|
|[S_integration_02](../assets/companion-gallery/index.html#S_integration_02)|Batch mixing and biological conservation|qc|matrix · Supplied score (0–1)|
|[S_integration_03](../assets/companion-gallery/index.html#S_integration_03)|Batch balance within biological identities|qc|fraction · Fraction of declared denominator|
|[S_integration_04](../assets/companion-gallery/index.html#S_integration_04)|Donor-level biological-effect preservation|interpretation|effects · STAT1 donor log2 fold change · supplied 95% interval|
|[S_integration_05](../assets/companion-gallery/index.html#S_integration_05)|Integration-choice sensitivity|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_integration_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_integration_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 高变基因与 PCA · `single_cell.hvg_pca`

核心输入：`variance_profile`、`loadings`、`feature_dispersion`。

方法/解释限制：Selection source and PC loading signs required; no PCA fit during plotting.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_hvg_pca_01](../assets/companion-gallery/index.html#S_hvg_pca_01)|Feature dispersion and mean expression|qc|scatter · Supplied mean expression / Supplied dispersion|
|[S_hvg_pca_02](../assets/companion-gallery/index.html#S_hvg_pca_02)|Supplied explained variance by PC|qc|profile · Principal component / Variance fraction|
|[S_hvg_pca_03](../assets/companion-gallery/index.html#S_hvg_pca_03)|Selected genes and principal-component loadings|interpretation|matrix · Supplied loading|
|[S_hvg_pca_04](../assets/companion-gallery/index.html#S_hvg_pca_04)|Feature support across donors|qc|fraction · Fraction of declared denominator|
|[S_hvg_pca_05](../assets/companion-gallery/index.html#S_hvg_pca_05)|Biological summaries across PC choices|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_hvg_pca_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_hvg_pca_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 分辨率与聚类流向 · `single_cell.resolution`

核心输入：`resolution_edges`、`stability`、`donor_support`。

方法/解释限制：Freeze cluster lineage and selected resolution; stability does not establish biological identity.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_resolution_01](../assets/companion-gallery/index.html#S_resolution_01)|Donor support at declared resolutions|qc|matrix · Supplied cell count|
|[S_resolution_02](../assets/companion-gallery/index.html#S_resolution_02)|Donor mixture within selected clusters|interpretation|fraction · Fraction of declared denominator|
|[S_resolution_03](../assets/companion-gallery/index.html#S_resolution_03)|Marker specificity across candidate clusters|interpretation|matrix · Supplied marker score|
|[S_resolution_04](../assets/companion-gallery/index.html#S_resolution_04)|Supplied resampling stability|interpretation|effects · Supplied stability · interval|
|[S_resolution_05](../assets/companion-gallery/index.html#S_resolution_05)|Independent annotation consistency|validation|effects · Label-agreement fraction difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_resolution_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_resolution_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 细胞注释证据 · `single_cell.annotation`

核心输入：`embedding`、`label_anchors`、`marker_means`、`detection_fractions`。

方法/解释限制：Atlas identity and specificity; per-subgroup multi-marker pages are complete separate companions. Annotation specificity and uncertainty require review.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_annotation_01](../assets/companion-gallery/index.html#S_annotation_01)|Reference-label coverage within donors|qc|fraction · Fraction of declared denominator|
|[S_annotation_02](../assets/companion-gallery/index.html#S_annotation_02)|Positive and exclusion marker evidence|interpretation|matrix · Supplied marker score|
|[S_annotation_03](../assets/companion-gallery/index.html#S_annotation_03)|Donor-level annotation confidence|interpretation|raincloud · Condition / Supplied donor median confidence|
|[S_annotation_04](../assets/companion-gallery/index.html#S_annotation_04)|Prediction uncertainty and review decisions|interpretation|matrix · Supplied confidence|
|[S_annotation_05](../assets/companion-gallery/index.html#S_annotation_05)|Identity support in independent cohorts|validation|effects · Label-support fraction difference · supplied 95% interval|
|[S_annotation_06](../assets/companion-gallery/index.html#S_annotation_06)|Discordant calls retained for review|validation|fraction · Fraction of declared denominator|

[配套组合](../assets/companion-gallery/index.html#S_annotation_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_annotation_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#S_annotation_ThreeColumns)。

## 逐亚群与多 marker · `single_cell.subcluster`

核心输入：`lineage_embedding`、`markers`、`parent_child_labels`。

方法/解释限制：Explicit parent selection and child annotation; subclustering requires actual reanalysis upstream.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_subcluster_01](../assets/companion-gallery/index.html#S_subcluster_01)|Parent-lineage donor support|qc|matrix · Supplied cell count|
|[S_subcluster_02](../assets/companion-gallery/index.html#S_subcluster_02)|Child-state positive and exclusion markers|interpretation|matrix · Supplied marker score|
|[S_subcluster_03](../assets/companion-gallery/index.html#S_subcluster_03)|Child-state composition within donors|interpretation|fraction · Fraction of declared denominator|
|[S_subcluster_04](../assets/companion-gallery/index.html#S_subcluster_04)|Donor-level child-state response|interpretation|effects · Child-state log abundance ratio · supplied 95% interval|
|[S_subcluster_05](../assets/companion-gallery/index.html#S_subcluster_05)|Child-state reproducibility across choices|validation|effects · Child-state log abundance ratio · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_subcluster_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_subcluster_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## Marker 特异性 · `single_cell.markers`

核心输入：`marker_means`、`detection_fractions`、`annotation_blocks`。

方法/解释限制：Denominator must be all declared cells in a group; marker ranking is not donor-level DE.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_markers_01](../assets/companion-gallery/index.html#S_markers_01)|Marker detection coverage|qc|matrix · Fraction of cells detected|
|[S_markers_02](../assets/companion-gallery/index.html#S_markers_02)|Marker mean-expression specificity|interpretation|matrix · Centered mean expression|
|[S_markers_03](../assets/companion-gallery/index.html#S_markers_03)|Donor-level marker effect estimates|interpretation|effects · Donor marker log2 fold change · supplied 95% interval|
|[S_markers_04](../assets/companion-gallery/index.html#S_markers_04)|STAT1 marker expression in independent donors|interpretation|raincloud · Condition / Supplied pseudobulk log2 STAT1 expression|
|[S_markers_05](../assets/companion-gallery/index.html#S_markers_05)|Marker evidence in independent donors|validation|effects · Donor marker log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_markers_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_markers_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 供体层面细胞组成 · `single_cell.composition`

核心输入：`donor_type_counts`、`donor_totals`。

方法/解释限制：Use complete donor denominators; pooled cell fractions do not provide independent replication.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_composition_01](../assets/companion-gallery/index.html#S_composition_01)|Complete donor cell-identity composition|qc|fraction · Fraction of declared denominator|
|[S_composition_02](../assets/companion-gallery/index.html#S_composition_02)|T-cell fractions in independent donors|interpretation|raincloud · Condition / Supplied T-cell fraction|
|[S_composition_03](../assets/companion-gallery/index.html#S_composition_03)|Prespecified compositional effects|interpretation|effects · Supplied log-ratio effect · interval|
|[S_composition_04](../assets/companion-gallery/index.html#S_composition_04)|Identity support across donors|qc|matrix · Supplied cell count|
|[S_composition_05](../assets/companion-gallery/index.html#S_composition_05)|Composition sensitivity to identity definitions|validation|effects · ln(Treated fraction / Control fraction) · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_composition_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_composition_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 差异丰度 · `single_cell.abundance`

核心输入：`neighborhood_effects`、`donor_fractions`、`coordinates`。

方法/解释限制：Milo/scCODA need distinct model/null/denominator; abundance and expression are different estimands.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_abundance_01](../assets/companion-gallery/index.html#S_abundance_01)|Neighborhood support across donors|qc|matrix · Supplied neighborhood cells|
|[S_abundance_02](../assets/companion-gallery/index.html#S_abundance_02)|Donor-aware neighborhood abundance effects|interpretation|effects · Supplied log abundance ratio · interval|
|[S_abundance_03](../assets/companion-gallery/index.html#S_abundance_03)|Selected neighborhood N01 donor fractions|interpretation|raincloud · Condition / Supplied N01 neighborhood fraction|
|[S_abundance_04](../assets/companion-gallery/index.html#S_abundance_04)|Neighborhood size and abundance effect|interpretation|scatter · Supplied neighborhood size / Supplied abundance effect|
|[S_abundance_05](../assets/companion-gallery/index.html#S_abundance_05)|Neighborhood and model-choice sensitivity|validation|effects · Log neighborhood abundance ratio · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_abundance_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_abundance_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 供体级伪 bulk · `single_cell.pseudobulk`

核心输入：`complete_donor_de`、`contrast`、`FDR`、`marginal_counts`。

方法/解释限制：Donor/celltype counts and design must be reviewed; no cell-level pseudoreplication.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_pseudobulk_01](../assets/companion-gallery/index.html#S_pseudobulk_01)|Cell support for each donor–identity aggregate|qc|matrix · Supplied aggregate cells|
|[S_pseudobulk_02](../assets/companion-gallery/index.html#S_pseudobulk_02)|Independent-donor library-size summaries|qc|raincloud · Condition / Aggregate library size (million UMIs)|
|[S_pseudobulk_03](../assets/companion-gallery/index.html#S_pseudobulk_03)|Donor-level differential-expression effects|interpretation|effects · Donor log2 fold change · supplied 95% interval|
|[S_pseudobulk_04](../assets/companion-gallery/index.html#S_pseudobulk_04)|STAT1 pseudobulk expression in independent donors|interpretation|raincloud · Condition / Supplied pseudobulk log2 STAT1 expression|
|[S_pseudobulk_05](../assets/companion-gallery/index.html#S_pseudobulk_05)|Celltype-specific differential responses|interpretation|matrix · Supplied log2 fold change|
|[S_pseudobulk_06](../assets/companion-gallery/index.html#S_pseudobulk_06)|Donor-omission sensitivity of effects|validation|effects · Donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_pseudobulk_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_pseudobulk_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 多细胞类型与多对比 · `single_cell.multi_contrast`

核心输入：`effect_grid`、`FDR_grid`、`tested_feature_counts`。

方法/解释限制：Keep separate comparison families and not-tested entries; do not pool donor and cell p-values.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_multi_contrast_01](../assets/companion-gallery/index.html#S_multi_contrast_01)|Independent support across contrast families|qc|matrix · Independent donor count|
|[S_multi_contrast_02](../assets/companion-gallery/index.html#S_multi_contrast_02)|Complete signed effect atlas|interpretation|matrix · Supplied log2 fold change|
|[S_multi_contrast_03](../assets/companion-gallery/index.html#S_multi_contrast_03)|Prespecified identity-by-condition effects|interpretation|effects · STAT1 donor log2 fold change · supplied 95% interval|
|[S_multi_contrast_04](../assets/companion-gallery/index.html#S_multi_contrast_04)|Effect concordance between contrasts|interpretation|scatter · Effect · contrast A / Effect · contrast B|
|[S_multi_contrast_05](../assets/companion-gallery/index.html#S_multi_contrast_05)|Cross-contrast replication effects|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_multi_contrast_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_multi_contrast_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 单细胞通路 · `single_cell.pathways`

核心输入：`NES_grid`、`FDR_grid`、`leading_edge`。

方法/解释限制：Preserve celltype contrast and set coverage; activity direction cannot be inferred from ORA.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_pathways_01](../assets/companion-gallery/index.html#S_pathways_01)|Measured gene-set support in T-cell aggregates|qc|fraction · Fraction of declared denominator|
|[S_pathways_02](../assets/companion-gallery/index.html#S_pathways_02)|Celltype-specific normalized enrichment|interpretation|matrix · Supplied NES|
|[S_pathways_03](../assets/companion-gallery/index.html#S_pathways_03)|Interferon scores in T-cell donor aggregates|interpretation|raincloud · Condition / Supplied donor interferon-pathway score|
|[S_pathways_04](../assets/companion-gallery/index.html#S_pathways_04)|Donor-level pathway responses|interpretation|effects · Donor pathway-score difference · supplied 95% interval|
|[S_pathways_05](../assets/companion-gallery/index.html#S_pathways_05)|Celltype-specific leading-edge support|function|matrix · Explicit leading-edge membership|
|[S_pathways_06](../assets/companion-gallery/index.html#S_pathways_06)|Pathway replication in independent donors|validation|effects · Donor pathway-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_pathways_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_pathways_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 通路与支持基因 · `single_cell.gene_support`

核心输入：`term_overlap`、`gene_term_membership`、`gene_effects`。

方法/解释限制：Preserve celltype-specific tested universe and exact annotation membership.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_gene_support_01](../assets/companion-gallery/index.html#S_gene_support_01)|Pathway membership of selected supporting genes|qc|matrix · Explicit membership|
|[S_gene_support_02](../assets/companion-gallery/index.html#S_gene_support_02)|Supporting-gene donor-level effects|interpretation|effects · Donor log2 fold change · supplied 95% interval|
|[S_gene_support_03](../assets/companion-gallery/index.html#S_gene_support_03)|STAT1 pseudobulk expression supporting the pathway|interpretation|raincloud · Condition / Supplied log2 STAT1 expression|
|[S_gene_support_04](../assets/companion-gallery/index.html#S_gene_support_04)|Support direction across identities|function|matrix · Supplied log2 fold change|
|[S_gene_support_05](../assets/companion-gallery/index.html#S_gene_support_05)|Supporting-gene external replication|validation|effects · Donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_gene_support_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_gene_support_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 细胞状态与程序 · `single_cell.states`

核心输入：`state_scores`、`coverage`、`donor_effects`。

方法/解释限制：Score coverage/cell cycle and donor model need review; cell scores do not increase independent n.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_states_01](../assets/companion-gallery/index.html#S_states_01)|State-program gene coverage|qc|fraction · Fraction of declared denominator|
|[S_states_02](../assets/companion-gallery/index.html#S_states_02)|Interferon state scores in independent donors|interpretation|raincloud · Condition / Supplied interferon-state score|
|[S_states_03](../assets/companion-gallery/index.html#S_states_03)|Donor-level state-program effects|interpretation|effects · Donor state-score difference · supplied 95% interval|
|[S_states_04](../assets/companion-gallery/index.html#S_states_04)|State, stress and cycle contexts|interpretation|matrix · Supplied state score|
|[S_states_05](../assets/companion-gallery/index.html#S_states_05)|State effects after prespecified cycle adjustment|validation|effects · Donor state-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_states_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_states_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 轨迹与程序变化 · `single_cell.trajectory`

核心输入：`embedding`、`pseudotime`、`branch_curves`、`gene_trends`。

方法/解释限制：Freeze root/branch and uncertainty; pseudotime is not chronological time or lineage proof.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_trajectory_01](../assets/companion-gallery/index.html#S_trajectory_01)|Donor support across branches|qc|matrix · Supplied cell count|
|[S_trajectory_02](../assets/companion-gallery/index.html#S_trajectory_02)|Interferon program along fixed branches|interpretation|profile · Supplied pseudotime / Supplied interferon-program score|
|[S_trajectory_03](../assets/companion-gallery/index.html#S_trajectory_03)|Branch A occupancy in independent donors|interpretation|raincloud · Condition / Supplied Branch A fraction|
|[S_trajectory_04](../assets/companion-gallery/index.html#S_trajectory_04)|Branch-specific donor-level effects|interpretation|effects · Branch-associated log2 fold change · supplied 95% interval|
|[S_trajectory_05](../assets/companion-gallery/index.html#S_trajectory_05)|Ordered expression on fixed pseudotime bins|function|matrix · Supplied scaled expression|
|[S_trajectory_06](../assets/companion-gallery/index.html#S_trajectory_06)|Root and branch-choice sensitivity|validation|effects · Branch-associated log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_trajectory_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_trajectory_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## RNA velocity · `single_cell.velocity`

核心输入：`vectors`、`spliced_unspliced`、`fit_diagnostics`。

方法/解释限制：Require assay-compatible splicing layers, fitted vectors and scale; arrows do not prove fate.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_velocity_01](../assets/companion-gallery/index.html#S_velocity_01)|STAT1 spliced–unspliced phase support|qc|scatter · Supplied normalized spliced counts / Supplied normalized unspliced counts|
|[S_velocity_02](../assets/companion-gallery/index.html#S_velocity_02)|Donor-level velocity confidence|qc|raincloud · Condition / Supplied donor median confidence|
|[S_velocity_03](../assets/companion-gallery/index.html#S_velocity_03)|Velocity model support by gene|qc|matrix · Supplied diagnostic|
|[S_velocity_04](../assets/companion-gallery/index.html#S_velocity_04)|STAT1 response along supplied latent time|interpretation|profile · Supplied latent time / Supplied normalized STAT1 response|
|[S_velocity_05](../assets/companion-gallery/index.html#S_velocity_05)|Direction stability across model choices|validation|effects · Velocity-direction agreement difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_velocity_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_velocity_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 细胞通讯 · `single_cell.communication`

核心输入：`sender_receiver`、`LR_scores`、`coverage`。

方法/解释限制：CellChat/LIANA/CellPhoneDB scores are method-specific; donor-aware contrast and permutations required.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_communication_01](../assets/companion-gallery/index.html#S_communication_01)|Ligand and receptor expression support|qc|matrix · Fraction detected|
|[S_communication_02](../assets/companion-gallery/index.html#S_communication_02)|Outgoing pathway contributions|interpretation|matrix · Supplied outgoing contribution|
|[S_communication_03](../assets/companion-gallery/index.html#S_communication_03)|Incoming pathway contributions|interpretation|matrix · Supplied incoming contribution|
|[S_communication_04](../assets/companion-gallery/index.html#S_communication_04)|Donor-aware signaling contrasts|interpretation|effects · Supplied signaling contrast · interval|
|[S_communication_05](../assets/companion-gallery/index.html#S_communication_05)|Changes in outgoing and incoming roles|interpretation|scatter · Supplied outgoing change / Supplied incoming change|
|[S_communication_06](../assets/companion-gallery/index.html#S_communication_06)|Ligand–receptor support across donors|qc|fraction · Fraction of declared denominator|
|[S_communication_07](../assets/companion-gallery/index.html#S_communication_07)|Signaling effects in an independent cohort|validation|effects · Donor signaling-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_communication_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_communication_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#S_communication_ThreeColumns)。

## 配体靶基因支持 · `single_cell.ligand_target`

核心输入：`ligand_activity`、`target_potential`、`network`。

方法/解释限制：NicheNet prior and receiver context required; target potential does not prove signaling causality.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_ligand_target_01](../assets/companion-gallery/index.html#S_ligand_target_01)|Prior coverage in the receiver context|qc|fraction · Fraction of declared denominator|
|[S_ligand_target_02](../assets/companion-gallery/index.html#S_ligand_target_02)|Prespecified ligand-activity contrasts|interpretation|effects · Donor ligand-activity difference · supplied 95% interval|
|[S_ligand_target_03](../assets/companion-gallery/index.html#S_ligand_target_03)|Ligand-to-target potential|function|matrix · Supplied target potential|
|[S_ligand_target_04](../assets/companion-gallery/index.html#S_ligand_target_04)|Receiver target-gene differential response|interpretation|effects · Receiver gene log2 fold change · supplied 95% interval|
|[S_ligand_target_05](../assets/companion-gallery/index.html#S_ligand_target_05)|Ligand-to-target evidence across prior choices|validation|effects · Donor ligand-activity difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_ligand_target_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_ligand_target_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## Regulon 与 TF 活性 · `single_cell.regulons`

核心输入：`regulon_scores`、`specificity`、`target_edges`。

方法/解释限制：SCENIC/AUCell motif/score evidence is not direct binding or causal regulation.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_regulons_01](../assets/companion-gallery/index.html#S_regulons_01)|Motif and target coverage by regulon|qc|fraction · Fraction of declared denominator|
|[S_regulons_02](../assets/companion-gallery/index.html#S_regulons_02)|STAT1 regulon activity in independent donors|interpretation|raincloud · Condition / Supplied STAT1 AUCell activity|
|[S_regulons_03](../assets/companion-gallery/index.html#S_regulons_03)|Donor-level regulon activity effects|interpretation|effects · Donor AUCell-activity difference · supplied 95% interval|
|[S_regulons_04](../assets/companion-gallery/index.html#S_regulons_04)|Regulon specificity across identities|interpretation|matrix · Supplied specificity|
|[S_regulons_05](../assets/companion-gallery/index.html#S_regulons_05)|Motif support and signed target priors|function|matrix · Supplied regulatory prior|
|[S_regulons_06](../assets/companion-gallery/index.html#S_regulons_06)|Regulon effects in independent donors|validation|effects · Donor AUCell-activity difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_regulons_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_regulons_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 拷贝数变化 CNV · `single_cell.cnv`

核心输入：`ordered_CNV`、`reference_cells`、`clone_support`。

方法/解释限制：Genomic coordinates and normal reference required; RNA-inferred CNV needs independent genomic validation.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_cnv_01](../assets/companion-gallery/index.html#S_cnv_01)|Reference-normal support by donor|qc|matrix · Supplied reference cells|
|[S_cnv_02](../assets/companion-gallery/index.html#S_cnv_02)|Genomically ordered CNV summaries|interpretation|profile · Ordered bin index · fictional reference / Supplied log2 relative CNV|
|[S_cnv_03](../assets/companion-gallery/index.html#S_cnv_03)|Clone composition within each donor|interpretation|fraction · Fraction of declared denominator|
|[S_cnv_04](../assets/companion-gallery/index.html#S_cnv_04)|Donor-level CNV burden summaries|interpretation|raincloud · Condition / Supplied CNV burden|
|[S_cnv_05](../assets/companion-gallery/index.html#S_cnv_05)|Clone-associated donor effects|interpretation|effects · Clone log abundance ratio · supplied 95% interval|
|[S_cnv_06](../assets/companion-gallery/index.html#S_cnv_06)|Orthogonal genomic support by chromosome|validation|matrix · Explicit support indicator|

[配套组合](../assets/companion-gallery/index.html#S_cnv_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_cnv_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## VDJ 与克隆 · `single_cell.vdj`

核心输入：`clonotype_counts`、`VDJ_QC`、`sharing`。

方法/解释限制：Require real VDJ calls and donor denominators; transcriptome-only data do not identify clonotypes.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_vdj_01](../assets/companion-gallery/index.html#S_vdj_01)|VDJ quality and productive-chain support|qc|fraction · Fraction of declared denominator|
|[S_vdj_02](../assets/companion-gallery/index.html#S_vdj_02)|Frozen clone-size distributions|interpretation|bins · Clonotype size / Supplied count|
|[S_vdj_03](../assets/companion-gallery/index.html#S_vdj_03)|Clone expansion classes within donors|interpretation|fraction · Fraction of declared denominator|
|[S_vdj_04](../assets/companion-gallery/index.html#S_vdj_04)|Clonotype sharing across sampled compartments|interpretation|matrix · Supplied overlap fraction|
|[S_vdj_05](../assets/companion-gallery/index.html#S_vdj_05)|Donor-level diversity contrasts|interpretation|effects · Supplied diversity contrast · interval|
|[S_vdj_06](../assets/companion-gallery/index.html#S_vdj_06)|Paired clonotype summaries over follow-up|interpretation|paired · Repeated condition / Supplied Shannon diversity score|
|[S_vdj_07](../assets/companion-gallery/index.html#S_vdj_07)|Repertoire findings in independent donors|validation|effects · Shannon-diversity difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_vdj_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_vdj_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 单细胞剪接 · `single_cell.splicing`

核心输入：`junction_coverage`、`delta_PSI`、`isoform_usage`。

方法/解释限制：Donor support and event mapping required; cell-level detection sparsity must be reviewed.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_splicing_01](../assets/companion-gallery/index.html#S_splicing_01)|T-cell STAT1 E01 physical junction support|qc|locus · Genomic position · declared reference build|
|[S_splicing_02](../assets/companion-gallery/index.html#S_splicing_02)|Event support across donors and identities|qc|matrix · Fraction of supported donors|
|[S_splicing_03](../assets/companion-gallery/index.html#S_splicing_03)|STAT1 event PSI in T-cell donor aggregates|interpretation|raincloud · Condition / Supplied event PSI|
|[S_splicing_04](../assets/companion-gallery/index.html#S_splicing_04)|T-cell donor differential splicing|interpretation|effects · Supplied delta PSI · interval|
|[S_splicing_05](../assets/companion-gallery/index.html#S_splicing_05)|Splicing-event effects across identities|interpretation|matrix · Supplied delta PSI|
|[S_splicing_06](../assets/companion-gallery/index.html#S_splicing_06)|T-cell event replication|validation|effects · Supplied delta PSI · interval|

[配套组合](../assets/companion-gallery/index.html#S_splicing_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_splicing_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## Perturb-seq · `single_cell.perturbseq`

核心输入：`guide_assignment`、`perturbation_effects`、`replicate_QC`。

方法/解释限制：Actual guide calls, controls and independent replicates required; guide abundance is not perturbation efficacy.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_perturbseq_01](../assets/companion-gallery/index.html#S_perturbseq_01)|Complete guide assignment by replicate|qc|fraction · Fraction of declared denominator|
|[S_perturbseq_02](../assets/companion-gallery/index.html#S_perturbseq_02)|Guide support across donors|qc|matrix · Supplied guide-assigned cells|
|[S_perturbseq_03](../assets/companion-gallery/index.html#S_perturbseq_03)|STAT1 response by guide and control|interpretation|effects · Perturbation-response log2 fold change · supplied 95% interval|
|[S_perturbseq_04](../assets/companion-gallery/index.html#S_perturbseq_04)|Perturbation program responses|interpretation|matrix · Supplied response|
|[S_perturbseq_05](../assets/companion-gallery/index.html#S_perturbseq_05)|Gene responses across independent guide designs|validation|effects · Perturbation-response log2 fold change · supplied 95% interval|
|[S_perturbseq_06](../assets/companion-gallery/index.html#S_perturbseq_06)|Perturbation response in independent donors|validation|effects · Perturbation-response log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_perturbseq_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_perturbseq_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 单细胞独立复现 · `single_cell.replication`

核心输入：`cohort_effects`、`transfer_confidence`、`coverage`。

方法/解释限制：Independent cohorts and matching cell ontology required; transfer confidence is not validation truth.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_replication_01](../assets/companion-gallery/index.html#S_replication_01)|Cross-cohort ontology and feature coverage|qc|fraction · Fraction of declared denominator|
|[S_replication_02](../assets/companion-gallery/index.html#S_replication_02)|T-cell gene-effect concordance|interpretation|scatter · Discovery effect / Replication effect|
|[S_replication_03](../assets/companion-gallery/index.html#S_replication_03)|Independent-cohort donor-level effects|interpretation|effects · STAT1 donor log2 fold change · supplied 95% interval|
|[S_replication_04](../assets/companion-gallery/index.html#S_replication_04)|Label-transfer confidence and review|qc|matrix · Supplied confidence|
|[S_replication_05](../assets/companion-gallery/index.html#S_replication_05)|Leave-one-cohort stability|validation|effects · STAT1 donor log2 fold change · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_replication_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_replication_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 空间转录组 · `single_cell.spatial`

核心输入：`registered_coordinates`、`region_scores`、`section_effects`。

方法/解释限制：Requires measured spatial assay and registration; dissociated UMAP is not tissue geography.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_spatial_01](../assets/companion-gallery/index.html#S_spatial_01)|Section and donor support by region|qc|matrix · Supplied region spots|
|[S_spatial_02](../assets/companion-gallery/index.html#S_spatial_02)|Interferon scores in donor region R01|interpretation|raincloud · Condition / Supplied regional interferon score|
|[S_spatial_03](../assets/companion-gallery/index.html#S_spatial_03)|Donor-aware region contrasts|interpretation|effects · Regional program-score difference · supplied 95% interval|
|[S_spatial_04](../assets/companion-gallery/index.html#S_spatial_04)|Region-program evidence|function|matrix · Supplied region score|
|[S_spatial_05](../assets/companion-gallery/index.html#S_spatial_05)|Measured-distance and neighborhood summaries|interpretation|scatter · Supplied tissue distance (µm) / Supplied neighborhood statistic|
|[S_spatial_06](../assets/companion-gallery/index.html#S_spatial_06)|Section and registration-choice sensitivity|validation|effects · Regional program-score difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_spatial_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_spatial_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

## 多组学与调控连接 · `single_cell.multiome`

核心输入：`paired_embeddings`、`peak_gene_links`、`motif_scores`。

方法/解释限制：Paired assay, build and peak/link evidence required; peak-gene association is not causal regulation.

|实际页|问题|阶段|绘图通道|
|---|---|---|---|
|[S_multiome_01](../assets/companion-gallery/index.html#S_multiome_01)|Paired-modality support within donors|qc|fraction · Fraction of declared denominator|
|[S_multiome_02](../assets/companion-gallery/index.html#S_multiome_02)|RNA and ATAC quality channels|qc|matrix · Supplied standardized diagnostic|
|[S_multiome_03](../assets/companion-gallery/index.html#S_multiome_03)|Motif and RNA response evidence|interpretation|matrix · Supplied standardized effect|
|[S_multiome_04](../assets/companion-gallery/index.html#S_multiome_04)|Prespecified peak–gene association estimates|interpretation|effects · Peak–gene regression coefficient · supplied 95% interval|
|[S_multiome_05](../assets/companion-gallery/index.html#S_multiome_05)|Frozen peak and gene-locus evidence|function|locus · Genomic position · declared reference build|
|[S_multiome_06](../assets/companion-gallery/index.html#S_multiome_06)|Regulatory association in independent donors|validation|effects · Peak–gene coefficient difference · supplied 95% interval|

[配套组合](../assets/companion-gallery/index.html#S_multiome_Evidence) · [扩展数据/一列阅读](../assets/companion-gallery/index.html#S_multiome_Layout)。每页可获取实际 PNG/SVG/PDF、准确 TSV 与 FigureSpec；组合包含的单页不在默认套件中重复输出。

[显式三列宽版](../assets/companion-gallery/index.html#S_multiome_ThreeColumns)。
