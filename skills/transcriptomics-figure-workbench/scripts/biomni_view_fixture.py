"""Bounded synthetic result tables for the Biomni-discovered display adapters."""
import numpy as np
import pandas as pd
from figure_biomni_views import (plot_sequence_logo,plot_contact_tracks,plot_branch_tree,
                                plot_slice_overlay,plot_registration_check)


def biomni_view_cases():
    cases={}
    def add(id_,adapter,fn,data,params,title,required,expression,limitations,family):
        cases[id_]=dict(adapter=adapter,function=fn,data=data,params=params,title=title,
                        data_required=required,expression=expression,limitations=limitations,family=family)
    letters=list('ACGT');rows=[]
    for i in range(12):
        heights=np.array([.06,.14,.23,.57]);heights=np.roll(heights,i%4)*(1+.4*np.sin(i*.8)**2)
        rows.extend(dict(position_id=str(i+1),symbol=s,height=float(h)) for s,h in zip(letters,heights))
    add('E38','sequence_logo',plot_sequence_logo,pd.DataFrame(rows),dict(position_order=[str(i+1) for i in range(12)],alphabet=letters,symbol_slots=dict(zip(letters,['G1','G3','G5','G7'])),height_definition='Frozen illustrative symbol heights in bits; no information-content estimation performed.',height_unit='Supplied height (bits)',title='Position-wise sequence logo'),
        '序列位点：字母高度堆叠','位置ID×字母完整表、非负高度、字母顺序及高度定义/单位','每个位点的字符偏好和总量，字母高度精确对应输入值','高度不是自动估计的频率、信息量或富集；不同定义不可混称。','G20')
    order=[f'B{i:02}' for i in range(16)];rows=[dict(record_type='bin',bin_id=b,start=i*1000,end=(i+1)*1000) for i,b in enumerate(order)]
    for i,a in enumerate(order):
        for j,b in enumerate(order[i:],i):
            v=float(1.7*np.exp(-(j-i)/4)+.6*np.exp(-((i-4)**2+(j-11)**2)/5))
            rows.append(dict(record_type='contact',bin_i=a,bin_j=b,value=np.nan if (i,j)==(2,13) else v))
    rows += [dict(record_type='signal',track=t,bin_id=b,value=float(.15+np.exp(-((i-c)/2)**2))) for t,c in [('Track A',4),('Track B',11)] for i,b in enumerate(order)]
    add('E39','contact_tracks',plot_contact_tracks,pd.DataFrame(rows),dict(bin_order=order,track_order=['Track A','Track B'],region_definition='Synthetic segment, 0-based half-open bins; frozen upper-triangle measurements.',coordinate_unit='Position (bp)',value_definition='Supplied contact intensity',value_limits=[0,2.1],track_unit='Supplied signal',title='Physical contact bins and aligned signal tracks'),
        '接触矩阵：物理分箱与对齐轨道','有序物理区间、上三角分箱对数值（含显式缺失）、相同分箱的轨道','位置对关系与同一基因组坐标上的局部信号','不执行Hi-C校正、TAD/环路识别；缺失不填零，线性尺度明确。','G26')
    rows=[dict(node_id='root',parent_id='',branch_length=0,label='Root')]
    rows += [dict(node_id=n,parent_id=p,branch_length=b,label=l) for n,p,b,l in [('n1','root',.20,'Clade A'),('n2','root',.45,'Clade B'),('A','n1',.17,'Object A'),('B','n1',.36,'Object B'),('C','n2',.12,'Object C'),('D','n2',.30,'Object D'),('E','n2',.48,'Object E')]]
    add('E40','branch_tree',plot_branch_tree,pd.DataFrame(rows),dict(root_id='root',leaf_order=list('ABCDE'),branch_unit='Supplied branch length',tree_definition='Frozen synthetic topology and branch lengths; distances are not linkage heights.',title='Supplied branch-length tree'),
        '树图：已给拓扑与真实枝长','节点ID、父节点ID、非负枝长、根、叶顺序、标签','共同祖先结构、累计枝长与叶端身份','不建树、不比对、不估计演化；枝长与聚类高度分别定义。','G56')
    rows=[];views=['Axial','Coronal','Sagittal']
    for vi,view in enumerate(views):
        for y in range(24):
            for x in range(28):
                radius=((x-13.5)/10)**2+((y-11.5)/9)**2
                intensity=float(.1+.65*np.exp(-radius*1.3)+.08*np.cos(x*.5+vi)*np.exp(-radius))
                label=1 if ((x-9-vi)/4)**2+((y-12)/4)**2<1 else 2 if ((x-19)/3)**2+((y-10-vi)/3)**2<1 else 0
                rows.append(dict(view=view,u=x*.7,v=y*.7,intensity=intensity,label=label))
    add('E41','slice_overlay',plot_slice_overlay,pd.DataFrame(rows),dict(view_order=views,axis_labels={v:['Supplied u (mm)','Supplied v (mm)'] for v in views},label_slots={'1':'G3','2':'G7'},intensity_limits=[0,1],registration_definition='Already registered synthetic orthogonal pixel grids, no patient images.',orientation_definition='Explicit supplied slice planes and u/v orientation; procedural background, not clinical anatomy.',title='Frozen orthogonal slice labels'),
        '影像切片：正交视图与分割叠加','各切面物理像素网格、背景强度、同坐标整数标签、方向与配准说明','既有区域标签在三个切面的空间位置和边界','不分割、不配准、不作诊断；方向必须由输入定义。','G23')
    rows=[]
    for y in range(24):
        for x in range(28):
            fixed=float(.05+.85*np.exp(-((x-12)**2+(y-12)**2)/70))
            registered=float(.05+.83*np.exp(-((x-12.5)**2+(y-11.6)**2)/70))
            rows.append(dict(u=x*.7,v=y*.7,fixed=fixed,registered=registered))
    add('E42','registration_check',plot_registration_check,pd.DataFrame(rows),dict(intensity_limits=[0,1],difference_limits=[-.15,.15],tile_pixels=4,coordinate_labels=['Supplied u (mm)','Supplied v (mm)'],registration_definition='Two already aligned procedural arrays in one physical pixel system and one intensity scale.',title='Registered image comparison'),
        '影像对照：棋盘拼接与差值','共同物理网格上的固定图/配准结果、共同强度尺度、棋盘块大小','图像边界接续与逐像素差值的空间分布','不估计变换、相似度或注册成功；差值不能替代已定义的质量指标。','G23')
    return cases
