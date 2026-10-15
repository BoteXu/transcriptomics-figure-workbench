# 按软件包和方法选择专用绘图入口

这些入口接收**已有分析结果导出的冻结表**，复用已实现绘图器，并增加专用字段、参数和方法说明。它们不安装或运行原软件包，不把 `.rds`、Seurat、AnnData 或模型对象直接带入本机分析环境。原始算法、软件名称和许可仍归原作者。

[8张专项预览与逐图记录](../assets/method-gallery/index.html)

## 已登记的25个入口

| 来源 / 方法 | 专用入口 | 需要保留的核心含义 |
|---|---|---|
| enrichplot | `enrichplot.gseaplot2`、`.overlay`、`.facets` | 单通路、同轴多通路、独立曲线面板；ES、命中与排序指标分层 |
| fgsea | `fgsea.plotEnrichment`、`fgsea.NES_matrix`、`fgsea.leading_edge` | 已有ES轨迹、NES/FDR、实际leading-edge成员；不由汇总表反推曲线 |
| clusterProfiler / enrichplot | `clusterProfiler.dotplot`、`clusterProfiler.lollipop` | ORA的Count/查询分母、调整概率和背景；与GSEA分开 |
| enrichplot | `enrichplot.ridgeplot`、`.cnetplot`、`.emapplot` | 已估计密度、已选节点边与固定坐标；不现场估计KDE/网络布局 |
| GSVA | `GSVA.score_heatmap` | 评分方法、分数单位和统一色阶；不重新评分或标准化 |
| DESeq2 / limma / MSstats | `DESeq2.volcano`、`limma.effect_forest`、`MSstats.volcano` | 对比方向、收缩状态、区间来源、FDR与过滤范围 |
| Seurat / Scanpy | `Seurat.DotPlot`、`Seurat.DimPlot`、`Scanpy.umap` | 点大小分母、均值语义、已有嵌入坐标；细胞不是独立受试者 |
| WGCNA | `WGCNA.module_trait`、`WGCNA.module_network` | 关联与概率分开、模块身份、TOM/adjacency及选择规则 |
| CellChat | `CellChat.communication_network` | 发送/接收方向、已有权重定义；概率不等于结合或因果信号 |
| decoupleR / PROGENy | `decoupleR.activity_heatmap`、`PROGENy.pathway_activity` | 活性评分方法、模型版本及量纲，不重新推断 |
| survival / survminer / pROC | `survminer.ggsurvplot`、`pROC.roc` | 已有阶梯/风险人数/删失或ROC坐标，保留评价队列和区间定义 |

每项的准确字段、固定参数和必填上下文由 `references/method-entries.json` 提供。入口数包括同一画法的不同方法绑定，不是25种新统计方法。原软件包对象读取和不同版本的原生导出仍应在已有服务器环境验收。

## 调用与配置

```sh
python scripts/workbench.py methods --search GSEA
python scripts/workbench.py method enrichplot.gseaplot2
python scripts/workbench.py method-spec --entry enrichplot.gseaplot2 --template selected-context.json --output selected-gsea.spec.json
python scripts/workbench.py plan --spec selected-gsea.spec.json --output selected-gsea.plan.json
python scripts/workbench.py render --plan selected-gsea.plan.json --output new-figures
```

`selected-context.json` 使用现有FigureSpec结构：明确输入表、课题主题、来源和该方法必需参数。`method-spec`选择固定绘图器、检查规范字段和源表哈希、保存相对路径；不猜测字段，不填充统计信息，不覆盖已有输出。已有表变动时必须重新准备。

离线Studio左侧选择“软件包 / 方法专用入口”，可检索、查看字段与上下文并导出入口说明。入口说明不是完整FigureSpec，也不是完成的分析。

## GSEA专项输入与样式

`gsea_tracks`有三种布局：`classic`单通路、`overlay`同轴多曲线、`facets`分面。上层显示已保存的running ES，中层显示实际命中条带，下层显示完整排序指标。侧栏保留NES、调整概率和交集基因集大小；可显示已有leading-edge加粗命中。

长表使用 `kind=curve/hit/metric/summary`：

- `curve`：`pathway, rank, value`，每条曲线完整覆盖1到`ranked_universe`，不进行插值。
- `hit`：`pathway, rank, gene, leading_edge`，标记必须为0/1，命中数与交集set size一致。
- `metric`：`rank, value`，只保留一份完整有序排序指标。
- `summary`：每通路一行`pathway, NES, padj, set_size`。NES不是曲线纵轴ES，不能互换。

同时提供排序指标定义、对比方向、基因集版本和完整排序背景。不得只提供差异基因列表来冒充完整排名。没有实际曲线/命中时，可选择NES汇总图；不能从NES/FDR生成一条看似真实的曲线。

`gsea_nes`保留完整所选通路×对比网格，`not_tested`显示叉号，非显著结果仍保留数值；颜色为NES，面积为set size，轮廓显示FDR阈值。`gsea_leading_edge`保留完整所选基因×通路成员表和已有基因效应；leading edge必须是成员子集。

ORA的`ora_terms`单独使用Count/查询分母与调整概率，提供气泡和棒棒糖两种样式。已有`density_ridges`入口要求冻结密度网格及估计范围；`typed_network`入口要求明确节点、边、权重和已有坐标。

## 公开原始文档与归属

- [GSEA官方用户指南](https://docs.gsea-msigdb.org/GSEA/GSEA_User_Guide/)：ES、排序指标、命中与leading-edge解释。
- [fgsea官方教程](https://bioconductor.org/packages/release/bioc/vignettes/fgsea/inst/doc/fgsea-tutorial.html)：结果字段和原生绘图工作流。
- [enrichplot作者文档](https://yulab-smu.top/biomedical-knowledge-mining-book/enrichplot-gsea.html)：gseaplot/gseaplot2、ridgeplot等表达。
- [富集路线选择](https://yulab-smu.top/biomedical-knowledge-mining-book/choose-a-route.html)：ORA、GSEA、比较与自定义基因集的区别。

本项目新增的是独立的冻结表绘图实现和路由配置，未复制这些软件包算法或重新分发MSigDB集合。真实研究需要另外核验物种、基因ID、基因集许可、排名方式、重复与统计设计。
