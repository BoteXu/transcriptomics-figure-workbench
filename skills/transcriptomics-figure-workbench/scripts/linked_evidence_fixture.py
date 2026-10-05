"""Bounded synthetic examples for linked membership and hierarchy displays.

This prepares illustrative frozen numbers. It does not run WGCNA, enrichment,
clustering, docking or target screening. Every composition panel uses saved data.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import figure_linked_evidence as linked
import figure_method_extensions as methods
import figure_network_extensions as network
import figure_general as general
import figure_publication as publication

def linked_cases():
    cases={};members=[f'F{i+1:02}' for i in range(20)];termids=[f'T{i+1:02}' for i in range(8)]
    def add(id_,adapter,fn,data,params,title,requires,expression,boundary,family='G14',mode='argument'):
        if fn is general.plot_xy_points:
            params=dict(params,palette={g:None for g in data.group.unique()})
        cases[id_]=dict(adapter=adapter,function=fn,data=data,params=params,title=title,data_required=requires,expression=expression,limitations=boundary,family=family,theme_mode=mode)
    terms=[];links=[]
    for i,t in enumerate(termids):
        ids=[members[(i*2+j)%20] for j in range(5+i%3)]
        terms.append(dict(record_type='term',term_id=t,label=['Adhesion','Transport','Signaling','Stress response','Matrix structure','Cell organization','Binding','Catalytic activity'][i],block=(['BP']*4+['CC']*2+['MF']*2)[i],ratio=len(ids)/20,padj=10**(-1.5-i*.28),count=len(ids)))
        links.extend(dict(record_type='link',member_id=id_,term_id=t) for id_ in ids)
    membership=pd.DataFrame([dict(record_type='member',member_id=id_,effect=float(np.sin(i*.8)*1.6)) for i,id_ in enumerate(members)]+terms+links)
    add('E34','membership_ribbons',linked.plot_membership_ribbons,membership,dict(member_order=members,term_order=termids,block_slots={'BP':'G1','CC':'G3','MF':'G7'},effect_limits=[-2,2],significance_limits=[0,4],ratio_max=.4,ratio_definition='Ratio = displayed members / 20 supplied background members',title='Membership links and term measurements'),'成员流线、条目与评分点阵','成员与条目ID、二元关系、成员效应、条目类别、已给比例/校正p/成员数','共享成员连接到哪些条目，并对齐读取条目的量值与覆盖数','等宽连接不表示流量或作用强度；不计算富集。',family='G15')
    sets=pd.DataFrame([dict(object_id=id_,**{'G1':int(i<14),'G7':int(i>=6)}) for i,id_ in enumerate(members)])
    add('c37_sets','two_set_overlap',methods.plot_two_set_overlap,sets,dict(set_columns=['G1','G7'],unit_label='Unique supplied feature IDs',title='Intersection of two declared sets'),'集合交集','完整对象与两集合0/1关系','交集与独有数量','示意圆面积不编码数量。',family='G45')
    bar=[]
    for t in terms:
        for s in ['G1','G3','G7']:bar.append(dict(object_id=t['term_id'],segment=s,value=-np.log10(t['padj']) if s=={'BP':'G1','CC':'G3','MF':'G7'}[t['block']] else 0))
    add('c37_terms','stacked_values',linked.plot_stacked_values,pd.DataFrame(bar),dict(object_order=termids,segment_order=['G1','G3','G7'],value_definition='Supplied -log10 adjusted p',additivity_definition='One nonzero category per term: G1=BP; G3=CC; G7=MF. Not a sum across tests.',title='Term scores by declared block'),'分类条目评分','条目、分类和已给得分','比较条目得分与分类','不重新排序或计算p。',family='G18')
    nodes=[dict(record_type='node',node_id=id_,label=id_,entity_type='feature',group='G1' if i<10 else 'G7',x=float(np.cos(i*2*np.pi/20)),y=float(np.sin(i*2*np.pi/20)),area=float(90+(i%5)*35)) for i,id_ in enumerate(members)]
    edges=[dict(record_type='edge',source=a,target=b,weight=.25+((i+j)%5)*.12,sign=1) for i,a in enumerate(members) for j,b in enumerate(members) if i<j and (j-i in [1,3] or i==3)]
    net=pd.DataFrame(nodes+edges);selected=members[1:8];sub=net[((net.record_type=='node')&net.node_id.isin(selected))|((net.record_type=='edge')&net.source.isin(selected)&net.target.isin(selected))].copy()
    np_=dict(edge_label='Supplied relationship',node_area_label='Given display area',relation_semantics='Explicit synthetic associations',shape_map={'feature':'o'})
    for id_,d,title in [('c37_network',net,'Complete supplied network'),('c37_local',sub,'Explicit induced subset: F02-F08')]:
        add(id_,'typed_network',network.plot_typed_network,d,dict(np_,title=title),title,'节点ID、固定位置、显示面积、已给边与权重','整体拓扑与明确子集对应','局部节点/边来自同一网络；没有重新拟合边。')
    leafids=members[:16];rows=[dict(record_type='leaf',node_id=id_,group=f'G{1+2*(i//4)}',metric=float(-2.2-(i%7)*.7),outer_value=float(1+(i%6)*.5),area_value=float(.1+(i%5)*.18)) for i,id_ in enumerate(leafids)]
    level=leafids[:];height=0;index=0
    while len(level)>1:
        height+=1;nextlevel=[]
        for j in range(0,len(level),2):
            id_=f'H{index:02}';rows.append(dict(record_type='merge',node_id=id_,left=level[j],right=level[j+1],height=float(height+.03*j)));index+=1;nextlevel.append(id_)
        level=nextlevel
    tree=pd.DataFrame(rows)
    add('E36','hierarchy_tracks',linked.plot_hierarchy_tracks,tree,dict(leaf_order=leafids,height_definition='Supplied merge height',title='Given hierarchy and module identities'),'层次树与对齐分类条','唯一叶ID、已有二叉树合并记录、合并高度、固定叶序和分类','树结构与对象分类逐一对齐','不执行聚类；模块名称和颜色分别指定。')
    add('E37','radial_hierarchy',linked.plot_radial_hierarchy,tree,dict(leaf_order=leafids,height_definition='Supplied merge height',metric_limits=[-8,-2],metric_definition='Supplied signed metric',outer_definition='Given quantity',area_definition='Given fraction [0,1]',label_ids=leafids[::3],title='Radial hierarchy with quantitative leaf tracks'),'环形层次树与叶端量值','已有层次树、叶序、叶端连续量/比例和独立外圈量值','同时看层级、叶端指标与外圈数量','树结构不是亲和力；独立对接能量不可默认相加为总亲和力。')
    modules=['G1','G3','G5','G7'];traits=['Trait A','Trait B','Trait C'];matrix=pd.DataFrame([dict(row_id=g,column_id=t,association=float(np.sin(i*1.2+j*.8)*.82),pvalue=float(10**(-.4-(i+j)%5*.75))) for i,g in enumerate(modules) for j,t in enumerate(traits)])
    add('E35','split_metric_matrix',linked.plot_split_metric_matrix,matrix,dict(row_order=modules,column_order=traits,row_slots={g:g for g in modules},association_limits=[-1,1],significance_limits=[0,4],association_definition='Supplied module-trait association coefficient',probability_definition='Supplied nominal p; no multiple testing performed here',title='Two supplied metrics in every cell'),'三角单元双量值矩阵','完整行×列的两种量值；各自单位、范围、检验和缺失定义','同格分别读取关联方向与证据量','p不是关联强度；名义p与调整p应按上游定义标注。',family='G11')
    for id_,vals,label,title in [('c38_fit',[.28,.53,.67,.79,.84,.87,.88,.90],'Given signed fit index','Supplied topology diagnostics'),('c38_degree',[210,110,70,43,28,18,14,10],'Given mean connectivity','Supplied connectivity diagnostics')]:
        d=pd.DataFrame([dict(unit_id=f'Power {i+1}',group='G1',x=i+1,y=v) for i,v in enumerate(vals)])
        add(id_,'xy_points',general.plot_xy_points,d,dict(x_label='Supplied candidate power',y_label=label,unit_label='One given candidate setting per row',connect_order=True),title,'候选参数与已有诊断值','候选值如何对应给定诊断结果','不自动选择阈值；不运行pickSoftThreshold。',family='G17',mode='wrapper')
    scores=pd.DataFrame([dict(unit_id=id_,group=f'G{1+2*(i//4)}',x=float(.3+i*.035),y=float(.18+i*.033+.1*np.sin(i*2))) for i,id_ in enumerate(leafids)])
    add('c38_scores','xy_points',general.plot_xy_points,scores,dict(x_label='Supplied |module membership|',y_label='Supplied |gene significance|',unit_label='Mapped feature IDs; declared common trait'), 'Module membership and feature scoring','成员ID与两个已有评分','成员归属与评分的关系','绝对值须由输入明确给定；不等于因果靶点。',family='G17',mode='wrapper')
    quantities=pd.DataFrame([dict(object_id=id_,segment=g,value=float(.3+(i+j)%6*.17)) for i,id_ in enumerate(leafids) for j,g in enumerate(['G1','G3','G7'])])
    add('c39_stack','stacked_values',linked.plot_stacked_values,quantities,dict(object_order=leafids,segment_order=['G1','G3','G7'],value_definition='Supplied additive quantity',additivity_definition='Given components share units and can be added; no normalization or binding interpretation.',title='The same leaf IDs: component quantities'),'排序堆叠量值','对象×可加成分量值与明确显示顺序','逐对象看总量与各分量','只有同单位可加量才能堆叠；输入保留完整。',family='G19')
    tom=pd.DataFrame([dict(feature=a,sample=b,value=float(1 if a==b else .70+.08*np.cos(i+j) if i//4==j//4 else .08+.03*np.cos(i-j)),feature_block=f'G{1+2*(i//4)}') for i,a in enumerate(leafids) for j,b in enumerate(leafids)])
    add('c40_matrix','annotated_matrix',publication.plot_aligned_matrix,tom,dict(value_label='Supplied similarity [0,1]',limits=[0,1],signed=False,block_palette={'G1':'#506AAA','G3':'#91BBDF','G5':'#F6D3D9','G7':'#E17692'},title='Given TOM-like matrix in frozen leaf order'),'模块相似矩阵','同一叶ID顺序下的完整相似矩阵与版本','模块内部与跨模块模式','示例数值是软件构造，不是实际TOM估计。',family='G10',mode='wrapper')
    mn=[dict(record_type='node',node_id=g,label=g,entity_type='feature',group=g,x=float(np.cos(i*np.pi/2)),y=float(np.sin(i*np.pi/2)),area=160) for i,g in enumerate(modules)]
    me=[dict(record_type='edge',source=modules[i],target=modules[j],weight=.3+.1*(i+j),sign=-1 if (i+j)%2 else 1) for i in range(4) for j in range(i+1,4)]
    add('c40_network','typed_network',network.plot_typed_network,pd.DataFrame(mn+me),dict(np_,title='Given module-summary relationships'),'模块代表值关系','模块ID、已有代表值关系、权重和符号','模块层面的关系结构','不从基因网络直接推断模块因果关系。')
    return cases
