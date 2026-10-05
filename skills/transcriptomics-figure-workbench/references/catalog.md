# 全流程图型目录

用途：按科学问题选图，不是要求每个项目把全部图型跑一遍。R/Python原生对象配方在 code-recipes.md；编号对应 sources.tsv。CORE表示附带本地适配器，DOC表示核验过文档但可选功能未在本机实跑；CONDITIONAL表示缺输入时不能做。

| 编号 | 分析/问题 | 首选图型 | 代码入口/来源 | 必要条件或解释边界 |
|---|---|---|---|---|
| F01 | 原始reads质量 | 碱基质量、GC、接头、重复率、多样本QC面板 | MultiQC S01 DOC | 原始工具日志；不由表达矩阵猜测reads质量 |
| F02 | 库大小与检出 | 样本散点、分布、检测数柱图 | ggplot2 CORE samples/qc | 单位为样本或barcode须明确 |
| F03 | 覆盖/比对 | gene-body覆盖、插入片段、链特异性摘要 | MultiQC S01 DOC | 要对应工具输出；不自动设过滤阈值 |
| F04 | PCA/MDS | 同坐标散点、样本标签、方差解释 | DESeq2 S02 DOC; CORE embedding | 原有坐标；PCA注明每轴解释量；小n不画不可靠椭圆 |
| F05 | 样本相关/距离 | 有样本注释的方形热图 | ComplexHeatmap S03 DOC | 距离、变换、聚类定义明确 |
| F06 | 批次/方差来源 | 方差贡献分布、调整前后对照 | variancePartition S04 DOC | 可估计模型；混杂不能图形消除 |
| F07 | 模型诊断 | MA、离散度、均值方差、影响点 | DESeq2 S02 DOC | 使用正式拟合对象；不由美化包装器重拟合 |
| F08 | 差异全景 | 火山图、分面对比 | CORE volcano | 固定效应阈值/FDR；全表和排除原因保留 |
| F09 | 目标表达 | 样本散点、效应区间、配对线 | CORE samples/forest; EXT paired已测 | 只有真实配对才连线；两条件完整配对 |
| F10 | 跨队列效应 | 分层森林图、方向矩阵 | CORE forest/heatmap | 相同效应单位；不强合并不同比较 |
| F11 | 差异集合交集 | UpSet、少量集合Venn | ComplexUpset S05 DOC | 全部集合背景一致；区分exclusive/inclusive |
| F12 | ORA | 排序点图/条形图、GeneRatio与计数 | enrichplot S06 DOC | 实际背景与FDR；不要只排序原始p |
| F13 | GSEA | running score、rank rug、leading edge | enrichplot S06 DOC | 正式排序列表和集合；曲线不是时间 |
| F14 | 通路冗余 | enrichment map、树图、语义分组 | enrichplot S06 DOC | 相似度/去冗余参数可追踪 |
| F15 | 多对比富集 | NES矩阵、分块气泡图 | CORE heatmap/dot适配; S06 | dot大小语义须重命名；不把NES当expression |
| F16 | 样本程序分数 | 样本点、热图、分面分布 | CORE samples/heatmap | 独立样本统计；评分重叠审查 |
| F17 | 时间表达 | 离散阶段图、真实时间曲线、聚类热图 | ClusterGVis S07 DOC | 时间点数/设计支持；不自动重聚类冻结模块 |
| F18 | 表达模式+功能 | 模块热图旁附趋势/GO注释 | ClusterGVis S07; ComplexHeatmap S03 | 2026-09-22实际查看组合版式；文字密集需拆页 |
| F19 | 剪接/DTU | sashimi、junction弧线、PSI点图、isoform结构 | Gviz S08 CONDITIONAL | BAM/junction/转录本与参考匹配；不能由gene counts推剪接 |
| F20 | barcode QC | knee/rank、UMI-gene散点、分文库QC | Scanpy S09; CORE qc | 未过滤液滴存在才评估完整empty-droplet行为 |
| F21 | 双细胞/环境RNA | 分数分布、嵌入叠加、校正前后 | Scanpy S09; CORE embedding | 上游已审核分数；不是画完即证明校正 |
| F22 | 全局/子群嵌入 | UMAP/tSNE分面、群体高亮；可叠加组间密度差 | SCpubr S10; SeuratExtend S11; CORE embedding基础图; TLS代码 S24密度图CONDITIONAL | 固定坐标；密度差是可视化描述，须核对各组细胞数和供体构成 |
| F23 | marker/注释 | grouped dotplot、matrixplot、stacked violin | Scanpy S09; SeuratExtend S11; CORE dot | 颜色均值定义、检测分母、标签置信度 |
| F24 | 组成/差异丰度 | 样本堆叠比例+比例点/区间；组别×细胞类型效应点阵 | CORE composition/forest; EXT effect_matrix已测; TLS代码 S24 | 捕获组成非组织绝对比例；点阵的颜色、大小分别标清效应和校正显著性；模型须处理样本/供体单位 |
| F25 | pseudobulk DE | 样本表达、火山、效应森林 | CORE samples/volcano/forest | 不是细胞级显著性 |
| F26 | NMF/状态程序 | loadings热图、使用强度、跨seed稳定矩阵、样本共识图 | CORE heatmap/forest; EXT annotated_heatmap已测; TLS代码 S24 | 图形适配器不等于NMF已验收；给定冻结rank/membership；不按热图美观选择rank |
| F27 | TF/regulon | 活性热图、靶基因点图、边证据表 | CORE heatmap/dot; ggraph S12 | 活性不是TF表达；先验边不是占据证据 |
| F28 | WGCNA/hdWGCNA | 树与模块条、模块效应、hub网络、TOM图 | hdWGCNA S13 DOC; CORE forest | metacell不是额外动物；模块色不表示强弱 |
| F29 | 网络保存 | preservation统计、模块匹配、参数稳定 | hdWGCNA S13及项目正式结果 | Jaccard稳定不等同外部保存 |
| F30 | 细胞通讯 | LR气泡、接收端热图、层级/弦图 | CellChat S25 DOC; S14历史对象对照; NicheNet S15 DOC | 每条边记录推断来源；无空间不证接触 |
| F31 | 轨迹/命运 | 拓扑图、pseudotime热图、smoother | dynplot S16; tradeSeq S17 CONDITIONAL | 根与拓扑合理；横断面不能当真实纵向 |
| F32 | RNA velocity | stream/grid/phase portrait | scVelo S18 CONDITIONAL | spliced/unspliced及模型诊断；无输入不画箭头 |
| F33 | 空间转录组 | 组织叠加、空间feature、邻域图、同切片丰度共变矩阵 | Squidpy S19; TLS代码 S24 CONDITIONAL | 真坐标、切片、尺度与图像配准；spot共变不证明细胞接触 |
| F34 | 虚拟KO/干预 | 扰动排名、支路矩阵、对照及种子稳定性 | CORE forest/heatmap/dot适配 | 距离不改名为表达FC；种子不是生物重复 |
| F35 | 反卷积/跨组学 | 成分样本图、效应一致性、块热图 | CORE composition/forest/heatmap | 比例输入另用明确比例配方；同源映射及参考覆盖 |
| F36 | 分类与ROC | ROC/PR、校准、混淆、增量性能 | tidymodels S20 DOC; CORE curve | 使用OOF/heldout；不翻转方向追求AUC |
| F37 | 特征/模型解释 | 系数区间、SHAP分布、选择频率 | CORE forest/heatmap; 专用模型API执行前核验 | 不从预测归因推出因果 |
| F38 | 临床/生存 | 调整效应森林、KM及风险人数、患者级组织标志物散点 | CORE forest; TLS代码 S24; 生存专用API执行前核验 | 真患者、删失/随访/临床变量存在才做；阈值和模型预先确定 |
| F39 | 多组图版 | A–H面板、共享图例、热图组合 | patchwork S21 DOC | 图例合并仅限相同语义和尺度 |
| F40 | 最终证据地图 | 模型×细胞×通路×证据等级矩阵 | CORE heatmap的分类专用适配/表格 | 未测量、阴性、探索分开；无任意综合打分 |
| F41 | TCR/BCR克隆谱 | 克隆大小嵌入图、样本级大小分布、克隆共享矩阵 | TLS代码 S24 CONDITIONAL | 必须有受体序列与细胞、样本身份的可信连接；共享定义和分母固定；细胞/克隆不是供体重复 |
| F42 | 细胞状态可分辨度 | 两条件Augur AUC散点与差值图 | EXT score_comparison合成数据已测; TLS代码 S24 | 用已审核AUC及匹配上游差值区间；Augur模型本身未运行；AUC差不是表达变化或干预效应 |

## 本轮看图所得（不是全部42项都完成原生场景视觉审阅）

- ClusterGVis作者仓库组合示意：左/中/右分别承载模式、矩阵和功能，优点是同一模块横向对齐。用于稀疏时间点时不照搬平滑趋势；行注释过长就拆分。
- SeuratExtend：先前已实际查看分类/样本UMAP与dotplot；学习分面和标签而不是照搬偏浅色卡。
- 本轮新增enrichplot图例与ComplexHeatmap实际页面的视觉检查在测试记录中登记；没有截图审阅的资源只标DOC。
- TLS_in_HNSCC 的固定提交包含38个R脚本；已核对目录并审读代表性代码。新增的是代码启发的图形模式；没有将其仓库脚本直接当成已测试的本地渲染器。具体输入与风险见 [tls-hnscc-visuals.md](tls-hnscc-visuals.md)。

## 自编与外部代码边界

旧实现层保留 Python 37 个绘图函数：9 个核心、4 个扩展、5 个可选风格、5 个出版布局、6 个多模态、3 个记录/矩阵润色以及5个通用函数。其中28个有R对应、9个为Python-only。42项为分析场景路由，不代表42个已执行原生模型适配器。图型入口和逐图参数见 [aesthetic-controls.md](aesthetic-controls.md)。F08/F09/F12/F13/F24的新画法和替换决策见[aesthetic-upgrades.md](aesthetic-upgrades.md)。测试成熟度见capabilities.tsv。复杂原生对象由官方代码入口按版本适配；不要声称所有包安装、所有图件可立即运行。通用heatmap可承载已审核矩阵，但应使用正确色阶和图例，不把所有值都叫z-score。CellChat当前入口为S25；S14仅历史对照。


2026-10-05新增参考、独立panel与关系扩展之后，当前总计68个Python绘图函数，28个历史R对应保留。37个旧函数的50种展示形式、25张参考、43个独立panel、15套色卡、20个实际组合与12个关系扩展示例均保留独立ID。主目录按48个通用数据绘图/组合入口组织，另列结构和色卡库；示例数不等于图型数。数据结构选图见[data-expression-router.md](data-expression-router.md)，完整内容保留见[content-preservation.md](content-preservation.md)，关系扩展见[network-expansion.md](network-expansion.md)。
