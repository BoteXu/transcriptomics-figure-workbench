# 配套证据页的方法与设计来源

以下是实际阅读的方法文档/作者教程。它们约束通道含义与应检查的问题；本项目没有宣称执行这些后端，没有复制其图片或分析代码。原有逐图期刊参考仍在 [来源设计记录](source-design-v093.md)。2025–2026 年文档优先，稳定的较早作者教程也保留；不把更新日期当作科学有效性证据。

|作者/维护方与原始来源|采用到本项目|舍弃/边界|
|---|---|---|
|Love 等，[DESeq2 vignette](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html)|离散度、Cook 影响、表达支持、收缩前后效应与设计诊断分别有配套页|不在画图时运行 DESeq2、重估 FDR、收缩或归一化|
|Seqera，[MultiQC FastQC 模块](https://docs.seqera.io/multiqc/modules/fastqc)|逐碱基、adapter、完整读段类别、显式 GC 参考分开展示|参考分布必须供给，不能把条件曲线改名冒充参考；阈值状态不代替研究 QC|
|Castelo 等，[GSVA vignette](https://bioconductor.org/packages/release/bioc/vignettes/GSVA/inst/doc/GSVA.html)|供体评分、基因集覆盖、效应及跨队列支持|单样本评分与差异效应不同；不混用 ES/NES/GSVA|
|Badia-i-Mompel、Vélez-Santiago，[decoupleR vignette](https://www.bioconductor.org/packages/release/bioc/vignettes/decoupleR/inst/doc/decoupleR.html)|TF 活性、表达、带符号先验与目标覆盖分别提供|不同推断方法的量纲不可交换；活性与结合证据不能等同|
|rnaseqDTU 作者工作流，[Differential transcript usage](https://www.bioconductor.org/packages/release/workflows/vignettes/rnaseqDTU/inst/doc/rnaseqDTU.html)|转录本比例、母基因/转录本通道、结构与版本敏感性分别展示|使用变化不是表达变化；模糊映射与缺失不作为零|
|Dann、Morgan，[Milo 教程，2026](https://bioconductor.org/packages/release/bioc/vignettes/miloR/inst/doc/milo_demo.html)|供体×邻域支持、丰度效应、邻域大小与模型敏感性|邻域重叠与 SpatialFDR 定义必须保留；细胞数不作为独立 n|
|CellChat 作者，[多数据集比较教程](https://github.com/jinworks/CellChat/blob/main/tutorial/Comparison_analysis_of_multiple_datasets.Rmd)|表达支持、incoming/outgoing 角色、通路贡献、供体效应与复现分开|不以通信分数证明真实细胞信号传递；不自动推断因果|
|单细胞最佳实践作者，[Cell–cell communication](https://www.sc-best-practices.org/mechanisms/cell-cell-communication/)|把表达支持、先验覆盖、配体靶基因与统计单位作为伴随证据|不能只展示漂亮网络而省略输入支持和方法前提|
|Scanpy 作者，[clustering tutorial](https://scanpy.readthedocs.io/en/stable/tutorials/basics/clustering.html)|保留 QC、HVG/PCA、聚类、marker 与注释的不同问题|不为美化重新计算坐标或修改身份；已有逐亚群多 marker 页继续使用|
|scVelo 作者，[Velocity basics](https://scvelo.readthedocs.io/en/stable/VelocityBasics.html)|spliced/unspliced 支持、置信度、基因拟合支持与模型选择配套|箭头/latent time 不等于实验时间或因果方向；不本地拟合 velocity|
|Broad inferCNV 作者，[Interpreting the figure](https://github.com/broadinstitute/infercnv/wiki/Interpreting-the-figure)|参考正常、基因组排序、克隆组成与正交支持分开|RNA 推断的 CNV 不作为 DNA 拷贝数确认|
|Scirpy/scverse 作者，[BCR tutorial](https://scirpy.scverse.org/en/latest/tutorials/tutorial_5k_bcr.html)|链 QC、克隆大小/扩增、跨采样共享、多样性及随访配对|保留所有已选克隆与供体，不能为减少拥挤静默去掉单例；CDR3 距离不是功能确认|
|Squidpy 作者，[spatial neighbors](https://squidpy.readthedocs.io/en/latest/notebooks/examples/graph/compute_spatial_neighbors.html)|空间距离、section/供体支持、区域程序与注册选择敏感性|空间相邻不等于通信；spot 不作为独立受试者|
|Seurat 作者，[multimodal tutorial](https://satijalab.org/seurat/articles/multimodal_vignette.html)|模态配对、各自 QC、RNA/ATAC/调控支持与物理基因座|不同模态通道不能共用未经定义的原始尺度；peak–gene 关联不是因果|

每章更具体的输入与解释限制保留在 `transcriptomic-chapters.json` 和实际 FigureSpec。上表是语义与组件来源，不能声称每一行都来自相同图型的近期高影响因子原图。
