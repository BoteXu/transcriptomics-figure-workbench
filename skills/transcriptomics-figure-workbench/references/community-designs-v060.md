# 社区方案的选择与来源

优秀的画法可以来自作者博客、GitHub、教学文章、公众号或软件包示例。是否官方不作为美观排名。先确认正文和实际图例可读，再比较层级、配色、图例、信息密度和目标尺寸；只采用与输入字段兼容的表达。

## 本轮核查与采用

| 来源与原作者 | 实际查看范围 | 工作台采用 | 边界 |
|---|---|---|---|
| [GseaVis manual / JunJun](https://junjunlab.github.io/gseavis-manual/basic-usage.html#new-style-graphic) | 作者文档及新风格实际图 | REF01 渐变 ES、细命中线、排名色带；REF02 多通路对齐分面 | 原创 Python 实现；完整 ES、hit、metric、NES/FDR 均由输入提供；没有运行 GseaVis |
| [Cédric Scherer / Mario Kart doubledumbbell](https://r-graph-gallery.com/web-lollipop-plot-with-r-mario-kart-64-world-records.html)；[作者代码](https://github.com/z3tt/TidyTuesday/blob/master/R/2021_22_MarioKart.Rmd) | 教程、作者代码页和最终实际图 | REF04 细灰连接、对齐行、独立差值区间 | 使用工作台 P22 的六个合成特征；不复制代码、字体、图片或数据；特征相同不证明生物学配对 |
| [ggprism / Charlotte Dawson](https://csdaw.github.io/ggprism/articles/web-only/ex1-dose.html) | 作者教程及剂量图实际图 | 采用清楚的形状、轴线和图例层级原则 | 不整体套用粗体或拟合曲线；没有运行剂量模型 |
| [linkET / Houyun Huang](https://github.com/Hy4m/linkET) | README 与作者 README.Rmd | REF05 将相关与 Mantel 关系改为两个对齐矩阵，减少交叉线 | 自行实现；没有采用包代码或将仓库可见性当作再分发许可；两类统计量保留独立色条 |
| [corrmorant / Roman M. Link](https://github.com/r-link/corrmorant) | 作者仓库说明 | 对称矩阵和不同区域的表达选择参考 | 没有执行原生包；并非 REF05 的代码来源 |
| [ggdist / Matthew Kay](https://mjskay.github.io/ggdist/articles/lineribbon.html) | 作者 lineribbon 文档 | REF03 细曲线与供应的区间带分层 | 仅使用供应的坐标和上下界，不估计分布、区间或平滑结果 |
| [ComplexHeatmap / Zuguang Gu](https://jokergoo.github.io/ComplexHeatmap-reference/book/a-single-heatmap.html#heatmap-split) | 作者分组切片文档 | 既有 VIS02 分组留白与注释轨道继续优选 | 不新增聚类或重新排序 |
| [ComplexUpset / Michał Krassowski](https://krassowski.github.io/complex-upset/articles/Examples_R.html) | 作者示例文档 | 多集合优先考虑对齐交集矩阵 | 参考路线；没有声称本轮新增原生包验收 |
| [ggside / Justin Landis](https://jtlandis.github.io/ggside/articles/ggside_basic_usage.html) | 作者边际图文档 | 检查主体、边际分布与图例的关系 | 已有边际图展示冻结结果；不增加新的密度估计 |
| [plotnine composition](https://plotnine.org/guide/plot-composition.html) | 官方组合文档 | 图与独立面板阅读分开交付 | 并未替换现有组合引擎 |

本轮没有复制第三方代码或参考图片，没有下载或打包第三方字体、权重和数据。若以后确需复用代码，必须单独记录文件、版本、许可、修改及再分发义务。设计思想参考与代码来源分别记录。

## 采用判断

1. 优先比较同一份冻结数据的实际图；标题好看或缩略图吸引人不足以采用。
2. 先确保含义准确，再检查配色、留白、对齐、清晰度和目标尺寸。颜色不能代替缺失的数值或假设。
3. 单通路可用渐变 ES；多通路优先分面。连续颜色的零点附近需要足够的曲线边界对比。
4. 大量网络交叉时优先提供矩阵；所有节点、边和原始统计仍保留于准确表格。
5. 大量面板提供概览、独立图和阅读 PDF。可读的分页版不使原组合自动达到论文版心要求。
6. 各方案保留原作者署名和链接。社区参考不等于原生软件包执行或科学验收。

公众号入口仍可用于搜集方案。本轮未取得新的可读公众号正文，因此没有声称整合未读正文中的代码。
