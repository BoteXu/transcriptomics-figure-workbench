# 按分析导出整套绘图模板

从实际 FigureSpec 生成；章节、图页、调用视图与科学算法数量分别统计。所有示例均为冻结合成绘图材料，没有运行分析后端。

|分析|默认配套视图|替代／布局|
|---|---:|---:|
|设计与独立样本 (`bulk.design`)|2|0|
|测序读段质控 (`bulk.reads`)|2|0|
|比对与覆盖 (`bulk.alignment`)|2|0|
|基因检出与过滤 (`bulk.filtering`)|2|0|
|标准化与均值方差 (`bulk.normalization`)|2|0|
|样本关系与批次 (`bulk.batch`)|1|0|
|差异表达 (`bulk.differential`)|2|0|
|交互效应 (`bulk.interaction`)|2|0|
|模型诊断 (`bulk.model_qc`)|6|0|
|基因程序与效应 (`bulk.programs`)|2|0|
|ORA 功能富集 (`bulk.ora`)|2|0|
|GSEA 完整证据 (`bulk.gsea`)|1|0|
|通路跨对比 (`bulk.pathway_contrasts`)|2|0|
|通路支持基因 (`bulk.gene_support`)|2|0|
|多通路 GSEA (`bulk.gsea_multitrack`)|1|0|
|GSVA／基因集评分 (`bulk.gsva`)|4|0|
|WGCNA 共表达网络 (`bulk.wgcna`)|23|12|
|转录因子活性 (`bulk.tf_activity`)|4|0|
|细胞组成反卷积 (`bulk.deconvolution`)|2|0|
|可变剪接 (`bulk.splicing`)|5|0|
|转录本使用 (`bulk.dtu`)|3|0|
|时间与纵向变化 (`bulk.timecourse`)|3|0|
|独立队列复现 (`bulk.replication`)|3|0|
|生存与临床关联 (`bulk.survival`)|3|0|
|蛋白互作 PPI (`bulk.ppi`)|3|0|
|扰动签名匹配 (`bulk.connectivity`)|2|0|
|非编码 RNA (`bulk.noncoding`)|2|0|
|融合与转录本结构 (`bulk.fusions`)|2|0|
|供体与单细胞设计 (`single_cell.design`)|2|0|
|Barcode 与检出 (`single_cell.barcode`)|2|0|
|单细胞质控 (`single_cell.qc`)|1|0|
|环境 RNA 与双细胞 (`single_cell.ambient_doublet`)|2|0|
|整合与批次 (`single_cell.integration`)|2|0|
|高变基因与 PCA (`single_cell.hvg_pca`)|3|0|
|分辨率与聚类流向 (`single_cell.resolution`)|3|1|
|细胞注释证据 (`single_cell.annotation`)|10|0|
|逐亚群与多 marker (`single_cell.subcluster`)|7|0|
|Marker 特异性 (`single_cell.markers`)|1|0|
|供体层面细胞组成 (`single_cell.composition`)|1|0|
|差异丰度 (`single_cell.abundance`)|2|0|
|供体级伪 bulk (`single_cell.pseudobulk`)|1|0|
|多细胞类型与多对比 (`single_cell.multi_contrast`)|3|0|
|单细胞通路 (`single_cell.pathways`)|3|0|
|通路与支持基因 (`single_cell.gene_support`)|2|0|
|细胞状态与程序 (`single_cell.states`)|3|0|
|hdWGCNA 共表达网络 (`single_cell.hdwgcna`)|26|12|
|轨迹与程序变化 (`single_cell.trajectory`)|5|2|
|RNA velocity (`single_cell.velocity`)|3|0|
|细胞通讯 (`single_cell.communication`)|2|0|
|配体靶基因支持 (`single_cell.ligand_target`)|3|0|
|Regulon 与 TF 活性 (`single_cell.regulons`)|4|0|
|拷贝数变化 CNV (`single_cell.cnv`)|2|0|
|VDJ 与克隆 (`single_cell.vdj`)|4|0|
|单细胞剪接 (`single_cell.splicing`)|5|0|
|Perturb-seq (`single_cell.perturbseq`)|3|0|
|单细胞独立复现 (`single_cell.replication`)|3|0|
|空间转录组 (`single_cell.spatial`)|3|0|
|多组学与调控连接 (`single_cell.multiome`)|3|0|

## 使用

`analysis-library --search WGCNA` 列出对应整套路线。`analysis-suite --chapter bulk.wgcna --output <fresh-directory>` 导出该分析的全部默认合成模板、准确 TSV 和批量绘图 manifest；加 `--include-variants` 才导出相近替代与布局。`analysis-render --manifest <fresh-directory>/manifest.json --output <fresh-render-directory>` 串行绘制这些合成模板。实际项目应使用 `book-plan`，逐项绑定已经完成且 QC 审核的真实结果。

默认与替代由实际数据语义决定；没有云形时不估算密度，没有完整命中时不冒充完整 GSEA，没有模块结果时不生成 WGCNA 结论。模板完整性与真实结果可用性是不同状态。各章节的主图和诊断／验证视图不是所有分析方法已穷尽的声明。
