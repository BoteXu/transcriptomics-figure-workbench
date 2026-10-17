# WGCNA、已有层次结果与关联网络的绘图路由

## v0.9.1 专用实现与实际实例

当前使用 `figure_wgcna_views.plot_wgcna_view`。下列均有可运行 FigureSpec、准确输入 TSV 和 PNG/SVG/PDF：[专用图库](../assets/wgcna-gallery/index.html)。通过 `chapter-views --chapter bulk.wgcna` 或 `single_cell.hdwgcna` 查看具体入口，再用 `view-template` 导出。下方早期通用路由保留为替代画法，不再把通用组合图当作基础覆盖已经齐全的证据。

|具体视图|冻结输入与必需含义|
|---|---|
|SoftPower|候选 power、signed fit、mean connectivity；明确预选值和可选参考线，不自动选 power|
|SampleTree|样本叶序、完整合并树、批次/条件两条分类轨道|
|ModuleTree|基因叶序、完整合并树、dynamic/merged 模块条；合并高度与叶序必须一致|
|ModuleTrait|完整模块×性状的 r、已给 p/q 和有效独立 n，明确 raw/adjusted|
|MM_GS / Absolute|每基因的模块、kME/MM、GS；signed 与上游 absolute 两种约定分别保留|
|TOM / Dissimilarity|对称完整矩阵与固定顺序；TOM、adjacency、1−TOM 分别标名，不自动混换|
|EigengeneNetwork|定向后的模块 eigengene 相关矩阵，不在绘图时计算相关|
|EigengeneProfiles|每个独立供者的模块代表值与条件，保留全部供者点|
|HubConnectivity|明确选择的基因、模块、kWithin 和 kME，不按图形美观筛 hub|
|Preservation|模块大小、Zsummary、medianRank；参考线只来自明确参数|
|MetacellQC|metacell→供者/细胞型、构成细胞数、共享细胞数；metacell 不增加供者 n|
|ModuleActivity|每个模块的同一批细胞、完全相同坐标和共同声明的评分范围|

`context` 必须声明网络类型（signed/unsigned/signed hybrid）、相关方法、独立单位及网络来源 n、模块版本、来源版本和选择范围。图中 n 是上下文声明；样本子集、metacell 和细胞显示需同时检查精确输入数量，不能以网络总 n 代替性状相关的有效 n。`module_order` 必须完整覆盖选中模块。分面列数由数据量与用户要求决定；大型矩阵保留全表并使用阅读版，不能为了标签方便删掉叶或基因。

依据输入结构选择画法；WGCNA 是上游分析方法，不是一个新的通用图形种类。本包读取已审核的诊断表、树、模块身份、矩阵、评分和边表；不运行相关检验、软阈值选择、模块检测、TOM 计算或 hub 筛选。

|已有数据|需要保留的字段/语义|推荐画法与表达|
|---|---|---|
|候选 power 的拓扑诊断|候选值、已给 signed fit 指标与 mean connectivity；各指标定义|XY 点/有序线 T33/T31；K38 A/B 同时看两个诊断量，不能只凭美观选阈值|
|已有基因层次树与分类|叶 ID、完整合并记录、合并高度、固定叶序、模块 ID|E36 树与对齐分类条；E37 环形模式可增加叶端连续值、点面积和外圈独立数量|
|TOM 或 adjacency 等矩阵|完整对应的行列 ID、叶序、矩阵类型、网络版本及是否 signed|T34 通用热图；K40 B 的冻结矩阵与树共享对象。TOM、adjacency 与 1−TOM 不能混称|
|模块代表值与性状关系|模块/性状 ID、系数、给定 p 或 adjusted p、有效独立样本数和缺失规则|E35 每格三角区分别表达系数与 −log10 p；也可用 T34 色块系数＋已给数值。两量值分别给色键|
|MM/kME 与 GS 评分|成员 ID、模块 ID、目标性状、原始 signed 或已给绝对值、评分定义|T33 XY；K38 E 与树共享成员 ID。绝对值与带符号值是输入约定，不是自动转换|
|模块代表值之间的边|同一模块 ID、边估计、权重/符号、阈值及版本|R25 网络；K40 C 配合模块性状矩阵。不给网络图增添不存在的因果方向|
|kWithin/kTotal 等连接指标|对象 ID、已计算量、单位、排序及入选规则|T32 条形或 P11a 棒棒糖；保留阈值与被选择对象的规则|
|成员、条目与富集结果|二元关系、成员效应、条目类别、同一背景的比例与已给 p/count|E34 等宽曲线＋对齐条目气泡；K37 与集合、分类得分和整体/子网络组合|
|同对象的可加贡献表|完整对象×成分表、共同单位、非负可加量、固定顺序|T10 的绝对量模式；K39 与同叶 ID 的环形树联合展示。独立对接能量不可默认相加解释总亲和力|

K38、K40 是同一“模块结果组合”入口的两种布局模式。K37、K39 保存各自明确的 panel 关系。每个 panel 的 TSV、参数、矢量导出与统一主题均单独保存；组合不会重算分析。

## 编码与统计约定

- 分类身份用稳定模块 ID→课题色卡槽位。模块名称、上游软件的传统颜色名称和本课题实际显示颜色分别记录，不能因改色而重新归属模块。
- 树分支高度表示给定合并高度；环形布局不意味着时间、亲和力或演化距离。叶端点面积、颜色和外圈长度是三个独立量，各有明确范围和定义。
- 保留 signed/unsigned 网络定义、相关方法、样本顺序、批次/协变量、缺失处理、模块版本和上游阈值。有效样本数指相关计算的独立样本，不是基因数或细胞数。
- 同格 p 与系数分别解读。名义 p 与调整 p 明确标注，校正方法和检验范围由上游提供。多性状、重复采样和混杂处理属于分析设计，不由画图解决。
- 网络边、模块相关与“高连接度”是所声明方法下的统计/结构描述；不能独立建立调控机制、靶点因果性或实验验证。
- E34 的等宽曲线只表示成员关系。条目 count 必须与展示的唯一成员数一致；比例背景另行声明，部分展示不得冒充完整富集结果。

## 原始方法与官方可视化参考

官方教程分别提供网络构建、模块与外部信息关系、网络可视化的输入/输出说明。本路由据这些语义整理冻结结果的画法，不复制分析实现：

- [官方教程入口](https://edo98811.github.io/WGCNA_official_documentation/)
- [网络构建与软阈值教程](https://edo98811.github.io/WGCNA_official_documentation/FemaleLiver-02-networkConstr-auto.pdf)
- [模块与外部性状、MM 与 GS](https://edo98811.github.io/WGCNA_official_documentation/FemaleLiver-03-relateModsToExt.pdf)
- [网络可视化教程](https://edo98811.github.io/WGCNA_official_documentation/FemaleLiver-05-Visualization.pdf)
- [WGCNA 原始论文](https://pmc.ncbi.nlm.nih.gov/articles/2631488/)

参考图的曲线、三角格和环形树分别由明确的关系/双量值/层次输入实现。实际应用必须按来源验证各字段的意义，不能从截图反推原始数值或认定所有参考 panel 都来自 WGCNA。
