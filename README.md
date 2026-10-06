# 科研数据绘图工作台 · Transcriptomics Figure Workbench

按**数据结构与想表达的问题**选择图形，保留原始数值与参考图的视觉语言，用一套课题色卡和字体统一所有图。可安装为 Codex skill，也可以直接使用 Python/R 的冻结结果表绘图器。

当前版本 **v0.2.3**。名称保留历史兼容性；支持的数据表达已经扩展至多组学、统计结果、关联网络、模型解释与计算生物学。

矩阵入口不再把热图、点图、混淆矩阵、关联矩阵和组合面板的行列写死：支持长表和明确列出的宽表，任意行列数量、行列字段名、完整显示顺序和别名。行名默认全部保留，长标签可换行并自动增加边距；真实缺失单元必须显式使用掩膜模式，不会被当成零。详见 [矩阵输入说明](skills/transcriptomics-figure-workbench/references/matrix-input.md)。

[下载安装包](https://github.com/BoteXu/transcriptomics-figure-workbench/releases/latest) · [去重画法与组合PDF](examples/overview/visualization-overview.pdf) · [去重示意长图](examples/overview/visualization-overview.jpg) · [通用画法总览](examples/overview/general-patterns.jpg) · [数据需求索引](examples/overview/index.tsv)

![通用画法总览](examples/overview/general-patterns.jpg)

## 完整内容

| 内容 | 数量与含义 |
|---|---|
| 主目录 | 92 个画法与组合：68 个通用表达入口、24 个组合入口；另有15套色卡、3个结构示例和1个附表入口 |
| 保留来源 | 244 个稳定编号；旧236个PNG/PDF原字节保留；包含40张实际组合、15套色卡、3个公共坐标结构示例 |
| Python 绘图函数 | 100；28个历史R对应函数另行保留，函数数不等于入口数 |
| 历史 R 对应函数 | 28；不宣称所有 Python 新功能都有 R 对应 |
| 示意图总览 | 主总览只放各入口的唯一代表；[244个来源档案](examples/overview/source-archive-v021.pdf)另列重复与历史示例 |

默认目录按视觉编码去重；数据标签、色卡、坐标尺度和重复分面不增加画法数量。T14/T18、P21a/P21b、M02/M03等归入通用入口，亚群与marker、网络与矩阵等组合变体放在入口内选择。原编号、输入契约、导出文件和浏览器意见键完整保留。

这些数量是不同维度的清单，不能相加当作算法数。同类柱状图、折线图、热图合并到通用画法，保留有意义的变体与组合。雨云图、带堆积边际分布的火山图、精细森林图、相关性矩阵/网络、亚群与 marker 联合视图都保留。

每个预览说明需要什么数据、能表达什么、怎么画、哪些审美参数可调，以及使用边界。全部图片是自行生成的示例；除明确标注的公共蛋白坐标外，数据用于合成演示。原始参考图片和私人研究结果不随包分发。

## 本版增量和完整检查

本轮补充成员→条目曲线与评分气泡、双量值三角格、矩形/环形层次树、同对象可加量堆叠，以及4张集合/通路/网络/模块组合。14个独立panel都保存表格、参数与矢量导出。[WGCNA绘图路由](skills/transcriptomics-figure-workbench/references/wgcna-visualization-router.md)列出诊断、树、模块性状、TOM/adjacency、MM/GS及模块网络需要的数据；不执行这些上游分析。

新增富集点阵、GO成员效应环形、成员弦/矩阵/重叠网络、ECDF/QQ、协变量平衡、Bland–Altman、已有生存与个体随访、分析规格、已有向量场、三元组成、全局/局部关联轨道、漏斗、数量层级、嵌套区间与四种冻结模型诊断。

课件相关多组学增量包括：跨层效应、因子解释量与载荷、同对象多视图、特征相关圆、注册空间身份/分子叠加、质谱镜像与色谱、基因组候选连接、通路底图和同位素组成。已有矩阵、曲线和堆积画法直接复用，不按应用场景重复计算为新方法。

[完整逐项检查](skills/transcriptomics-figure-workbench/references/consolidation-audit.md) · [新画法数据契约与原始文档](skills/transcriptomics-figure-workbench/references/methods-extension-router.md) · [课件多组学路由](skills/transcriptomics-figure-workbench/references/course-visualization-router.md) · [新增组合](skills/transcriptomics-figure-workbench/references/extended-combinations.md)

## 安装为 Codex skill

任选一种方式：

1. 下载 Release 中的 `transcriptomics-figure-workbench-v0.2.3.zip`，解压后将其中的 `transcriptomics-figure-workbench` 文件夹放入你的 Codex skills 目录（默认 `~/.codex/skills/`）。若已有同名 skill，先备份，再明确选择替换；不要直接覆盖私人项目配置。
2. 在 Codex 中使用 skill-installer，指定仓库 `BoteXu/transcriptomics-figure-workbench` 和路径 `skills/transcriptomics-figure-workbench`。
3. 克隆仓库，只复制 `skills/transcriptomics-figure-workbench/` 至自己的 skills 目录。

新会话中调用 `$transcriptomics-figure-workbench`，例如：

> 我有每个样本的分组、指标值和独立单位ID。先说明适合的图形与组合，用课题指定色卡和字体绘制雨云图及效应区间图；保留单独panel，图例不要遮挡数据。

仅安装 skill 不会安装依赖、调用服务器、分析数据或上传结果。

## 查看完整图谱

克隆或下载仓库后，直接打开 `examples/gallery/index.html`，可按数据/表达搜索，切换同类变体、放大、查看单独图和组合、打开 TSV/参数/元数据，并按稳定编号记录审美意见。

需要通过本机浏览器服务查看时，在仓库目录运行：

```sh
python -m http.server 8768 --bind 127.0.0.1 --directory .
```

然后访问 `http://127.0.0.1:8768/examples/gallery/`。审美意见仅保存在你的浏览器中，可以导入/导出 JSON；没有远程上传。总览、说明与示例资产均来自当前公开仓库。

## 统一课题颜色和字体

一个课题使用一个 `project_theme.json`：指定色卡、固定“身份→颜色”映射、字体与字号层级、连续色阶的范围和中心。调整色卡/字体后用同一输入表重绘，检查图例、色标、标题与内容之间的间距。颜色和字体替换不得改变数值、阈值、坐标、区间、点面积或矩阵顺序。

[15 套色卡](skills/transcriptomics-figure-workbench/references/reference-palette-guide.md)包含 7 套原海报色值与 8 套注明来源的 Tol/ColorBrewer 色卡。仅明确标题为“科研配色方案”的原海报登记为原始色卡。示例 C06/Arial 是演示配置，实际课题由用户选择；目标机器必须有所选字体。原生结构与 R 后端的自动替换范围以文档声明为准。

全部15套可按C01–C15编号查找：13套类别卡、C14顺序卡、C15分歧卡。主题工具 `--list-cards` 完整列出；`--card C06 --sequential-card C14 --diverging-card C15` 明确三种颜色角色。只换字体保留已选连续色阶。

## 直接绘图与依赖

核心 Python 冻结表适配器使用 numpy、pandas、matplotlib；需要 PDF/灰度检查或组合时另外使用 Pillow/PyMuPDF。在自己选择的环境中**明确安装**依赖即可；本 skill 不自动安装软件：

```sh
python -m pip install -r requirements.txt
# 可选的导出检查和 PDF 组合
python -m pip install -r requirements-review.txt
```

例如重绘 R05 相关性椭圆示例，在仓库目录执行（输出目录应为新的空目录）：

```sh
python skills/transcriptomics-figure-workbench/scripts/render_reference_table.py R05 --input examples/gallery/figures/R05/R05.tsv --style examples/gallery/figures/R05/R05.style.json --meta examples/gallery/metadata/R05.json --output outputs/R05
```

整批独立 panel 使用 `render_project_panels.py --manifest INPUT_MANIFEST --theme PROJECT_THEME --output NEW_OUTPUT_DIRECTORY`；输入结构见 [课题样式说明](skills/transcriptomics-figure-workbench/references/project-style.md)。组合使用 `compose_panels.py`，兼容关系见 [组合路由](skills/transcriptomics-figure-workbench/references/combinations-router.md)。R 基础函数见 [代码配方](skills/transcriptomics-figure-workbench/references/code-recipes.md)；原生蛋白结构使用已有结构查看器或 PyMOL，并明确来源、链与残基。

新增固定适配器：`render_frozen_table.py ADAPTER --input INPUT.tsv --style STYLE.json --meta META.json --theme PROJECT_THEME.json --output NEW_OUTPUT_DIRECTORY --id FIGURE_ID`。43个注册适配器保持对象字符串与数值字段分离，不调用任意模块或执行科学分析。

40个组合均有已保存的 [布局与组件注册表](skills/transcriptomics-figure-workbench/references/combination-recipes.json)：`compose_catalog_examples.py --gallery examples/gallery --all --output NEW_OUTPUT_DIRECTORY` 可重建全部组合。组合的32个辅助panel也保存了独立导出、输入表、设置和 `render_saved_components.py` 重绘入口。图库中的“单独Panel”链接分别打开各组件。

最小依赖版本是声明范围，不代表每个组合都已在所有版本验证。实际发布检查和历史测试范围见 [release-validation.md](docs/release-validation.md)。

## 科研使用边界

使用已经审核的结果表与坐标，声明独立单位、单位、比较、分母、排除规则、缺失值和不确定性。绘图不默默重做差异分析、统计检验、富集、聚类、轨迹、SHAP、PCA 或结构预测。细胞、点位和模拟帧不能自动当作独立样本。

图例与数据各占独立空间；调整字体、长标签或图幅后重新看实际导出。导出器保留精确 TSV、PNG/PDF/SVG 和来源/设置哈希，拒绝不匹配的输入与覆盖写入。复杂原生对象、极大规模、平台字体及特定期刊尺寸仍需目标环境验收。合成示例、软件检查和漂亮布局都不能证明科学结论。

## 许可与来源

原创实现按 [MIT](LICENSE) 发布；外部软件、色卡、论文、公共坐标和字体保持各自许可与归属。详见 [THIRD_PARTY.md](THIRD_PARTY.md)。私人项目画像、本机绝对路径、原始参考图片、浏览器审美意见和运行凭据不在公开包中。

---

**English:** A Codex skill for scientific figures from frozen results. The deduplicated primary directory contains 68 drawing families and 24 composition entries, with meaningful modes inside each entry. All 244 source IDs remain accessible, including 40 saved compositions, 15 attributed color cards and 3 native public-coordinate examples. Python saves 100 plot functions; 28 historical R counterparts remain. Fourteen new linked-display panels add membership curves, two-metric triangle cells and hierarchy tracks, with WGCNA-specific input guidance. Plotting, synthetic tests and visual quality do not establish scientific validity.
