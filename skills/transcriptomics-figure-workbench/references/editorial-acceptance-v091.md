# 图稿重新验收：读者能否看清问题与证据

## 撤回过宽的通过判断

用户否定了拥挤的总图与零散的 marker 小图。此前的 `SCREEN_REVIEWED`
只说明对应像素实际被检查过，不能理解为用户认可、期刊接收、独立审稿或
整套方案已经足够美观。历史文件和检查记录保留；被替换的默认版式停止推荐。
文件通过、字号通过、屏幕检查、美观选择、科学解释是不同状态。

## 实际淘汰条件

- 标题、图例、标注或面板发生重叠：返工。
- 第一眼无法知道主问题，注释、比例、效应混为一页：拆成有明确用途的图。
- 同一页存在多种没有组织的阅读方向：重排。
- 主要图被长标题或装饰挤成窄条，小图只能放大后辨认：重排或给独立阅读页。
- 色标远离对应面板、重复图例抢占主体、点大小没有定义：返工。
- 大块空白与局部拥挤同时存在：调整比例和间距。
- 只改变配色而没有解决以上问题：不能通过。
- 新布局没有实际出图并看过：保持未审状态。

## 每个亚群的多个 marker

`figure_annotation_views.plot_annotation_evidence(mode='subgroup')` 的输入为：

|记录|需要的字段|约束|
|---|---|---|
|embedding|object_id, group, x, y|细胞唯一；保留所有亚群背景和原始坐标|
|marker_dot|feature, group, value, fraction, feature_group|所选基因×全部亚群完整；均值与检测比例语义分开|
|feature_map|object_id, feature, x, y, value|每个 marker 都有所有细胞；坐标逐一相同|

必须显式给定 `focus_group`、`marker_order`、`expression_label`、
`detection_definition` 和从零开始的共同 `expression_limits`。
`ncols`、`nrows`、面板宽高和导出物理宽度可调整。超过每页容量时，
按明确的 marker 清单拆成完整的连续阅读页，记录每页清单；不能偷偷截断。
未提供的表达矩阵不在本地重算，未提供的 marker 不自动推断。

Atlas 模式只显示身份和跨群 marker 证据，避免把供体比例、差异表达、
通路及全部基因表达图都塞进同一页。每群详细页保留多个 marker，
供体层面的效应、比例及通路仍有各自的完整图。

## 参考与实现范围

对照 [Seurat 教程](https://satijalab.org/seurat/articles/pbmc3k_tutorial.html)
的多 marker 表达展示与
[scRNAtoolVis 作者说明](https://junjunlab.github.io/scRNAtoolVis-manual/jjdotplot.html)
的 marker 分组组织。采用信息组织思路，由本项目实现固定结果表绘图，
没有复制第三方脚本或运行 Seurat 分析后端。合成示例只验证绘图和输入约束，
不证明这些基因对某个真实研究具有特异性，也不构成文章接收判断。
