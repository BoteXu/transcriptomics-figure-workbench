"""Consolidate presentation duplicates into forms with explicit, source-bound extensions."""
import argparse, collections, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
GROUPS=[
 ('heatmap','热图','P12a P12b P15 P16a P17a P17b P17c T03 T16 T30 T34 T41 E09 E47 E48 E49 M02 M03 AUX_marker_matrix AUX_adjacency AUX_membership AUX_flow_matrix AUX_c40_matrix AUX_term_scores NEW_A06 PKG12 PKG22 PKG23 PKG06 AUX_marker_counts CLR08 CLR09 VIS02 P36 E19 E35'),
 ('dot-matrix','点阵与气泡矩阵','P13 P14 P16b T11 R20 E01 AUX_marker_fraction PKG16 PKG05 GSEA05 GSEA06'),
 ('forest','效应与区间森林图','P19a P19b P20a P20b P21a P21b E21 E22 E30b AUX_estimate_forest AUX_delta_estimate NEW_A02 PKG14 VIS04'),
 ('volcano','火山图','P08 P09 P10 T24 NEW_A01 PKG13 PKG15'),
 ('gsea','GSEA 富集曲线','N08 AUX_hit_window PKG01 PKG02 PKG03 PKG04 GSEA01 GSEA02 GSEA03 GSEA04 REF01 REF02'),
 ('enrichment-summary','富集结果点线图','P11a P11b ORA01 ORA02 PKG07 PKG08'),
 ('term-circle','通路环形效应图','E02 E03 E04 E05 E06a E06b E06c E06d'),
 ('paired','配对观测图','P03 AUX_paired NEW_A03'),
 ('point-interval','观测与区间图','P04 AUX_point_interval AUX_paired_deltas'),
 ('raincloud','雨云与半眼分布','P05 AUX_raincloud VIS01 EXT01'),
 ('box','箱线图','P02 T36 QDE_sample_boxstats'),
 ('violin','小提琴图','T08'),
 ('embedding','嵌入与主成分散点','P06 T07 T19 E25 R18 R19 QDE_pca_scores M04 PKG17 PKG18 VIS05'),
 ('feature-embedding','特征着色嵌入图','P07 E26 AUX_marker_coordinates'),
 ('scatter','散点与给定趋势','P01 P33 T05 T15 T29 T33 T40 E24 AUX_c38_fit AUX_c38_degree AUX_c38_scores M01'),
 ('ribbon','曲线与给定区间带','P29 T09 T14 T18 T28 T31 T39 E32 E50 REF03'),
 ('profile','有序曲线与剖面','T35 CLR01 VIS03 AUX_marker_profiles E46 M07'),
 ('bars','分组柱状图','P34 T06 T13 T25 T27 T32 T38 T43 AUX_subgroup_counts QDE_deg_counts AUX_event_counts AUX_c37_terms P32'),
 ('stacked','堆叠与组成柱状图','P23 T10 T17 M10 AUX_stage_composition AUX_c39_stack'),
 ('donut','环形组成图','T12 T26 AUX_subgroup_shares QDE_deg_donut'),
 ('histogram','直方图与频数轮廓','P35 QDE_pvalue_hist'),
 ('ridges','山脊分布图','P37 E12 PKG09'),
 ('roc','ROC 曲线','P25a P26a NEW_A04 PKG25'),
 ('precision-recall','精确率与召回曲线','P25b P26b EXT03'),
 ('calibration','校准曲线与样本支持','P25c P27 E45'),
 ('network','关系网络','N01 N02 N03 N12 R06 R25 E23 AUX_c37_network AUX_c37_local AUX_c40_network PKG10 PKG11 PKG20 PKG21'),
 ('chord','弦图','N04 E08'),
 ('membership-links','成员连线与带状图','E34'),
 ('flow','流向与桑基图','N05'),
 ('upset','集合交集图','N06 AUX_membership_upset'),
 ('venn','双集合重叠图','E07 AUX_c37_sets'),
 ('correlation','相关矩阵','P18 R05 R07 REF05 PKG19'),
 ('joint','联合散点与边际分布','R08 R12 R13'),
 ('rank','排名轨迹与范围','N09 NEW_A05 EXT04'),
 ('gating','门控散点','T20 T21 T22 T23'),
 ('annular','环带剖面图','R01 R02'),
 ('contribution','贡献蜂群图','R10 R11 CLR03 CLR04 CLR05 CLR06 CLR07'),
 ('effect-distribution','效应分布与区间','R16 CLR02'),
 ('spatial','配准空间图','E33a E33b'),
 ('slice','切片叠加','E41 ALT_E41_horizontal ALT_E41_vertical CLR10'),
 ('registration','配准检查','E42 ALT_E42_horizontal ALT_E42_vertical CLR11'),
 ('hierarchy','层次与分支树','E31 E36 E37 E40'),
 ('interval-tracks','坐标与基因组轨道','P28 M08 E29'),
 ('field','二维密度与等高场','N10 N11 AUX_bubble_hex'),
 ('state-matrix','事件状态矩阵','N07 E20 P31a P31b P31c'),
 ('scores','双条件分数与差值','P22 REF04'),
 ('palettes','参考配色','C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12 C13 C14 C15'),
 ('structures','分子结构展示','S01 S02 S03'),
 ('decision','决策曲线','EXT02'),
 ('survival','生存曲线与风险人数','E15 PKG24'),
 ('maps','地图数值展示','T01 T02'),
 ('geographic-links','地理连线','T04'),
 ('radar','雷达剖面','T37'),
 ('object-schematic','对象示意图','T42'),
 ('ma','MA 图','QDE_ma'),
 ('radial-effects','径向效应图','QDE_radial_effects'),
 ('ranked-effects','效应排序图','QDE_ranked_effects'),
 ('mosaic','马赛克图','NEW_B01'),('waffle','计数方格','NEW_B02'),('horizon','地平线剖面','NEW_B03'),
 ('connected-scatter','有序连线散点','NEW_B04'),('mirrored-bars','镜像柱图','NEW_B05'),('rainfall','基因组降雨图','NEW_B06'),
 ('composition','多面板拼版',''),
 ('qq','分位数对照图','E11 M11b'),
 ('residual-diagnostics','残差诊断散点','M11a M11c M11d'),
 ('dashboards','复合图与仪表板','P24 R03 R04 R14 R15 R24'),
]
LABELS={'P12a':'有符号值','P12b':'非负值','P15':'行列注释条','P16a':'旁侧计数','P17a':'组别标题带','P17b':'分组留白','P17c':'转置视图','T34':'给定层次树','M03':'多层注释','VIS02':'分块与缺失标记',
        'P09':'精选标签与引线','P10':'边际直方图','PKG01':'经典三轨','PKG02':'多通路曲线','PKG03':'分面曲线','REF01':'连续色轨与直接标注',
        'E02':'BP 示例','E03':'MF 示例','E04':'CC 示例','E05':'Pathway 示例','E06a':'BP 条目键','E06b':'MF 条目键','E06c':'CC 条目键','E06d':'Pathway 条目键',
        'R01':'环带与面积标记','R02':'同构配色示例','T20':'门控示例一','T21':'同构示例二','T22':'同构示例三','T23':'同构示例四'}


def build(plan,output):
    data=json.loads(plan.read_text(encoding='utf8'));assigned={};groups={}
    for key,title,ids in GROUPS:
        groups[key]=dict(id=key,title=title,default=None,extensions=[],compatibility_aliases=[])
        for i in ids.split():
            assert i not in assigned,i
            assigned[i]=key
    rows=data['items']+data['compositions']
    for r in rows:
        k=r['id'];m=json.loads((ROOT/r['source']['meta']).read_text(encoding='utf8'))
        spec=m.get('figure_spec',{});mode=spec.get('kind_mode') or r.get('kind') or 'composition'
        key=assigned.get(k)
        if r.get('components'):key='composition'
        if key is None:
            key=mode.replace('_','-');groups.setdefault(key,dict(id=key,title=r.get('context',{}).get('title_en') or mode.replace('_',' '),default=None,extensions=[],compatibility_aliases=[]))
        g=groups[key];assigned[k]=key
        ext=dict(id=k,label=LABELS.get(k,spec.get('options',{}).get('title') or r.get('context',{}).get('title_en') or mode.replace('_',' ')),
                 variant_mode=mode,options=spec.get('options',{}),example='examples/forms-v080/'+k+'/'+k+'.png',
                 bundle='examples/forms-v080/'+k+'/',source_record=r['source']['meta'],components=r.get('components',[]),
                 scientific_channels='Use exact source units, scale, ordering, uncertainty and membership; visual similarity does not make result definitions interchangeable')
        g['extensions'].append(ext);g['compatibility_aliases'].append(k)
    picks={'heatmap':'P17b','dot-matrix':'P13','gsea':'REF01','forest':'E21','volcano':'P09','profile':'CLR01','contribution':'CLR03','effect-distribution':'CLR02','joint':'R08','correlation':'R05','composition':'K01'}
    nonempty=[]
    for key,g in groups.items():
        if not g['extensions']:continue
        g['default']=picks.get(key,g['extensions'][0]['id']);assert g['default'] in g['compatibility_aliases']
        variants={}
        for e in g['extensions']:
            k=e['id'];mode=e['variant_mode']
            if key=='heatmap':
                v=('分组留白' if k in ['P17b','VIS02'] else '转置' if k=='P17c' else '给定聚类树' if k=='T34' else
                   '旁侧统计' if k in ['P16a','E09','AUX_marker_counts','CLR09'] else '行列注释' if k in ['P15','E47','M03','PKG12','PKG22','PKG23'] else
                   '格内数值' if k in ['CLR08','P36'] else '双变量色键' if k=='E19' else '双指标三角格' if k=='E35' else '基础矩阵')
            elif key=='gsea':v='连续色轨' if k.startswith('REF') else e['options'].get('mode','classic')
            elif key=='composition':v='纵向' if k.endswith('_vertical') else '横向' if k.endswith('_horizontal') else '均衡拼版'
            elif key in ['bars','stacked','donut','gating','palettes','structures','ridges','box','histogram','paired','violin','roc','precision-recall','rank','annular']:
                v='基础画法'
            elif key=='volcano':v='边际分布' if k=='P10' else '精选标注' if k in ['P09','PKG13','PKG15'] else '基础画法'
            elif key=='ribbon':v='多层区间' if k=='E32' else '曲线与区间'
            elif key=='contribution':v='多类拼版' if k=='R11' else '单类明细'
            elif key=='embedding':v='给定椭圆与参考线' if k in ['T07','R18','R19','QDE_pca_scores'] else '标签与坐标'
            else:v=mode
            group=variants.setdefault(v,dict(id=key+'-'+str(len(variants)+1),label=v,example_ids=[],preferred_example=k))
            group['example_ids'].append(k)
            if k==g['default']:group['preferred_example']=k
            e['extension_id']=group['id']
        g['variants']=list(variants.values())
        human={'dot':'表达与比例','package_dot':'表达点阵','package_nes':'NES与显著性','gsea_nes':'NES与显著性','gsea_leading_edge':'成员与效应',
               'publication_grouped_forest':'分组与数值栏','package_forest':'效应与数值栏','effect_matrix':'效应矩阵','editorial_rebuild':'简洁排版',
               'enrichment_lollipop':'点线与支持度','package_ora':'基因比例与支持度','ora_terms':'条目点图','term_effect_circle':'环形效应','term_key':'条目名称表',
               'classic':'经典三轨','overlay':'多通路叠加','facets':'对齐分面','reference_mantel_matrix':'矩阵与Mantel连线','reference_ellipse_correlation':'椭圆与数值',
               'association_matrix':'数值与缺失标记','refined_association':'分开对齐的矩阵','package_module':'模块与性状数值',
               'sample_distribution':'观测与汇总','publication_plus_halfeye':'供应分布与区间','reference_facet_bubble_matrix':'分面气泡矩阵',
               'multi_group_enrichment_grid':'多组标记与独立色键','package_network':'带权网络','typed_network':'类型与关系','reference_signed_network':'有符号连线',
               'frozen_qc_de':'冻结QC结果示例','publication_aligned_matrix':'固定顺序矩阵','reference_joint':'联合散点与边际分布',
               'reference_state_dashboard':'状态与标记组合','reference_embedding_atlas':'嵌入与标记组合','reference_training_dashboard':'训练记录组合','reference_activity_dashboard':'活动矩阵组合','reference_process_dashboard':'过程示意组合',
               'model_diagnostic_residual':'残差对照','model_diagnostic_scale_location':'尺度与位置','model_diagnostic_influence':'影响与杠杆值'}
        for v in g['variants']:v['label']='基础画法' if len(g['variants'])==1 else human.get(v['label'],v['label'].replace('_',' '))
        g['default_variant']=next(e['extension_id'] for e in g['extensions'] if e['id']==g['default'])
        g['policy']='one base entry; options and source examples nested; no independent method count for colour/data/layout duplicates'
        nonempty.append(g)
    assert len({r['id'] for r in rows})==458
    assert len([e for g in nonempty for e in g['extensions']])==458
    result=dict(schema_version=1,version='0.8.0',counts=dict(base_forms=len(nonempty),retained_examples=458,standalone=332,compositions=126,new_chart_types=0),
                forms=nonempty,aliases={k:assigned[k] for k in sorted(r['id'] for r in rows)},scientific_acceptance=False)
    output.parent.mkdir(exist_ok=True,parents=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['counts']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();build(a.plan,a.output)
