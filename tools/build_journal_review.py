# -*- coding: utf-8 -*-
"""Generate per-form decisions from actual search and separately reviewed sources."""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'skills/transcriptomics-figure-workbench/references'
CHOICES='''heatmap|分块标签、一次完整标签区、声明尺度；相近热图作为同型扩展
dot-matrix|用点面积表达检测率、颜色表达均值；另标 marker 归属，禁用半径冒充面积
forest|效应与区间对齐；比值型以 1、差值型以 0 为参考；长名称采用横向布局
volcano|兼容时用边际及精确堆叠计数，保留效应、FDR 和受限标签
gsea|完整运行曲线、命中位置、排名度量及 NES/FDR；多个集合可分面且不挤图例
enrichment-summary|对齐通路与基因支持，声明分母；多对比用同一 NES 尺度
term-circle|仅短名称、少通路时选环形；长名称与精确比较优先直角坐标证据页
paired|连接真实配对 ID，保留未配对状态；有重复测量时明确单位
point-interval|完整点估计与区间；点、区间、样本量各有单独通道
raincloud|原始点、分布和给定区间互补；小样本不依赖平滑外形
box|箱体与独立观测并列，标明须的定义；不遮住离群值范围
violin|给出真实样本与样本量，避免用对称平滑轮廓暗示大量独立重复
embedding|可用时优先给定椭圆、边际及数量；不为美观拟合新的 PCA/UMAP
feature-embedding|全背景、相同坐标、共同尺度，按指定 marker 顺序连续阅读
scatter|点密度与给定趋势互补；需显示完整范围和所用单位
ribbon|画给定的不确定性，明确区间类型；缺口不自动连成连续证据
profile|用给定时间或顺序，分面拆开异量纲；不要只以线的外形推断动态
bars|比较精确数值优先横向柱或点区间；保留零基线及独立观测
stacked|顺序与分母一致，组成和绝对量分开；细小组保留完整阅读版
donut|类别少且用于组成概览时可用；精确比较附对齐柱或数值
histogram|组间共享分箱与范围，频数和密度明确；缺失数量单列
ridges|共享横轴、基线及归一化定义，控制重叠；大量类别提供阅读版
roc|声明终点、时间窗、队列、给定 AUC/CI 及随机参考
precision-recall|显示真实患病率基线，明确平均方式；不把随机水平固定为 0.5
calibration|等比例坐标、同范围和身份参考；给定样本支持与区间，不冒充临床验证
network|真实节点、边类型和权重分开；拥挤时按问题拆子网，不造方向
chord|少组、有真实权重时可用；稠密边优先矩阵，保留方向与分母
membership-links|成员边和基因效应分通道；优先对齐矩阵，少量重要关系再用连线
flow|节点阶段和流量守恒要可解释；不要把不同分母的比例连成流
upset|明确全交集或包含关系，保留零交集定义；多集合优于多圆重叠
venn|仅两个集合且交集可解释时使用；面积不成比例要明说
correlation|对称范围、明确系数与缺失值；相同排序用于比较矩阵
joint|边际与主体共享范围；频数、密度和散点各有清楚单位
rank|明确排名指标、并列和范围；同一对象跨条件使用稳定颜色
gating|保留完整父群体、轴变换、门多边形和给定门内数；不得推断新门
annular|按给定顺序展示简短周期剖面；精确比较另给线图，避免面积误读
contribution|显示给定贡献分布和特征值；不把贡献正负当作干预效应
effect-distribution|以独立单位为点，展示分布及给定区间；类别样本量不等要可见
spatial|固定物理坐标、方向、尺度和组织范围；选择区域可追溯
slice|真实切片与有限叠加层，明确透明度和坐标系；不可生成缺失图像证据
registration|显示给定对应点与残差，不以叠合外观证明配准正确
hierarchy|保持真实父子关系与分支语义；大树用总览与可定位的局部
interval-tracks|保持物理坐标、链、组装与轨道单位；不能类别等距排基因组位置
field|共享密度或等高尺度；明确给定场的单位，不把视觉峰值当显著性
state-matrix|状态、未检验与缺失不同；行列顺序及注释可追溯
scores|给定两条件与差值对齐，声明配对和量纲；同色不混用原分数与差值
palettes|离散身份稳定、连续量单调，色觉缺陷和灰度可辨；禁用无定义彩虹
structures|明确结构来源、链、残基与置信度；用局部放大支持特定位点问题
decision|标明阈值和 treat-all/none 参考；限制有真实临床意义的范围
survival|阶梯、删失、给定区间与风险人数配合；组名、终点和时间窗一致
maps|区域、投影、缺失和分母明确；数值填色不等于疾病风险显著性
geographic-links|真实起终点与权重；连线密集改分面或聚合阅读，保留范围说明
radar|少轴、同量纲且有明确偏好时用；多特征精确比较优先点图或热图
object-schematic|只画已给定对象和关系；示意图与实验观察采用清楚不同的视觉语义
ma|保持均值尺度、效应和精确方向计数；低信号区域不隐藏
radial-effects|径向作为可选概览，完整效应与区间留给直角坐标阅读版
ranked-effects|给定效应排序，阈值与上下调一致；不把视觉排名当新检验
mosaic|面积代表正确分母，明确条件比例；小格保留数值表与残差含义
waffle|每格单位与舍入规则明确；少量类别概览，不代替精确率差比较
horizon|解释色带折叠和基线，另附完整曲线；不只凭压缩色块比较幅度
connected-scatter|显示给定顺序与方向，标注端点；不能由几何邻近推断时间
mirrored-bars|两侧含义、绝对量和共同范围明确；负向排版不代表负丰度
rainfall|横轴物理位置、纵轴给定相邻距离，标明对数轴；不凭外观调用 kataegis
composition|用研究问题组织总览、局部与定量支持；不以固定行列强塞所有分析
qq|期望与观测分位、变换及参考带明确；图形偏离不是单独的偏倚诊断
residual-diagnostics|残差类型、拟合值及单位清楚；不为美化重拟合模型或删除异常点
dashboards|总览、筛选、原像素阅读和来源路径相连；交互不能成为缺少静态完整证据的借口
residue-confidence|残基索引与链映射不丢失；pLDDT、PAE 和实验误差不得互换
reference-parallel-trials|轴方向、单位和归一化明确；保留准确数值，不用线交叉量推断分群
reference-group-beeswarm|只在类别方向排点，保持定量值；组间支持与独立单位可见
reference-strip-effects|把点估计、范围与类别对齐；必要时扩展标签区而非缩小字号
reference-aligned-tracks|共享物理横轴和选区，轨道单位各自标注；不盲目共用不兼容量纲
reference-surface-grid|明确给定网格与视角；静态定量比较优先等高线和截面
distribution-ecdf|共享范围与完整样本支持；说明删失、权重或重复单位，不按光滑程度判断优劣
covariate-balance|展示前后同一变量及给定 SMD，阈值有说明；平衡图不是消除混杂的证明
bland-altman-supplied|均值轴、差值方向及给定一致性界限明确；异方差不能靠裁剪消除
swimmer-followup|每行真实个体、起止与事件，未完成随访和删失不同；长个体名提供阅读版
specification-curve|显示完整已运行规格及选择规则；仅显示有利规格会误导
supplied-vector-field|向量单位、尺度、来源和观测背景一致；图形方向不自动建立谱系
ternary-composition|三个分量同分母且和为一；标轴和刻度齐全，不把距离作因果关系
genome-association-overview|染色体真实坐标、显著性定义与检验家族明确；注释不遮住主体
funnel-supplied-results|给定效应和精度、参考区间与研究数可见；不对称不等于发表偏倚
feature-correlation-projection|解释 loadings、scores 和缩放；相关圆不能被误读为样本置信区间
mass-spectrum-mirror|给定 m/z 对齐、匹配容差和强度规则；镜像方向不代表负强度
pathway-quantity-overlay|保持真实节点/关系及版本，数量叠加有单位；图的颜色不证明通路激活
splice-tracks|coverage、junction counts、转录本和链分层；物理坐标对齐，零与缺失不同
variant-posteriors|每个给定信号的 PIP 和 credible set 对齐；无集合和未分析不得填零
contribution-waterfall|完整贡献与基线闭合到预测值；正负不解释为因果方向
sequence-logo|按位置展示给定权重或信息量，字母高度和单位明确；缺口不当碱基
contact-tracks|接触 bin 的物理边界、归一化与同坐标轨道明确；不推断不存在的 loop'''

def build(check=False):
    forms=json.loads((REF/'form-catalog.json').read_text(encoding='utf8'))['forms']
    search=json.loads((REF/'journal-search-v092.json').read_text(encoding='utf8'))
    sources=json.loads((REF/'journal-design-v092.json').read_text(encoding='utf8'))['sources']
    choices=dict(line.split('|',1) for line in CHOICES.splitlines())
    assert {f['id'] for f in forms}==set(choices)=={r['form'] for r in search['records']}
    look={r['form']:r for r in search['records']};records=[]
    lines=['# 90 个基础图型逐项检索与选择','',
      '检索记录不是原图验收。已核查原图的来源单独列出；候选可能属于同批其他查询。未采用新来源的图型仍保留现有代码与示例，不因此新增近似入口。','',
      '| 图型 / 现有入口 | 选择与限制 | 已看过原图的相关设计来源 | 本轮检索候选 |','|---|---|---|---|']
    for f in forms:
        k=f['id'];reviewed=[s for s in sources if k in s['forms']]
        row=dict(form=k,title=f['title'],default=f['default'],search_date=search['search_date'],
          decision=choices[k],reviewed_source_ids=[s['id'] for s in reviewed],
          adoption_state='reviewed_design_principles' if reviewed else 'retain_existing_verified_form_no_new_default_adopted',
          recent_source_required=False,search_inspection='search_results_only')
        records.append(row)
        rtext='<br>'.join('['+s['journal']+' Fig. '+s['figure']+']('+s['figure_url']+')' for s in reviewed) or '本轮未采用新的期刊默认设计；沿用原有验证画法'
        urls=look[k]['candidates'][:2]
        candidates='<br>'.join('[候选 '+str(i+1)+']('+c['url']+')' for i,c in enumerate(urls))
        lines.append('| '+f['title']+' / `'+f['default']+'` | '+choices[k]+' | '+rtext+' | '+candidates+' |')
    outputs={'journal-form-review-v092.json':json.dumps(dict(schema_version=1,forms=90,records=records,scientific_acceptance=False),indent=2,ensure_ascii=False)+'\n','journal-form-review-v092.md':'\n'.join(lines)+'\n'}
    for name,text in outputs.items():
        if check:assert (REF/name).read_text(encoding='utf8')==text,'Stale generated journal review: '+name
        else:(REF/name).write_text(text,encoding='utf8')
    print(json.dumps(dict(status='PER_FORM_JOURNAL_REVIEW_GENERATED',forms=len(records),forms_with_reviewed_design_sources=sum(bool(r['reviewed_source_ids']) for r in records))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');build(p.parse_args().check)
