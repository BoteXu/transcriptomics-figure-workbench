# 图形改画：优先改善阅读，不改变证据

新增实现为 `scripts/figure_styles.R` / `.py`。保留旧核心函数；不是强制替换所有画法，也不需要新增依赖。R先source figure_core.R，再source figure_styles.R；Python从figure_styles导入。仍使用API v2导出器。

## 哪些图值得换画法

| 现有图/问题 | 建议画法 | 本地状态与约束 |
|---|---|---|
| 拥挤火山图、标签盖点 | 灰色背景圆点＋蓝/赭圆点区分方向＋两侧标签通道 | plot_volcano_editorial；坐标、阈值和点数不变；只标明确指定基因，不自动挑“好看”的基因 |
| 标准火山图：同时展示两轴的基因分布 | 圆点火山图＋顶部 log2FC、右侧 -log10(FDR) 堆叠边际直方图；目标基因浅灰描边 | R/Python `plot_volcano_marginal` 为默认建议；两侧柱图统计同一批全部绘图基因，不新增检验或独立样本；不截断轴和极端点。R 版需要 patchwork，缺少时仍可用简版或补齐环境 |
| GO/KEGG长名称条形图 | 横向棒棒糖/气泡：位置GeneRatio、面积Count、颜色FDR证据 | 新增plot_enrichment_lollipop；不在出图时做富集或筛topN；GeneRatio必须说明分母 |
| GSEA只展示显著性 | 以0为参照的双向NES棒棒糖 | 同一新增函数score_type='NES'；颜色为-log10FDR，不把正/负NES说成已证实激活/抑制 |
| 堆叠细胞比例难比较中间色块 | 保留堆叠总览，附各细胞类型逐样本分面点图 | 新增plot_composition_panels；一列样本/供体关系须核验，不汇总细胞后制造组级重复 |
| 均值柱图掩盖样本差异 | 全体样本散点＋旁置中位数/IQR | 新增plot_sample_distribution；只有n>=5显示描述性IQR，小n只画点；不是置信区间或显著性检验 |
| marker点图太密 | 按已冻结的细胞谱系/marker模块拆面板，固定顺序、面积和色阶 | 复用CORE dot；不自动挑marker；检测率分母与颜色均值分开说明。过密时用矩阵热图，不强塞标签 |
| 热图只有红蓝大色块 | 样本组别注释＋行模块色条＋明确的发散/顺序色阶 | 复用EXT annotated_heatmap；只对已知signed值以0为中心；不自动z-score/重聚类 |
| 森林图、配对结果 | 点区间＋直接标签；真正配对用细连接线 | 复用CORE forest/EXT paired；少行仍是简单点区间最好，不为装饰改成雷达图 |
| UMAP多组点互相覆盖 | 灰背景群体高亮或共同坐标的小多图，附样本构成 | 原生对象配方DOC；需对象实测，不能为更漂亮重跑UMAP或画虚假分群边界 |
| 通讯“毛线团”、多集合Venn | 聚焦发送/接收端气泡矩阵、UpSet | 文档方案；需正式边权/集合背景，未新增模型运行器；弦图不作默认主图 |

一般风格：白底、深灰文字、稳定蓝/赭比较色、浅灰参考线；空间留给标签。用位置、形状、直接标签冗余编码，避免只靠颜色。禁止3D柱、雷达替代精确效应比较或无条件环形化。已有项目色卡优先，不为统一风格改写分组身份。

## 改画函数的输入与边界

1. `plot_volcano_editorial`：gene,log2FC,padj；参数labels,alpha,fc。padj必须在(0,1]，0值需上游明确显示下限。每侧最多6个标签，每个最多24字符；超限要求拆图/伴随表。固定标签通道不是自动避让所有数据点的算法，实际图仍需检查引线、稀疏/密集程度。背景点在Python矢量文件中栅格化，文字和线仍保留矢量；不声称每个点可独立编辑。
   常规新图优先用 `plot_volcano_marginal`，输入列相同，另可设 `x_bins`、`y_bins`（整数 8–200）。边际柱高是基因数，不是样本数；目标圈线为浅灰，标签文字保持可读深灰。极值保留，必要时通过图注解释而非裁掉。R 需先载入 figure_core.R 和 figure_styles.R，且有 ggplot2、patchwork；Python 直接导入 figure_styles。
2. `plot_enrichment_lollipop`：term,score,padj,count；参数score_type仅NES或GeneRatio，必填denominator_label、count_label。count须为正整数，面积从0起。NES的count可用已提供的leading-edge基因数，但标签必须明确。最多20个唯一通路，保留输入行序；更长列表拆页。零命中/缺测/无法估计项另列，不能偷偷删后声称全覆盖。不同NES规范化方式、基因背景/FDR家族不直接拼为同一panel。
3. `plot_composition_panels`：sample,group,celltype,count；palette按组映射，unit_label说明每个点是谁。要求完整sample×celltype表，确认的零显式填0，未知不得填0。每样本分母为全部提供类别的count之和；先按完整类型计算，再想只画部分类型需专门适配，不能删类型后重算分母。最多12类型/4组。y_max默认1，可显式设共同上限（测试例0.5），必须容纳所有点、从0起，记录在sidecar；不自动为每格独立缩放。没有供体映射时只叫sample/capture，不叫donor。样本数n不是细胞数。
4. `plot_sample_distribution`：sample_id,group,value；每独立单位一行，palette按组，y_label注明单位。全部值显示，横向位移仅按输入顺序展开，**不是beeswarm密度估计**。n>=5使用R type7/Python linear分位数显示Q1-Q3和中位数，n<5无摘要框；这个门槛是本模板的保守显示约定，不是统计学充分样本标准。无KDE、无小提琴、无P值计算；配对数据用paired模板。

```python
from figure_styles import plot_volcano_marginal, plot_enrichment_lollipop
fig = plot_volcano_marginal(de_table, labels=reviewed_label_genes, alpha=.05, fc=1)
# 用原始de_table和真实meta交给figure_core.export_figure；不要把副本统计表当原始输入导出。
fig = plot_enrichment_lollipop(ora_table, score_type='GeneRatio',
    denominator_label='Mapped query genes in the reviewed ORA input', count_label='Overlap genes')
```

```r
source(file.path(skill_dir,'scripts','figure_core.R'))
source(file.path(skill_dir,'scripts','figure_styles.R'))
p <- plot_composition_panels(count_table, group_palette, unit_label='biological sample', y_max=1)
p <- plot_sample_distribution(sample_table, group_palette, y_label='log2 CPM')
# export_figure(p, sample_table, new_output, 'sample_distribution', real_meta)
```

## 来源与采用方式

- S06：[enrichplot作者教材](https://yulab-smu.top/biomedical-knowledge-mining-book/enrichplot.html)，2026-09-26重新核对14.1–14.2等章节的富集编码/标签策略。参考信息分工，自编表格绘图器；没有调用或复制作者统计脚本。
- S31：[ggrepel作者仓库](https://github.com/slowkow/ggrepel)，文档核对文本避让原则；本地采用固定侧栏通道，不声称实现ggrepel、不新增该依赖。
- S32：[ggplot2箱线图文档](https://ggplot2.tidyverse.org/reference/geom_boxplot.html)，参考将分布与原始观察结合；本地只画明确定义的中位数/IQR，不伪称Tukey须线图。
- S33：[ggplot2分面文档](https://ggplot2.tidyverse.org/reference/facet_wrap.html)，共享尺度的小多图。R实际调用facet_wrap，Python使用matplotlib子图。
- 前轮公众号作者镜像与ClusterGVis线索继续见sources.tsv；本轮没有把无法访问的公众号原文标为已读。外部案例是设计参考，不是本地验证证据。

## 复测

先运行 `python scripts/style_test.py NEW_PYTHON_OUTPUT`，再运行 `Rscript --vanilla scripts/style_test.R NEW_R_OUTPUT NEW_PYTHON_OUTPUT/_input`。同一套合成输入产生每语言9包（3个旧版对照＋6种新版），每包6文件；14项拒绝用例，以及火山坐标、比例分母、小n显示和输出哈希检查。所有图均标SYNTHETIC DEMO，不用于课题结论。最终PNG查看与已知限制登记在validation.md。
