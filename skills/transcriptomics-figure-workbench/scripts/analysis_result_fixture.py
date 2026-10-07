"""Original procedural frozen tables for analysis-specific visualization modes."""
import numpy as np
import pandas as pd
from figure_analysis_results import plot_splice_tracks,plot_variant_posteriors,plot_contribution_waterfall
from figure_multimodal import plot_calibration_counts,plot_frozen_dynamics
from figure_core import plot_heatmap


def analysis_result_cases():
    cases={}
    def add(id_,adapter,fn,data,params,title,required,expression,limitations,family):
        cases[id_]=dict(adapter=adapter,function=fn,data=data,params=params,title=title,data_required=required,expression=expression,limitations=limitations,family=family)
    samples=['G1','G7'];rows=[]
    for j,s in enumerate(samples):
        for x in range(100,900,10):
            value=6+24*np.exp(-((x-200)/60)**2)+18*np.exp(-((x-480)/75)**2)+28*np.exp(-((x-740)/60)**2)
            rows.append(dict(record_type='coverage',sample_id=s,group=s,start=x,end=x+10,value=float(value*(1+j*.15))))
        for a,b,n,l in [(250,440,42-j*22,1),(540,680,30+j*8,1),(250,680,9+j*25,2),(540,720,0,2)]:
            rows.append(dict(record_type='junction',sample_id=s,start=a,end=b,count=n,lane=l))
    for t,intervals in [('Isoform A',[(160,250),(440,540),(680,800)]),('Isoform B',[(160,250),(680,800)])]:
        rows += [dict(record_type='exon',transcript_id=t,exon_id=t+':'+str(i),start=a,end=b) for i,(a,b) in enumerate(intervals)]
    add('E43','splice_tracks',plot_splice_tracks,pd.DataFrame(rows),dict(sample_order=samples,transcript_order=['Isoform A','Isoform B'],region=[100,900],coordinate_definition='Synthetic segment; 0-based half-open intervals; increasing position, strand not inferred',coverage_definition='Supplied coverage in a common scale for both samples',junction_definition='Supplied junction read count; zero counts retained; arc height is layout only',title='Coverage, splice junctions and isoforms'),
        '剪接：覆盖、连接弧与异构体','混合表：样本分箱覆盖、连接起止/整数计数/布局层、转录本外显子区间；明确参考坐标','同一位置轴上的覆盖模式、连接支持量与已给异构体结构','不读取BAM、不估计PSI或差异剪接；弧高是排版，宽度才对应计数。','G26')
    rows=[]
    for j,s in enumerate(samples):
        for i in range(24):
            pip=float(.78*np.exp(-((i-7-j*8)/1.5)**2)+.18*np.exp(-((i-16+j*6)/2)**2))
            rows.append(dict(signal=s,variant_id=f'v{i+1:02}',position=100000+i*500,pip=pip,credible_set='CS'+str(j+1) if abs(i-7-j*8)<=2 else 'none'))
    add('E44','variant_posteriors',plot_variant_posteriors,pd.DataFrame(rows),dict(signal_order=samples,region=[99500,112000],coordinate_definition='Synthetic assembly and segment; supplied one-based variant positions',posterior_definition='Frozen multi-signal PIPs and supplied credible-set membership; no probability normalization',label_ids=['v08','v16'],title='Variant posteriors across supplied signals'),
        '精细定位：多信号PIP与可信集','信号×变异完整表、共同位置、已给PIP、可信集身份、坐标版本','每个信号的候选分布及已给可信集；共用位置便于比较','不运行精细定位或共定位；多信号PIP不要求总和为1，位置重叠不等于同一因果变异。','G26')
    rows=[]
    for j,m in enumerate(samples):
        for i in range(8):
            left=i/8;right=(i+1)/8;p=(left+right)/2;v=float(np.clip(p+(.025 if j==0 else .11)*np.sin(p*np.pi),.01,.99))
            rows.append(dict(model=m,bin_left=left,bin_right=right,predicted=p,estimate=v,lower=max(0,v-.065),upper=min(1,v+.065),n=18+int(65*np.exp(-((p-.3-j*.18)/.3)**2))))
    add('E45','calibration_counts',plot_calibration_counts,pd.DataFrame(rows),dict(palette={s:None for s in samples},interval_label='Supplied illustrative bin bounds, not fitted confidence intervals',evaluation_label='Synthetic held-out evaluation records; counts are per model and cannot be summed',title='Frozen calibration and bin support'),
        '预测评价：校准与分箱支持人数','模型×固定概率分箱、平均预测概率、观察比例、给定区间和实际分箱n','概率与发生比例是否接近，以及各段受多少独立评价单位支持','不重分箱或拟合；模型间人数不可加总，训练表现不能当外部验证。','G22')
    rows=[]
    for series in samples+['G3','G4']:
        for t in np.linspace(.05,.65,20):
            v=(.25-.29*t if series=='G1' else .22-.31*t if series=='G7' else .28-.72*t/(1-t) if series=='G3' else 0.)
            rows.append(dict(series=series,time=float(t),estimate=float(v),lower=float(v),upper=float(v)))
    add('E46','frozen_dynamics',plot_frozen_dynamics,pd.DataFrame(rows),dict(palette={s:None for s in samples+['G3','G4']},time_label='Risk threshold',value_label='Supplied net benefit',unit_label='Same synthetic evaluation cohort; G1/G7=model, G3=treat all, G4=treat none',interval_label='No uncertainty supplied: bounds equal the frozen curves; opt-in decision convention',title='Decision curves with declared reference strategies'),
        '决策曲线：净获益与参考策略','策略×概率阈值×已算净获益、给定区间、同评价群体与决策约定','不同阈值下的净获益，并和全部/无人策略比较','不计算DCA、不推导临床阈值；净获益定义、患病率与评价群体需明确。','G25')
    regulators=['Regulator A','Regulator B','Regulator C','Regulator D'];subjects=['S01','S02','S03','S04','S05','S06']
    rows=[dict(feature=r,sample=s,value=float(.85*np.sin(i*.9+j*.7)+(j-2.5)*.15)) for i,r in enumerate(regulators) for j,s in enumerate(subjects)]
    activity=pd.DataFrame(rows);activity.loc[(activity.feature=='Regulator A')&(activity['sample']=='S01'),'value']=.62
    add('E47','heatmap',plot_heatmap,activity,dict(row_order=regulators,column_order=subjects,value_label='Supplied signed activity score',title='Frozen regulator activity by sample',column_annotations={'Condition':{s:'G1' if i<3 else 'G7' for i,s in enumerate(subjects)}},annotation_palettes={'Condition':{'G1':'#506AAA','G7':'#E17692'}}),
        '调控活性：完整评分矩阵','调控因子×样本已给有符号评分、样本身份/条件、评分版本与覆盖说明','调控活性评分跨样本的模式与异质性','不把评分当因果活性；缺失靶标覆盖和正负权重定义必须由上游保留。','G10')
    terms=[f'Term {i}' for i in range(1,7)];rows=[]
    for i,a in enumerate(terms):
        for j,b in enumerate(terms):rows.append(dict(feature=a,sample=b,value=1. if i==j else float(.7*np.exp(-abs(i-j)/1.3))))
    add('E48','heatmap',plot_heatmap,pd.DataFrame(rows),dict(row_order=terms,column_order=terms,value_label='Supplied Jaccard overlap [0,1]',scale_type='sequential',title='Pathway redundancy in explicit term order',label_rotation=35),
        '通路冗余：共享成员相似矩阵','条目ID×条目ID完整已给相似量、成员全集和相似定义','条目之间的共享程度和成组冗余','不重算富集、不自动删条目；背景、成员ID版本和筛选全集需保留。','G10')
    rows=[dict(feature=f'Resolution {r:.1f}',sample=f'Threshold {t:.1f}',value=float(.4+.42*np.exp(-((r-.9)**2+(t-.45)**2)/.20))) for r in [.5,.7,.9,1.1,1.3] for t in [.2,.3,.4,.5,.6,.7]]
    add('E49','heatmap',plot_heatmap,pd.DataFrame(rows),dict(value_label='Supplied partition agreement [0,1]',scale_type='sequential',title='Network sensitivity across two settings',label_rotation=35),
        '网络稳定性：双参数敏感性矩阵','阈值×分辨率×已有稳定性指标、固定节点全集与对照分区定义','网络分区对两种设置的敏感区间','不推断生物稳定性；算法重复、重采样或空模型不能当生物学重复。','G56')
    rows=[]
    for j,s in enumerate(samples):
        for t in range(0,101,5):
            v=float(.22+.03*j+.11*np.exp(-t/16)+.015*np.sin(t/11+j));w=float(.012+.018*np.exp(-t/25))
            rows.append(dict(series=s,time=t,estimate=v,lower=v-w,upper=v+w))
    add('E50','frozen_dynamics',plot_frozen_dynamics,pd.DataFrame(rows),dict(palette={s:None for s in samples},time_label='Supplied time (ns)',value_label='Frozen block RMSD (nm)',unit_label='Synthetic independent run IDs G1/G7; frames and time blocks are not independent runs',interval_label='Supplied block ranges, not confidence intervals across independent trajectories',title='Returned trajectory blocks in physical time'),
        '动力学：时间分块摘要与独立运行','运行ID×真实时间×已有指标/分块范围、单位与参考结构','各独立运行的时间变化、瞬态与已有分块范围','不计算RMSD或自由能、不宣称收敛；帧和分块不充当独立重复。','G25')
    values=[.24,-.13,.31,.18,-.11,.08,-.04,.09];ids=[f'Target {i+1}' for i in range(len(values))]
    add('E51','contribution_waterfall',plot_contribution_waterfall,pd.DataFrame(dict(component_id=ids,label=ids,contribution=values)),dict(component_order=ids,baseline=0.,total=.62,quantity_definition='Supplied activity-score contribution',contribution_definition='Synthetic Regulator A / S01 decomposition; complete additive weighted target terms; no attribution calculation',title='Complete signed contributions to one score'),
        '贡献分解：有符号瀑布与总量','明确顺序的完整贡献表、基线、同单位总量及可加性定义','各正负项如何从基线逐项累积到一个总量','总量必须等于基线加完整贡献；无可加定义不能堆积，不等于机制证明。','G23')
    return cases
