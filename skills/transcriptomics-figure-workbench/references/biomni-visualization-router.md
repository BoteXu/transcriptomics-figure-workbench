# Biomni 结果类型与新增表达

本版先检查当前 Biomni 状态、绘图/影像、基因组与系统生物学目录，再按输入和视觉编码筛选。`research.select_tools(intent="network_render")`实际返回了 Cytoscape 导入/绘图的规划；状态是 plan_only，没有导入网络、改变布局或启动软件。当前包提供的网络表达已经覆盖该需求，因此没有再增加同类网络入口。

目录中的影像叠加/配准可视化、染色质接触、motif 和已有树结果提示了以下缺口。对应上游函数的 runtime_state 尚未验证；本次实现和测试的是原创冻结表绘图器，没有运行这些上游分析或复制第三方分析代码。

|示例与适配器|必须提供的数据|视觉表达与可组合关系|
|---|---|---|
|E38 / sequence_logo|position_id、symbol、非负 height 的完整位置×字母表；显式零值、位置/字母顺序、symbol_slots、高度定义/单位|字符本身与高度编码；同一位置的高度堆叠。适合已有位点频率、概率或信息量；不同高度定义须明确区分。|
|E39 / contact_tracks|bin记录：bin_id、start、end；contact记录：bin_i、bin_j、value；可选signal记录：track、bin_id、value。已排序连续物理分箱、完整上三角位置对（未知值显式缺失）、完整轨道、量值范围和坐标版本|三角接触矩阵用x=(u+v)/2、y=(v−u)/2转换物理区间；不把不等宽区间当等宽。轨道共用位置轴。并入数值矩阵入口的模式。|
|E40 / branch_tree|node_id、parent_id、branch_length、label；根ID及零根枝长、完整叶顺序、枝长单位与来源|树拓扑和累计枝长；支持多叉树。并入已有树图入口；枝长与聚类高度保留不同契约。|
|E41 / slice_overlay|view、物理u/v、intensity、整数label；规则完整网格、每切面方向与坐标标签、共同强度范围、标签色槽和已完成配准说明|正交切面背景和同位置区域叠加；横/纵排列可切换。并入注册背景叠加入口。|
|E42 / registration_check|共同规则物理网格的u、v、fixed、registered；共同强度范围、带正负的差值范围、棋盘块像素数、配准与方向定义|固定图、注册图、交替棋盘和逐像素registered−fixed；棋盘是独立编码，新设通用入口。|

全部绘图脚本位于 scripts/figure_biomni_views.py，示例数据生成位于 scripts/biomni_view_fixture.py。每个新增示例均保存 TSV、style.json、PNG、PDF、SVG和元数据。

切片和配准对照的 `arrangement="horizontal"/"vertical"` 改变内部 panel 排列；通用 `page_layout="landscape"/"portrait"` 调整画布方向。两者不混称。不读取私人影像、不执行分割/注册、不创建树、不发现motif、不识别TAD/loop。研究数据应用时使用已审核的结果、坐标版本和计量定义。

```sh
python skills/transcriptomics-figure-workbench/scripts/render_frozen_table.py --help
```

选择策略：相同编码的新场景作为模式；字母高度和棋盘交替两种新编码独立登记。因此增加5个脚本画法和5个来源示例，主目录只增加2个画法，继续保留全部旧编号。

表达依据的原始文档：[WebLogo](https://weblogo.readthedocs.io/en/latest/)、[cooltools接触矩阵显示](https://cooltools.readthedocs.io/en/latest/notebooks/viz.html)、[Biopython树对象与显示](https://biopython.org/docs/latest/Tutorial/chapter_phylo.html)、[Nilearn解剖影像显示](https://nilearn.github.io/stable/modules/generated/nilearn.plotting.plot_anat.html)。本包只实现已给表格的静态显示，不声称等同这些软件的完整科学分析或原生文件支持。
