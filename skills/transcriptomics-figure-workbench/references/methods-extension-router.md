# 新增结果结构、编码与解释边界

这是冻结结果绘图接口。函数数、示例数、图形语法与分析方法数分别计数；没有自动分析、统计检验、整合、聚类或远程任务。

| 数据与表达 | 示例 | 精确输入/编码 | 边界与来源 |
|---|---|---|---|
| 多组/亚群的富集证据与比例 | E01、K21 | 完整term×column网格，group/class/block、padj/GeneRatio、reported/tested_absent/not_tested；形状表组、填充面积表比例、颜色表−log10q | 各组色限一致；零报告和未检测不同；最多2组独立色条。参考原图的分组顶栏、分块、术语列和图例留白都保留 |
| 术语内成员效应＋术语统计 | E02–05、E06a–d、K22 | 独立term行与member行；内轨高度−log10padj，内轨颜色为已给方向分数；外轨半径为成员效应，颜色为同一效应，表单独给说明 | 高度不代表方向；角位置仅排布，每点对应已给成员。[GOplot原始论文](https://academic.oup.com/bioinformatics/article/31/17/2912/184136)、[GOCircle手册](https://search.r-project.org/CRAN/refmans/GOplot/html/GOCircle.html) |
| 成员关系的弦、矩阵和冗余网络 | E08/E09/E23、K23 | 42条去重成员边；矩阵42个1；网络来自同一成员集合的Jaccard | 成员弦等宽，仅表示成员关系；N04数量带宽弦另保留。[GOChord作者手册](https://github.com/cran/GOplot/blob/master/man/GOChord.Rd)、[富集绘图教程](https://yulab-smu.top/biomedical-knowledge-mining-book/04-visualization.html) |
| 两/多集合交集 | E07、N06 | 完整二元成员；精确集合/交集数和明确分母 | Venn圈面积是示意；多集合优先UpSet；不能用未纳入全集计算百分比。[UpSet官方API](https://upsetplot.readthedocs.io/en/latest/api.html) |
| 分布、尾部和与参考分布偏离 | E10/E11/E12、K24 | ECDF/QQ已有坐标，密度已有共同x网格/非负密度；密度高度采用一个共同尺度 | E12是生成合成值的解析密度，不是样本KDE；ECDF不拟合密度。[SciPy ECDF](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ecdf.html) |
| 协变量平衡＋模型区间 | E13/E21、K26 | covariate×stage SMD；另外给estimand/区间结果 | 0.1是说明阈值，不能证明无混杂；不同表同阶段身份，不伪称运行匹配。[cobalt作者说明](https://ngreifer.github.io/cobalt/articles/cobalt.html) |
| 配对方法一致性 | E14/E24、K25 | 同一对象的XY或mean/difference；显式bias/LoA定义 | 相关性不等于一致性，重复测量需要合适上游分析。[Bland–Altman原始论文](https://pubmed.ncbi.nlm.nih.gov/2868172/) |
| 时间到事件与个体随访 | E15/E16、K27 | 已有阶梯S/区间、风险表、期初/期末约定、删失；个体起止/事件 | 期末风险人数逐时点与结束表核对；不拟合KM或执行log-rank。[lifelines风险表说明](https://lifelines.readthedocs.io/en/latest/lifelines.plotting.html) |
| 分析规格的敏感性 | E17 | specification×estimate/interval，完整决策0/1矩阵和固定顺序 | 不自动挑规格、重估模型；区间定义单独注明。[规格曲线原始方法](https://www.nature.com/articles/s41562-020-0912-z) |
| 已给局部方向与亚群/marker | E18/E25/E26、K28 | 完全相同对象ID/XY，加类别、特征值、已有vx/vy | 箭头展示已投影向量，不计算RNA velocity、轨迹或流线。[scVelo作者教程](https://scvelo.readthedocs.io/en/stable/VelocityBasics.html) |
| 二元量的地图色键 | E19 | tile×两项已有数值及显式3×3分箱 | 两项指标不同单位分别声明；不是相关性检验 |
| 三种成分平衡 | E27 | 同一分母三非负比例，和为1；仿射重心坐标 | 不自动归一化；闭合组成非独立变量。[mpltern作者文档](https://mpltern.readthedocs.io/en/latest/) |
| 全局关联与局部位点轨道 | E28/E29、K29 | variant ID、assembly/segment/position/p；局部LD、重组率、基因跨度与strand/lane | 不选lead、不计算LD、不推断共定位；LD缺失不填0。[LocusZoom作者数据说明](https://statgen.github.io/locuszoom/docs/guides/data_retrieval.html) |
| 研究效应与精度 | E30/E30b、K31 | study ID、效应/SE及给定指南线；另给完整区间 | 不合并研究；不对称本身不能证明发表偏倚。[metafor funnel说明](https://wviechtb.github.io/metafor/reference/funnel.html) |
| 层级和数量 | E31 | acyclic parent/node/value和已给矩形；子总量/父总量、嵌套、不重叠、面积/数量一致 | 面积表示可相加量；边框表示层级，不建立新聚类。[HCIL作者历史与方法](https://www.cs.umd.edu/hcil/treemap-history/) |
| 多级不确定性 | E32 | group×x×coverage及中心/上下界，显式完整和嵌套 | 不估计预测区间；置信/预测/后验区间不能混同。[ggdist lineribbon作者说明](https://mjskay.github.io/ggdist/articles/lineribbon.html) |
| 注册空间上的身份/分子 | E33a/b、K32 | RGB完整像素表、尺度、已给物理半径与注册坐标、类别/数值 | 不配准、不分割；示例背景不冒充H&E。[Squidpy空间绘图说明](https://squidpy.readthedocs.io/en/stable/api/squidpy.pl.spatial_scatter.html) |
| 多组学因子/分数/载荷/质谱/通路 | M01–10、K33–36 | 每种结果有独立对象ID、量纲与映射 | 详见[课件路由](course-visualization-router.md)，不要把现成热图或堆积变体登记为新算法 |
| 冻结模型的四诊断视角 | M11a–d、K30 | 同48个对象的拟合值、残差、标准残差、leverage/Cook；QQ另给排序残差/参考分位 | 不拟合模型、平滑、检验正态或删点；Cook用面积并附转换说明。[statsmodels诊断教程](https://www.statsmodels.org/stable/examples/notebooks/generated/linear_regression_diagnostics_plots.html) |

## 直接重绘

`render_frozen_table.py`注册38个固定适配器，不接受任意模块或可执行表达式。TSV中的对象字符串（包括前导零和文字NA）保持身份；数值字段按适配器显式转换；混合记录表中别类字段可为空，但本类要求字段不允许缺失。

例：`render_frozen_table.py term_effect_circle --input INPUT.tsv --style STYLE.json --meta META.json --theme PROJECT_THEME.json --output NEW_DIRECTORY --id FIGURE_ID`。参数声明模块/函数时须匹配注册适配器。案例构建脚本只产生确定性合成结果，不提供科研分析。

更换课题色卡/字体后，所有可比类别使用固定身份槽，连续量保留各自单位与limits/center；不能让加载顺序改变颜色。新52个单独示例有真实运行的重绘与几何不变检查。R或原生结构后端仍需其自己的替换与目标平台验证。
