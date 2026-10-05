# 参考图迁移目录：按数据与表达组织

25 张图型参考；7 张明确写有“科研配色方案”的海报另列为 C01–C07 色卡。计算生物学是使用场景之一，目录不按研究领域、物种或技术名称分组。

当前示例复现的是布局和视觉编码。原图没有配套原始数值，输出使用独立生成并明确标注的演示数据，不能当作原论文结果。

## 如何选图

| 数据形状 | 适合参考 | 能表达什么 |
|---|---|---|
| 类别、系列、数值或比例 | R01/R02/R17 | 分组规模、分布与中心 |
| 共同键对齐的多矩阵和轨道 | R03/R04/R15/R20/R22 | 多种量之间的对照与块结构 |
| 成对关联和带权边 | R05/R06/R07 | 正负关联、强度与连接 |
| 成对观测和上游摘要 | R08/R12/R13/R18/R19 | 趋势、一致性、位置及分散 |
| 试次、特征贡献或迭代记录 | R09/R10/R11/R14 | 参数组合、贡献和过程诊断 |
| 效应、区间或比较 | R16/R21 | 方向、分散、区间与筛选后记录数 |
| 连续二维网格或流程组合 | R23/R24 | 峰谷地形及多层信息叙事 |

## 共同输入约定

每个复合图使用一张带 `record_type` 的长表。一个记录类型所需的字段必须完整、数值有限；其他类型不用的字段可以留空，不能把缺失观测填成零。原始单位 ID、顺序、比较方向、量纲、分母、统计来源、区间定义和筛选范围需另写 provenance。

输入 schema 的机器版本见 reference-patterns.json，颜色注册见 reference-palettes.json。示例 *_style.json 记录实际传入的参数；这是继续调整审美的起点。字体、页宽、颜色、标签位置可以改，数据和分析定义应冻结。

通用步骤：确认上游结果及单位 → 固定表与顺序 → 选布局和数值映射 → 绘制各层 → 检查真实 PDF/PNG → 保存 TSV、参数、图和来源校验。渲染器不会重算降维、聚类、拟合、KDE、SHAP 或检验。

## R01 · 环形轮廓＋分层气泡（明亮色）

**需要的数据**：每个类别、系列一行：主数值和非负第二数值；给定类别顺序、系列顺序及量纲。

**能呈现的表达**：一个圆内同时比较多系列主值轮廓和第二数值的规模。

**怎么画、怎么迁移**：把类别映射为角度、主值映射为半径；在各系列固定环上画面积与第二值成比例的气泡；中心留空放指标名。

**审美调节**：内孔比例、填充透明度、轮廓线宽、气泡面积比例、标签距离、系列颜色。

**解释与使用边界**：无序类别默认不连成连续曲线；示例平滑仅为有界显示连接，不生成新观测。

适配器：`figure_reference.plot_annular_profile`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| profile | category, series, value, area | value, area | 必需 |

## R02 · 环形轮廓＋分层气泡（柔和色）

**需要的数据**：与 R01 完全相同；可直接替换 palette，不改表。

**能呈现的表达**：同一种数据的另一种视觉气质，可强调一个系列。

**怎么画、怎么迁移**：复用 R01 的半径和面积映射，只替换系列色和填充层次。

**审美调节**：重点系列颜色、其余系列透明度、线条对比度。

**解释与使用边界**：R01/R02 示例输入哈希一致；柔和颜色不适合作为白底细小文字。

适配器：`figure_reference.plot_annular_profile`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| profile | category, series, value, area | value, area | 必需 |

## R03 · 坐标小窗＋证据点阵＋双矩阵

**需要的数据**：已有二维坐标及所属块；状态顺序表；状态×条件的效应与证据强度；状态×特征的两种数值矩阵。

**能呈现的表达**：把群体位置、条件关联、平均值及标准化得分按共同状态对齐。

**怎么画、怎么迁移**：建立共享行坐标和块间留白；点阵面积编码证据强度、颜色编码效应；两种矩阵各用独立明确色标。

**审美调节**：块间距、坐标窗大小、列名倾角、点面积、矩阵宽度、各色标位置。

**解释与使用边界**：不计算降维、效应或标准化；mean、evidence 和 score 的定义必须上游提供。

适配器：`figure_reference.plot_state_dashboard`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| embedding | unit_id, family, x, y | x, y | 必需 |
| state | state, family, order | order | 必需 |
| effect | state, condition, value, evidence | value, evidence | 必需 |
| mean | state, feature, value | value | 必需 |
| program | state, feature, value | value | 必需 |

## R04 · 环形坐标总览＋径向计数＋层次点阵

**需要的数据**：二维坐标和类别；类别×段的整数计数；给定树线段和叶顺序；类别×特征的表达比例及平均值。

**能呈现的表达**：从整体类别分布看到组成数量，再对齐层次、数量和特征特征。

**怎么画、怎么迁移**：已有坐标统一居中缩放进入圆形视窗；外围按类别画径向堆叠条；下方依给定叶顺序对齐树、柱和点阵。

**审美调节**：圆半径、外围轨道间隔、类别编号、图例列数、底部面板高度、文字大小。

**解释与使用边界**：不重新拟合坐标或聚类；70 类示例应在最终论文尺寸下考虑分图，颜色不独自承担识别。

适配器：`figure_reference.plot_embedding_atlas`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, layer, group, x, y | x, y | 必需 |
| count | layer, group, segment, value | value | 必需 |
| leaf | group, order | order | 必需 |
| tree | segment_id, x0, y0, x1, y1 | x0, y0, x1, y1 | 必需 |
| marker | group, feature, fraction, value | fraction, value | 必需 |

## R05 · 椭圆＋数值相关矩阵

**需要的数据**：变量顺序及每个无重复变量对的相关系数，范围 [-1,1]。

**能呈现的表达**：上三角直观显示关联方向和强度，下三角提供准确数值。

**怎么画、怎么迁移**：用 sqrt(1+r)、sqrt(1-r) 确定椭圆轴；固定倾角；下三角写 r；色标固定 -1 至 1。

**审美调节**：椭圆比例、网格强度、数字字号、色标、变量标签。

**解释与使用边界**：相关不说明因果；沿用参考黄紫色时数字改深色以保证可读性。

适配器：`figure_reference.plot_ellipse_correlation`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| correlation | a, b, r | r | 必需 |

## R06 · 圆形带符号网络

**需要的数据**：节点 ID 与展示顺序；无自环、无重复无向边的端点与带符号权重。

**能呈现的表达**：显示对象间连接方向符号、强弱以及网络分布。

**怎么画、怎么迁移**：固定节点圆周顺序；贝塞尔曲线连接端点；边色编码符号、线宽编码绝对值；节点大小默认固定。

**审美调节**：节点间隔、外移标签、边曲率、线宽、透明度、节点样式。

**解释与使用边界**：不推断网络、真实方向或作用机制；密集边可迁移为矩阵或分面。

适配器：`figure_reference.plot_signed_network`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| node | node, order | order | 必需 |
| edge | a, b, r | r | 必需 |

## R07 · 三角关联矩阵＋外接检验网络

**需要的数据**：完整上三角 r、p；集合 ID 到目标变量的检验 r、p；明确原始或校正 p。

**能呈现的表达**：同时呈现变量内部相关与另一组对象对这些变量的关联。

**怎么画、怎么迁移**：矩阵方块面积编码 |r|、色编码 r；外接线宽编码 |检验 r|、颜色编码给定 p 档；星号只由提供的 p 映射。

**审美调节**：三角矩阵偏移、外接节点位置、弧度、p 档颜色、图例分区。

**解释与使用边界**：Mantel 等检验需要上游的距离矩阵和置换方案；本函数仅显示已有结果。

适配器：`figure_reference.plot_mantel_matrix`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| correlation | a, b, r, p | r, p | 必需 |
| mantel | specimen, target, r, p | r, p | 必需 |

## R08 · 散点＋二维密度＋边缘直方图

**需要的数据**：每单位 x、y、组；给定相同边界的边缘计数；二维密度网格及可选统计文字。

**能呈现的表达**：同时看组间位置、重叠范围与两个变量各自的分布。

**怎么画、怎么迁移**：用共享 x/y 范围搭建主窗与边缘窗；点保持原坐标；给定二维网格画等高线；边缘画固定分箱。

**审美调节**：点大小、组透明度、等高线层数、边缘高度、文字框、图例。

**解释与使用边界**：图中边缘为 Count；只有值确为概率密度时才标 Density；不自动算 KDE、rho 或 p。

适配器：`figure_reference.plot_joint_reference`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, group, x, y | x, y | 必需 |
| marginal | group, axis, coordinate, value | coordinate, value | 必需 |
| density2d | group, x, y, value | x, y, value | 可选 |
| fit | group, x, y, lower, upper | x, y, lower, upper | 可选 |
| annotation | group, x, y, text | x, y | 可选 |
| box | group, q1, median, q3, low, high | q1, median, q3, low, high | 可选 |
| bracket | a, b, text |  | 可选 |

`marginal_mode="bins"` 还需 `left`、`right`，且所有组共享 bin 边界。

## R09 · 平滑平行坐标

**需要的数据**：试次 ID、维度名、各维数值、每试次固定评价值；各轴真实上下限。

**能呈现的表达**：同时看多参数组合如何对应评价表现。

**怎么画、怎么迁移**：分别按声明量纲归一化每条轴的展示位置；试次跨轴连接为贝塞尔线；颜色编码评价。

**审美调节**：线条透明度、曲率、轴间距、评价色标、离散轴刻度。

**解释与使用边界**：平滑线只是连接；评价来自上游，绘图不执行调参，也不决定测试集选优。

适配器：`figure_reference.plot_parallel_trials`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| trial | trial_id, dimension, value, score | value, score | 必需 |

## R10 · 贡献蜂群图

**需要的数据**：单位 ID、特征、已计算贡献值，以及用于着色的特征值（本适配器要求已声明为 [0,1] 展示尺度）。

**能呈现的表达**：看每个特征的正负贡献、贡献分布与高低特征值的关系。

**怎么画、怎么迁移**：固定特征顺序；横坐标使用原贡献；纵向仅做确定性防重叠排布；颜色编码特征值。

**审美调节**：点径、排布宽度、行距、零线、特征顺序、连续色图。

**解释与使用边界**：不会算 SHAP/GeoShapley；名称中包含交互项并不能代替真正的交互贡献。

适配器：`figure_reference.plot_contribution_swarm`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| contribution | unit_id, feature, contribution, feature_value | contribution, feature_value | 必需 |

## R11 · 多类贡献蜂群＋玫瑰插图＋多环份额

**需要的数据**：各类单位×特征贡献和特征值；各类特征非负份额且每类合计 1；各类特征顺序。

**能呈现的表达**：比较各类别的贡献分布和已定义的整体贡献份额。

**怎么画、怎么迁移**：每类一个蜂群；等角玫瑰的扇形面积与份额成比例；每类一条环，环上角度编码份额。

**审美调节**：各面板共享范围、插图位置与半径、环间距、类别顺序、图例、总页宽。

**解释与使用边界**：有符号单位贡献与绝对贡献份额是两种量，份额计算定义必须提供；示例小字需按最终版面放大或拆图。

适配器：`figure_reference.plot_multiclass_contributions`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| contribution | unit_id, class, feature, contribution, feature_value | contribution, feature_value | 必需 |
| share | class, feature, value | value | 必需 |

## R12 · 一致性散点＋边缘密度＋残差摘要

**需要的数据**：单位 ID、组、两方法测量；给定边缘密度；给定差值箱线摘要和比较文字。

**能呈现的表达**：看两种测量与 y=x 的偏离，以及各组误差和分布。

**怎么画、怎么迁移**：保留成对点；画 y=x 参照；上下/右侧画给定密度；插图使用已提供的 y-x 五数摘要。

**审美调节**：身份线样式、点径、密度填充、残差插图大小、摘要字号。

**解释与使用边界**：相关强不代表一致；统计结论需另外提供；箱线不能替代正式一致性分析。

适配器：`figure_reference.plot_joint_reference`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, group, x, y | x, y | 必需 |
| marginal | group, axis, coordinate, value | coordinate, value | 必需 |
| density2d | group, x, y, value | x, y, value | 可选 |
| fit | group, x, y, lower, upper | x, y, lower, upper | 可选 |
| annotation | group, x, y, text | x, y | 可选 |
| box | group, q1, median, q3, low, high | q1, median, q3, low, high | 可选 |
| bracket | a, b, text |  | 可选 |

`marginal_mode="bins"` 还需 `left`、`right`，且所有组共享 bin 边界。

## R13 · 多组回归散点＋边缘密度＋统计框

**需要的数据**：单位 x/y 与组；拟合 x/y、lower/upper；边缘密度；显示用统计文字。

**能呈现的表达**：比较组间线性趋势与分布差异。

**怎么画、怎么迁移**：原点坐标上叠加给定拟合与范围带；共享边缘坐标；角落放统计框并保留组色边框。

**审美调节**：点大小、拟合线粗、带透明度、文字框位置、密度轮廓。

**解释与使用边界**：不拟合回归或计算 R²/RMSE/p；带的 CI/PI/SD 含义必须写明。

适配器：`figure_reference.plot_joint_reference`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, group, x, y | x, y | 必需 |
| marginal | group, axis, coordinate, value | coordinate, value | 必需 |
| density2d | group, x, y, value | x, y, value | 可选 |
| fit | group, x, y, lower, upper | x, y, lower, upper | 可选 |
| annotation | group, x, y, text | x, y | 可选 |
| box | group, q1, median, q3, low, high | q1, median, q3, low, high | 可选 |
| bracket | a, b, text |  | 可选 |

`marginal_mode="bins"` 还需 `left`、`right`，且所有组共享 bin 边界。

## R14 · 损失曲线＋运行热图＋梯度诊断

**需要的数据**：训练/验证等系列的阶段值与上下界；运行×阶段矩阵；正值梯度及界限；已选阶段。

**能呈现的表达**：看收敛过程、运行间波动和梯度尺度。

**怎么画、怎么迁移**：损失共享轴和范围带；右上矩阵按运行与阶段对齐；右下正值采用对数轴；标出外部提供的选定阶段。

**审美调节**：主辅面板比例、带透明度、选定阶段符号、网格、对数轴刻度。

**解释与使用边界**：不训练、不自动早停；区间必须解释是重复运行范围还是统计不确定性。

适配器：`figure_reference.plot_training_dashboard`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| loss | series, epoch, value, lower, upper | epoch, value, lower, upper | 必需 |
| heat | run, epoch, value | epoch, value | 必需 |
| gradient | epoch, value, lower, upper | epoch, value, lower, upper | 必需 |
| reference | epoch, value | epoch, value | 必需 |

## R15 · 带边缘统计的块状矩阵

**需要的数据**：完整矩阵、行所属组、冻结行列顺序、每列柱值与线值、各组给定密度。

**能呈现的表达**：显示模块块结构，并同时看列尺度和各组分布。

**怎么画、怎么迁移**：矩阵按给定顺序画格；左侧连续分组色条；顶部柱与线使用明确分别标注的尺度；右侧密度分窗。

**审美调节**：块边界、色条宽度、矩阵色限、顶部高度、曲线颜色、各密度间距。

**解释与使用边界**：不聚类或行标准化；两个顶部量量纲不同时须明确双轴，不能通过缩放营造相关。

适配器：`figure_reference.plot_activity_dashboard`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| matrix | row, column, value | value | 必需 |
| row | row, group |  | 必需 |
| top | column, bar, line | bar, line | 必需 |
| density | group, coordinate, value | coordinate, value | 必需 |

## R16 · 效应分布＋森林摘要（双面板）

**需要的数据**：每行每面板的效应记录；给定汇总效应、上下界、样本数字标签和 p；给定行顺序。

**能呈现的表达**：同时看汇总方向、区间宽度和原始效应分散程度。

**怎么画、怎么迁移**：交替淡灰行底；散点保留效应值；菱形位于汇总值、横线显示给定区间；给定 p 映射标记。

**审美调节**：行距、底色、点透明度、菱形尺寸、区间线宽、计数列。

**解释与使用边界**：不合并效应或做元分析；n(k) 的两个数字各是什么必须定义；相关效应不自动成为独立研究。

适配器：`figure_reference.plot_effect_distribution_forest`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| effect | effect_id, panel, row, value | value | 必需 |
| summary | panel, row, value, lower, upper, count_text, p | value, lower, upper, p | 必需 |

## R17 · 组间蜂群＋中心值

**需要的数据**：单位 ID、组和值；每组已计算中心值，以及中心值的定义。

**能呈现的表达**：看分布形状、离群范围和组中心；点密集的宽处表示局部观测多。

**怎么画、怎么迁移**：纵坐标保持测量值；横向仅防重叠排点；中心值用深色点加白边。

**审美调节**：蜂群宽、点间距、组距、透明度、零线、中心标记。

**解释与使用边界**：黑点到底是平均数还是中位数由输入定义；图形宽度不等同置信区间。

适配器：`figure_reference.plot_group_beeswarm`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| observation | unit_id, group, value | value | 必需 |
| summary | group, value | value | 必需 |

## R18 · 坐标散点＋质心连线＋椭圆

**需要的数据**：每单位两维坐标、组；给定质心；给定椭圆中心、宽高和角度。

**能呈现的表达**：显示样本到组中心的离散、方向及组间位置。

**怎么画、怎么迁移**：保留坐标；每个点连到指定中心；中心白边强调；椭圆按给定几何参数画。

**审美调节**：连线透明度、质心大小、椭圆线宽、点大小、图例位置。

**解释与使用边界**：PCA 解释方差及椭圆含义由上游提供；不把散布椭圆默认叫 95% CI。

适配器：`figure_reference.plot_pca_reference`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, group, x, y | x, y | 必需 |
| centroid | group, x, y | x, y | 必需 |
| ellipse | group, x, y, width, height, angle | x, y, width, height, angle | 必需 |

## R19 · 坐标景观＋形状分组＋边缘短线

**需要的数据**：与 R18 同一张表；附给定的轴解释和分组颜色、符号。

**能呈现的表达**：强调分组重叠、象限位置以及各轴的投影分布。

**怎么画、怎么迁移**：在共享二维坐标上用颜色和形状双重编码；画零线、淡象限及每个原始点的边缘 rug。

**审美调节**：象限底色、形状、椭圆透明度、rug 长度、边界和轴粗细。

**解释与使用边界**：R18/R19 示例输入哈希一致；背景象限不会改变数据，也不能产生类别分界结论。

适配器：`figure_reference.plot_pca_reference`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| point | unit_id, group, x, y | x, y | 必需 |
| centroid | group, x, y | x, y | 必需 |
| ellipse | group, x, y, width, height, angle | x, y, width, height, angle | 必需 |

## R20 · 分面气泡矩阵

**需要的数据**：两种分面键、特征、时间/窗口坐标、已算关联 r；完整组合网格。

**能呈现的表达**：比较不同条件和窗口的关联方向、大小及一致性。

**怎么画、怎么迁移**：分面使用同一行列顺序；圆面积正比 |r|、颜色编码 r；所有分面共享尺度与面积图例。

**审美调节**：圆最大面积、格线、分面间距、分面标题、色标、窗口标签。

**解释与使用边界**：这里面积是效应大小，不能误读为比例或显著性；偏相关的控制变量需记录。

适配器：`figure_reference.plot_facet_bubble_matrix`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| association | row_facet, column_facet, feature, window, r | window, r | 必需 |

## R21 · 多比较有符号效应条带

**需要的数据**：特征 ID、比较、面板、效应、padj、已固定的水平展示抖动。

**能呈现的表达**：在多个比较中同时显示正负变化及符合声明条件的特征数。

**怎么画、怎么迁移**：每个比较一列；竖坐标效应、固定抖动分散；按明确 padj/效应门槛给 eligible 点着色；底带为比较色。

**审美调节**：点径、列宽、灰底、比较带高度、正负色、计数位置。

**解释与使用边界**：全输入保留在 TSV；显示计数是符合条件的特征记录数，不是受试者数；不重算差异或 FDR。

适配器：`figure_reference.plot_strip_effects`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| effect | feature, panel, contrast, value, padj, jitter | value, padj, jitter | 必需 |

## R22 · 共用类别轴的柱轨道＋多行矩阵

**需要的数据**：类别顺序与连续块归属；每个轨道×类别的整数计数；每个矩阵×行×类别的值；各矩阵范围。

**能呈现的表达**：把同一批类别的数量与多种关联/比例量上下对齐。

**怎么画、怎么迁移**：所有面板共用 x 位置；上方分别柱轨道；下方分别矩阵和色标；底部按连续类别块加括号。

**审美调节**：轨道高度、矩阵行高、组括号、类别标签倾角、独立色标。

**解释与使用边界**：不按跨物种等领域归类；可以迁移到任意共同类别轴；每种矩阵的量纲和范围保持独立。

适配器：`figure_reference.plot_aligned_tracks`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| count | track, category, value | value | 必需 |
| matrix | matrix, row, category, value | value | 必需 |
| category | category, block |  | 必需 |

## R23 · 连续三维曲面

**需要的数据**：完整、无重复的 (x,y,z) 网格；x/y 真正量纲、z 数值定义及范围。

**能呈现的表达**：显示两个维度变化下的数值地形、峰谷与梯度。

**怎么画、怎么迁移**：按冻结网格构造 surface，颜色映射 z；不插值、重采样；声明相机俯仰和方位；添加独立色标。

**审美调节**：相机角度、色图、网格线、坐标刻度、纵横比与色限。

**解释与使用边界**：3D 可能遮挡数值，精确比较可配二维热图；原截图未提供原始网格。

适配器：`figure_reference.plot_surface_grid`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| grid | x, y, z | x, y, z | 必需 |

## R24 · 流程＋对象图＋候选矩阵＋地形＋阶段柱

**需要的数据**：流程节点和有类型连线；对象轮廓或真实结构渲染；给定候选矩阵；三份二维数值网格和峰标记；两组阶段计数。

**能呈现的表达**：把方法逻辑、对象外观、评价地形及阶段数量放在同一页。

**怎么画、怎么迁移**：流程层以节点/线型表达不同输入；矩阵横向对齐；地形按已有网格画；对象图保持独立相机；阶段柱用同一颜色字典。

**审美调节**：流程宽度、模块圆角、连线类型、对象视角、界面高亮、曲面布局、柱图尺寸和阶段色。

**解释与使用边界**：R24 的轮廓仅是示意，没有原始 PDB/mmCIF；真实蛋白必须走结构可视化入口，不用随机轮廓冒充结构。

适配器：`figure_process_dashboard.plot_process_dashboard`。

| record_type | 必需字段 | 数值字段 | 是否可省略整类记录 |
|---|---|---|---|
| node | node_id, x, y, width, height, group, text | x, y, width, height | 必需 |
| edge | edge_id, x0, y0, x1, y1, line_style | x0, y0, x1, y1 | 必需 |
| path | object_id, order, x, y, group, shape | order, x, y | 必需 |
| matrix | matrix_id, row, column, value | row, column, value | 必需 |
| surface | surface_id, x, y, z | x, y, z | 必需 |
| landmark | surface_id, landmark, x, y, z, group | x, y, z | 必需 |
| count | bar_group, category, stage, value | value | 必需 |

## 参考来源与访问状态

输入是用户提供的图片和一个独立图片链接；参考图水印保留在私人对照材料中，未打包进 skill。R23 的私人参考是浏览器实际显示截图，包含边缘，不等同下载到的原图文件。四篇微信正文当前未读到：web 请求失败；色卡文章的浏览器访问被安全策略阻止，未尝试绕过。七张用户补充色卡提供了直接可核验的 Hex。不能把未读文章写成已提取完整教程。

可运行代码为独立实现；粘贴文本仅作为不完整教程参考，未直接执行。实际画法可核查 Matplotlib Ellipse、Path 与颜色归一化官方文档。Natural Earth 公共地图轮廓用于 C01，地图上的数值仍是合成示例。


## R25 多实体网络

节点ID、类型、类别、固定XY、面积；边的端点、符号、权重及关系来源；不同条件共享布局与比例。

形状区分实体类型，颜色固定类别，线色表达正负，线宽表达给定权重；找跨类型关联和中心连接；并排比较不同输入网络。

仅有截图，原边表和原统计方法不可恢复。当前使用合成网络复现形状／颜色／关系／比较语言；关联不是因果或生化通路。 新的输入格式、通路关系和组合方案见[network-expansion.md](network-expansion.md)与[combinations-router.md](combinations-router.md)。
