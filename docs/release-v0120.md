# v0.12.0 · 冻结结果交接、联动检查与技能路由

- 新增 `handoff-plan`：消费 BioResearchWorkbench 的 FigureHandoff v1，绑定当前 TSV、QC、上下文和来源，再复用原有 FigureSpec 与 render。变更后旧计划失效。
- 新增 `linked-views`：同对象的多视图联动、键盘选择、固定轴域、缺失值显示、完整分页和对齐 SVG。实际示例复用已有冻结三维坐标，包含 48／96／144 对象和双列自定义布局。
- 将过长 skill 入口整理成按任务加载的路由和操作顺序，完整旧说明保存在 references。原来 42 个升级配方、三维散点、体渲染、分子轨迹、复杂 bulk／单细胞默认画法与历史实例均保留。
- 根据 SciSpace 检索，并核对 Vitessce 和 Workflow Run RO-Crate 原始论文，明确采用设计思路与未采用的框架／标准能力。没有纳入第三方代码、论文图或私有结果。

调用与真实示例：[连接工作流说明](../skills/transcriptomics-figure-workbench/references/connected-workflows-v0120.md)。所有工程、浏览器、视觉和科学状态分别记录；本版不执行科学分析，也不增加科研后端。
