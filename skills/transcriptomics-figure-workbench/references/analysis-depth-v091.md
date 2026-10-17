# 分析内部的画法与实际入口

每项绑定真实绘图器、输入和实例。章节内的单个面板可用 `view-template` 单独导出；改变布局后需要重新审图。此表只记已实现的画法，不表示执行过对应分析。

|分析|具体画法|入口|形式|
|---|---|---|---|
|bulk.design|Covariates and independent units|`bulk.design.p1`|matrix|
|bulk.design|Capture contribution by donor|`bulk.design.p2`|stack|
|bulk.reads|Per-base quality profile|`bulk.reads.p1`|curve|
|bulk.reads|Complete read classes|`bulk.reads.p2`|stack|
|bulk.alignment|Alignment categories|`bulk.alignment.p1`|stack|
|bulk.alignment|Gene-body coverage|`bulk.alignment.p2`|curve|
|bulk.filtering|Filtering sensitivity|`bulk.filtering.p1`|curve|
|bulk.filtering|Sensitivity of selected effects|`bulk.filtering.p2`|interval|
|bulk.normalization|Supplied RLE profiles|`bulk.normalization.p1`|curve|
|bulk.normalization|Mean-variance relationship|`bulk.normalization.p2`|points|
|bulk.batch|Sample structure · dispersion and marginal proportions|`bulk.batch.complete`|pca|
|bulk.differential|Differential response · stacked distributions|`bulk.differential.complete`|volcano|
|bulk.interaction|Condition-by-time predictions|`bulk.interaction.p1`|curve|
|bulk.interaction|Interaction terms|`bulk.interaction.p2`|interval|
|bulk.model_qc|Residual structure|`bulk.model_qc.p1`|points|
|bulk.model_qc|Dispersion trend|`bulk.model_qc.p2`|curve|
|bulk.programs|Coordinated sample-level patterns|`bulk.programs.p1`|matrix|
|bulk.programs|Donor-level effects and uncertainty|`bulk.programs.p2`|interval|
|bulk.ora|ORA themes, ratios and supporting genes|`bulk.ora.complete`|ora|
|bulk.gsea|bulk.gsea|`bulk.gsea.complete`|complete|
|bulk.pathway_contrasts|Pathway enrichment across contrasts|`bulk.pathway_contrasts.complete`|gsea_comparison|
|bulk.gene_support|Pathway membership and signed gene evidence|`bulk.gene_support.complete`|gene_support|
|bulk.gsea_multitrack|bulk.gsea_multitrack|`bulk.gsea_multitrack.complete`|complete|
|bulk.gsva|Coordinated sample-level patterns|`bulk.gsva.p1`|matrix|
|bulk.gsva|Donor-level effects and uncertainty|`bulk.gsva.p2`|interval|
|bulk.wgcna|Module–trait associations · coefficient, q and effective n|`bulk.wgcna.complete`|module_trait|
|bulk.tf_activity|Coordinated sample-level patterns|`bulk.tf_activity.p1`|matrix|
|bulk.tf_activity|Donor-level effects and uncertainty|`bulk.tf_activity.p2`|interval|
|bulk.deconvolution|Within-donor composition|`bulk.deconvolution.p1`|stack|
|bulk.deconvolution|Prespecified compositional comparisons|`bulk.deconvolution.p2`|interval|
|bulk.splicing|Frozen junction/coverage profiles|`bulk.splicing.p1`|curve|
|bulk.splicing|Junction usage differences|`bulk.splicing.p2`|interval|
|bulk.splicing|Transcript usage|`bulk.splicing.p3`|stack|
|bulk.dtu|Within-donor composition|`bulk.dtu.p1`|stack|
|bulk.dtu|Prespecified compositional comparisons|`bulk.dtu.p2`|interval|
|bulk.timecourse|Longitudinal expression profiles|`bulk.timecourse.p1`|curve|
|bulk.timecourse|Time interaction estimates|`bulk.timecourse.p2`|interval|
|bulk.replication|Independent-cohort effect estimates|`bulk.replication.p1`|interval|
|bulk.replication|Feature-level direction and magnitude|`bulk.replication.p2`|matrix|
|bulk.survival|Supplied survival estimates|`bulk.survival.p1`|curve|
|bulk.survival|At-risk counts|`bulk.survival.p2`|matrix|
|bulk.survival|Adjusted outcome associations|`bulk.survival.p3`|interval|
|bulk.ppi|Explicit evidence relationships|`bulk.ppi.p1`|network|
|bulk.ppi|Selected relationship support|`bulk.ppi.p2`|matrix|
|bulk.connectivity|Signature connection scores|`bulk.connectivity.p1`|interval|
|bulk.connectivity|Signature coverage across contexts|`bulk.connectivity.p2`|matrix|
|bulk.noncoding|Coordinated sample-level patterns|`bulk.noncoding.p1`|matrix|
|bulk.noncoding|Donor-level effects and uncertainty|`bulk.noncoding.p2`|interval|
|bulk.fusions|Independent breakpoint support|`bulk.fusions.p1`|bars|
|bulk.fusions|Breakpoint evidence checklist|`bulk.fusions.p2`|matrix|
|single_cell.design|Covariates and independent units|`single_cell.design.p1`|matrix|
|single_cell.design|Capture contribution by donor|`single_cell.design.p2`|stack|
|single_cell.barcode|Barcode rank profile|`single_cell.barcode.p1`|curve|
|single_cell.barcode|Droplet classification|`single_cell.barcode.p2`|stack|
|single_cell.qc|Sample distributions|`single_cell.qc.complete`|qc|
|single_cell.ambient_doublet|Doublet and ambient diagnostics|`single_cell.ambient_doublet.p1`|points|
|single_cell.ambient_doublet|Reviewed calls by donor|`single_cell.ambient_doublet.p2`|stack|
|single_cell.integration|Fixed integrated coordinates|`single_cell.integration.p1`|embedding|
|single_cell.integration|Biology and batch diagnostics|`single_cell.integration.p2`|matrix|
|single_cell.hvg_pca|Explained-variance profile|`single_cell.hvg_pca.p1`|curve|
|single_cell.hvg_pca|Selected PC loadings|`single_cell.hvg_pca.p2`|matrix|
|single_cell.resolution|Resolution changes · cell flows and cluster sizes|`single_cell.resolution.complete`|cluster_tree|
|single_cell.annotation|Cell identities and marker evidence|`single_cell.annotation.complete`|atlas|
|single_cell.subcluster|Selected lineage and child annotations|`single_cell.subcluster.p1`|embedding|
|single_cell.subcluster|Child-state marker specificity|`single_cell.subcluster.p2`|bubble|
|single_cell.markers|Marker specificity · annotation blocks and detection fractions|`single_cell.markers.complete`|marker_dot|
|single_cell.composition|single_cell.composition|`single_cell.composition.complete`|complete|
|single_cell.abundance|Donor-aware abundance contrasts|`single_cell.abundance.p1`|interval|
|single_cell.abundance|Complete donor composition|`single_cell.abundance.p2`|stack|
|single_cell.pseudobulk|Myeloid donor response · stacked distributions|`single_cell.pseudobulk.complete`|volcano|
|single_cell.multi_contrast|Celltype-by-contrast effect atlas|`single_cell.multi_contrast.p1`|matrix|
|single_cell.multi_contrast|Prespecified celltype comparisons|`single_cell.multi_contrast.p2`|interval|
|single_cell.pathways|Celltype pathway responses|`single_cell.pathways.complete`|gsea_comparison|
|single_cell.gene_support|Celltype pathway membership and gene evidence|`single_cell.gene_support.complete`|gene_support|
|single_cell.states|Coordinated sample-level patterns|`single_cell.states.p1`|matrix|
|single_cell.states|Donor-level effects and uncertainty|`single_cell.states.p2`|interval|
|single_cell.hdwgcna|Metacell support · donors, celltypes and overlap|`single_cell.hdwgcna.complete`|metacell_qc|
|single_cell.trajectory|Branch identity and progression · shared frozen graph|`single_cell.trajectory.complete`|trajectory|
|single_cell.velocity|Supplied velocity field|`single_cell.velocity.p1`|vector|
|single_cell.velocity|Splicing phase diagnostics|`single_cell.velocity.p2`|points|
|single_cell.communication|Sender-receiver landscape|`single_cell.communication.p1`|matrix|
|single_cell.communication|Ligand-receptor support|`single_cell.communication.p2`|bubble|
|single_cell.ligand_target|Explicit evidence relationships|`single_cell.ligand_target.p1`|network|
|single_cell.ligand_target|Selected relationship support|`single_cell.ligand_target.p2`|matrix|
|single_cell.regulons|Coordinated sample-level patterns|`single_cell.regulons.p1`|matrix|
|single_cell.regulons|Donor-level effects and uncertainty|`single_cell.regulons.p2`|interval|
|single_cell.cnv|Genomically ordered copy-number scores|`single_cell.cnv.p1`|matrix|
|single_cell.cnv|Clone support by donor|`single_cell.cnv.p2`|stack|
|single_cell.vdj|Within-donor composition|`single_cell.vdj.p1`|stack|
|single_cell.vdj|Prespecified compositional comparisons|`single_cell.vdj.p2`|interval|
|single_cell.vdj|Clonotype sharing|`single_cell.vdj.p3`|matrix|
|single_cell.splicing|Frozen junction/coverage profiles|`single_cell.splicing.p1`|curve|
|single_cell.splicing|Junction usage differences|`single_cell.splicing.p2`|interval|
|single_cell.splicing|Transcript usage|`single_cell.splicing.p3`|stack|
|single_cell.perturbseq|Guide assignments by replicate|`single_cell.perturbseq.p1`|stack|
|single_cell.perturbseq|Guide-level donor response|`single_cell.perturbseq.p2`|interval|
|single_cell.perturbseq|Perturbation programs|`single_cell.perturbseq.p3`|matrix|
|single_cell.replication|Independent-cohort effect estimates|`single_cell.replication.p1`|interval|
|single_cell.replication|Feature-level direction and magnitude|`single_cell.replication.p2`|matrix|
|single_cell.spatial|Registered measured spatial coordinates|`single_cell.spatial.p1`|embedding|
|single_cell.spatial|Donor/section region contrasts|`single_cell.spatial.p2`|interval|
|single_cell.spatial|Regional molecular programs|`single_cell.spatial.p3`|matrix|
|single_cell.multiome|Frozen paired-cell coordinates|`single_cell.multiome.p1`|embedding|
|single_cell.multiome|Motif and RNA support|`single_cell.multiome.p2`|matrix|
|single_cell.multiome|Frozen peak-gene links|`single_cell.multiome.p3`|network|
|bulk.wgcna,single_cell.hdwgcna|Soft power · topology and connectivity|`WGCNA_SoftPower`|soft_threshold|
|bulk.wgcna,single_cell.hdwgcna|Samples · frozen clustering and design tracks|`WGCNA_SampleTree`|sample_tree|
|bulk.wgcna,single_cell.hdwgcna|Gene hierarchy · dynamic and merged modules|`WGCNA_ModuleTree`|module_dendrogram|
|bulk.wgcna,single_cell.hdwgcna|Module–trait associations · coefficient, q and effective n|`WGCNA_ModuleTrait`|module_trait|
|bulk.wgcna,single_cell.hdwgcna|Module membership and gene–trait association|`WGCNA_MM_GS`|membership_significance|
|bulk.wgcna,single_cell.hdwgcna|Upstream absolute MM and GS · separate declared convention|`WGCNA_MM_GS_Absolute`|membership_significance|
|bulk.wgcna,single_cell.hdwgcna|Topological overlap · complete selected frozen matrix|`WGCNA_TOM`|tom|
|bulk.wgcna,single_cell.hdwgcna|Topological dissimilarity · explicitly 1 − TOM|`WGCNA_TOM_Dissimilarity`|tom|
|bulk.wgcna,single_cell.hdwgcna|Relationships among oriented module eigengenes|`WGCNA_EigengeneNetwork`|eigengene_network|
|bulk.wgcna,single_cell.hdwgcna|Donor-level module eigengenes · all units retained|`WGCNA_EigengeneProfiles`|eigengene_profiles|
|bulk.wgcna,single_cell.hdwgcna|Prespecified hub candidates · connectivity and membership|`WGCNA_HubConnectivity`|hub_connectivity|
|bulk.wgcna,single_cell.hdwgcna|External module preservation · size, Zsummary and medianRank|`WGCNA_Preservation`|preservation|
|single_cell.hdwgcna|Metacell support · donors, celltypes and overlap|`hdWGCNA_MetacellQC`|metacell_qc|
|single_cell.hdwgcna|Module activity · identical cells, coordinates and scale|`hdWGCNA_ModuleActivity`|module_activity|
|single_cell.resolution|Resolution changes · cell flows and cluster sizes|`ClusterFlow_2Column`|cluster_tree|
|single_cell.resolution|Resolution changes · cell flows and cluster sizes|`ClusterFlow_1Column`|cluster_tree|
|single_cell.trajectory|Branch identity and progression · shared frozen graph|`Trajectory_2Column`|trajectory|
|single_cell.trajectory|Branch identity and progression · shared frozen graph|`Trajectory_1Column`|trajectory|
|single_cell.trajectory|Gene progression on supplied branches|`Trajectory_GeneDynamics`|dedicated|
|single_cell.resolution|Cluster support by donor|`Resolution_DonorSupport`|dedicated|
|single_cell.hvg_pca|Variable features · supplied mean and normalized dispersion|`HVG_MeanDispersion`|dedicated|
|bulk.gene_support,single_cell.gene_support|Method_E08|`Method_E08`|dedicated|
|single_cell.annotation,single_cell.vdj|Method_N05|`Method_N05`|dedicated|
|bulk.differential,bulk.ora,single_cell.multi_contrast|Method_N06|`Method_N06`|dedicated|
|bulk.model_qc|Frozen model check · qq|`Method_M11b`|qq|
|bulk.model_qc|Frozen model check · residual|`Method_M11a`|residual|
|bulk.model_qc|Frozen model check · scale location|`Method_M11c`|scale_location|
|bulk.model_qc|Frozen model check · influence|`Method_M11d`|influence|
|single_cell.velocity|Method_E18|`Method_E18`|dedicated|
|bulk.splicing,single_cell.splicing,bulk.dtu|Coverage, splice junctions and isoforms|`Method_E43`|dedicated|
|single_cell.annotation,single_cell.subcluster|B cells · marker evidence|`Subgroup_01`|subgroup|
|single_cell.annotation,single_cell.subcluster|T cells · marker evidence|`Subgroup_02`|subgroup|
|single_cell.annotation,single_cell.subcluster|Stromal · marker evidence|`Subgroup_03`|subgroup|
|single_cell.annotation,single_cell.subcluster|Endothelial · marker evidence|`Subgroup_04`|subgroup|
|single_cell.annotation,single_cell.subcluster|Myeloid · marker evidence|`Subgroup_05`|subgroup|
|single_cell.annotation|B cells · marker evidence|`Layout_02Markers_1Columns`|subgroup|
|single_cell.annotation|B cells · marker evidence|`Layout_04Markers_2Columns`|subgroup|
|single_cell.annotation|B cells · marker evidence|`Layout_08Markers_3Columns`|subgroup|

## 使用顺序

先用 `choose` 明确研究问题、数据语义、独立单位和实际数据量，再用 `chapter-views` 查看具体画法。`view-template` 导出一个可运行示例，`book-plan` 的 `view` 可区分同一章节、同一对比下的基础图、诊断图和阅读页。通用面板代码复用不代表方法、检验族或单位可以混用。

## 来源与实现边界

本轮对照作者材料检查了 [DESeq2](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html)、[clustree](https://lazappi.github.io/clustree/articles/clustree.html)、[Monocle3](https://cole-trapnell-lab.github.io/monocle3/docs/trajectories/)、[CellChat](https://github.com/sqjin/CellChat/blob/master/tutorial/CellChat-vignette.Rmd)、[ggsashimi](https://github.com/guigolab/ggsashimi) 和 [hdWGCNA](https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html)。采用信息组织和科学语义，绘图为本项目实现；没有复制或运行第三方分析脚本，也未运行上述分析后端。
