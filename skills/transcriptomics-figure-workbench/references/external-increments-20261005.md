# 四个来源的增量与采用边界

检索日期：2026-10-05。用户未提供链接；以下是按名称找到的原始候选，固定提交后静态审查。没有安装外部 skill、执行外部脚本、复制其图像或把它们的目录数量算作本 skill 可执行能力。新增代码由本次工作原创实现，来源作为设计参考保留。

| 来源与固定提交 | 已吸收的设计增量 | 落地位置 | 未采用的部分 |
|---|---|---|---|
| [EasyPlot](https://github.com/jiumao2/EasyPlot/tree/a6c6cfd4f9fd507e86dcc255b6d27aef686d99a1)，MIT | 先确定布局、命名面板、显式位置与尺寸、给图例/色条留空间 | Python `named_layout`、`axis_bounds`、物理尺寸与检查流程 | MATLAB 环境、强制字号/函数组织要求 |
| [SciPilot Figure](https://github.com/Haojae/scipilot-figure-skill/tree/43098ddb9e6a6d142218540c114f9ed38922fc42)，MIT | 问题/表格决定图型、已有字体覆盖、机器检查结合实际画面 | `resolve_font`、`audit_layout`、图型选择与审阅流程 | 自动统计探索/拟合、自动装依赖、固定问答步骤 |
| [Scientific Figure Making](https://github.com/ChenLiu-1996/figures4papers/tree/f0bb7559abe90f5e1828797126d4d133c1bd47d7) | 集中样式参数、独立图例区域、通用统计图形布局 | 原创 `DesignSpec`、`legend_zone`、冻结表格通用图 | 未复制其代码、文本模板或图片；未把大画布示例字号当作期刊标准 |
| [Academic Figure Skill](https://github.com/TingxiYu/academic-figure-skill/tree/1df9940dd01ac939f072b12fe28d6353b79b90f9)，Apache-2.0 | 参数分层、多面板叙事、逐图反馈、区分语义/数据/外观/导出检查 | 原创 Python/R 样式层、固定图号意见记录、审阅说明 | copy-first 自动执行、环境变量动态求值、强制色卡/面积比例、未验证的“期刊实例”或审稿案例 |

Scientific Figure Making 的 [仓库 LICENSE](https://github.com/ChenLiu-1996/figures4papers/blob/f0bb7559abe90f5e1828797126d4d133c1bd47d7/LICENSE) 是 CC BY-NC 4.0，而其 skill 元数据写 MIT；本次记录该冲突，采用一般设计思想和独立实现，没有将受限内容纳入可分发包。其他仓库许可证也不授权复制第三方论文图片。

静态扫描加人工复核覆盖 67 份获取的文本文件。EasyPlot 无规则命中；其他命中包含网络文档、安装建议、子进程、临时文件清理和动态求值。已将这些指令视为审查材料。Academic 的 compose.py 中以环境变量提供 R 文本并求值的实现没有采用。未发现的风险不等于不存在；本记录只确认所选增量的实现边界。

本 skill 沿用原来的输入冻结、科学单位、精确 TSV 哈希和版本化导出契约。样式改动不授权重新分析、上传私有表格、装包或提交远程计算。
