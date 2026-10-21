# v0.12：来源交接与同对象联动检查

本轮扩展现有画法的检查和调用方式，不增加分析算法，不替换 42 个升级配方或三维、体渲染、轨迹动画。

<a id="handoff"></a>

## 从 BioResearchWorkbench 接收冻结结果

生产端 `research_quality.prepare_figure_handoff` 绑定一份明确选择的 TSV、FigureSpec、独立单位、contrast、方法／参考版本、QC、执行来源和位置明确的证据。详细参数见 [BioResearchWorkbench 的合同说明](https://github.com/BoteXu/BioResearchWorkbench/blob/v2.16.0/CONNECTED_FIGURES.md)。两个项目使用同一份原创标准库合同实现。

实际可调用示例：[完整 JSON](../assets/connected-examples/handoff/figure-handoff.json)、[准确输入](../assets/connected-examples/handoff/frozen.tsv)。它复用已发布的 96 个三维合成对象，声明 `frozen_results_supplied`，没有虚构服务器完成记录。

从 skill 根目录运行：

```sh
python scripts/workbench.py handoff-plan --handoff assets/connected-examples/handoff/figure-handoff.json --output outputs/handoff-plan.json
python scripts/workbench.py render --plan outputs/handoff-plan.json --output outputs/handoff-render
```

`handoff-plan` 会核验当前表格字节／形状、整体元数据绑定、同一上下文的 QC、执行状态、FigureSpec 与实际绘图器。render 再次检查输入、交接与源码；变更后须准备新计划。提交、未知状态、旧 QC 或变更字节均不能冒充当前可用。保持执行回执的来源审查，哈希不认证调度器或科学真实性。

此交接最大 5 MiB、20,000 行、250 列，面向选定绘图摘要。大矩阵、原始数据和科研计算继续使用既有服务器流程。单图交接不能代替全套分析结果的完整性、方法或科学验收。

<a id="linked-views"></a>

## 同对象的离线联动视图

[直接打开实际示例](../assets/connected-examples/index.html)：48、96、144 个对象，以及 96 对象双列自定义布局。原始三维图仍保留；这里用 XY、XZ、YZ 互补投影检查遮挡和共同身份。每行对应同一个明确对象，不按近似标签合并。

从 skill 根目录复制现有请求，或直接重放：

```sh
python scripts/workbench.py linked-views --request assets/connected-examples/medium/request.json --output outputs/linked-medium
python scripts/workbench.py linked-views --request assets/connected-examples/custom/request.json --output outputs/linked-custom
```

新目录包含 `index.html`、完整 `input.tsv`、可重放 `request.json` 和完整性记录。浏览器不需要服务、令牌或网络，可点击／键盘选中对象、按组显示、按 ID 高亮、翻阅完整寄存表，并导出对齐 SVG。SVG 保留当前显示／选中状态、图例、轴和范围说明；输入仍保留所有对象。

| 请求字段 | 必需含义 |
|---|---|
| schema_version | 整数 1 |
| title、subtitle | 明确对象和读图问题，不把交互当作分析证据 |
| input | path 与准确 sha256，一份 TSV，最大 5 MiB、5,000 个对象 |
| id_column、group_column | 唯一、非空的共享对象 ID 和明确组别；不同模态要先有已审查的一一对应 |
| views | 2–6 个对象，各有唯一 id、title、x、y、x_label、y_label；标签写明单位 |
| colors | 对所有实际组别明确命名、固定十六进制颜色；最多 20 组 |
| context | independent_unit、scope、missingness 文本，以及 synthetic 布尔值 |
| layout | columns=`auto`／1／2／3，width_px=700–2200，panel_height=240–560；视口变窄时适应布局 |

可将 x/y 换成已经提供的嵌入、匹配模态或 marker 数值列。它不会配准不同模态、建立细胞注释、估计 marker 特异性、拟合嵌入或计算统计相关。对象对应关系和单位必须先审查；细胞、帧和技术重复不自动成为独立生物学样本。

空值、`NA`、`NaN` 是未提供，不填零；图上显示缺失坐标对数量，寄存表保留对象。筛选不改变轴域，不丢弃隐含选中对象；在当前范围外的选择仍保留并提示。每张图的点、寄存表与选择共享同一 ID。完整表格分页只改变显示，不裁掉输入。

## 科学设计来源与采用边界

SciSpace 帮助定位 [Vitessce 原始论文](https://www.nature.com/articles/s41592-024-02436-x)；出版方确认其 2024 年在线发表、2025 年卷期。我们采用共享对象轴、协调选择和稳定身份颜色，独立编写轻量 HTML/SVG 检查器。没有复制其图像、代码或声称具备同等大规模多模态加载能力。图形互补性先于增加面板数量。

[Workflow Run RO-Crate](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309210) 区分预期流程和实际运行来源。本项目采用这个来源分层原则，但 FigureHandoff 是自有契约，尚不是 RO-Crate 标准实现。SciSpace 的平台出版类型、生成摘要和“局限性未提到”均不作为原文事实；继续复核原始论文和覆盖范围。

## 验收范围

标准库合同测试覆盖变更输入、旧 QC、未知执行、重复身份、错误布局和缺失坐标；实际浏览器检查覆盖选中联动、键盘、固定轴域、完整分页、SVG 与桌面／平板／窄屏。浏览器验收和文件哈希不能批准美观，需查看这四种实际示例及其选择、布局和导出图，再记录最终图像哈希。合成图只验证绘图，不建立科研结果。
