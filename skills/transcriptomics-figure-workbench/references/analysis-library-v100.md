# 按分析导出整套绘图模板

从实际 FigureSpec 生成；章节、图页、调用视图与科学算法数量分别统计。所有示例均为冻结合成绘图材料，没有运行分析后端。

|分析|默认配套视图|替代／布局|
|---|---:|---:|
|设计与独立样本 (`bulk.design`)|7|3|
|测序读段质控 (`bulk.reads`)|9|2|
|比对与覆盖 (`bulk.alignment`)|8|2|
|基因检出与过滤 (`bulk.filtering`)|7|2|
|标准化与均值方差 (`bulk.normalization`)|7|2|
|样本关系与批次 (`bulk.batch`)|6|2|
|差异表达 (`bulk.differential`)|9|3|
|交互效应 (`bulk.interaction`)|7|2|
|模型诊断 (`bulk.model_qc`)|11|2|
|基因程序与效应 (`bulk.programs`)|7|2|
|ORA 功能富集 (`bulk.ora`)|8|2|
|GSEA 完整证据 (`bulk.gsea`)|7|3|
|通路跨对比 (`bulk.pathway_contrasts`)|7|2|
|通路支持基因 (`bulk.gene_support`)|7|2|
|多通路 GSEA (`bulk.gsea_multitrack`)|6|2|
|GSVA／基因集评分 (`bulk.gsva`)|10|2|
|WGCNA 共表达网络 (`bulk.wgcna`)|23|12|
|转录因子活性 (`bulk.tf_activity`)|10|2|
|细胞组成反卷积 (`bulk.deconvolution`)|7|2|
|可变剪接 (`bulk.splicing`)|11|2|
|转录本使用 (`bulk.dtu`)|9|2|
|时间与纵向变化 (`bulk.timecourse`)|8|2|
|独立队列复现 (`bulk.replication`)|8|2|
|生存与临床关联 (`bulk.survival`)|9|2|
|蛋白互作 PPI (`bulk.ppi`)|8|2|
|扰动签名匹配 (`bulk.connectivity`)|7|2|
|非编码 RNA (`bulk.noncoding`)|7|2|
|融合与转录本结构 (`bulk.fusions`)|7|2|
|供体与单细胞设计 (`single_cell.design`)|7|2|
|Barcode 与检出 (`single_cell.barcode`)|7|2|
|单细胞质控 (`single_cell.qc`)|7|2|
|环境 RNA 与双细胞 (`single_cell.ambient_doublet`)|7|2|
|整合与批次 (`single_cell.integration`)|7|2|
|高变基因与 PCA (`single_cell.hvg_pca`)|8|2|
|分辨率与聚类流向 (`single_cell.resolution`)|8|3|
|细胞注释证据 (`single_cell.annotation`)|16|3|
|逐亚群与多 marker (`single_cell.subcluster`)|12|2|
|Marker 特异性 (`single_cell.markers`)|6|2|
|供体层面细胞组成 (`single_cell.composition`)|6|2|
|差异丰度 (`single_cell.abundance`)|7|2|
|供体级伪 bulk (`single_cell.pseudobulk`)|7|2|
|多细胞类型与多对比 (`single_cell.multi_contrast`)|8|2|
|单细胞通路 (`single_cell.pathways`)|9|2|
|通路与支持基因 (`single_cell.gene_support`)|7|2|
|细胞状态与程序 (`single_cell.states`)|8|2|
|hdWGCNA 共表达网络 (`single_cell.hdwgcna`)|26|12|
|轨迹与程序变化 (`single_cell.trajectory`)|11|4|
|RNA velocity (`single_cell.velocity`)|8|2|
|细胞通讯 (`single_cell.communication`)|9|3|
|配体靶基因支持 (`single_cell.ligand_target`)|8|2|
|Regulon 与 TF 活性 (`single_cell.regulons`)|10|2|
|拷贝数变化 CNV (`single_cell.cnv`)|8|2|
|VDJ 与克隆 (`single_cell.vdj`)|11|2|
|单细胞剪接 (`single_cell.splicing`)|11|2|
|Perturb-seq (`single_cell.perturbseq`)|9|2|
|单细胞独立复现 (`single_cell.replication`)|8|2|
|空间转录组 (`single_cell.spatial`)|9|2|
|多组学与调控连接 (`single_cell.multiome`)|9|3|

## 使用

`analysis-library --search WGCNA` 列出对应整套路线。`analysis-suite --chapter bulk.wgcna --output <fresh-directory>` 导出该分析的全部默认合成模板、准确 TSV 和批量绘图 manifest；加 `--include-variants` 才导出相近替代与布局。`analysis-render --manifest <fresh-directory>/manifest.json --output <fresh-render-directory>` 串行绘制这些合成模板。实际项目应使用 `book-plan`，逐项绑定已经完成且 QC 审核的真实结果。

默认与替代由实际数据语义决定；没有云形时不估算密度，没有完整命中时不冒充完整 GSEA，没有模块结果时不生成 WGCNA 结论。模板完整性与真实结果可用性是不同状态。各章节的主图和诊断／验证视图不是所有分析方法已穷尽的声明。
