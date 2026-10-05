"""Small deterministic software fixtures; never substitute these for research data."""
from pathlib import Path
import argparse, json, hashlib
from statistics import NormalDist
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import figure_method_extensions as methods
import figure_core as core
import figure_general as general
import figure_publication as publication
import figure_network_extensions as network
from project_theme import create_theme, render_with_theme, render_panel, apply_project_style
from panel_layout_audit import audit_panel_layout


def fixture_cases():
    rng=np.random.default_rng(2026100511)
    slots={f'G{i+1}':i for i in range(7)}|{'CT1':2,'CT2':3,'CT3':5,'Set A':0,'Set B':3,'Before':0,'After':6}
    slots.update({'Neither':3,'X only':0,'Y only':4,'Both':6,'RNA':0,'Protein':6,'ATAC':2,'Metabolite':4,'Observed':0,'Reference':6,'M+0':0,'M+1':2,'M+2':4,'M+3':6})
    theme=create_theme('figure-library-v0.2-preview','card_06',slots,font_family='Arial')
    cases={}
    def add(id_,fn,d,params,title,requires,expression,how,boundary,mode='theme_argument'):
        cases[id_]={'function':fn,'data':d,'params':params,'title':title,'data_required':requires,'expression':expression,'how_to_draw':how,'limitations':boundary,'theme_mode':mode}
    labels=['component adhesion','intracellular signaling','response to external stimulus','matrix organization','cellular transport','regulation of growth','response to stress','protein interaction','membrane trafficking','catalytic activity','binding affinity','ion transport']
    effects={f'F{i+1:02}':float(np.sin(i*.65)*1.8+.10) for i in range(24)};circle_data={};keys={}
    for k,block in enumerate(['BP','MF','CC','PW']):
        rows=[];key=[];order=[block+f'{i+1:02}' for i in range(6)]
        for i,t in enumerate(order):
            genes=[f'F{(i*3+j+k*2)%24+1:02}' for j in range(7)]
            val=np.array([effects[g] for g in genes]);z=float((np.sum(val>0)-np.sum(val<0))/np.sqrt(len(val)))
            rows.append(dict(record_type='term',term_id=t,padj=10**(-float(1.4+(i+k)%6*.65)),zscore=z))
            rows.extend(dict(record_type='member',term_id=t,gene_id=g,effect=effects[g]) for g in genes)
            key.append(dict(term_id=t,description=labels[(i+k*2)%len(labels)]))
        d=pd.DataFrame(rows);circle_data[block]=d;keys[block]=pd.DataFrame(key)
        add(f'E{k+2:02}',methods.plot_term_effect_circle,d,dict(term_order=order,effect_limits=[-2,2],zscore_limits=[-3,3],significance_max=6,zscore_definition='Descriptive GOplot-style (n_up - n_down)/sqrt(n_members); supplied by the fixture, not calculated by the renderer',effect_label='Supplied log2 fold change',title=block+' terms and member effects'),
            block+' 环形富集－成员效应轨道','术语ID、校正p、方向分数；明确术语-成员关系和每个成员的效应值',
            '内圈显著性高度与方向色；外圈每个成员的效应分布',
            '内圈高度=-log10校正p，颜色=已给方向分数；外圈径向坐标=效应，角度仅用于排布',
            '方向分数不是默认统计检验；零p不接受，不补生成员或推断leading-edge。')
        add('E06'+chr(97+k),methods.plot_term_key,keys[block],dict(title=block+' term key'),
            block+' 术语ID－描述对照表','一行一个唯一术语ID和已有完整说明','读出环形轨道、网络或点阵使用的ID对应何种条目',
            '输入原顺序；独立表格，行高与字号固定；不自动查询或截断定义','描述来自上游；长内容拆为附表，不缩成不可读的小字。')
    rows=[];columns=[f'{g}/{c}' for g in ['G1','G7'] for c in ['CT1','CT2','CT3']];terms=[]
    for block in ['BP','MF','PW']:
        lookup=keys[block].set_index('term_id').description.to_dict()
        for r in circle_data[block].query("record_type == 'term'").itertuples():
            i=len(terms);terms.append(r.term_id)
            for j,col in enumerate(columns):
                g,c=col.split('/');status='reported' if j==0 else 'not_tested' if (i+j)%17==0 else 'tested_absent' if (i+2*j)%6==0 else 'reported'
                rows.append(dict(term_id=r.term_id,term_label=lookup[r.term_id],block='KEGG' if block=='PW' else block,column_id=col,group=g,cell_class=c,status=status,padj=float(r.padj) if j==0 else 10**(-float(1.2+(i+j)%8*.56)) if status=='reported' else np.nan,gene_ratio=7/40 if j==0 else float(.04+((i*3+j)%6)*.033) if status=='reported' else np.nan))
    add('E01',methods.plot_enrichment_grid,pd.DataFrame(rows),dict(significance_limits=[0,6],ratio_max=.25,block_slots={'KEGG':'G1','BP':'G7','MF':'G3'},column_order=columns,term_order=terms,title='Terms across groups and cell classes'),
        '分组富集点阵：形状＋面积＋显著性＋分类条','完整术语×组别/亚类点阵；term_id、block、status、校正p、GeneRatio及列身份',
        '同一术语在各条件是否报告、报告的比例和证据量；显式区分未报告与未检验',
        '共享显著性范围；组形状归一化填充面积；顶部两层身份条，术语与图例各有独立区域',
        '本例G1/CT1的BP/MF/PW术语ID、p与环形图对应，GeneRatio=7/40；其他列另给合成结果。不计算富集或FDR。')
    membership=pd.DataFrame([dict(object_id=f'F{i+1:02}',**{'Set A':int(i<16),'Set B':int(i>=8)}) for i in range(24)])
    add('E07',methods.plot_two_set_overlap,membership,dict(set_columns=['Set A','Set B'],unit_label='Unique supplied feature IDs',title='Two explicit sets'),
        '两个集合的交集、独有数与比例','完整对象ID×两个集合的0/1成员关系；并集中的对象一行一次','读出两个集合的独有项和共同项数量',
        '用成员表精确计数，百分比分母为并集；等面积示意圆不编码集合大小','面积不是比例；三个以上集合用现有UpSet；全零对象应另声明背景总体。')
    bp=circle_data['BP'];edges=bp[bp.record_type=='member'][['gene_id','term_id','effect']].copy();go=list(pd.unique(edges.gene_id));to=list(pd.unique(edges.term_id))
    add('E08',methods.plot_gene_term_chord,edges,dict(gene_order=go,term_order=to,effect_limits=[-2,2],effect_label='Supplied log2 fold change',title='Members connected to terms'),
        '成员－术语弦图：关系＋成员效应色','去重的成员-术语边表，每个成员已有效应与明确显示顺序','看哪些术语共享成员，并查出这些成员的效应方向',
        '成员扇区按效应着色，每条关系等宽；扇区与外置名称保持映射','弦宽不表示作用强度，关系不代表因果；最多24成员、8术语，过密改矩阵。')
    mr=[]
    for g in go:
        count=int((edges.gene_id==g).sum())
        for t in to:mr.append(dict(feature=g,sample=t,value=int(((edges.gene_id==g)&(edges.term_id==t)).any()),row_count=count,feature_block='G7' if effects[g]>0 else 'G1'))
    add('E09',publication.plot_aligned_matrix,pd.DataFrame(mr),dict(value_label='Explicit membership (0 or 1)',limits=[0,1],signed=False,block_palette={'G1':theme['palette_colors'][0],'G7':theme['palette_colors'][6]},count_label='Term memberships',continuous_colors=theme['continuous']['sequential'],title='The same member-term links'),
        '成员关系矩阵＋方向条＋成员覆盖数','完整成员×术语的0/1矩阵；方向标签与已计数的覆盖数','弦图中相同关系的精确逐格查询和成员覆盖度',
        '复用通用注释矩阵入口；保持同一成员和术语順序；颜色是成员关系状态','零必须是已知不属于该集合；缺失成员关系不能填成零。',mode='theme_wrapper')
    dist=[];qq=[];density=[]
    x=np.linspace(-3.5,3.5,110)
    for j,g in enumerate(['G1','G3','G7']):
        reference=np.array([NormalDist().inv_cdf((i+1)/29) for i in range(28)])
        values=reference*(1+j*.12)+(j-1)*.5
        dist.extend(dict(group=g,x=float(v),y=float((i+1)/len(values))) for i,v in enumerate(values))
        qq.extend(dict(group=g,x=float(v),y=float(y)) for v,y in zip(reference,values))
        den=np.exp(-.5*((x-(j-1)*.5)/(1+j*.12))**2)/(np.sqrt(2*np.pi)*(1+j*.12))
        density.extend(dict(group=g,x=float(v),density=float(z)) for v,z in zip(x,den))
    add('E10',methods.plot_distribution_result,pd.DataFrame(dist),dict(mode='ecdf',x_label='Supplied measurement',y_label='Supplied cumulative fraction',title='Frozen empirical cumulative steps'),
        '已有经验累积分布 ECDF','组别×升序量值×已有累计概率','全分布位置、尾部和跨组差异；不依赖分箱','输入阶梯坐标原顺序，累计概率不重新拟合',
        '重复观测和权重须在上游处理；有删失的数据不能冒充普通经验CDF。')
    add('E11',methods.plot_distribution_result,pd.DataFrame(qq),dict(mode='qq',x_label='Supplied reference quantile',y_label='Supplied observed quantile',reference_distribution='Given standard normal quantiles at j/29 compared to the same 28 observations as E10; no fitted distribution',title='Matched quantiles'),
        '已有分位数对照 QQ','参考分位数与观测分位数的配对坐标；参考分布定义','偏移、尺度差异和尾部偏离','复用分布结果入口，散点与等值线；不拟合回归线',
        '图本身不进行正态性检验；坐标已标准化与否需明确。')
    add('E12',general.plot_density_ridges,pd.DataFrame(density),dict(palette={g:None for g in ['G1','G3','G7']},x_label='Supplied measurement',density_label='Supplied normalized density',height_scale=1.8,title='Distribution ridges'),
        '密度山脊：统一尺度的多组分布','组别×共用x网格×已有非负密度，密度定义与带宽','多组的位置、宽度及分布形状','复用旧山脊函数，用同一个高度乘数，不单组峰值归一','本例为生成E10/E11样本的解析模型密度，不是样本拟合；不同归一化或带宽不直接比较。',mode='theme_wrapper')
    balance=pd.DataFrame([dict(covariate=c,group=g,smd=float((j+1)*.038*(-1 if j%2 else 1)*(1 if g=='Before' else .22))) for j,c in enumerate(['Age','Baseline value','Exposure level','Score A','Score B','Follow-up']) for g in ['Before','After']])
    add('E13',methods.plot_balance,balance,dict(stage_order=['Before','After'],threshold=.1,metric_definition='Supplied signed SMD with the same declared standardizing denominator in both stages',title='Covariate balance across stages'),
        '协变量平衡 Love 图','协变量×调整阶段×已有SMD，SMD分母与参考阈值','逐协变量诊断调整前后的观测平衡变化','同一协变量横线连已有阶段值；双侧阈值线独立于数据','只诊断已观测变量；不能证明不存在未观测混杂或因果可识别。')
    agreement=pd.DataFrame([dict(object_id=f'O{i+1:03}',group='G1' if i%2 else 'G7',mean=float(6+i*.16),difference=float(.35+np.sin(i*1.4)*1.1+np.cos(i*.37)*.35)) for i in range(76)])
    add('E14',methods.plot_agreement,agreement,dict(bias=.35,loa=[-1.2,1.9],unit_label='One paired object per row; synthetic fixture',difference_definition='Method B - Method A',title='Agreement of paired measurements'),
        'Bland–Altman：差值＋已有限界','同对象配对平均值、差值；已有偏倚、上下相合限界和单位定义','量程相关偏差与个体差值分布','保留已有平均和差值坐标，水平线直接读取已审查的偏倚/限界','相关不等于相合；重复测量的限界需匹配其设计，不在绘图时重算。')
    surv=[];swim=[]
    for g,ends in [('G1',[6,12,15,18,21,24]),('G7',[5,10,13,17,20,23])]:
        # Fixed six-object illustration: events at positions 0/2/4, censored ends
        # at 1/3/5. Steps are supplied and consistent; bands are illustrative.
        pp=[1,5/6,5/6,5/8,5/8,5/16,5/16];tt=[0,*ends]
        if tt[-1]<24:tt.append(24);pp.append(pp[-1])
        for t,p in zip(tt,pp):surv.append(dict(record_type='step',group=g,time=t,survival=p,lower=max(0,p-.16) if t else 1,upper=min(1,p+.16) if t else 1))
        for t in [0,6,12,18,24]:surv.append(dict(record_type='risk',group=g,time=t,at_risk=sum(e>t for e in ends)))
        for i,end in enumerate(ends):
            id_=g+'-'+str(i+1);swim.append(dict(record_type='interval',object_id=id_,group=g,start=0,end=end))
            event='Recorded event' if i%2==0 else 'Censored end';swim.append(dict(record_type='event',object_id=id_,time=end,event=event))
            if i%2:surv.append(dict(record_type='censor',group=g,time=end,survival=pp[i+1]))
    add('E15',methods.plot_survival_result,pd.DataFrame(surv),dict(time_label='Elapsed time (supplied unit)',risk_convention='end_of_period',interval_definition='Supplied illustrative pointwise uncertainty band',title='Supplied survival steps and support'),
        '已有生存阶梯＋区间＋风险人数','阶梯时间、S(t)、上下界；指定时点风险人数；删失标记另行提供','随时间的概率变化、不确定性与仍被随访的人数','阶梯和区间使用相同post定义；风险人数独立下轨，指定期初/期末口径','不拟合KM或log-rank；本入口不支持风险集重新进入。')
    sd=pd.DataFrame(swim)
    add('E16',methods.plot_swimmer,sd,dict(time_label='Elapsed time (supplied unit)',event_shapes={'Censored end':'|','Recorded event':'D'},object_order=list(pd.unique(sd.object_id)),title='The same twelve individual follow-up intervals'),
        '个体随访 Swimmer：区间＋记录事件','对象ID、组、随访开始/结束；事件时间、类型与显示顺序','个体随访长度、断续区间和事件时序','绘制已有区间；形状表示已记录事件；事件不得超出随访区间','不从区间拟合生存模型；断续区间不是连续暴露，删失类型须声明。')
    specifications=[];so=[f'S{i+1:02}' for i in range(16)];dec=['Covariate set B','Restricted cohort','Alternative endpoint','Robust estimator']
    for i,s in enumerate(so):
        v=float(-.10+i*.035+np.sin(i)*.06);specifications.append(dict(record_type='estimate',spec_id=s,estimate=v,lower=v-.13,upper=v+.13))
        for j,de in enumerate(dec):specifications.append(dict(record_type='decision',spec_id=s,decision=de,included=(i//2**j)%2))
    add('E17',methods.plot_specification_curve,pd.DataFrame(specifications),dict(spec_order=so,decision_order=dec,effect_scale='difference',interval_definition='Supplied illustrative estimate intervals',title='Reviewed specifications and model decisions'),
        '规范曲线：估计区间＋模型选择矩阵','规格ID、已有估计/区间，以及完整规格×模型决策0/1表','查看分析选择与结果变动的对应关系','上方估计区间，下方决策点阵严格同一规格顺序；无静默按显著性挑选','展示不等于联合稳健性推断；备选规格应科学合理并提前界定。')
    vectors=[]
    for i in range(140):
        a=i*.31;radius=.3+(i%11)*.065;xv=float(np.cos(a)*radius+(i%2)*1.6);yv=float(np.sin(a)*radius)
        vectors.append(dict(object_id=f'C{i+1:03}',group='G1' if i%2 else 'G7',x=xv,y=yv,vx=float(.15-.08*yv),vy=float(.08*np.cos(a))))
    vec=pd.DataFrame(vectors)
    add('E18',methods.plot_vector_field,vec,dict(arrow_scale=1,vector_definition='Already projected synthetic dx/dy per supplied time unit',coordinate_definition='Frozen synthetic 2D coordinates, not a newly calculated UMAP',title='Given local directions on fixed coordinates'),
        '已有二维向量场＋身份分组','对象ID、已有x/y、vx/vy、身份，以及投影与向量单位定义','坐标中已计算局部方向与幅度','直接画已有向量；不重新投影、不平滑、不积分流线','二维方向不能单独证明轨迹、时间顺序或因果；RNA velocity另需其分析输入与模型。')
    bivariate=pd.DataFrame([dict(row=f'R{i+1}',column=f'C{j+1}',metric_x=float((i+j)%6*.16+.05),metric_y=float((i*2+j)%6*.16+.05)) for i in range(8) for j in range(9)])
    add('E19',methods.plot_bivariate_tiles,bivariate,dict(x_breaks=[0,.33,.66,1],y_breaks=[0,.33,.66,1],x_label='Metric X',y_label='Metric Y',title='Two metrics in the same cells'),
        '双变量格网＋二维色键','完整行×列单元；两种连续量及各自明确分箱边界','识别两个指标同时高、低或不一致的位置','两维分箱映射课题角色色的明确混合色键；同格保留两个原值','混合色是另行说明的扩展，不是原色卡；不能代替精确数值或显著性。')
    missing=pd.DataFrame([dict(row=f'Variable {i+1}',column=f'O{j+1:02}',states='Not tested' if (i+j)%11==0 else 'Missing' if (i*2+j)%7==0 else 'Observed') for i in range(8) for j in range(16)])
    add('E20',network.plot_multistate_matrix,missing,dict(state_order=['Observed','Missing','Not tested'],state_slots={'Observed':'G1','Missing':'G7','Not tested':'G4'},title='Explicit recorded availability'),
        '缺失模式矩阵：复用多状态矩阵','完整对象×变量的已记录状态；Observed/Missing/Not tested明确区分','检查缺失聚集和未检验的范围','复用已有状态矩阵入口，以类别状态绘制，不把缺失插补为零','图不判断MCAR/MAR/MNAR；状态定义和对象总体由上游提供。')
    estimates=pd.DataFrame([dict(label=('Before' if i<4 else 'After')+f' / Model {i%4+1}',group='Before' if i<4 else 'After',estimate=float(v),lower=float(v-.24),upper=float(v+.22)) for i,v in enumerate([.45,-.3,.18,.64,-.25,.32,.05,-.10])])
    for id_,d,scale in [('E21',estimates,'difference'),('E22',estimates.assign(estimate=np.exp(estimates.estimate),lower=np.exp(estimates.lower),upper=np.exp(estimates.upper)),'ratio')]:
        add(id_,publication.plot_publication_forest,d,dict(palette={'Before':None,'After':None},x_label='Supplied difference' if scale=='difference' else 'Supplied ratio (log axis)',interval_label='Full supplied intervals; illustrative fixture',effect_scale=scale,title='Compact estimates and intervals'),
            '紧凑森林图＋完整估计与区间'+('（差值）' if scale=='difference' else '（比值）'),'每行标签、身份、已有点估计和上下界；差值/对数比值/比值尺度',
            '逐行对比效应方向、大小与区间，精确读出所有数值','统一森林图入口；独立标签、区间和完整数字栏，比值用对数轴','区间定义必须已给；森林图不自动做meta分析或替换统计模型。',mode='theme_wrapper')
    node_rows=[dict(record_type='node',node_id=g,label=g,entity_type='term',group=['G1','G3','G7','G2','G4','G6'][i],x=float(np.cos(i*np.pi/3)),y=float(np.sin(i*np.pi/3)),area=90) for i,g in enumerate(to)]
    sets={t:set(edges.loc[edges.term_id==t,'gene_id']) for t in to}
    frozen_pairs=[(a,b,len(sets[a]&sets[b])/len(sets[a]|sets[b])) for i,a in enumerate(to) for b in to[i+1:] if len(sets[a]&sets[b])/len(sets[a]|sets[b])>=.15]
    node_rows.extend(dict(record_type='edge',source=a,target=b,weight=w,sign=0) for a,b,w in frozen_pairs)
    add('E23',network.plot_typed_network,pd.DataFrame(node_rows),dict(edge_label='Supplied Jaccard overlap',node_area_label='Constant term display area',relation_semantics='overlap',shape_map={'term':'D'},title='Selected term redundancy'),
        '已核验集合重叠网络：复用通用网络','已有term集合两两Jaccard边表、固定坐标、身份和显示面积','选定条目的成员重叠与冗余，保留所有条目','复用多实体网络入口；无方向边宽读取已有Jaccard','与E08/E09同一BP成员边表，合成集合的Jaccard另通过Biomni实算核对；不提供富集检验，不删冗余term。')
    xy=agreement.rename(columns={'object_id':'unit_id'}).assign(x=agreement['mean']-agreement.difference/2,y=agreement['mean']+agreement.difference/2)[['unit_id','group','x','y']]
    add('E24',general.plot_xy_points,xy,dict(palette={'G1':None,'G7':None},x_label='Method A',y_label='Method B',unit_label='Same paired synthetic objects as E14'),
        '配对测量的XY位置：复用通用散点','每个配对对象的两种已有量值、身份和唯一ID','两种测量的取值范围与关系，和差值相合图联合查看','复用通用散点；图例外置；不重新拟合相关或回归','XY关系不能代替相合性，散点不构成独立样本设计。',mode='theme_wrapper')
    embedding=vec.rename(columns={'object_id':'cell_id'})[['cell_id','x','y','group']].copy()
    add('E25',core.plot_embedding,embedding,dict(palette={'G1':None,'G7':None},axis_prefix='Stored coordinate'),
        '相同对象的身份坐标：复用分类坐标','对象ID×同一x/y×明确身份','向量和marker数据对应哪个已有亚群或身份','复用已有分类坐标入口；保持与E18/E26相同对象与坐标','本图不计算PCA/UMAP，也不重新注释亚群。',mode='theme_wrapper')
    features=pd.DataFrame([dict(cell_id=r.cell_id,x=r.x,y=r.y,feature=f'Feature {j+1}',value=float((1+np.sin(r.x*(j+1)+r.y))/2*3)) for r in embedding.itertuples() for j in range(3)])
    add('E26',publication.plot_feature_facets,features,dict(value_label='Supplied feature value',limits=[0,3],continuous_colors=theme['continuous']['sequential'],point_size=8,title='Same objects, fixed feature coordinates'),
        '相同对象的marker分面：复用特征坐标','完整对象×特征表；同对象每个特征坐标完全一致、已有非负特征值','每个身份中的已有连续特征位置，与分类/向量图共同查询','复用现有特征分面；共用色标范围，同一课题顺序色阶','不从颜色判断注释真实性；不插补表达，不计算向量或新坐标。',mode='theme_wrapper')
    return theme,dict(sorted(cases.items()))


def draw_case(case,theme):
    if case['theme_mode']=='theme_wrapper':
        fig=render_with_theme(case['function'],case['data'],case['params'],theme)
        fig._omics_spec['demo_label_style']='compact'
        if case['function'] in [general.plot_xy_points,core.plot_embedding,core.plot_composition,general.plot_grouped_estimates] or case['function'].__name__=='plot_frozen_dynamics':
            fig.set_layout_engine(None);ax=fig.axes[0];ax.set_position([.12,.30,.60,.50] if case['function'].__name__=='plot_frozen_dynamics' else [.12,.20,.60,.62]);legend=ax.get_legend()
            if legend:legend.set_bbox_to_anchor((1.07,1));legend.set_loc('upper left')
            fig.canvas.draw()
        elif case['function']==general.plot_density_ridges:
            fig.set_layout_engine(None);fig.axes[0].set_position([.15,.20,.76,.63])
        return fig
    fig=case['function'](case['data'],theme,**case['params'])
    if fig._suptitle is not None and fig._suptitle.get_text().startswith('SYNTHETIC DEMO'):fig._suptitle.set_text('')
    fig._omics_spec['demo_label_style']='compact'
    return fig


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(exist_ok=False)
    theme,cases=fixture_cases();(a.output/'project_theme.json').write_text(json.dumps(theme,indent=2),encoding='utf8');records=[]
    for id_,case in cases.items():
        fig=draw_case(case,theme);audit=audit_panel_layout(fig)
        if audit['issues']:raise ValueError(id_+' guide layout '+str(audit['issues']))
        meta=dict(source='Original deterministic software fixture; seed 2026100511',palette=theme['palette_name'],input_unit=case['data_required'],experimental_unit='Synthetic display objects; no biological inference',contrast='Synthetic illustration of frozen-result visual grammar',denominator='All supplied fixture records; explicit membership denominators where stated',model='No research analysis model fitted',limits='Explicit renderer settings in figure_spec',filtering='No aesthetic exclusions; complete fixture retained',uncertainty='Supplied illustrative intervals, not research confidence intervals',interpretation_limit=case['limitations'],synthetic=True,layout_audit=audit)
        paths=core.export_figure(fig,case['data'],a.output/'figures',id_,meta);plt.close(fig)
        settings={k:v for k,v in case['params'].items() if k!='palette'}
        record={k:v for k,v in case.items() if k not in ['function','data','params']};record.update(id=id_,module=case['function'].__module__,function=case['function'].__name__,params=settings,numeric_columns=[c for c in case['data'] if pd.api.types.is_numeric_dtype(case['data'][c])],rows=len(case['data']),output={f.name:core.file_sha256(f) for f in paths})
        (a.output/'figures'/id_/(id_+'.style.json')).write_text(json.dumps(dict(module=record['module'],function=record['function'],theme_mode=record['theme_mode'],params=case['params']),ensure_ascii=False,indent=2),encoding='utf8')
        records.append(record);print(id_+' rendered',flush=True)
    (a.output/'increment_manifest.json').write_text(json.dumps({'schema_version':1,'synthetic':True,'scientific_analysis':False,'records':records},ensure_ascii=False,indent=2),encoding='utf8')
    print(str(len(records))+' independent frozen-table exports')

if __name__=='__main__':main()
