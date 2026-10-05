"""Deterministic bounded software examples; no biological research analysis."""
from pathlib import Path
import argparse,json,inspect
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import figure_multiscale as scale
import figure_multiomics_views as multi
import figure_publication as pub
import figure_general as general
import figure_method_extensions as methods
import figure_core as core
from method_extension_fixture import fixture_cases,draw_case
from panel_layout_audit import audit_panel_layout


def multiview_cases():
    rng=np.random.default_rng(2026100520);theme,_=fixture_cases()
    theme['group_slots'].update({'Neither':3,'X only':0,'Y only':4,'Both':6,'RNA':0,'Protein':6,'ATAC':2,'Metabolite':4,'Observed':0,'Reference':6,'M+0':0,'M+1':2,'M+2':4,'M+3':6})
    cases={}
    def add(id_,fn,d,params,title,requires,expression,boundary,mode='theme_argument'):
        if 'palette' in inspect.signature(fn).parameters:
            from project_theme import group_palette
            field=next(c for c in ['group','series','celltype','model'] if c in d)
            params=dict(params,palette=group_palette(theme,list(pd.unique(d[field]))))
        cases[id_]=dict(function=fn,data=d,params=params,title=title,data_required=requires,expression=expression,how_to_draw='按明确ID、顺序、范围和量纲绘制已有结果；外置图例，课题色卡与字体统一',limitations=boundary,theme_mode=mode)
    d=pd.DataFrame(rng.dirichlet([3,4,2],size=60),columns=['A','B','C']);d['object_id']=[f'U{i:02}' for i in range(60)];d['group']=['G1' if i<30 else 'G7' for i in range(60)]
    add('E27',scale.plot_ternary_composition,d,dict(components=['A','B','C'],denominator_definition='Three fractions of the same supplied total',title='Three-component composition'),'三组分组成：三元坐标','对象ID、组别、同一分母的三个非负比例，和为1','三种成分的相对平衡和组间位置','闭合组成不可直接当独立相关；不归一化输入。')
    rows=[]
    for c in ['1','2','3','4']:
        for j in range(70):
            pos=(j+1)*10000;score=.15+((j*17+int(c)*7)%38)/10
            if c=='2':score+=4*np.exp(-((pos-350000)/95000)**2)
            rows.append(dict(variant_id=f'V{c}_{j:02}',chromosome=c,position=pos,pvalue=10**(-score)))
    genome=pd.DataFrame(rows)
    add('E28',scale.plot_genome_overview,genome,dict(chromosome_order=['1','2','3','4'],chromosome_lengths={c:720000 for c in ['1','2','3','4']},segment_slots={'1':'G1','2':'G7','3':'G1','4':'G7'},assembly='SYNTHETIC assembly; not a human build',coordinate_definition='Supplied one-based synthetic position',thresholds={'Illustrative threshold':1e-5},title='Global association overview'),'全局位置关联：Manhattan形式','变异ID、染色体、位置、已有p；明确版本、段长度及阈值','全基因组已有信号位置与局部聚集','不做GWAS、LD计算、clumping或自动挑选lead。')
    locus=[];q=genome[(genome.chromosome=='2')&(genome.position.between(220000,480000))]
    for i,r in enumerate(q.itertuples()):locus.append(dict(record_type='association',variant_id=r.variant_id,position=r.position,pvalue=r.pvalue,ld_r2=np.nan if i%9==0 else np.exp(-abs(r.position-350000)/85000)))
    locus += [dict(record_type='gene',gene_id='Gene A',start=235000,end=285000,strand='+',lane=0),dict(record_type='gene',gene_id='Gene B',start=310000,end=380000,strand='-',lane=1),dict(record_type='gene',gene_id='Gene C',start=405000,end=465000,strand='+',lane=0)]
    locus += [dict(record_type='recombination',position=float(x),rate=float(2+5*np.exp(-((x-420000)/27000)**2))) for x in np.linspace(220000,480000,45)]
    add('E29',scale.plot_locus_tracks,pd.DataFrame(locus),dict(position_limits=[220000,480000],chromosome='2',assembly='SYNTHETIC assembly',coordinate_definition='One-based synthetic positions',ld_reference='V2_34',ld_definition='Illustrative provided r2; no population genotype calculation',recombination_unit='Supplied rate',title='Selected region and independent tracks'),'局部关联＋LD＋重组率＋基因位置','同一位置体系中的关联、已有LD、重组率与基因跨度/方向','局部信号与多条轨道对应；未知LD单独标识','不把邻近基因当作用靶点，不推断共定位、外显子或调控。')
    studies=pd.DataFrame([dict(study_id=f'S{i+1:02}',group='G1' if i<9 else 'G7',estimate=float(.25+.06*np.sin(i)+(.02+i*.02)*np.cos(i*1.6)),se=float(.04+i*.017)) for i in range(18)])
    funnel=[dict(record_type='study',**r) for r in studies.to_dict('records')]
    funnel += [dict(record_type='guide',guide_id=name,estimate=float(.25+sign*1.96*s),se=float(s)) for name,sign in [('Left guide',-1),('Right guide',1)] for s in np.linspace(0,.36,35)]
    add('E30',scale.plot_funnel_result,pd.DataFrame(funnel),dict(reference_estimate=.25,effect_definition='Supplied difference',precision_definition='Supplied standard error',guide_definition='Given pseudo95% lines: reference +/-1.96 SE',title='Effect and precision'),'效应与精度：漏斗图','研究ID、效应、SE；给定参考值和两条参考边界坐标','效应估计与精度分布，核对小样本与不对称结构','不做合并估计、Egger或补齐；不对称不等于发表偏倚。')
    f=studies.assign(label=studies.study_id,lower=studies.estimate-1.96*studies.se,upper=studies.estimate+1.96*studies.se)
    add('E30b',pub.plot_publication_forest,f,dict(x_label='Supplied difference',interval_label='Given illustrative estimate +/-1.96 SE',effect_scale='difference',title='The same study effects'),'漏斗图对应研究森林图','同一研究ID、分组、效应及已有区间','精度图可回到每一研究的完整估计与区间','仅为已有通用森林图的配套输入示例。',mode='theme_wrapper')
    tree=[('All','ROOT','G1',100,0,0,1,1),('A','All','G1',60,0,0,.6,1),('B','All','G7',40,.6,0,1,1),('A1','A','G1',36,0,0,.6,.6),('A2','A','G1',24,0,.6,.6,1),('B1','B','G7',28,.6,0,1,.7),('B2','B','G7',12,.6,.7,1,1)]
    add('E31',scale.plot_hierarchy_partition,pd.DataFrame(tree,columns=['node_id','parent_id','group','value','x0','y0','x1','y1']),dict(root_id='All',quantity_definition='Supplied additive quantity',title='Hierarchy and proportional area'),'层级组成：矩形树图','唯一节点/父节点、正的可加数量和已给面积布局','各叶子占整体份额与层级归属','面积编码可加量；不可把父子值重复累加，不新做聚类。')
    fan=pd.DataFrame([dict(group=g,x=float(x),coverage=c,center=float(.3+x*.23+gi*.7),lower=float(.3+x*.23+gi*.7-w*(.2+x*.025)),upper=float(.3+x*.23+gi*.7+w*(.2+x*.025))) for gi,g in enumerate(['G1','G7']) for x in np.arange(11) for c,w in [(.5,.65),(.8,1.28),(.95,1.96)]])
    add('E32',scale.plot_uncertainty_fan,fan,dict(coverage_order=[.5,.8,.95],interval_definition='Supplied illustrative nested prediction intervals',x_label='Supplied time',y_label='Supplied response',title='Nested uncertainty'),'多层不确定性：扇形区间','组×有序X×区间覆盖率；已有中心和相互嵌套上下界','中央轨迹与不同覆盖范围','区分CI/预测区间/可信区间；不估计或预测。')
    spatial=[]
    for y in range(35):
        for x in range(42):
            v=.92-.06*np.cos(x*.3)*np.sin(y*.3);spatial.append(dict(record_type='pixel',x=x,y=y,red=v,green=v*.985,blue=v*.97))
    spatial += [dict(record_type='spot',object_id=f'P{j*8+i:02}',group='G1' if i<4 else 'G7',x=4+i*4.5,y=3+j*4,radius=1.15,value=float(3*(i+j)/13)) for j in range(7) for i in range(8)]
    for suffix,mode in [('a','categorical'),('b','continuous')]:
        add('E33'+suffix,scale.plot_spatial_overlay,pd.DataFrame(spatial),dict(mode=mode,pixel_size=5,physical_unit='um',background_definition='Procedural neutral software background, not tissue histology',value_limits=[0,3],value_label='Supplied feature',title='Registered spot '+mode),'空间背景＋'+('类别' if suffix=='a' else '连续特征'),'RGB像素、同一配准体系的对象中心与物理半径、像素尺度、类别/特征','同一物理位置的身份与测量','此背景不是H&E；不做配准、分割或反卷积。')
    effects=[]
    for i in range(76):
        x=float(rng.normal(0,.9));y=float(.65*x+rng.normal(0,.55));qx=.01 if i%3==0 else .2;qy=.015 if i%4==0 else .3
        status='Both' if qx<=.05 and qy<=.05 else 'X only' if qx<=.05 else 'Y only' if qy<=.05 else 'Neither'
        effects.append(dict(feature_id=f'F{i+1:02}',status=status,effect_x=x,effect_y=y,q_x=qx,q_y=qy))
    add('M01',multi.plot_cross_effects,pd.DataFrame(effects),dict(x_label='RNA: supplied log2 change',y_label='Protein: supplied log2 change',comparison_definition='Mapped feature identity; same synthetic comparison, explicit separate assay units',alpha=.05,label_ids=[],title='RNA and protein effects'),'跨层效应一致性：四证据状态','映射后共同特征ID、两层效应及各自q、相同对比方向','同向/异向与每层独立的显著证据状态','不同层单位要明示；不把共有名单或同向作为因果。')
    variance=pd.DataFrame([dict(feature=v,sample=f'Factor {j+1}',value=float((1+i+j)%5/20+.02)) for i,v in enumerate(['RNA','Protein','ATAC']) for j in range(4)])
    add('M02',pub.plot_aligned_matrix,variance,dict(value_label='Supplied explained fraction',limits=[0,.3],signed=False,title='Factor variance by view'),'多组学因子：各层解释方差','模态×因子完整已给方差比例表、模型版本与缺失策略','每个因子在哪些层解释更多变异','复用通用矩阵；方差份额不作为各因子无条件可加量。',mode='theme_wrapper')
    loads=pd.DataFrame([dict(feature=f'{v}_{i+1}',sample=f'Factor {j+1}',value=float(np.sin((i+1)*(j+1)+vi)*.8),feature_block=v) for vi,v in enumerate(['RNA','Protein','ATAC']) for i in range(4) for j in range(4)])
    add('M03',pub.plot_aligned_matrix,loads,dict(value_label='Supplied signed loading',limits=[-1,1],signed=True,block_palette={'RNA':theme['palette_colors'][0],'Protein':theme['palette_colors'][6],'ATAC':theme['palette_colors'][2]},count_label='One supplied feature',title='Feature loadings, fixed factor order'),'因子载荷：模态分块矩阵','特征×因子权重、模态归属和固定因子方向','因子由哪些分子特征共同构成','复用通用块矩阵；因子符号任意，比较前冻结方向。',mode='theme_wrapper')
    views=[]
    for i in range(36):
        group='G1' if i<18 else 'G7';base=-1 if i<18 else 1;x=float(base+rng.normal(0,.3));y=float(rng.normal(0,.5))
        for vi,v in enumerate(['RNA','Protein','ATAC']):views.append(dict(object_id=f'U{i:02}',group=group,view=v,x=x+vi*.13*np.sin(i),y=y+vi*.08*np.cos(i)))
    add('M04',multi.plot_aligned_views,pd.DataFrame(views),dict(view_order=['RNA','Protein','ATAC'],coordinate_definition='Frozen assay-specific synthetic component scores; matched IDs',draw_links=True,title='Matched objects in separate view spaces'),'同对象多视图：独立分数轴＋身份连线','对象ID×2/3模态已有坐标、组别、明确配对/非配对','各模态的组间位置及对象对应','轴空间各自独立；连线只表示相同对象，不表示位移。')
    projection=pd.DataFrame([dict(feature_id=f'{v}{i+1}',group=v,x=float(.75*np.cos(vi*2+i*.32)),y=float(.75*np.sin(vi*2+i*.32))) for vi,v in enumerate(['RNA','Protein','ATAC']) for i in range(4)])
    add('M05',multi.plot_loading_projection,projection,dict(x_label='Correlation with component 1',y_label='Correlation with component 2',projection_definition='Supplied feature-component correlations, not arbitrary loadings',title='Cross-view selected feature correlations'),'跨组学特征圆：相关投影','特征ID、模态、与两个已给成分的相关坐标','不同模态特征指向哪些成分方向','坐标为相关而非任意载荷；不推断因果边或显著性。')
    spectra=pd.DataFrame([dict(peak_id=f'{s[0]}{i+1}',spectrum=s,mz=float(80+i*18+si*.7),intensity=float(10+80*np.exp(-((i-7)/3)**2)+15*(i%3))) for si,s in enumerate(['Observed','Reference']) for i in range(16)])
    add('M06',multi.plot_mass_spectrum,spectra,dict(spectrum_order=['Observed','Reference'],mass_definition='m/z',intensity_definition='Supplied intensity',normalization_definition='Given common arbitrary instrument scale; no normalization',mirror=True,label_peak_ids=[],title='Observed and reference peaks'),'质谱棒图与镜像比较','谱图ID、峰ID、m/z、非负强度、归一化/仪器/匹配说明','实测与参考碎片的位置和强度分布','不自动归一化、匹配、定结构；镜像负号仅排版。')
    curves=pd.DataFrame([dict(group=g,x=float(x),estimate=float((1+gi*.4)*np.exp(-((x-(5+gi*.4))/.7)**2)),lower=float((1+gi*.4)*np.exp(-((x-(5+gi*.4))/.7)**2)),upper=float((1+gi*.4)*np.exp(-((x-(5+gi*.4))/.7)**2))) for gi,g in enumerate(['G1','G7']) for x in np.linspace(2,8,70)])
    from figure_multimodal import plot_frozen_dynamics
    curves=curves.rename(columns={'group':'series','x':'time'})
    add('M07',plot_frozen_dynamics,curves,dict(time_label='Supplied retention time (min)',value_label='Supplied ion intensity',unit_label='Given software chromatogram',interval_label='No uncertainty band: supplied bounds equal center',title='Frozen chromatogram'),'色谱/离子流：通用有序曲线','曲线ID、有序保留时间及强度/明确已给区间','峰形、保留时间和不同条件的曲线位置','复用有序曲线；不提峰、积分、对齐或平滑。',mode='theme_wrapper')
    links=[dict(record_type='signal',track=v,start=i*1000,end=(i+1)*1000,value=float(.1+3*np.exp(-((i-8-vi*6)/2.5)**2))) for vi,v in enumerate(['RNA','ATAC','Protein']) for i in range(30)]
    links += [dict(record_type='link',link_id=f'L{i}',start=a,end=b,score=s) for i,(a,b,s) in enumerate([(5000,14000,.8),(9000,23000,.5),(19000,26000,.65)])]
    add('M08',multi.plot_genomic_links,pd.DataFrame(links),dict(track_order=['RNA','ATAC','Protein'],region=[0,30000],assembly='SYNTHETIC assembly',chromosome='segment A',coordinate_definition='zero-based half-open positions',value_definition='Common supplied display quantity, matched synthetic scale',link_definition='Given candidate association links and bounded scores; not direct regulation',title='Multi-layer signal and candidate links'),'基因组多轨道＋候选连接弧','已分箱不重叠信号、共同版本/坐标/单位、已有连接端点和分数','峰信号和候选跨位点连接','同图不同测量若单位不一致应分轴；不把弧线当调控因果。')
    nodes=[('A','Input',0,1,.7),('B','Pool A',1,1,-.6),('C','Pool B',2,1,.3),('D','Pool C',2,0,1.1),('E','Pool D',1,0,-.4),('F','Output',0,0,.5)]
    path=[dict(record_type='node',node_id=n,label=label,x=x,y=y,value=v) for n,label,x,y,v in nodes]
    path += [dict(record_type='edge',source=a,target=b,direction='known') for a,b in [('A','B'),('B','C'),('C','D'),('D','E'),('E','B'),('E','F')]]
    add('M09',multi.plot_pathway_overlay,pd.DataFrame(path),dict(node_limits=[-1.5,1.5],node_value_definition='Supplied log2 abundance change',edge_definition='Fixed fictional pathway topology; arrows are known-map order only',title='Abundance on a fixed pathway map'),'通路底图叠加分子数量','明确节点ID/坐标/已有数值和已知拓扑、边证据','将数量变化定位到功能图中的位置','箭头为已有底图；不把丰度画成通量或补完整机制。')
    from figure_core import plot_composition
    iso=[]
    for j,g in enumerate(['G1','G7']):
        vals=[.6,.2,.15,.05] if j==0 else [.4,.25,.25,.1]
        for i,v in enumerate(vals):iso.append(dict(sample=g,celltype=f'M+{i}',count=int(v*1000)))
    add('M10',plot_composition,pd.DataFrame(iso),dict(y_label='Fraction of supplied isotopologue counts'),'同位素组成：已有堆积通用画法','样本×M+i已给数量；总计数和分母、校正状态','各样本标记组成','仅示意通用组成；M+i份额不等于绝对浓度或代谢通量。',mode='theme_wrapper')
    from statistics import NormalDist
    residual=rng.normal(0,1,48);diagnostics=pd.DataFrame(dict(unit_id=[f'D{i:02}' for i in range(48)],group=['G1' if i<24 else 'G7' for i in range(48)],fitted=np.linspace(-2,2,48),residual=residual*.8,standard_residual=residual,leverage=np.linspace(.01,.18,48),cook=(residual**2)*np.linspace(.01,.18,48)/4,reference_quantile=[NormalDist().inv_cdf((i+.5)/48) for i in range(48)],ordered_residual=np.sort(residual)))
    for suffix,mode in zip('abcd',['residual','qq','scale_location','influence']):
        add('M11'+suffix,multi.plot_diagnostic_panel,diagnostics,dict(mode=mode,model_definition='One frozen synthetic diagnostic output; no research regression fitted',reference_definition='Supplied standard-normal (i+0.5)/48 quantiles',cook_area_scale=180,title='Frozen model: '+mode),'同一模型诊断：'+mode,'对象ID、已有拟合值/残差/标准残差、leverage、Cook、参考分位与已排序残差','同时检查残差形态、分布、尺度和高影响对象','四个模式复用同一表；不拟合模型或平滑，不自动删除高影响对象。')
    return theme,dict(sorted(cases.items()))


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
    theme,cases=multiview_cases();(a.output/'project_theme.json').write_text(json.dumps(theme,indent=2),encoding='utf8');records=[]
    for id_,c in cases.items():
        fig=draw_case(c,theme);audit=audit_panel_layout(fig)
        if audit['issues']:raise ValueError(id_+' '+str(audit['issues']))
        meta=dict(source='Original deterministic bounded software fixture, seed 2026100520',palette=theme['palette_name'],input_unit=c['data_required'],experimental_unit='Synthetic display objects, no biological inference',contrast='Explicit frozen-table software demonstration',denominator='Declared in figure_spec',model='No research model fitted',limits='Explicit fixed renderer settings',filtering='Complete fixture, no aesthetic exclusions',uncertainty='Illustrative supplied intervals only',interpretation_limit=c['limitations'],synthetic=True,layout_audit=audit)
        paths=core.export_figure(fig,c['data'],a.output/'figures',id_,meta);plt.close(fig)
        record={k:v for k,v in c.items() if k not in ['function','data','params']};record.update(id=id_,module=c['function'].__module__,function=c['function'].__name__,params=c['params'],rows=len(c['data']),numeric_columns=[x for x in c['data'] if pd.api.types.is_numeric_dtype(c['data'][x])],output={f.name:core.file_sha256(f) for f in paths})
        (a.output/'figures'/id_/(id_+'.style.json')).write_text(json.dumps(dict(module=record['module'],function=record['function'],theme_mode=c['theme_mode'],params=c['params']),ensure_ascii=False,indent=2),encoding='utf8')
        records.append(record);print(id_+' rendered',flush=True)
    (a.output/'increment_manifest.json').write_text(json.dumps(dict(schema_version=1,synthetic=True,scientific_analysis=False,records=records),ensure_ascii=False,indent=2),encoding='utf8')


if __name__=='__main__':main()
