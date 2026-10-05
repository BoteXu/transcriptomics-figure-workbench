# 逐图审美调整与通用绘图增量

## 选择与修改

先看科学问题和已审核表格，再选择主图：关系用单位级散点；组间估计用点区间或分组估计柱；分类结果用计数矩阵；分布用原始点、固定分箱或已计算密度。已有图形能回答问题时直接调整；只在图形选择有实质歧义时补问用户。不要为满足某种“主图”模板增加分析、强行分面或删去阴性结果。

按稳定图号保存意见、参数和输出版本。每次集中调整用户指出的颜色、字号、线点、坐标轴、图例或位置；用户未确认的样式作为候选。颜色优先沿用项目语义；改颜色时同步所有比较图和图例。轴尺度、统计阈值、分箱、密度带宽、平滑、聚类和样本选择属于分析决策，不能当成审美参数。

多面板先用毫米确定最终画布和读图顺序；明确每个面板回答的问题。需要时给主要证据更多空间，避免重复展示同一统计量。共享图例只适用于相同含义和映射；为图例、色条、长标签预留独立空间。跨面板同尺度来自分析设计，不从照片外观推断。具体期刊尺寸要求应查当前作者指南；不要把某个模板字号当成所有期刊的要求。

## Python：可保存的参数与命名布局

`scripts/figure_design.py` 提供 `DesignSpec`、`design_for`、`apply_design`、`named_layout`、`resolve_font` 和 `audit_layout`。新图及第一次审美调整推荐先用 `apply_design(fig, design_for(fig))`：统一可读字号和最小物理尺寸，密集矩阵留出标签空间，给记录型图件的标题/脚注与演示标记分配不同区域。它返回可修改的参数，不能保证任意真实标签自动排好。原函数调用保持兼容。普通类别颜色仍通过绘图函数的 `palette` 参数传入；连续值色阶沿用对应函数的语义参数。

```python
from figure_core import plot_samples, export_figure
from figure_design import DesignSpec, apply_design, audit_layout

fig = plot_samples(reviewed_table, project_palette, 'Measured value')
spec = DesignSpec(width_mm=180, height_mm=115, label_pt=10, tick_pt=9,
                  spine_mode='minimal', grid='none', x_tick_rotation=30)
apply_design(fig, spec)
spec.write('P01_style_v2.json')  # 新路径；不覆盖旧参数
export_figure(fig, reviewed_table, 'new_output', 'P01_v2', reviewed_meta)
report = audit_layout(fig)      # 导出后标记也参与检查
```

可以用 `DesignSpec.read(path)` 复用 JSON；未知字段拒绝，不执行配置文本。字段：`width_mm/height_mm`、`font_family`、`label_pt/tick_pt/title_pt/note_pt`、`spine_width`、`spine_mode=keep|minimal|boxed`、`grid=keep|none|x|y|both`、`x_tick_rotation`、`axis_bounds`、`figure_text_positions`、`figure_text_wraps`、`legend_zone`、`legend_columns`、`legend_title_width`。

`axis_bounds` 用轴的显式 gid 或从 0 起的索引映射到 `[左,下,宽,高]` 画布比例。必须同时核对色条和辅助面板，不能只压缩主轴。`figure_text_positions` 用已有图级文字的完整内容映射到 `[x,y]`；用于给标题、脚注与合成演示标记让出空间，不改文字含义。`figure_text_wraps` 和 `legend_title_width` 仅插入可读换行，不删改词语。显式布局关闭自动布局；随后检查实际导出。

`legend_zone` 预留独立区域，搬移已有图例并保留每份图例的标题、顺序和句柄；多个图例上下排列后仍需实际检查。不要把色条误当普通图例。参数不隐藏图例、不重算比例、不归并类别。图例移位层重复调用会拒绝；从原函数重新渲染后应用新参数。

`named_layout(fig, {'main':[...], 'legend':[...], ...})` 用于空画布上的原创组合图。命名布局本身不是数据适配器；组合图仍需自己的审核输入/stamp。不要将已有矢量图拆成截图再声称保持完全可编辑。

字体仅从本机已安装字体选择。`resolve_font(preferred, text)` 检查给定字符覆盖；不自动安装。Python 调整前后比对数据图元、色阶范围、坐标尺度/范围的几何摘要，并保留精确表格哈希。检查失败时丢弃内存中的候选图，使用原函数重绘；哈希不是科学正确性证明。

## R：可选样式层

先 source `figure_core.R`，再 source `figure_design.R`。`apply_design(p, label_pt=10, tick_pt=9, grid='none', spine_mode='minimal', x_tick_rotation=30, legend_position='bottom')` 保留原输入属性并核对 `ggplot_build` 的图层数据未变。画布尺寸用原 `export_figure(width=180/25.4, height=115/25.4)`。R 不包含 Python 的 JSON 参数对象、命名轴定位、字体字形检查或自动边界审查；R 字体可用性和版面需检查真实导出。复杂 patchwork 组合继续使用原有官方路径。

## 五个新增冻结表格函数（Python 与 R）

| 函数/图号 | 必需列 | 必须声明 | 数据边界 |
|---|---|---|---|
| `plot_xy_points` / P33 普通关系散点 | unit_id, group, x, y | x/y 标签、unit_label、palette | 每个独立单位一行；不拟合回归、不计算相关或 p 值 |
| `plot_grouped_estimates` / P34 分组估计与区间 | category, group, estimate, lower, upper | y_label、interval_label、palette | 完整唯一类别×组别格；原估计和区间直接绘制；零基线保留 |
| `plot_binned_distribution` / P35 固定分箱分布 | group, left, right, count | x_label、denominator_label、palette | 非负整数、组内有序无重叠、组间相同分箱；不重新分箱或归一化，空隙不连线 |
| `plot_confusion_counts` / P36 计数混淆矩阵 | actual, predicted, count | unit_label | 完整方格、相同类别集、非负整数；行=观测，列=预测；不训练或选择阈值 |
| `plot_density_ridges` / P37 预计算山脊图 | group, x, density | x_label、density_label、palette | 同一递增 x 网格、非负密度；仅共享显示缩放，不按组独立放大；上游给出密度来源与带宽 |

区间、密度和模型预测必须已经审核；为画图临时拟合会违反本 skill 的边界。山脊图纵向位置标识类别，密度高度采用共同显示系数，不能把组间偏移当成定量 y 轴。

## 版面检查与审阅

`audit_layout` 检查绘制后的文字越界、相邻刻度重叠、标题/图级文字重叠、过小字体和字体缺字；结果始终标记 `LAYOUT_CHECKS_ONLY`。它忽略坐标范围之外未绘制的刻度，按对象去重。它不验证统计、色觉可读性、图例是否遮盖数据或审美优劣。

检查可分为五项：问题和图型是否匹配；输入/单位/分母与图元是否一致；标题/图例/尺度是否明确；实际成品是否清楚；矢量/栅格与来源记录是否完整。实际 PDF/SVG 在最终尺寸的检查单独登记。示例中的重叠、标签挤压和错用色阶是设计问题的例子，不自动等同于期刊审稿人的意见。

版本与来源见 [external-increments-20261005.md](external-increments-20261005.md)；实际验收范围见 [validation-increments-20261005.md](validation-increments-20261005.md)。

## 可复用审美图册

`python scripts/build_aesthetic_gallery.py SELECTED_GALLERY_DIRECTORY [NEW_NAME.html]` 从该目录的 `manifest.json` 创建新 HTML，拒绝覆盖已有文件。需要 `version`、`base_functions` 和 `records`。每条记录有 `id/base_id/title/category/variant/description/inputs/limits`、本地相对 `png/svg/pdf/tsv/thumbnail` 路径，以及 `png_sha256/svg_sha256/pdf_sha256/input_sha256`。可选 `baseline_svg/baseline_svg_sha256` 提供原版对照。它检查资产路径范围与文件摘要，目录中应另有完整 PDF 图册和 `qa/overview.png`。

页面支持搜索、分类、SVG 放大、两个图形并排比较、原版对照、逐图决定和笔记。导出前显示完整修改清单，支持下载或复制；清单记录图形版本、输入/图形摘要。笔记仅保存在本机浏览器，可通过文件导入迁移；不自动修改 skill、图形或服务器。不要把未确认的笔记当成已批准的默认样式。
