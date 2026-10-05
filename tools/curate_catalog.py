"""Build a visual-grammar index without deleting any saved source example.

Scientific input contracts remain per preset. A shared drawing family is not a
claim that its inputs, estimands, intervals or scientific interpretations match.
"""
from pathlib import Path
import json, csv, re

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / 'examples/gallery'
REF = ROOT / 'skills/transcriptomics-figure-workbench/references'

# Canonical preview, title, visual grammar, every retained source ID.
RULES = [
 ('P04','分组原始点与中心区间','category-positioned observations; optional jitter/swarm and supplied summary','P01 P04 R17 P24'),
 ('T36','箱线概括','five-number boxes, whiskers and optional outliers','P02 T36'),
 ('P05','雨云：半密度、箱线与原始点','half-density + box + individual observations','P05'),
 ('T08','小提琴与箱线','full mirrored density + box','T08'),
 ('P35','分箱数量分布','fixed-bin rectangles','P35'),
 ('E12','密度山脊','aligned offset densities on a shared value axis','P37 E12'),
 ('T31','有序曲线与区间带','ordered series; line/step/offset; supplied single or nested bands','P29 T09 T14 T18 T28 T31 T35 T39 M07 E10 E32 P25a P25b P25c P26a P26b N09'),
 ('P03','配对点与主体连线','same-ID observations joined across conditions','P03'),
 ('T33','XY散点与给定参考层','XY points; supplied fit, reference lines, boundaries, group overlays or aligned diagnostic facets','P06 P33 T05 T07 T19 T33 R18 R19 E11 E14 E24 E25 E30 M01 M11a M11b M11c K30'),
 ('T29','三变量气泡散点','XY position + an independently declared area variable','T15 T29 T40 M11d'),
 ('T20','连续密度着色与固定门','positive XY with supplied density colors and explicit gate boundaries','T20 T21 T22 T23'),
 ('N10','六边形支持量','hexagonal bins with count color','N10'),
 ('E26','相同坐标的连续特征分面','registered XY repeated for continuous feature colors','P07 E26'),
 ('T32','条形估计与给定误差线','category rectangles + optional supplied intervals; orientation is a setting','P34 T06 T13 T25 T27 T32 T38 T43 P32'),
 ('P11a','棒棒糖评分','stem length + endpoint; optional independent color/area','P11a P11b'),
 ('E21','森林与多系列区间','row-positioned estimates + optional intervals, numeric columns and series offsets','P19a P19b P20a P20b P21a P21b E13 E21 E22 E30b K26'),
 ('T10','组成堆叠柱','stacked category fractions or declared counts','P23 T10 T17 M10'),
 ('T12','整体组成环形图','annular sectors for one declared denominator','T12 T26'),
 ('T34','数值热图与可选注释','rectangular cell colors; optional supplied hierarchy, labels, masks and facets','P12a P12b P15 P17a P17b P17c P18 P36 T03 T16 T30 T34 T41 M02 M03 K33'),
 ('R22','共享轴的矩阵与数量轨道','aligned colored matrices, bars and optional marginal densities','P16a P16b P31a P31b P31c R15 R22 E09'),
 ('E01','点阵：面积、颜色与状态','row/column-positioned symbols with declared independent area/color/status; optional facets','P13 P14 T11 R20 E01'),
 ('R05','椭圆与数值相关矩阵','ellipse angle/eccentricity + signed color + lower-triangle numbers','R05'),
 ('R25','节点关系网络','explicit nodes/edges; shape, color, width; circular/bipartite/layered/pathway layouts are settings','R06 R25 N01 N02 N03 N12 E23 M09'),
 ('N04','弦图：关系与数量带','annular nodes + ribbons; weighted quantity or explicit equal-width membership','N04 E08'),
 ('N05','跨阶段流带','categorical stages joined by quantity-height paths','N05'),
 ('N06','集合交集 UpSet','intersection bars + membership dot matrix + set-size bars','N06'),
 ('E07','两集合交集','two overlapping regions with unique/intersection counts','E07'),
 ('N07','多状态事件矩阵','multiple categorical states within a cell; optional aligned counts','N07 E20 K20'),
 ('N11','二维连续场与等值线','registered two-dimensional field + isovalue contours','N11'),
 ('R23','三维数值曲面','height surface over two declared coordinates','R23'),
 ('T01','地理数值场','projected geographic field; global/regional extent is a setting','T01 T02'),
 ('T04','地理连接路径','projected endpoints with explicit route edges','T04'),
 ('E33b','配准背景上的测量叠加','registered background pixels + categorical/continuous marks; optional aligned facets','E33a E33b K32'),
 ('R01','环形轮廓与分层气泡','radial multiseries profile + independently sized bubbles','R01 R02'),
 ('R09','平行坐标','multiple declared axes joined by one record per path','R09'),
 ('R10','多行贡献蜂群','row-positioned contribution swarms + continuous feature-value color','R10'),
 ('T37','雷达轮廓','radial declared indicator axes joined per series','T37'),
 ('R21','多比较有符号条带','comparison strips with signed effects and declared qualifying counts','R21'),
 ('T42','对象与流程箭头示意','explicit illustrative objects, connections and steps','T42'),
 ('E02','条目与成员效应环形轨道','term significance/direction ring + member-effect distributions','E02 E03 E04 E05'),
 ('E15','阶梯概率、区间与支持人数','supplied probability steps + intervals + aligned at-risk table','E15'),
 ('E16','个体区间与事件时间','one row per object with duration segments and event symbols','E16'),
 ('E17','规格曲线与选择矩阵','ordered estimates/intervals aligned with a decision matrix','E17'),
 ('E18','已有向量场','XY locations + supplied vector direction/magnitude','E18'),
 ('E19','双变量色块与二维色键','two independent values per registered tile + two-dimensional key','E19'),
 ('E27','三元组成坐标','three parts of one denominator on a simplex','E27'),
 ('E28','分段位置与关联信号','ordered segment positions + signal height + declared thresholds','E28'),
 ('E29','共用位置轴的多轨道与连接','position-linked point/line/interval tracks + optional given connection arcs','P28 P30 E29 M08'),
 ('E31','层级数量矩形树图','given hierarchical area partitions for additive amounts','E31'),
 ('M04','同对象多视图与身份连线','separate coordinate views with matched-ID gutter connections','M04'),
 ('M05','特征相关投影圆','unit circle + origin rays + supplied feature projections','M05'),
 ('M06','离散峰棒与镜像','peak positions/intensities as sticks; optional mirrored reference spectrum','M06'),
 ('N08','排序曲线、命中与排名量','aligned running curve, hit ticks and ranked metric; optional zoom window','N08 K19'),
 ('P09','效应与证据火山','effect/evidence XY + declared status and optional side labels','P08 P09 T24'),
 ('P10','火山与堆积边际分布','same-point volcano + stacked marginal counts','P10'),
 ('R13','散点与边际分布','same XY + two aligned marginal distributions; optional supplied fits/residual summary','R08 R12 R13'),
 ('P27','曲线与分箱支持量','aligned calibration values, supplied intervals and bin-support rectangles','P27'),
 ('R07','关联矩阵与外接检验网络','triangle pairwise association matrix + cross-set tested edges','R07'),
 ('R11','多类贡献与份额组合','aligned class contribution swarms, rose insets and multiring shares','R11'),
 ('P22','配对评分与差值区间','paired XY + independently supplied difference intervals','P22'),
 ('R16','效应分布与森林摘要','aligned individual-effect clouds + supplied summary intervals','R16'),
 ('R04','环形坐标、计数与层次点阵','embedding atlas + radial counts + hierarchical marker matrix','R04'),
 ('R03','坐标小窗与证据双矩阵','aligned state-coordinate windows + dot evidence + two value matrices','R03'),
 ('R14','训练曲线与运行诊断','loss curves + run heatmap + gradient curve','R14'),
 ('R24','流程、对象、矩阵与评价地形','process diagram + object views + candidate matrices + landscapes + stage counts','R24'),
 ('E34','成员流线、条目与评分点阵','binary membership ribbons aligned to term rows and quantitative bubbles','E34'),
 ('E35','双量值三角单元矩阵','two separately colored triangles per cell with independent quantitative keys','E35'),
 ('E37','已有层次树、叶端标记与量值轨道','given hierarchy in rectangular/radial mode with categorical or quantitative leaf tracks','E36 E37'),
]

# A second matrix, axis scale or added marginal count alone is a preset, not a
# new recipe. Distinct component relationships remain independently selectable.
COMBINATION_ALIASES = {'K02':'K01','K03':'K01','K07':'K01','K08':'K01','K09':'K01','K28':'K01','K15':'K14','K16':'K14','K23':'K18','K40':'K38'}
MODE_EXAMPLES = {
 'E37':[('E37','环形树与叶端量值'),('E36','矩形树与分类色条')],
 'P04':[('P04','原始点与中心/IQR'),('R17','蜂群排布'),('P24','分面比例点')],
 'T31':[('T31','曲线与一层区间'),('P26a','阶梯曲线'),('T35','偏移谱线'),('E32','多层嵌套区间')],
 'T33':[('T33','点与给定拟合'),('R19','分类点与给定范围'),('R18','质心连线'),('E11','分位数对照'),('E14','差值与给定相合限界'),('M01','四种已给证据状态'),('M11a','给定残差参考层'),('M11c','给定尺度参考层'),('E30','给定精度边界'),('K30','同模型四个诊断分面')],
 'E21':[('E21','单系列与数字列'),('E22','比值与对数轴'),('P21a','多系列并排'),('E13','多阶段点估计'),('K26','两种量值独立分面')],
 'T34':[('T34','已有层次树'),('T30','普通矩阵'),('P15','分类注释条'),('P17b','分块与分面'),('P18','三角区域与缺失状态'),('P36','格内数值'),('K33','不同量值独立色标')],
 'R22':[('R22','多矩阵与计数轨道'),('R15','矩阵与边际密度'),('P16a','矩阵与侧计数'),('P31b','计数与数值表')],
 'E01':[('E01','分类条、形状与状态'),('P13','颜色与独立面积'),('R20','多条件分面')],
 'R25':[('R25','多实体形状与符号边'),('R06','圆形布局'),('N03','二部布局'),('N12','已有层级布局'),('M09','功能底图数量叠加')],
 'N04':[('N04','带宽表达数量'),('E08','等宽表达成员关系')],
 'N07':[('N07','格内多状态'),('E20','缺失与未检测状态'),('K20','矩阵与对象计数')],
 'T01':[('T01','全球范围'),('T02','区域范围')],
 'E33b':[('E33b','连续量叠加'),('E33a','分类叠加'),('K32','同背景独立分面')],
 'E29':[('E29','关联、区间与信号轨道'),('P28','已有区间信号'),('M08','轨道与候选连接弧'),('P30','单条位置轨道')],
 'N08':[('N08','排序三层图'),('K19','三层图与局部窗口')],
 'R13':[('R13','散点与边际密度'),('R08','散点与边际直方图'),('R12','增加给定残差摘要')],
 'K01':[('K01','坐标与矩阵'),('K02','坐标与原位置特征分面'),('K03','增加同对象组成'),('K07','原位置分面与汇总矩阵'),('K09','坐标与颜色/面积点阵'),('K08','增加给定数量'),('K28','增加已有向量场')],
 'K14':[('K14','网络与邻接矩阵'),('K16','网络与对应条件矩阵'),('K15','成员网络、矩阵与UpSet')],
 'K18':[('K18','数量弦图与矩阵'),('K23','成员弦图、矩阵与集合关系网络')],
 'K38':[('K38','已有诊断与模块性状'),('K40','增加相似矩阵与模块网络')],
}

def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def build():
    c=json.loads((G/'catalog.json').read_text(encoding='utf8'))
    items=c['preserved_examples']; by={x['id']:x for x in items}; methods=[]; assigned=set()
    def add(mid,canonical,title,grammar,members,role):
        assert canonical in members and not assigned.intersection(members), (mid,members)
        assert set(members)<=set(by), (mid,set(members)-set(by))
        assigned.update(members)
        modes=MODE_EXAMPLES.get(canonical,[(canonical,'通用形式')])
        assert set(i for i,_ in modes)<=set(members)
        method=dict(id=mid,title=title,role=role,default=canonical,grammar=grammar,members=members,
                    modes=[dict(example=i,label=t) for i,t in modes])
        method['contracts']=[dict(example=i,data_required=by[i]['data_required'],expression=by[i]['expression'],
                                  limitations=by[i]['limitations'],metadata=by[i]['meta']) for i in members]
        methods.append(method)
    for n,(canonical,title,grammar,ids) in enumerate(RULES,1):
        add(f'D{n:02}',canonical,title,grammar,ids.split(),'figure')
    for x in items:
        if x['role']=='combination' and x['id'] not in assigned and x['id'] not in COMBINATION_ALIASES:
            members=[x['id']]+[i for i,j in COMBINATION_ALIASES.items() if j==x['id']]
            add('B'+x['id'][1:],x['id'],x['title'],'explicit saved panel relationship: '+x['expression'],members,'combination')
    add('H01','E06a','条目ID与说明对照表','supporting ID/description key',['E06a','E06b','E06c','E06d'],'support')
    for x in items:
        if x['role'] in ['protein','palette']:
            add(('STRUCT-' if x['role']=='protein' else 'CARD-')+x['id'],x['id'],x['title'],x['expression'],[x['id']],x['role'])
    assert assigned==set(by), ('Unmapped source IDs',sorted(set(by)-assigned))
    drawings=[m for m in methods if m['role']!='palette']
    assert len({m['grammar'] for m in drawings})==len(drawings)
    mapping={i:m for m in methods for i in m['members']}
    for x in items:
        m=mapping[x['id']]; old=x['curation']['decision']
        decision='recommended' if x['id']==m['default'] else 'replace_style' if old=='replace_style' else 'parameter_variant'
        reason='该画法的唯一主预览；来源与数据契约分别保留。' if decision=='recommended' else '合并到 '+m['title']+'；数据名称、色卡、轴尺度、注释或重复分面作为设置，原表格和科学定义保留。'
        x['curation']=dict(decision=decision,canonical=m['default'],reason=reason)
        x['method']=m['id']
    c['schema_version']=3;c['version']='0.2.1';c['drawing_methods']=methods
    c['curation_policy']='One main preview per visual grammar. Source IDs and contracts are preserved. Different data labels, palettes, scales and repeat facets never create new methods.'
    write_json(G/'catalog.json',c)
    counts={role:sum(m['role']==role for m in methods) for role in ['figure','combination','support','protein','palette']}
    registry=dict(schema_version=1,version=c['version'],source_examples=len(items),counts=counts,
                  policy=c['curation_policy'],methods=methods)
    write_json(REF/'drawing-methods.json',registry)
    ledger=json.loads((REF/'catalog-audit.json').read_text(encoding='utf8'));ledger['version']=c['version']
    for row in ledger['entries']:
        x=by[row['id']];row.update(x['curation']);row['method']=x['method']
        row['png_sha256']=x['png_sha256']
    # New examples are audited from their actual saved table and metadata.
    old_ids={x['id'] for x in ledger['entries']}
    for x in items:
        if x['id'] in old_ids:continue
        meta=json.loads((G/x['meta']).read_text(encoding='utf8'))
        if x.get('tsv'):
            with (G/x['tsv']).open(encoding='utf8',newline='') as f: rows=list(csv.reader(f,delimiter='\t'))
        else:rows=[['separately_saved_component_tables']]+[[t] for t in x.get('component_tables',[])]
        from PIL import Image
        ledger['entries'].append(dict(id=x['id'],family=x['family'],title=x['title'],role=x['role'],
            **x['curation'],method=x['method'],input_columns=rows[0],input_rows=len(rows)-1,
            data_required=x['data_required'],expression=x['expression'],render_kind=meta.get('figure_spec',{}).get('kind'),
            semantic_settings=meta.get('figure_spec',{}),png_dimensions=list(Image.open(G/x['png']).size),png_sha256=x['png_sha256']))
    write_json(REF/'catalog-audit.json',ledger)
    with (REF/'catalog-audit.tsv').open('w',encoding='utf8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['id','method','family','decision','canonical','reason','data_required','expression','png_sha256'])
        for x in items:w.writerow([x['id'],x['method'],x['family'],x['curation']['decision'],x['curation']['canonical'],x['curation']['reason'],x['data_required'],x['expression'],x['png_sha256']])
    old_registry=json.loads((REF/'generic-patterns.json').read_text(encoding='utf8'))
    old_registry['status']='Historical broad-topic navigation. Use drawing-methods.json for deduplicated selection.'
    for group in old_registry['entries']:
        for source in group['examples']:source['curation']=by[source['id']]['curation']
        known={x['id'] for x in group['examples']}
        for x in items:
            if x['family']==group['id'] and x['id'] not in known:
                group['examples'].append({k:x[k] for k in ['id','data_required','expression','how_to_draw','limitations','curation']})
    write_json(REF/'generic-patterns.json',old_registry)
    # Maintain inline manifests; the small script works with local file:// too.
    html=(G/'index.html').read_text(encoding='utf8')
    start=html.index('<script>const items=')+len('<script>const items=')
    _,end=json.JSONDecoder().raw_decode(html[start:])
    html=html[:start]+json.dumps(items,ensure_ascii=False)+html[start+end:]
    marker='const methods='
    if marker in html:
        start=html.index(marker)+len(marker);_,end=json.JSONDecoder().raw_decode(html[start:])
        html=html[:start]+json.dumps(methods,ensure_ascii=False)+html[start+end:]
    else:
        start=html.index('const familyByExample=')
        html=html[:start]+marker+json.dumps(methods,ensure_ascii=False)+';'+html[start:]
    (G/'index.html').write_text(html,encoding='utf8')
    lines=['# 去重后的画法与组合','',f'{len(methods)}个主预览；{len(items)}个来源示例完整映射。','',
           '同一画法的数据单位、区间含义、缺失状态与参考线仍由各自数据契约决定。主总览只显示每种画法一次；模式选项改变编码或布局，来源档案保存原编号。','',
           '|入口|通用画法|主预览|保留来源数|','|---|---|---|---|']
    lines += [f"|{m['id']}|{m['title']}|{m['default']}|{len(m['members'])}|" for m in methods]
    (REF/'drawing-methods.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(methods=len(methods),sources=len(items),counts=counts),ensure_ascii=False))

if __name__=='__main__':build()
