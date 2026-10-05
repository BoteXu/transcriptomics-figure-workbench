# R 与 Python 绘图配方

核心适配器为本次自编，不复制网络包源码。复杂对象示例为文档适配配方，**未经过当前真实对象的执行测试**；先检查版本和函数参数，再运行选中的片段。不给“安装全部”命令，也不对整个Seurat/AnnData对象无条件转换或复制。

## 1. 两套核心模板的输入约定

| 图形 | R | Python | 必要列 |
|---|---|---|---|
| UMAP/PCA等已算坐标 | plot_embedding | plot_embedding | cell_id,x,y,group；PCA用真实样本ID并提供轴方差说明 |
| 样本散点 | plot_sample_points | plot_samples | sample_id,group,value；每独立单位一行 |
| 森林/区间 | plot_forest | plot_forest | label,estimate,lower,upper；必填effect_scale |
| 火山 | plot_volcano | plot_volcano | gene,log2FC,padj；缺测另报，0需显式display floor |
| 检出率点图 | plot_dot | plot_dot | feature,group,fraction[0,1],value；必填value_semantics、denominator_label |
| 有正负中心的热图 | plot_heatmap | plot_heatmap | feature,sample,value；完整矩形，不自动zscore |
| 分文库QC箱线 | plot_qc | plot_qc | cell_id,sample,value |
| 细胞组成 | plot_composition | plot_composition | sample,celltype,count；非负整数，真实分母 |
| ROC/PR/校准 | plot_curve | plot_curve | model,x,y；[0,1]且保留上游曲线顺序 |

R因子levels和Python输入首次出现顺序用于控制多数坐标顺序；两套默认类别排序不保证相同，跨语言复现应明确排序。细胞分组图点顺序可导致遮挡，正式出图需审计重叠并记录绘制顺序。行热图有负数不一定是下降：例如row-zscore是相对均值。

所有函数只渲染已有结果，不计算DE、FDR、UMAP或临床模型。forest的effect_scale必须为difference、log_ratio或ratio；ratio自动使用以1为参照的对数轴并拒绝非正区间，输入OR/HR原值。log_ratio用于已经取对数的比值。dot的value_semantics可选mean_all、mean_detected、scaled、signed_effect；后两类使用以0为中心的发散色阶。普通heatmap可显式选scale_type='sequential'，不自动缩放矩阵。

新增四种表格适配器及来源见 [expanded-patterns.md](expanded-patterns.md)，执行前读取与目标图型有关的输入约定。

标准火山图优先选用 `figure_styles.R/.py` 的 `plot_volcano_marginal`（圆点＋顶部/右侧边际直方图＋浅灰目标圈线）；空间受限时仍可用核心简版或 `plot_volcano_editorial`。富集棒棒糖、样本比例分面与散点/IQR等其余画法见 [aesthetic-upgrades.md](aesthetic-upgrades.md)。这些样式函数不改变API v2导出约定。

### API v2迁移

- 删除meta中的手写input_hash；导出器自动计算最终TSV的SHA256，并验证导出表与绘图器收到的表一致。
- 文件来源用source_file与expected_source_sha256参数传入；不提供文件时只建立绘图表的身份，不声称核验了上游文件。
- 每张图改为output_directory/figure_id/内的6个文件。返回值仍是6个文件路径；旧的扁平输出不会被覆盖。
- 森林图补effect_scale；点图补value_semantics和denominator_label。R依赖新增digest，R注释热图/双面板分数图需要patchwork；检查已有环境，不自动安装。
- 导出JSON中的figure_spec由绘图器记录实际图例、阈值或参照线等设置。用户修改图中文字时保留原始stamp；更改数据/统计语义后必须重新调用适配器。

### R核心使用

```r
source(file.path(skill_dir, 'scripts', 'figure_core.R'))
tab <- read.delim(input_tsv, check.names=FALSE)
pal <- c(Control='#35618F', Treated='#C45A2D')
p <- plot_sample_points(tab, pal, y_label='log2 CPM')
# meta必须来自真实分析，不使用下面的文字作为占位科学结果。
# 完整字段见figure-contract.md和smoke_test.R（后者只供测试）。
export_figure(p, tab, output_directory, 'target_expression', meta)
```

### Python核心使用

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(skill_dir) / 'scripts'))
from figure_core import plot_samples, export_figure
import pandas as pd
tab = pd.read_csv(input_tsv, sep='\t')
fig = plot_samples(tab, {'Control':'#35618F','Treated':'#C45A2D'}, 'log2 CPM')
export_figure(fig, tab, output_directory, 'target_expression', meta)
```

## 2. R原生对象配方（DOC/需版本与输入核验）

### Seurat：复用嵌入、分组feature、marker

来源S11及Seurat正式文档；明确对象assay/layer、细胞范围及scale，使用原有嵌入。不要调用RunUMAP或FindMarkers仅为出图。

```r
# seu具有已冻结umap与celltype、sample_id metadata。
p <- Seurat::DimPlot(seu, reduction='umap', group.by='celltype',
                     cols=celltype_palette, label=TRUE, repel=TRUE)
p_split <- Seurat::DimPlot(seu, reduction='umap', group.by='celltype',
                           split.by='sample_id', cols=celltype_palette)
# 按已核验API设置共同的表达色限，缺少目标则报告而非插补。
p_feature <- Seurat::FeaturePlot(seu, features=target_genes,
                                reduction='umap', keep.scale='all')
# 跨基因共同色阶不一定合适；通常分基因跨组统一，图注说明选择。
```

### ComplexHeatmap：样本注释、行模块与关键基因

来源S03。输入为已经确认含义的有限数值矩阵；先用ID对齐样本注释。该代码不自动缩放也不挑显著基因。

```r
stopifnot(identical(colnames(mat), metadata$sample_id))
stopifnot(all(is.finite(mat)))
ha <- ComplexHeatmap::HeatmapAnnotation(
  Group=metadata$group, col=list(Group=group_palette))
ht <- ComplexHeatmap::Heatmap(mat, name='row z-score',
  top_annotation=ha, row_split=module_id,
  cluster_columns=FALSE, show_row_names=FALSE,
  col=circlize::colorRamp2(c(-2,0,2),c('#35618F','#F7F7F5','#B84E35')))
# 上述色限会饱和[-2,2]外数值；使用前确认合理且写入sidecar。
# 只有输入实际为row-zscore才可使用这个name。
pdf(output_pdf,width=7.1,height=6)
tryCatch(ComplexHeatmap::draw(ht), finally=dev.off())
```

### 富集：多对比、GSEA、通路关联

来源S06。直接使用经过审核的enrichResult/gseaResult；不要在画图时重新富集。新的文档函数可能不在旧enrichplot内，核验formals与packageVersion。

```r
p_dot <- enrichplot::dotplot(enrichment_result, showCategory=15)
p_gsea <- enrichplot::gseaplot2(gsea_result, geneSetID=selected_term_id)
# 网络图需要预先计算并保存的termsim；此处不隐式重算。
p_map <- enrichplot::emapplot(result_with_termsim, showCategory=20)
```

### 模块、通讯与组合排版

来源S13、S15、S21、S25（维护中的jinworks/CellChat）。S14为已归档旧版，仅作历史对象对照。模块或通讯统计由上游负责；topN仅是绘图子集，保留完整表。先登记CellChat对象、安装版本、数据库版本和正式标签顺序，选择相符教程；不为美化自动升级对象或数据库。

```r
# hdWGCNA官方网络函数，用已算TOM和模块结果；先检查参数签名。
print(formals(hdWGCNA::ModuleNetworkPlot))
# CellChat: 气泡图聚焦接收端，发送/接收索引由正式标签映射。
p_lr <- CellChat::netVisual_bubble(cellchat,
  sources.use=sender_indices, targets.use=receiver_indices)
# NicheNet绘图函数的实际输入结构见S15；勿把CellCall分数当CellChat概率。
# patchwork只合并等价图例，不把不同值单位合并。
page <- patchwork::wrap_plots(A=p_dot,B=p_gsea,C=p_map,
                             design='AB\nCC',guides='keep')
```

### UpSet与时序组合

来源S05/S07。使用完整逻辑membership；不同宇宙的集合不要直接混合。ClusterGVis可能集成聚类与富集，冻结结果的美化应导入已有簇和富集，不调用一键重分析。

```r
p_intersection <- ComplexUpset::upset(membership_table,set_columns,
                                     sort_sets=FALSE)
# 已有时间/阶段结果：使用输入的点/区间；不要自动拟合光滑曲线。
```

## 3. Python原生对象配方（DOC/需版本与输入核验）

### Scanpy：UMAP、marker、QC、程序展示

来源S09/S23。显式指定使用的layer，避免默认raw改变数值。下面不计算邻居/UMAP/markers。大数据只导出必要obs与坐标；不要densify完整表达矩阵。

```python
import scanpy as sc
assert 'X_umap' in adata.obsm
sc.pl.umap(adata, color='celltype', palette=celltype_palette,
           legend_loc='right margin', frameon=False, show=False)
sc.pl.dotplot(adata, marker_dict, groupby='celltype',
              layer=reviewed_layer, use_raw=False,
              standard_scale=None, show=False)
sc.pl.matrixplot(adata, target_genes, groupby='sample_id',
                 layer=reviewed_layer, use_raw=False,
                 standard_scale=None, show=False)
# standard_scale='var'会改变视觉含义；如使用，必须登记。
```

### scVelo与Squidpy：仅有适配数据时

来源S18/S19。不因为想画流线或组织图而自动运行模型或借用别人的坐标。

```python
import scvelo as scv
# upstream_velocity_review通过，且spliced/unspliced、velocity相关结果已验收。
assert 'spliced' in adata.layers and 'unspliced' in adata.layers
scv.pl.velocity_embedding_stream(adata, basis='umap', color='celltype', show=False)

import squidpy as sq
assert 'spatial' in spatial_adata.obsm
sq.pl.spatial_scatter(spatial_adata, color='celltype',
                      library_id=reviewed_library_id)
# 检查所装版本signature，不传未记录的show参数。
# 图像、scale factor、真实坐标/距离单位也须在上游核验。
```

### 网络、交集和模型解释

使用已有节点坐标与完整边表，由matplotlib画点/线或适配networkx；若需计算布局，固定seed且比较图共用一次布局，布局不代表真实细胞空间。Python upsetplot和SHAP属于扩展候选，当前未做API执行验证，按所装版本官方文档适配；不冒充本次已测试功能。

ROC/PR/校准优先用核心读取上游曲线。若输入是患者OOF概率而非曲线，计算性能属于单独的结果分析步骤：确认正类、概率方向、重复预测聚合、患者ID及置信区间方法后再使用sklearn等；不能让出图顺手训练新模型。

## 4. 测试和可移植性

R: `Rscript --vanilla scripts/smoke_test.R NEW_DIRECTORY`。
Python: `python scripts/smoke_test.py NEW_DIRECTORY`。

Windows环境如出现无效LC_*及中文命令行路径编码错误，先只读检查locale。2026-09-26已在本机R进程内LC_CTYPE='English_United States.utf8'及Microsoft YaHei字体下验证中文输出路径和示例标签；Python也验证了同一字体。R可用options(omics.font_family='Microsoft YaHei')，Python在覆盖整次绘图/导出的plt.rc_context中设置font.family。该证据不覆盖任意机器或全部中文字形，不改变系统全局区域。旧LC_ALL=C不是中文路径的已验证运行环境。
