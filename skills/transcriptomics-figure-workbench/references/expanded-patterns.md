# 2026-09-26 扩展图型与来源

适用：已有审核结果，需配对图、效应点阵、注释热图或AUC对照布局。新增实现为本地原创代码，分别在figure_extensions.R/.py；R先source figure_core.R。两种语言均不拟合统计模型。

## 已实现的四种模板

| 函数 | 输入列及额外参数 | 图形含义与门槛 | 参考 |
|---|---|---|---|
| plot_paired | subject_id,condition,value；palette、condition_order两条件、y_label | 一个真实独立主体各条件一行；缺配对、重复测量必须先审计；线只连接同一主体，不生成P值 | 科学契约中的样本级展示规则；SeuratExtend分组展示提供版式线索，不继承细胞级检验 |
| plot_effect_matrix | feature,contrast,estimate,lower,upper,padj；effect_label、effect_scale、evidence_cap | 完整可估计网格。色表示有方向效应；面积表示截顶-log10(FDR)，空方框标记已提供比较，padj=1允许零面积。比值输入颜色使用log2比值；区间保留在导出表，精确读数配forest | TLS S24 Fig1/Fig2效应点阵；不复用作者细胞汇总GLM |
| plot_annotated_heatmap | feature,sample,value,sample_group,feature_block；两套命名调色板、value_label、scale_type | sample列可表示样本或已声明的汇总列；标签需与实际单位相符。按ID验证注释一致性，保留首次出现顺序，无聚类/标准化。signed/ sequential必须声明；可设column_annotation_label、row_annotation_label | ClusterGVis S07/S26：列注释、行模块、共同矩阵尺度；原生ComplexHeatmap仍是复杂版式候选 |
| plot_score_comparison | feature,score_a,score_b,delta,lower_delta,upper_delta；score_label、两条件名称 | 左侧0–1分数对角散点，右侧B-A与已提供区间；delta须等于B-A。差值区间须来自匹配上游评估，不能由两个AUC区间相减构造。超过十几个标签应分面/筛选并登记全表 | TLS S24 Fig7 Augur；不运行Augur，不将AUC解释为因果反应强度 |

示例调用（Python）：

```python
from figure_extensions import plot_effect_matrix
fig = plot_effect_matrix(reviewed_table, 'Log odds ratio',
                         effect_scale='log_ratio', evidence_cap=6)
# 使用figure_core.export_figure，meta来自上游记录；无需手写哈希。
```

R对应：`plot_effect_matrix(reviewed_table, 'Log odds ratio', 'log_ratio', evidence_cap=6)`。

## 公众号 / GitHub查证记录

- **ClusterGVis作者仓库与手册**：[仓库](https://github.com/junjunlab/ClusterGVis/tree/b79200cbe1b0d7a038720148f3cca14db555f385)、[样本/行注释章节](https://junjunlab.github.io/ClusterGvis-manual/basic-usage.html)。2026-09-26读到样本注释、行注释与组合图的输入要求。仓库固定SHA，在线手册未独立锁定。GitHub许可识别为NOASSERTION，README标MIT；这里只保存原创布局与链接。
- 作者仓库链接的“添加多个样本注释”“添加自定义图形注释”“添加行注释”三篇公众号文章（S27–S29）本轮均无法直接打开，标ACCESS_FAILED_AUTHOR_DOC_CHECKED。只确认标题和作者仓库链接，不宣称读过原文或检查了文章内图片。对应功能依据作者手册核对。
- **公众号“生信探索”作者镜像**：[SeuratExtend可视化教程](https://www.cnblogs.com/BioQuest/p/19009675)，自述基于1.2.3，2025-07-28发布；2026-09-26核对文字/代码。官方对照：[SeuratExtend](https://github.com/huayc09/SeuratExtend/tree/c917a47e20cab9fb3399ff7ed078d3e8139339f0)。分组点图/样本分布可借鉴；VlnPlot2中的stat.method、CalcStats的排序、VolcanoPlot的对象输入可能触发分析，不能随美化直接执行。三基因混色仅作补充，主图保留独立面板与单色标，避免混色掩盖单基因强度。
- **CellChat**：维护仓库S25固定`75253cd0c9e68410e6e721a6d3a0419a1d7e358f`。README说明v2/v3，旧sqjin仓库仅保留历史来源。确认对象版本、安装版本、数据库和标签顺序后再选原生API；本轮没有运行CellChat。

## 后续可选拓展（尚非已测试适配器）

1. 同一嵌入上的split feature/密度差：记录共享坐标、数值变换、带宽与捕获量；密度差无差异丰度检验资格。
2. 模块热图＋已有通路摘要＋时间趋势：输入固定模块、通路全表与已有趋势，不调用clusterData/enrichCluster重新分析；需要各面板对齐验收。
3. 供体级TCR/BCR克隆共享矩阵：必须有序列、克隆定义与样本连接；目前只有来源和输入门槛，未实跑。
4. 空间组织底图＋细胞丰度：须有配准图像和尺度；同一spot中的共变不证明细胞接触。本轮未渲染空间原生对象。

这些候选保留为CONDITIONAL/DOC。优先由真实任务选择并验证，不能把目录中的候选数量当完成数。

## 公开数据验收

来源：[SeuratExtend的pbmc.rda](https://raw.githubusercontent.com/huayc09/SeuratExtend/c917a47e20cab9fb3399ff7ed078d3e8139339f0/data/pbmc.rda)，3,746,494字节，SHA256 `f2fecfcbc8a6360362ac45d2a68c9cd798e0ceb2e95768b2311000c71dc9ebda`。上游README明确data目录rda文件为CC0，代码为GPL-3.0。测试数据放任务验证目录，不随skill分发。

对象包含500个细胞、12627个feature、已有UMAP/PCA。保留作者cluster注释；示例sample/condition字段并未验证为真实供体，测试不用它们做组间推断。挑选8个预先列出的marker，只做counts>0检出率及RNA data槽的算术均值；不重新标准化、分群或寻找差异基因。

显式下载并核验上面的固定数据后，运行：

```text
Rscript --vanilla scripts/public_fixture.R PINNED_PBMC_RDA NEW_R_OUTPUT
python scripts/public_fixture.py NEW_R_OUTPUT PINNED_PBMC_RDA NEW_PYTHON_OUTPUT
```

后者使用R导出的同一组行，因此可核验跨语言数值一致性。三种图为存储UMAP、marker点图、注释热图。出图是公开数据上的绘图验收，不是TLS论文复现或课题生物学验证；配对/效应/AUC模板的统计输入仍只通过合成数据验收。
