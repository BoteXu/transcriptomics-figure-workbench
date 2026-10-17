# v0.9.7：分析配套图、输入边界与实际检查

## 本轮解决的问题

此前 WGCNA 有14份专用实例，但常规 bulk／单细胞图库没有引导到它们，章节只展示一张模块–性状图；GSVA、TF、剪接等的配套表现也偏薄。本版同时补绘图实现和选择路线。

- 58章进入同一离线目录，172个调用视图合并为125个实际图页，避免同一个章节面板重复生成缩略图。
- WGCNA 有23个默认配套视图；hdWGCNA 有26个。替代、简版及自定义布局单列为可选扩展，不伪装成额外分析方法。
- 本轮43个实际导出：14个既有专用诊断重新导出，23个新增配套实例，6个数量／布局实例。所有最终PNG逐张屏幕查看，审阅绑定在 `assets/analysis-gallery/review-ledger.json`；未通过的中间版本保留在作者私有工作区。
- 43页PDF由实际导出的单页PDF合并。没有声称对其进行纸面校样或独立审美评审，也没有把其他历史图库一并算成本轮重新审阅。

## 按分析调用

从 `scripts/workbench.py` 使用：

```text
analysis-library --search WGCNA
analysis-suite --chapter bulk.wgcna --output <fresh-template-directory>
analysis-render --manifest <fresh-template-directory>/manifest.json --output <fresh-render-directory>
```

整套导出包含准确合成TSV、FigureSpec及清单；`--include-variants` 才纳入替代画法和布局。批量绘图串行处理，输出保留逐图回执，失败保存已完成结果并报告失败项，不自动重试或覆盖原目录。`analysis-render` 仅用于这些明确标注的合成模板；真实科研结果通过既有 `book-plan`／`book-render`，先绑定来源、设计、独立单位及已经审核的上游QC。

常规 `study-plan` 遇到 WGCNA、GSVA、regulon、CellChat、轨迹等明确分析名会提示专用套件路线，不能把一个“小型常规图集”冒充该分析的全套图。普通 bulk／单细胞核心图集继续使用原有角色与清单。

## 新增配套模式的准确数据语义

调用 `figure_coexpression_evidence.plot_coexpression_evidence`，`mode` 按下表选择。所有视图要求 `title`、`context` 和 `definition`；后者声明上游算法／版本、量尺、选择范围及区间／检验族定义。网络上下文沿用既有WGCNA契约；非网络的程序结果使用独立单位、n、方法版本、来源版本和选择范围，不冒用建网方法名称。

|模式|需要的冻结列／结构|保留与拒绝条件|
|---|---|---|
|`module_size`|module, genes, assigned|模块规模和未分配基因分开；非负整数及明确归属|
|`hub_network`|node: gene,module,x,y,kME；edge: source,target,weight|使用已有坐标、边及明确边含义；拒绝未知节点、自连边、重复无向边；不运行布局算法|
|`module_overlap`|reference,query,count，完整交集网格|流宽对应基因数；显式零与缺失不同；不推导Jaccard、显著性或最佳匹配|
|`connectivity_change`|gene,module,k_reference,k_query,estimate,lower,upper|同一批已选基因；原始连接度和独立供应的效应区间并列，不在绘图中估计区间|
|`module_effects`|module,contrast,estimate,lower,upper,q,n|完整选定模块／对比网格，区间包含估计；有效独立n不能超过上下文支持；长名称自动折行|
|`module_enrichment`|module,term,overlap,query_size,term_size,universe,q|共同测试背景、每模块固定query；面积严格对应比例，零比例面积为零；数字保留实际重叠基因数|
|`module_expression`|record_type,module,unit,gene,group,value|已有基因尺度与定向eigengene；完全对齐供体列；不重新标准化、聚类或求特征向量|
|`topology`|已有leaf/merge树，以及a,b,value完整TOM|严格核对相同基因、树连接、对称矩阵与[0,1]；树、模块条、矩阵使用同一顺序|
|`module_dynamics`|module,branch,position,estimate,lower,upper,n|已有分支／时间点和区间；统一纵轴；不拟合平滑曲线、伪时间或细胞谱系|
|`stability`|module,setting,estimate,lower,upper,n_resamples|明确[0,1]稳定性量尺及完整设置网格；不选择最优参数或重复抽样|
|`trait_scatter`|module,unit,group,trait,eigengene|供体身份、分组和连续性状一致；保留全部单位与共同eigengene量尺；不拟合相关或回归|
|`projection`|module,cohort,retained_genes,tested_genes,estimate,lower,upper,n|同时显示覆盖和相关区间；零保留也可显式记录；投影相关不等于网络保留性|
|`preservation_attributes`|module,attribute,probability,permutations|逐个属性展示明确的原始或校正概率及完整属性范围；不平均P值，不解释成Zsummary|
|`program_profile`|module,unit,group,value；每程序／组的cloud_shapes|半云为上游冻结grid/width/n/definition，检查范围和人数；全部单位保留；不估计KDE，缺少云形时不能假装画出云雨图|

`columns='auto'` 按实际模块／分面数组织；可明确请求1–6列。完整网络、分区流和TOM属于一个视图，不能用“多列”拆坏内部坐标关系。数量不同或更换布局后必须重新审图。有限示例测试了1／3／4／12模块、8／24供体、单列／双列／三列及有长名称的两对比。它不是对任意数量和任意名字均已通过的承诺。

既有 `plot_wgcna_view` 继续提供样本树、动态／合并模块树、module–trait、MM–GS、TOM及1−TOM、eigengene关系、连接度、Zsummary／medianRank、metacell支持与共同坐标活动图。软阈值模式增加 `diagnostics='complete'`：已有signed fit、mean／median／max connectivity和slope全部保留；预选power由调用方给定。树可展示调用方明确给定的 `merge_reference`，不据此重新合并模块。

## 作者材料与取舍

本轮于2026-10-17复查以下作者／官方材料，仅采用数据语义、互补面板和组织方法。本项目自行实现冻结表绘图，没有复制第三方分析脚本、论文图片、权重或数据。

|材料|采用|明确没有照搬|
|---|---|---|
|[WGCNA 官方手册](https://cran.r-project.org/web/packages/WGCNA/WGCNA.pdf)|power、层次树、模块／性状、eigengene、TOM、保留性分层检查|绘图阶段不选择power、建网、推断模块或重做保留性检验|
|[hdWGCNA 网络图](https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html)|分模块与联合hub网络、节点量和边量明确、跨模块边弱化|不把自动抽边、随机选择节点或UMAP／力导向布局藏进绘图|
|[hdWGCNA 保留性](https://smorabit.github.io/hdWGCNA/articles/module_preservation.html)|覆盖、拓扑对照、独立属性与验证结果分开读|不将示例中的属性P值平均解释为一个校准的合成检验；投影不冒充建网|
|[hdWGCNA DME](https://smorabit.github.io/hdWGCNA/articles/differential_MEs.html)|模块效应和跨对比表达|未照搬细胞层面的默认检验；真实推断需供体／实验单位模型及上游区间|
|[GSVA 官方说明](https://bioconductor.org/packages/release/bioc/vignettes/GSVA/inst/doc/GSVA.html)|样本级基因集评分与后续组间效应分别呈现|不把GSVA、ssGSEA、PLAGE和ORA／GSEA结果混为同一量尺；未运行GSVA|
|[Monocle3 轨迹](https://cole-trapnell-lab.github.io/monocle3/docs/trajectories/)|已有根、分支、顺序与程序曲线的上下文|不把伪时间当真实时间或因果方向；没有在绘图阶段学习轨迹|
|[ggsashimi](https://github.com/guigolab/ggsashimi)|既有物理覆盖／junction图与新增供体PSI分布互补|PSI云雨不是sashimi替代品；没有从覆盖重新调用剪接事件|

这些是方法作者资料，其中部分教程发表于2024年；没有将其冒称为近两年新论文。此前的2025–2026期刊原图取舍另见既有来源记录。

## 实际返工与验收层级

逐张检查发现并修复了：TOM及层次树的注释条远离内容、长轴标题碰撞、长程序名挤窄效应面板、连续性状rug与刻度混杂、不同模块的纵轴不一致、模块活动页过高、敏感性／验证页留白、布局实例的长标题。

可重复检查覆盖未知／重复图节点、交集缺项、无效区间或独立n、无效富集分母、TOM不对称、云形人数／范围错误、缺失稳定性设置／保留属性、零面积语义、共享量尺及完整便携模板。浏览器检查负责本地页面加载、逐图解码、章节检索、替代视图、前后页、缩放与窄屏；它不能批准审美或科学结论。

公开发布仅含源代码、合成输入、脱敏导出和上述公开来源。本地目录、服务器信息、真实课题输入、私有可选流程、注册表、运行日志及私人配置不进入发布包；已有安装中的私人课题配置由同步工具保护。
