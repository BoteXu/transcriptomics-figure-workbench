"""Original table-based layouts inspired by documented visual patterns.

No clustering, differential tests, density estimation or model fitting occurs.
See references/expanded-patterns.md for provenance and interpretation limits.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, to_rgba
from matplotlib.patches import Patch
from figure_core import checked, palette_check, canvas, stamp, effect_reference


def plot_paired(data, palette, condition_order, y_label):
    d=checked(data,['subject_id','condition','value'],['value'])
    if len(condition_order)!=2 or len(set(condition_order))!=2 or set(d.condition)!=set(condition_order):
        raise ValueError('Specify the two observed conditions in order')
    if d.duplicated(['subject_id','condition']).any() or (d.groupby('subject_id').size()!=2).any():
        raise ValueError('Each subject must have exactly one observation per condition; report incomplete pairs separately')
    palette_check(d.condition,palette)
    fig,ax=canvas()
    mat=d.pivot(index='subject_id',columns='condition',values='value').reindex(columns=condition_order)
    for row in mat.to_numpy(): ax.plot([0,1],row,color='#AAB2BB',alpha=.6,linewidth=.8,zorder=1)
    for i,g in enumerate(condition_order): ax.scatter(np.repeat(i,len(mat)),mat[g],color=palette[g],s=28,zorder=2)
    ax.set_xticks([0,1],condition_order); ax.set_ylabel(y_label); ax.set_xlim(-.3,1.3)
    ax.set_title(f'{len(mat)} complete paired subjects')
    return stamp(fig,data,'paired',condition_order=list(condition_order),palette=palette,y_label=y_label,n_subjects=len(mat))


def plot_effect_matrix(data, effect_label, *, effect_scale, evidence_cap=6):
    d=checked(data,['feature','contrast','estimate','lower','upper','padj'],['estimate','lower','upper','padj'])
    effect_reference(effect_scale)
    if d.duplicated(['feature','contrast']).any() or len(d)!=d.feature.nunique()*d.contrast.nunique():
        raise ValueError('Effect matrix must be a complete unique grid; unestimable comparisons belong in a separate table')
    if ((d.lower>d.estimate)|(d.upper<d.estimate)|(d.padj<=0)|(d.padj>1)).any(): raise ValueError('Invalid bounds or padj; no implicit zero-p floor')
    if not np.isfinite(evidence_cap) or evidence_cap<=0: raise ValueError('Invalid evidence cap')
    if effect_scale=='ratio' and (d[['estimate','lower','upper']]<=0).any().any(): raise ValueError('Ratio bounds must be positive')
    colors=np.log2(d.estimate) if effect_scale=='ratio' else d.estimate
    score=np.minimum(-np.log10(d.padj),evidence_cap)
    rows=list(pd.unique(d.feature)); cols=list(pd.unique(d.contrast))
    x=[cols.index(v) for v in d.contrast]; y=[rows.index(v) for v in d.feature]
    fig,ax=canvas(); fig.set_size_inches(max(7.1,len(cols)*1.1),max(4.5,len(rows)*.4+1.5))
    ax.scatter(x,y,s=180,facecolors='none',edgecolors='#D8DDE2',marker='s',linewidths=.6)
    extent=max(abs(colors).max(),1e-9)
    dots=ax.scatter(x,y,s=score/evidence_cap*160,c=colors,cmap='RdBu_r',norm=TwoSlopeNorm(0,-extent,extent))
    fig.colorbar(dots,ax=ax,label=('log2 of '+effect_label) if effect_scale=='ratio' else effect_label)
    levels=sorted(set([min(1,evidence_cap),min(3,evidence_cap),evidence_cap]))
    ax.legend(handles=[ax.scatter([],[],s=v/evidence_cap*160,color='#5D6975',label=f'{v:g}') for v in levels],
              title=f'-log10(FDR)\ncapped at {evidence_cap:g}',loc='upper left',bbox_to_anchor=(1.3,1),frameon=False)
    ax.set_xticks(range(len(cols)),cols,rotation=30,ha='right'); ax.set_yticks(range(len(rows)),rows)
    ax.invert_yaxis(); ax.margins(.15)
    return stamp(fig,data,'effect_matrix',effect_scale=effect_scale,effect_label=effect_label,
                 area='min(-log10(padj), evidence_cap)',evidence_cap=evidence_cap,
                 empty_square='supplied estimable comparison with zero-sized evidence dot possible')


def plot_annotated_heatmap(data, value_label, group_palette, block_palette, *, scale_type,
                           column_annotation_label='Column group', row_annotation_label='Feature block'):
    d=checked(data,['feature','sample','value','sample_group','feature_block'],['value'])
    if d.duplicated(['feature','sample']).any() or len(d)!=d.feature.nunique()*d['sample'].nunique(): raise ValueError('Incomplete or duplicate heatmap grid')
    if (d.groupby('sample').sample_group.nunique()!=1).any() or (d.groupby('feature').feature_block.nunique()!=1).any(): raise ValueError('Annotation ID mismatch')
    if scale_type not in ('signed','sequential'): raise ValueError('Declare signed or sequential scale')
    palette_check(d.sample_group,group_palette); palette_check(d.feature_block,block_palette)
    rows=list(pd.unique(d.feature)); cols=list(pd.unique(d['sample']))
    mat=d.pivot(index='feature',columns='sample',values='value').reindex(index=rows,columns=cols)
    groups=d.drop_duplicates('sample').set_index('sample').loc[cols,'sample_group']
    blocks=d.drop_duplicates('feature').set_index('feature').loc[rows,'feature_block']
    # Explicit panels reserve room for shared titles/captions and annotation legends.
    fig=plt.figure(figsize=(max(8,len(cols)*.45+3),max(5,len(rows)*.3+2)))
    grid=fig.add_gridspec(2,1,height_ratios=[.035,1],
                         left=.22,right=.69,bottom=.24,top=.88,hspace=.04)
    ax=fig.add_subplot(grid[1,0]); top=fig.add_subplot(grid[0,0])
    pos=ax.get_position()
    # Keep the row annotation outside the text-label gutter.
    left=fig.add_axes([.03,pos.y0,.018,pos.height])
    extent=max(abs(d.value).max(),1e-9)
    im=ax.imshow(mat,aspect='auto',cmap='RdBu_r' if scale_type=='signed' else 'Blues',
                 norm=TwoSlopeNorm(0,-extent,extent) if scale_type=='signed' else None)
    top.imshow(np.array([[to_rgba(group_palette[g]) for g in groups]]),aspect='auto')
    left.imshow(np.array([[to_rgba(block_palette[g])] for g in blocks]),aspect='auto')
    top.set_axis_off(); left.set_axis_off()
    ax.set_xticks(range(len(cols)),cols,rotation=45,ha='right'); ax.set_yticks(range(len(rows)),rows)
    cax=fig.add_axes([.75,.18,.20,.025])
    colorbar=fig.colorbar(im,cax=cax,orientation='horizontal'); colorbar.set_label(value_label,fontsize=8)
    colorbar.ax.tick_params(labelsize=8)
    group_handles=[Patch(color=group_palette[g],label=str(g)) for g in pd.unique(groups)]
    block_handles=[Patch(color=block_palette[g],label=str(g)) for g in pd.unique(blocks)]
    fig.legend(handles=group_handles,loc='upper left',bbox_to_anchor=(.73,.90),frameon=False,
               title=column_annotation_label,fontsize=8,title_fontsize=8)
    next_y=.90-(len(group_handles)+2)*12/(fig.get_figheight()*72)
    fig.legend(handles=block_handles,loc='upper left',bbox_to_anchor=(.73,next_y),frameon=False,
               title=row_annotation_label,fontsize=8,title_fontsize=8)
    return stamp(fig,data,'annotated_heatmap',value_label=value_label,scale_type=scale_type,
                 group_palette=group_palette,block_palette=block_palette,
                 column_annotation_label=column_annotation_label,row_annotation_label=row_annotation_label,
                 ordering='first appearance; no clustering')


def plot_score_comparison(data, score_label, condition_labels):
    columns=['feature','score_a','score_b','delta','lower_delta','upper_delta']
    d=checked(data,columns,columns[1:])
    if len(condition_labels)!=2 or condition_labels[0]==condition_labels[1]: raise ValueError('Two distinct condition labels required')
    if d.feature.duplicated().any() or ((d[['score_a','score_b']]<0)|(d[['score_a','score_b']]>1)).any().any(): raise ValueError('Unique features and bounded scores required')
    if not np.allclose(d.delta,d.score_b-d.score_a,rtol=1e-8,atol=1e-12): raise ValueError('delta must equal score_b - score_a')
    if ((d.lower_delta>d.delta)|(d.upper_delta<d.delta)|(d.lower_delta < -1)|(d.upper_delta > 1)).any(): raise ValueError('Invalid supplied delta interval')
    fig,axes=plt.subplots(1,2,figsize=(9,4.5),layout='constrained')
    ax=axes[0]; ax.plot([0,1],[0,1],':',color='grey'); ax.scatter(d.score_a,d.score_b,color='#35618F')
    for row in d.itertuples(): ax.annotate(row.feature,(row.score_a,row.score_b),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1),xlabel=f'{condition_labels[0]} {score_label}',ylabel=f'{condition_labels[1]} {score_label}',aspect='equal')
    ax=axes[1]; y=np.arange(len(d)); ax.axvline(0,color='grey',linestyle=':')
    ax.errorbar(d.delta,y,xerr=[d.delta-d.lower_delta,d.upper_delta-d.delta],fmt='o',color='#35618F',capsize=3)
    ax.set_yticks(y,d.feature); ax.invert_yaxis(); ax.set_xlabel(f'{condition_labels[1]} - {condition_labels[0]}')
    return stamp(fig,data,'score_comparison',score_label=score_label,conditions=list(condition_labels),
                 uncertainty='supplied delta intervals; never derived from marginal AUC intervals')
