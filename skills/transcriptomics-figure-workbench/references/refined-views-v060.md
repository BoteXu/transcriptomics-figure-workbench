# 精修绘图与完整阅读版

## 精修入口

别名 `refined` 调用 `plot_refined_views(data, theme, view=..., contract=..., options=...)`。完整 FigureSpec 和可运行示例在 [精修图库](../assets/refined-gallery/index.html)。`contract` 沿用冻结结果的来源、单位、分母、数值、选择、缺失和区间定义。未知选项直接拒绝。

| view | 必需字段 / options | 约束 |
|---|---|---|
| `gsea_strip` | 使用既有 GSEA `kind/pathway/rank/value/gene/leading_edge/NES/padj/set_size` 长表；`curve_order, ranked_universe, metric_label, contrast, gene_set_version, line_encoding, title` | `line_encoding` 为 `rank_metric` 或 `pathway`；渐变仅单通路；完整排名、曲线、hit、metric 必须一致；细灰底线确保渐变零点可见；不计算 ES/NES/FDR |
| `ribbon` | `series,x,estimate,lower,upper`，可选成对 `inner_lower,inner_upper`；`series_order, interval_definition, x_label, y_label, title, subtitle` | 1–4 条有序曲线；不排序修复、插值、平滑或拟合；内外界必须真实供应并嵌套 |
| `score_shift` | `feature,score_a,score_b,delta,lower_delta,upper_delta`；`feature_order,label_a,label_b,score_label,difference_label,interval_definition,title,subtitle` | 最多24个唯一特征；检查供应的 delta 与 B−A 一致；差值区间与原始得分分开；不能推断生物学配对 |
| `association` | `record_type,r,p`；correlation 行用 `a,b`，mantel 行用 `specimen,target`；`variable_order,specimen_order,correlation_label,title,subtitle` | 完整两两组合和完整集合×变量表；r 在[−1,1]、p 在[0,1]；两种统计量独立色条；原始 p 保留表中，本视图不以颜色或星号编码 p |

`design` 已增加 `curves`、`score_comparison`、`associations` 三类比较结构，共14类；`enrichment` 在供应完整排名时优先考虑精简轨道。推荐只检查字段与上下文，精确 renderer 参数仍需 FigureSpec 和 preflight 验证。

## 阅读版命令

```text
python scripts/workbench.py reading-plan --index <figure-index.json> --root <selected-root> --output <fresh-plan.json>
python scripts/workbench.py reading-export --plan <plan.json> --output <fresh-reading-directory>
```

索引的每条记录需有唯一 `id`、`assets` 和 `sha256`（`pdf/png/svg/meta`），组合额外列明 `components`，只指向包含在索引里的独立图。路径必须在选定目录内，全部源文件哈希必须一致。计划含本机路径，应私下保存；公开交付只使用脱敏后的阅读索引。

- A4 阅读宽度100–180 mm；正文最小目标6–12 pt，默认178 mm与7.5 pt。每卷最多90张源图、总数最多500。
- 对每张源 PDF 只做统一缩放；需要时分为有重叠的区域，并提供完整概览和位置小地图。所有区域被覆盖，不改变局部轴比例、原始坐标或字形比例。
- 组合保留全图概览，并链接独立图的卷号/页码。独立图可能是更新版本，历史组合不自动声称已采用新配色。
- 字号检测使用页面中部8%–92%高度内的全部可测文本，不取低分位替代最小值。轮廓字/栅格字标记为未评估；页眉页脚另行排版。
- 压缩前后校验解码后的 PDF 绘制指令一致，保留矢量与文本。压缩不是视觉验收。
- 增加 PDF 功能需已有 `pypdf` 与 `reportlab`；它们在选定阅读导出时加载。索引和计划命令不加载科研分析环境。

阅读版用于核对密集内容。最终论文图仍须依据实际版心重排面板、控制选择范围，并单独检查字号和视觉效果。
