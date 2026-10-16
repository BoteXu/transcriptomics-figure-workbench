# 科研数据绘图工作台 · Transcriptomics Figure Workbench

按**数据结构与想表达的问题**选择图形，保留原始数值与参考图的视觉语言，用一套课题色卡和字体统一所有图。可安装为 Codex skill，也可以直接使用 Python/R 的冻结结果表绘图器。

本版为 **v0.4.0**。25 个软件包/方法入口现已全部提供重新设计的实际示例（重画8张、补齐17张），并可在 Studio 内直接预览。新版重构为统一的“选择画法 → 输入预检 → 绘图 → 外观修改 → 独立验收”工作流。保留历史 Python/R 接口、260 个稳定示例和全部已有组合。

[打开六种重设计与六种新增图预览](examples/aesthetic-v030/index.html) · [重构设计与输入要求](skills/transcriptomics-figure-workbench/references/aesthetic-rebuild.md) · [打开新版 Figure Studio](examples/studio/index.html) · [统一工作流](skills/transcriptomics-figure-workbench/references/workbench-v030.md) · [自动生成的能力与参数目录](skills/transcriptomics-figure-workbench/references/renderer-directory.md)

| 升级 | 实际实现 |
|---|---|
| 架构 | 121 个 Python 绘图函数统一登记；79 个固定别名；只在选定绘图时加载依赖 |
| 输入 | 一个 FigureSpec 保存数据、参数、课题主题和来源；变动使旧计划失效 |
| 外观 | 论文、紧凑、报告、大字四种字号层级，复用15套现有色卡与固定分组颜色 |
| 交互 | 离线 SVG 导入、字体/字号预览、修改前后比较、可拖动组图草案与重绘配置 |
| 导出 | PDF/SVG、300或600 DPI PNG、可选TIFF、准确绘图表和来源记录；完整输出后才发布目录 |
| 验收 | 文件检查、真实视觉检查、科学复核分别记录；改动导出后旧视觉验收失效 |

## v0.3 保留的重设计与补充

原八张接口测试图未通过美观验收，保留为机械测试。默认版式重新设计：减轻标题、正文用深色、移除碎片底纹、排名仅用整数刻度、图例放到数据区外，配对点用同对共用的横向偏移减少遮挡且不移动Y值。新增模板在导出前阻断文字越界和相互遮挡。

- **重画六种模式：** 火山、森林、配对变化、ROC、排名轨迹、连续矩阵。
- **新增六个入口：** 面积马赛克、精确计数方格、地平线时间序列、时间连线散点、双向条形、基因组降雨。
- **实际交付：** 12张合成示例，每张有PNG、SVG、PDF、准确表格、来源和重绘配置；逐图意见可留在本机并导出。

[逐图查看并记录意见](examples/aesthetic-v030/index.html) · [美观自检记录](docs/aesthetic-self-review-v030.md)

![本轮六种补充画法](docs/new-drawing-modes-v030.jpg)

## v0.4 软件包专项图全面补齐

**25 / 25 个入口都有实际导出**，使用14套绘图规则。GSEA单通路/叠加/分面、NES、leading edge、ORA、ridge/cnet/emap、GSVA、DESeq2、limma、MSstats、Seurat/Scanpy、WGCNA、CellChat、decoupleR、PROGENy、生存和ROC均有对应示例。

[打开全部25张新示例](examples/package-v040/index.html) · [设计与参考来源](docs/package-styles-v040.md) · [逐张自检记录](examples/package-v040/self-review.json)

每张均有 PNG / PDF / SVG、准确绘图 TSV、可复用 FigureSpec 和来源回执。示例数据为原创建模展示夹具，未运行上游生物信息学分析。参考了实际浏览过的 GseaVis、scCustomize、survminer 图例，重做比例、标注、图例、分组条带与色阶；没有复制或重新分发参考图。美观自检不代表每个用户的审美偏好，也不保证换入任意数据后无需调整。

![新版专项图选览](docs/package-styles-v040.jpg)

Studio 选择“软件包 / 方法专用入口”后直接显示对应示例，可打开矢量图、数据与重绘配置。原来的8张专项示例与400张完整图库继续保留。

## 按软件包 / 方法进入，含GSEA专项

新增 **25 个专用入口**：enrichplot/fgsea、clusterProfiler、GSVA、DESeq2、limma、MSstats、Seurat/Scanpy、WGCNA、CellChat、decoupleR/PROGENy、survminer和pROC的冻结结果可按方法选择字段与参数。它们复用实际绘图器，不在本机运行原软件包。

GSEA现有专门的单通路、正负曲线、同轴叠加、分面、NES对比和leading-edge成员图；ORA独立提供气泡和棒棒糖图。**8张新增专项示例已实际绘制**，与原400项全图谱分开列出。

[8张GSEA/ORA专项预览](examples/method-v030/index.html) · [专用入口、字段与调用方法](skills/transcriptomics-figure-workbench/references/package-method-entries.md)

## 全图谱升级与逐张自检

**400 个最终导出已逐张查看并绑定图像哈希**：260 个历史主图、32 个辅助面板、88 个横纵或替代排版、8 个 QC/DE 图、12 个重设计和新增示例。其中 274 个独立导出、126 个组合导出。这个数量包含变体，不是 400 种新算法。

[打开 400 项逐图检查版](examples/gallery/publication-v030/index.html) · [完整总览 PDF](examples/overview/full-atlas-v030.pdf) · [逐项哈希与自检记录](examples/gallery/publication-v030/review-index.json) · [全图谱改动说明](docs/full-atlas-review-v030.md)

统一了标题层级、深色正文、图例区、留白和紧凑来源标识；对遮挡、标签、矩阵轨道和结构图外框逐项修正。所有历史原图和源表仍保留。三张蛋白图整理原有公共坐标渲染的画框，没有重新计算结构。极宽组合以原分辨率分块导出再拼接，避免浏览器纹理边界导致右侧内容重复。

本轮视觉自检针对实际 PNG；关联 SVG/PDF 做文件和结构检查，未逐页进行 PDF 像素对照或纸张打样。大型横纵组合保留原物理字号，需要按目标版心重新取舍面板和检查。合成演示不代表真实研究的科学验收。

Studio 新增“整理版式”入口：在冻结 SVG 上整理文字和留白，提供修改前后预览及未验收记录，不重新拟合结果。Studio 不启动常驻服务，不上传文件。已有导出记录可以绑定SVG哈希；未绑定的配置不能当作图形来源证明。SVG文字预览与最终重绘分别标记，组图草案不冒充最终排版。

![Figure Studio 实机界面](docs/studio-desktop-v030.png)

### 继承的 v0.2.5 内容

v0.2.5 增量：新增八种冻结 QC / DE 模式；逐项审查用户提供的转录组绘图脚本并复用既有图形，详见 [代码审查与输入契约](skills/transcriptomics-figure-workbench/references/qc-de-article-review.md) 和 [增量预览](examples/qc-de/index.html)。原有 v0.2.4 内容保留：新增剪接连接、精细定位PIP、校准与决策评价、调控活性/贡献、通路冗余、网络稳定性和动力学结果模式；补充序列字母堆叠、接触矩阵/轨道、枝长树、切片叠加、影像棋盘与差值；同时修正流线数量、矩阵/组别对齐、点阵通道对应与导出版式。名称保留历史兼容性；支持的数据表达已经扩展至多组学、统计结果、关联网络、模型解释与计算生物学。

矩阵入口不再把热图、点图、混淆矩阵、关联矩阵和组合面板的行列写死：支持长表和明确列出的宽表，任意行列数量、行列字段名、完整显示顺序和别名。行名默认全部保留，长标签可换行并自动增加边距；真实缺失单元必须显式使用掩膜模式，不会被当成零。详见 [矩阵输入说明](skills/transcriptomics-figure-workbench/references/matrix-input.md)。

[下载安装包](https://github.com/BoteXu/transcriptomics-figure-workbench/releases/latest) · [去重画法与组合PDF](examples/overview/visualization-overview.pdf) · [去重示意长图](examples/overview/visualization-overview.jpg) · [通用画法总览](examples/overview/general-patterns.jpg) · [数据需求索引](examples/overview/index.tsv)

![通用画法总览](examples/overview/general-patterns.jpg)

## 完整内容

| 内容 | 数量与含义 |
|---|---|
| 主目录 | 98 个画法与组合：72 个通用表达入口、26 个组合入口；另有15套色卡、3个结构示例和1个附表入口 |
| 保留来源 | 260 个稳定编号；旧244个PNG/PDF原字节保留；包含42张实际组合、15套色卡、3个公共坐标结构示例 |
| Python 绘图函数 | 121；28个历史R对应函数另行保留，函数数不等于入口数 |
| 历史 R 对应函数 | 28；不宣称所有 Python 新功能都有 R 对应 |
| 示意图总览 | 主总览只放各入口的唯一代表；[260个来源档案](examples/overview/source-archive-v021.pdf)另列重复与历史示例 |
| 横纵排版 | [42张组合的84种完整布局](examples/gallery/layout_review/index.html)，另有切片/影像对照横纵模式 |

默认目录按视觉编码去重；数据标签、色卡、坐标尺度和重复分面不增加画法数量。T14/T18、P21a/P21b、M02/M03等归入通用入口，亚群与marker、网络与矩阵等组合变体放在入口内选择。原编号、输入契约、导出文件和浏览器意见键完整保留。

这些数量是不同维度的清单，不能相加当作算法数。同类柱状图、折线图、热图合并到通用画法，保留有意义的变体与组合。雨云图、带堆积边际分布的火山图、精细森林图、相关性矩阵/网络、亚群与 marker 联合视图都保留。

每个预览说明需要什么数据、能表达什么、怎么画、哪些审美参数可调，以及使用边界。全部图片是自行生成的示例；除明确标注的公共蛋白坐标外，数据用于合成演示。原始参考图片和私人研究结果不随包分发。

## 本版增量和完整检查

[按分析结果查看模式与组合](examples/gallery/analysis_modules.html) · [模块的数据契约与路线](skills/transcriptomics-figure-workbench/references/analysis-modules-router.md)

[本版14个新模式与2个组合示意](examples/overview/new-result-modes-v024.jpg)

本版另新增9个结果模式和2个明确组合：剪接覆盖/连接/异构体、多信号变异PIP、校准人数、决策净获益、调控评分、通路共享矩阵、网络参数敏感性、独立轨迹分块和有符号贡献瀑布。矩阵、曲线、校准与评分沿用现有画法，仅剪接和瀑布新增编码入口。K41连接校准与决策评价，K42把一个明确样本/调控因子的矩阵值与完整贡献总量对应；所有panel独立保存。

基于 Biomni 当前目录和实际工具规划，新增5个冻结结果表绘图器。矩阵、树和叠加图归入已有入口的模式，字母高度与棋盘交替设为新入口，不把相似变体冒充新方法。每个示例保存输入表、参数、PNG、PDF、SVG及来源记录。[新增方式与数据契约](skills/transcriptomics-figure-workbench/references/biomni-visualization-router.md)。

流线逐连接保留真实权重，零量不画最小宽度；点阵面积与颜色按同一单元对应；活动矩阵数量/分组条共享单元中心，已有树顺序必须匹配矩阵。图例进入独立区域，合成说明不覆盖标题。完整panel横纵排版与数据共轴分别声明，后者核对范围、尺度和导出几何。[对齐与流线规则](skills/transcriptomics-figure-workbench/references/alignment-and-flow.md)。

本轮补充成员→条目曲线与评分气泡、双量值三角格、矩形/环形层次树、同对象可加量堆叠，以及4张集合/通路/网络/模块组合。14个独立panel都保存表格、参数与矢量导出。[WGCNA绘图路由](skills/transcriptomics-figure-workbench/references/wgcna-visualization-router.md)列出诊断、树、模块性状、TOM/adjacency、MM/GS及模块网络需要的数据；不执行这些上游分析。

新增富集点阵、GO成员效应环形、成员弦/矩阵/重叠网络、ECDF/QQ、协变量平衡、Bland–Altman、已有生存与个体随访、分析规格、已有向量场、三元组成、全局/局部关联轨道、漏斗、数量层级、嵌套区间与四种冻结模型诊断。

课件相关多组学增量包括：跨层效应、因子解释量与载荷、同对象多视图、特征相关圆、注册空间身份/分子叠加、质谱镜像与色谱、基因组候选连接、通路底图和同位素组成。已有矩阵、曲线和堆积画法直接复用，不按应用场景重复计算为新方法。

[完整逐项检查](skills/transcriptomics-figure-workbench/references/consolidation-audit.md) · [新画法数据契约与原始文档](skills/transcriptomics-figure-workbench/references/methods-extension-router.md) · [课件多组学路由](skills/transcriptomics-figure-workbench/references/course-visualization-router.md) · [新增组合](skills/transcriptomics-figure-workbench/references/extended-combinations.md)

## 安装为 Codex skill

任选一种方式：

1. 下载 Release 中的 `transcriptomics-figure-workbench-v0.3.0.zip`，解压后将其中的 `transcriptomics-figure-workbench` 文件夹放入你的 Codex skills 目录（默认 `~/.codex/skills/`）。若已有同名 skill，先备份，再明确选择替换；不要直接覆盖私人项目配置。
2. 在 Codex 中使用 skill-installer，指定仓库 `BoteXu/transcriptomics-figure-workbench` 和路径 `skills/transcriptomics-figure-workbench`。
3. 克隆仓库，只复制 `skills/transcriptomics-figure-workbench/` 至自己的 skills 目录。

新会话中调用 `$transcriptomics-figure-workbench`，例如：

> 我有每个样本的分组、指标值和独立单位ID。先说明适合的图形与组合，用课题指定色卡和字体绘制雨云图及效应区间图；保留单独panel，图例不要遮挡数据。

仅安装 skill 不会安装依赖、调用服务器、分析数据或上传结果。

## 查看新版 Studio 与完整图谱

新版可直接打开仓库中的 `examples/studio/index.html`；安装版可以让 Codex 运行 `scripts/workbench.py studio --output figure-studio.html` 生成单文件离线界面。完整历史图谱继续保留。

## 传统图谱入口

克隆或下载仓库后，直接打开 `examples/gallery/index.html`，可按数据/表达搜索，切换同类变体、放大、查看单独图和组合、打开 TSV/参数/元数据，并按稳定编号记录审美意见。

需要通过本机浏览器服务查看时，在仓库目录运行：

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory .
```

然后访问 `http://127.0.0.1:8000/examples/gallery/`。审美意见仅保存在你的浏览器中，可以导入/导出 JSON；没有远程上传。总览、说明与示例资产均来自当前公开仓库。

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

新增固定适配器：`render_frozen_table.py ADAPTER --input INPUT.tsv --style STYLE.json --meta META.json --theme PROJECT_THEME.json --output NEW_OUTPUT_DIRECTORY --id FIGURE_ID`。57个注册适配器保持对象字符串与数值字段分离，不调用任意模块或执行科学分析。

42个组合均有已保存的 [布局与组件注册表](skills/transcriptomics-figure-workbench/references/combination-recipes.json)：`compose_catalog_examples.py --gallery examples/gallery --all --output NEW_OUTPUT_DIRECTORY` 可重建全部组合。组合的32个辅助panel也保存了独立导出、输入表、设置和 `render_saved_components.py` 重绘入口。图库中的“单独Panel”链接分别打开各组件。

最小依赖版本是声明范围，不代表每个组合都已在所有版本验证。实际发布检查见 [v0.2.4检查记录](docs/release-validation-v024.md)，历史范围见 [release-validation.md](docs/release-validation.md)。

## 科研使用边界

使用已经审核的结果表与坐标，声明独立单位、单位、比较、分母、排除规则、缺失值和不确定性。绘图不默默重做差异分析、统计检验、富集、聚类、轨迹、SHAP、PCA 或结构预测。细胞、点位和模拟帧不能自动当作独立样本。

图例与数据各占独立空间；调整字体、长标签或图幅后重新看实际导出。导出器保留精确 TSV、PNG/PDF/SVG 和来源/设置哈希，拒绝不匹配的输入与覆盖写入。复杂原生对象、极大规模、平台字体及特定期刊尺寸仍需目标环境验收。合成示例、软件检查和漂亮布局都不能证明科学结论。

## 许可与来源

原创实现按 [MIT](LICENSE) 发布；外部软件、色卡、论文、公共坐标和字体保持各自许可与归属。详见 [THIRD_PARTY.md](THIRD_PARTY.md)。私人项目画像、本机绝对路径、原始参考图片、浏览器审美意见和运行凭据不在公开包中。

---

**English:** A Codex skill for scientific figures from frozen results. The primary directory contains 72 drawing families and 26 composition entries. All 260 source IDs remain accessible, including 42 compositions, 15 color cards and 3 public-coordinate structure examples. The source-derived registry lists 120 Python plot functions and 78 fixed aliases; 28 historical R counterparts remain. Analysis-result modules, Biomni-discovered views, weight-conserving flows, exact-index tracks, explicit shared-axis composition and 84 horizontal/vertical arrangement alternatives extend the workbench. Upstream analysis runtimes and native/R backend parity are not implied by the static rendering checks.
