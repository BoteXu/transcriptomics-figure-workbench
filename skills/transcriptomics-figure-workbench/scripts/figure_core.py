"""Newly authored static transcriptomics renderers; never run biological inference.

Accept reviewed pandas tables. Optional native AnnData APIs are documented separately.
"""
from pathlib import Path
import hashlib
import json
import platform
import re
import os
import shutil
import tempfile
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_rgba
import numpy as np
import pandas as pd
from matrix_input import normalize_matrix, axis_labels, matrix_frame

def table_bytes(data):
    """Hash and export exactly the same UTF-8 TSV bytes, including row order."""
    return data.to_csv(sep='\t', index=False, lineterminator='\n').encode('utf-8')

def file_sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''): digest.update(chunk)
    return digest.hexdigest()

def stamp(fig, data, kind, **spec):
    fig._omics_input_sha256 = hashlib.sha256(table_bytes(data)).hexdigest()
    fig._omics_spec = dict(kind=kind, **spec)
    return fig

def effect_reference(effect_scale):
    if effect_scale not in ('difference', 'log_ratio', 'ratio'):
        raise ValueError('Declare effect_scale: difference, log_ratio, or ratio')
    return 1 if effect_scale == 'ratio' else 0

def checked(data, columns, numeric=()):
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise ValueError('Expected nonempty DataFrame')
    if not set(columns).issubset(data.columns):
        raise ValueError('Missing required columns')
    if data[list(columns)].isna().any().any():
        raise ValueError('Missing values: report separately, never silently fill zero')
    for key in numeric:
        if not pd.api.types.is_numeric_dtype(data[key]) or not np.isfinite(data[key]).all():
            raise ValueError(f'Nonfinite/non-numeric: {key}')
    return data.copy()

def palette_check(values, palette):
    if not set(values).issubset(palette):
        raise ValueError('Palette missing categories')
    for color in palette.values():
        to_rgba(color)

def canvas():
    # rc_context avoids altering the caller's global configuration.
    with plt.rc_context({'font.size': 10, 'svg.fonttype': 'none', 'pdf.fonttype': 42}):
        fig, ax = plt.subplots(figsize=(7.1, 4.5), layout='constrained')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(colors='#28323C')
    return fig, ax

def plot_embedding(data, palette, axis_prefix='UMAP'):
    d = checked(data, ['cell_id','x','y','group'], ['x','y'])
    if d.cell_id.duplicated().any():
        raise ValueError('Duplicate cell_id')
    palette_check(d.group, palette)
    fig, ax = canvas()
    for group in pd.unique(d.group):
        sub = d[d.group == group]
        ax.scatter(sub.x, sub.y, s=9, alpha=.85, color=palette[group], label=group, linewidths=0)
    ax.set(xlabel=f'{axis_prefix} 1', ylabel=f'{axis_prefix} 2', aspect='equal')
    ax.legend(loc='upper left', bbox_to_anchor=(1,1), frameon=False, markerscale=2)
    return stamp(fig, data, 'embedding', palette=palette, axis_prefix=axis_prefix)

def plot_samples(data, palette, y_label):
    d = checked(data, ['sample_id','group','value'], ['value'])
    if d.sample_id.duplicated().any():
        raise ValueError('One row per independent unit required')
    palette_check(d.group,palette)
    fig, ax = canvas()
    groups = list(pd.unique(d.group))
    fig.set_size_inches(max(4.8,1.05*len(groups)+1.8),4.3)
    for i,g in enumerate(groups):
        vals = d.loc[d.group==g,'value'].to_numpy()
        # Display-only rank offsets reveal repeated values without moving Y.
        ranks=np.argsort(np.argsort(vals,kind='stable'),kind='stable')
        offsets=.16*np.sin(ranks*2.399963229728653)
        ax.scatter(i+offsets,vals,color=palette[g],s=30,edgecolors='white',linewidths=.45,alpha=.88,zorder=3)
    ax.set_xticks(range(len(groups)),[str(g)+'\nn='+str(int((d.group==g).sum())) for g in groups]); ax.set_ylabel(y_label)
    ax.set_xlim(-.48,len(groups)-.52)
    ax.grid(axis='y',color='#EDF0F2',linewidth=.6);ax.set_axisbelow(True)
    return stamp(fig, data, 'samples', palette=palette, y_label=y_label,point_placement='Deterministic categorical offsets; quantitative Y unchanged',group_counts={str(g):int((d.group==g).sum()) for g in groups})

def plot_forest(data, x_label, interval_label, *, effect_scale):
    d = checked(data,['label','estimate','lower','upper'],['estimate','lower','upper'])
    if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():
        raise ValueError('Duplicate labels or invalid interval')
    null = effect_reference(effect_scale)
    if effect_scale == 'ratio' and (d[['estimate','lower','upper']] <= 0).any().any():
        raise ValueError('Ratio estimates and bounds must be positive')
    fig, ax = canvas(); y = np.arange(len(d))
    ax.axvline(null,color='#929AA1',linestyle='--',linewidth=.7)
    if effect_scale == 'ratio': ax.set_xscale('log')
    ax.errorbar(d.estimate,y,xerr=np.array([d.estimate-d.lower,d.upper-d.estimate]),fmt='o',color='#35618F',capsize=3)
    ax.set_yticks(y,d.label); ax.invert_yaxis()
    ax.set(xlabel=x_label,title=interval_label)
    return stamp(fig, data, 'forest', effect_scale=effect_scale, null_value=null,
                 x_label=x_label, interval_label=interval_label)

def plot_volcano(data, alpha=.05, fc=1):
    d = checked(data,['gene','log2FC','padj'],['log2FC','padj'])
    if d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any():
        raise ValueError('Genes must be unique; padj in (0,1]; zero requires explicit display floor')
    if not (0<alpha<1 and np.isfinite(fc) and fc>0):
        raise ValueError('Invalid thresholds')
    colors = np.where((d.padj<=alpha)&(d.log2FC>=fc),'#B84E35',np.where((d.padj<=alpha)&(d.log2FC<=-fc),'#35618F','#BFC5CB'))
    fig, ax = canvas(); ax.scatter(d.log2FC,-np.log10(d.padj),c=colors,s=16,alpha=.8,linewidths=0)
    ax.axhline(-np.log10(alpha),color='grey',linestyle='--',linewidth=.6)
    for cut in [-fc,fc]: ax.axvline(cut,color='grey',linestyle='--',linewidth=.6)
    ax.set(xlabel='log2 fold change',ylabel='-log10(adjusted p)')
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([],[],marker='o',linestyle='',color=c,label=l) for l,c in [('Up','#B84E35'),('Down','#35618F'),('Other','#BFC5CB')]],frameon=False)
    return stamp(fig, data, 'volcano', alpha=alpha, fc=fc)

def plot_dot(data, value_label, *, value_semantics, denominator_label,
             row_field='feature', column_field='group', fraction_field='fraction',
             value_field='value', row_order=None, column_order=None,
             row_aliases=None, column_aliases=None, row_label_wrap=None,
             column_label_wrap=None, label_rotation=None, figsize=None,continuous_colors=None,
             row_counts=None,count_label=None):
    required=[row_field,column_field,fraction_field,value_field]
    d0=checked(data,required,[fraction_field,value_field])
    if d0.duplicated([row_field,column_field]).any() or ((d0[fraction_field]<0)|(d0[fraction_field]>1)).any():
        raise ValueError('Invalid dot table')
    if value_semantics not in ('mean_all', 'mean_detected', 'scaled', 'signed_effect'):
        raise ValueError('Declare dot color semantics')
    if not isinstance(denominator_label, str) or not denominator_label.strip():
        raise ValueError('A detection denominator label is required')
    d,features,groups=normalize_matrix(d0,row_field=row_field,column_field=column_field,value_field=value_field,
                                        row_order=row_order,column_order=column_order)
    fraction=d0[[row_field,column_field,fraction_field]].rename(columns={row_field:'feature',column_field:'sample',fraction_field:'fraction'})
    fraction=fraction.drop_duplicates(['feature','sample']).set_index(['feature','sample']).reindex(
        pd.MultiIndex.from_frame(d[['feature','sample']]))['fraction'].to_numpy()
    labels_x=axis_labels(groups,column_aliases,'column'); labels_y=axis_labels(features,row_aliases,'row')
    if row_label_wrap is not None and (type(row_label_wrap) is not int or row_label_wrap<1): raise ValueError('row_label_wrap must be a positive integer or None')
    if column_label_wrap is not None and (type(column_label_wrap) is not int or column_label_wrap<1): raise ValueError('column_label_wrap must be a positive integer or None')
    labels_x=[textwrap.fill(x,column_label_wrap) if column_label_wrap else x for x in labels_x]
    labels_y=[textwrap.fill(x,row_label_wrap) if row_label_wrap else x for x in labels_y]
    if row_counts is not None:
        if not isinstance(row_counts,dict) or set(row_counts)!=set(features) or not count_label or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not np.isfinite(v) or v<0 or v%1 for v in row_counts.values()):raise ValueError('Complete nonnegative integer row_counts and a count_label are required')
    if figsize is None:
        row_lines=max((x.count('\n')+1 for x in labels_y),default=1)
        figsize=(max(5.8,len(groups)*.52+2.35)+(1.45 if row_counts is not None else 0),max(4.4,len(features)*max(.28,row_lines*.18)+2.0))
    if not isinstance(figsize,(tuple,list)) or len(figsize)!=2 or any(float(x)<=0 for x in figsize): raise ValueError('figsize must be a positive (width, height) pair')
    fig,ax=canvas(); fig.set_layout_engine(None); fig.set_size_inches(float(figsize[0]),float(figsize[1]))
    color_args = dict(cmap='Blues')
    if value_semantics in ('scaled','signed_effect'):
        extent = max(abs(d.value).max(), 1e-9)
        color_args = dict(cmap='RdBu_r', norm=TwoSlopeNorm(0,-extent,extent))
    if continuous_colors is not None:
        color_args['cmap']=LinearSegmentedColormap.from_list('project_dot',continuous_colors)
    # A complete cell grid and physically sized area key keep the two channels
    # legible. Empty fraction remains truly empty, never a minimum-sized dot.
    max_area=260.
    for i in range(len(features)):
        if i%2==0:ax.axhspan(i-.5,i+.5,color='#F3F6F8',zorder=0,linewidth=0)
    dots=ax.scatter([groups.index(g) for g in d['sample']],[features.index(g) for g in d['feature']],s=fraction*max_area,c=d['value'],edgecolors='none',zorder=3,**color_args)
    rotation=(45 if len(groups)>4 else 0) if label_rotation is None else label_rotation
    ax.set_xticks(range(len(groups)),labels_x,rotation=rotation,ha='right' if rotation else 'center')
    ax.set_yticks(range(len(features)),labels_y)
    left=min(.52,max(.16,.10+max((len(x.replace('\n','')) for x in labels_y),default=0)*.008))
    height=float(figsize[1]);bottom=(1.80 if rotation else 1.48)/height
    fig.subplots_adjust(left=left,bottom=bottom,right=.75 if row_counts is not None else .96,top=.95)
    if row_counts is not None:
        support=fig.add_axes([.78,bottom,.17,.95-bottom],sharey=ax)
        values=[row_counts[k] for k in features];maximum=max(values,default=0)
        support.barh(range(len(features)),values,height=.58,color='#8AA6B5',linewidth=0)
        support.set_xlim(0,max(maximum*1.32,1));support.tick_params(axis='y',left=False,labelleft=False);support.set_xticks([])
        for i,value in enumerate(values):support.text(value+max(maximum*.04,.01),i,f'{value:,}',va='center',fontsize=8,color='#526272')
        support.set_title(textwrap.fill(count_label,18),loc='left',fontsize=8.5,pad=9)
        for spine in support.spines.values():spine.set_visible(False)
    cax=fig.add_axes([left,.72/height,.34,.09/height])
    cb=fig.colorbar(dots,cax=cax,orientation='horizontal');cb.set_label(value_label,fontsize=9)
    cb.outline.set_visible(False);cb.ax.tick_params(length=2,labelsize=8)
    from matplotlib.lines import Line2D
    handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(f*max_area),color='#527B93',markeredgewidth=0,label=f'{f:.0%}') for f in [.25,.5,1]]
    # Follow the real colour-key start when long row labels enlarge the left
    # lane. A capped x position made the two keys overlap after wide resizing.
    fig.legend(handles=handles,loc='center left',bbox_to_anchor=(left+.38,.70/height),ncol=3,frameon=False,fontsize=8,handletextpad=.3,columnspacing=.8)
    fig.text(left,.08/height,textwrap.fill('Dot area: fraction of '+denominator_label,max(35,int(float(figsize[0])*10))),fontsize=8,color='#637381',va='bottom')
    ax.set_xlim(-.5,len(groups)-.5);ax.set_ylim(len(features)-.5,-.5)
    ax.spines[['left','bottom']].set_visible(False);ax.tick_params(length=0)
    return stamp(fig, data, 'dot', value_label=value_label, value_semantics=value_semantics,
                 denominator_label=denominator_label, area='fraction',row_field=row_field,column_field=column_field,
                 fraction_field=fraction_field,value_field=value_field,row_order=features,column_order=groups,
                 row_aliases=dict(zip(features,labels_y)),column_aliases=dict(zip(groups,labels_x)),figsize=list(map(float,figsize)),max_point_area=max_area,guide_design='Adjacent horizontal colour and exact-area keys; complete row bands',row_counts=row_counts,count_label=count_label)

def plot_heatmap(data, value_label, center=0, *, scale_type='signed',
                 row_field='feature', column_field='sample', value_field='value',
                 value_columns=None, row_order=None, column_order=None,
                 row_aliases=None, column_aliases=None, missing='error',
                 figsize=None, cell_width=.44, cell_height=.27,
                 label_rotation=45, show_labels=True, row_label_mode='all',
                 column_label_mode='all', row_label_wrap=None, column_label_wrap=None,
                 label_fontsize=None, title='',row_annotations=None,column_annotations=None,
                 annotation_palettes=None,continuous_colors=None):
    """Draw a signed/sequential heatmap from a long or wide matrix.

    The original three-column ``feature/sample/value`` call remains valid.
    For a wide table pass ``row_field`` and (when annotations are present)
    ``value_columns``.  Orders are display orders only and must include every
    supplied ID; absent cells can be explicitly rendered as masked cells with
    ``missing='mask'``.  No row/column count is fixed in the renderer.
    """
    d,features,samples=normalize_matrix(data,row_field=row_field,column_field=column_field,
                                        value_field=value_field,value_columns=value_columns,
                                        row_order=row_order,column_order=column_order,missing=missing)
    labels_x=axis_labels(samples,column_aliases,'column');labels_y=axis_labels(features,row_aliases,'row')
    if row_label_mode not in ('all','none') or column_label_mode not in ('all','none'):
        raise ValueError("row_label_mode and column_label_mode must be 'all' or 'none'")
    if row_label_wrap is not None and (type(row_label_wrap) is not int or row_label_wrap < 1):
        raise ValueError('row_label_wrap must be a positive integer or None')
    if column_label_wrap is not None and (type(column_label_wrap) is not int or column_label_wrap < 1):
        raise ValueError('column_label_wrap must be a positive integer or None')
    labels_x_display=[textwrap.fill(x,column_label_wrap) if column_label_wrap else x for x in labels_x]
    labels_y_display=[textwrap.fill(x,row_label_wrap) if row_label_wrap else x for x in labels_y]
    mat=matrix_frame(d,features,samples)
    fig,ax=canvas()
    fig.set_layout_engine(None)
    if figsize is None:
        # Keep every row name visible by default. Width tracks long column
        # labels; height tracks rows and wrapped row-label lines.
        row_lines=max((x.count('\n')+1 for x in labels_y_display),default=1)
        row_width=max((len(x.replace('\n','')) for x in labels_y_display),default=0)
        row_stride=max(float(cell_height),row_lines*.18)
        figsize=(max(7.1+min(max(row_width-16,0),80)*.025,len(samples)*float(cell_width)+3.6+min(max(len(x) for x in labels_x),48)*.015),
                 max(4.5,len(features)*row_stride+1.8))
    if not isinstance(figsize,(tuple,list)) or len(figsize)!=2 or any(float(x)<=0 for x in figsize):
        raise ValueError('figsize must be a positive (width, height) pair')
    fig.set_size_inches(float(figsize[0]),float(figsize[1]))
    finite=d.value.to_numpy(dtype=float)
    extent=max(abs(finite.min()-center),abs(finite.max()-center),1e-9)
    cmap=LinearSegmentedColormap.from_list('omics',['#35618F','#F7F7F5','#B84E35'])
    if scale_type not in ('signed','sequential'): raise ValueError('Unknown heatmap scale')
    shown=np.ma.masked_invalid(mat.to_numpy(dtype=float)) if missing=='mask' else mat.to_numpy(dtype=float)
    if continuous_colors is not None:cmap=LinearSegmentedColormap.from_list('project_heatmap',continuous_colors)
    im=ax.imshow(shown,aspect='auto',cmap=cmap if continuous_colors is not None or scale_type=='signed' else 'Blues',
                 norm=TwoSlopeNorm(center,center-extent,center+extent) if scale_type=='signed' else None)
    font_kwargs={} if label_fontsize is None else {'fontsize':label_fontsize}
    if show_labels and row_label_mode=='all' and column_label_mode=='all':
        ax.set_xticks(range(len(samples)),labels_x_display,rotation=label_rotation,ha='right' if label_rotation else 'center',**font_kwargs)
        ax.set_yticks(range(len(features)),labels_y_display,**font_kwargs)
    elif show_labels:
        ax.set_xticks(range(len(samples)),labels_x_display if column_label_mode=='all' else [],rotation=label_rotation,ha='right' if label_rotation else 'center',**font_kwargs)
        ax.set_yticks(range(len(features)),labels_y_display if row_label_mode=='all' else [],**font_kwargs)
    else:
        ax.set_xticks([]);ax.set_yticks([])
    fig.colorbar(im,ax=ax,label=value_label)
    if title: ax.set_title(title,loc='left')
    # A long identity label needs a real left margin; never clip it merely
    # because an example happened to use short gene symbols.
    if show_labels and row_label_mode=='all':
        left=min(.52,max(.12,.12+max((len(x.replace('\n','')) for x in labels_y_display),default=0)*.0045))
        bottom=.23 if label_rotation else .16
        fig.subplots_adjust(left=left,bottom=bottom,right=.86,top=.91)
    fig=stamp(fig, data, 'heatmap', value_label=value_label, scale_type=scale_type, center=center,
                 row_field=row_field,column_field=column_field,value_field=value_field,
                 value_columns=list(value_columns) if value_columns is not None else None,
                 row_order=features,column_order=samples,row_aliases=dict(zip(features,labels_y)),
                 column_aliases=dict(zip(samples,labels_x)),missing=missing,figsize=list(map(float,figsize)),
                 label_rotation=label_rotation,show_labels=bool(show_labels),row_label_mode=row_label_mode,
                 column_label_mode=column_label_mode,row_label_wrap=row_label_wrap,column_label_wrap=column_label_wrap,
                 label_fontsize=label_fontsize,title=title)
    if row_annotations or column_annotations:
        from indexed_alignment import add_matrix_annotations
        if column_annotations:
            b=list(ax.get_position().bounds);b[3]-=len(column_annotations)*.32/fig.get_figheight();ax.set_position(b)
            for position in ('left','center','right'):ax.set_title('',loc=position)
            if title:fig.text(b[0],.955,title,ha='left',va='top',fontsize=11)
        fig=add_matrix_annotations(fig,ax,features,samples,row_annotations=row_annotations,
                                   column_annotations=column_annotations,palettes=annotation_palettes)
    return fig

def plot_qc(data,y_label,*,metric_field=None,metric_labels=None,ncols='auto',nrows=None,panel_width=3.3,panel_height=3.5):
    d=checked(data,['cell_id','sample','value'],['value'])
    if metric_field is not None:
        d=checked(d,[metric_field]);metrics=list(pd.unique(d[metric_field]))
        if not isinstance(metric_labels,dict) or set(metric_labels)!=set(metrics) or any(not str(v).strip() for v in metric_labels.values()):raise ValueError('Every QC metric requires its explicit label and units')
        if d.duplicated(['cell_id','sample',metric_field]).any():raise ValueError('Duplicate cell/sample/metric')
        from figure_workbench.responsive import grid_shape,facet_slots,canvas_budget
        rows,cols=grid_shape(len(metrics),ncols,nrows);fig=plt.figure(figsize=canvas_budget(cols*panel_width,rows*panel_height),layout='constrained')
        axes=[fig.add_subplot(s) for s in facet_slots(fig,len(metrics),rows,cols)]
    else:
        if metric_labels is not None or ncols!='auto' or nrows is not None:raise ValueError('QC facet controls require an explicit metric field and labels')
        if d.duplicated(['cell_id','sample']).any(): raise ValueError('Duplicate cells within sample')
        fig,ax=canvas();metrics=[None];axes=[ax]
    for metric,ax in zip(metrics,axes):
        part=d if metric is None else d[d[metric_field]==metric];groups=list(pd.unique(part['sample']))
        ax.boxplot([part.loc[part['sample']==g,'value'] for g in groups],tick_labels=groups,patch_artist=True,
               boxprops={'facecolor':'#E3EBEF','edgecolor':'#708795','linewidth':.8},
               medianprops={'color':'#2B7285','linewidth':1.2},
               whiskerprops={'color':'#708795','linewidth':.8},capprops={'color':'#708795','linewidth':.8},
               flierprops={'marker':'.','markerfacecolor':'#708795','markeredgecolor':'none','markersize':4,'alpha':.65})
        ax.set(xlabel='Capture / sample',ylabel=y_label if metric is None else metric_labels[metric]);ax.spines[['top','right']].set_visible(False)
        if metric is not None:ax.tick_params(axis='x',labelrotation=90,labelsize=8)
    return stamp(fig, data, 'qc', y_label=y_label,metric_field=metric_field,metric_labels=metric_labels,metrics=metrics,statistics='Descriptive boxes; no filtering, threshold estimation or inference')

def plot_composition(data,palette,*,y_label='Fraction of included cells',mode='stacked',ncols='auto',nrows=None,panel_width=3.5,panel_height=2.6):
    d=checked(data,['sample','celltype','count'],['count'])
    if d.duplicated(['sample','celltype']).any() or ((d['count']<0)|(d['count']%1!=0)).any(): raise ValueError('Invalid counts')
    palette_check(d.celltype,palette)
    # Fill absent cell types only in this explicitly count-based composition table.
    matrix=d.pivot(index='sample',columns='celltype',values='count').reindex(index=list(pd.unique(d['sample'])),columns=list(pd.unique(d.celltype))).fillna(0)
    if (matrix.sum(axis=1)==0).any(): raise ValueError('Zero denominator')
    prop=matrix.div(matrix.sum(axis=1),axis=0)
    if mode not in ('stacked','facets'):raise ValueError('Composition mode must be stacked or facets')
    if mode=='facets':
        from figure_workbench.responsive import grid_shape,facet_slots,canvas_budget
        rows,cols=grid_shape(len(prop.columns),ncols,nrows)
        fig=plt.figure(figsize=canvas_budget(cols*panel_width,rows*panel_height+.45),layout='constrained')
        for k,slot in enumerate(facet_slots(fig,len(prop.columns),rows,cols)):
            ax=fig.add_subplot(slot);name=prop.columns[k]
            ax.bar(range(len(prop)),np.ones(len(prop)),color='#EDF1F4',width=.78,zorder=0)
            ax.bar(range(len(prop)),prop[name],color=palette[name],width=.78,zorder=2)
            ax.set(ylim=(0,1),xlim=(-.6,len(prop)-.4),title=str(name))
            ax.set_xticks(range(len(prop)),prop.index,rotation=90 if len(prop)>8 else 45,fontsize=8)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1));ax.spines[['top','right']].set_visible(False)
            ax.grid(axis='y',color='white',linewidth=.6);ax.set_axisbelow(True)
        fig.supylabel(y_label,fontsize=9)
        return stamp(fig,data,'composition',palette=palette,denominator='all supplied counts per sample',y_label=y_label,mode=mode,rows=rows,columns=cols,sample_order=list(prop.index),celltype_order=list(prop.columns),reference='Pale full-height column = entire supplied sample denominator')
    if ncols!='auto' or nrows is not None:raise ValueError('Use composition facets for row/column requests')
    fig,ax=canvas(); bottom=np.zeros(len(prop))
    for celltype in prop.columns:
        ax.bar(prop.index,prop[celltype],bottom=bottom,color=palette[celltype],label=celltype,width=.75)
        bottom+=prop[celltype].to_numpy()
    if not isinstance(y_label,str) or not y_label.strip():raise ValueError('Explicit denominator label required')
    ax.set_ylim(0,1); ax.set_ylabel(y_label)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
    ax.legend(loc='upper left',bbox_to_anchor=(1,1),frameon=False)
    return stamp(fig, data, 'composition', palette=palette, denominator='all supplied counts per sample',y_label=y_label,mode=mode,sample_order=list(prop.index),celltype_order=list(prop.columns))

def plot_curve(data,kind='ROC',*,palette=None,mode='auto',ncols='auto',nrows=None,panel_width=3.8,panel_height=3.6,prevalence=None,interval_label=None,interpolation='linear'):
    if kind not in ['ROC','PR','calibration']: raise ValueError('Unknown curve kind')
    d=checked(data,['model','x','y'],['x','y'])
    if ((d[['x','y']]<0)|(d[['x','y']]>1)).any().any(): raise ValueError('Curve values outside [0,1]')
    models=list(pd.unique(d.model))
    if mode not in ['auto','overlay','facets']:raise ValueError('Curve mode must be auto, overlay or facets')
    if palette is not None:palette_check(models,palette)
    has_interval=bool({'lower','upper'}&set(d))
    if has_interval:
        checked(d,['lower','upper'],['lower','upper'])
        if not interval_label or ((d.lower<0)|(d.upper>1)|(d.lower>d.y)|(d.upper<d.y)).any():raise ValueError('Declare valid supplied probability intervals and interval_label')
    if prevalence is not None and (kind!='PR' or not np.isfinite(prevalence) or not 0<prevalence<1):raise ValueError('A supplied prevalence in (0,1) is only valid for PR')
    facets=mode=='facets' or (mode=='auto' and (len(models)>4 or ncols!='auto' or nrows is not None))
    if mode=='overlay' and (ncols!='auto' or nrows is not None):raise ValueError('Use facets for row/column controls')
    if not facets and len(models)>4:raise ValueError('More than four overlapping curves require complete facets')
    if facets:
        from figure_workbench.responsive import grid_shape,facet_slots,canvas_budget
        rows,cols=grid_shape(len(models),ncols,nrows)
        fig=plt.figure(figsize=canvas_budget(cols*panel_width,rows*panel_height),layout='constrained')
        axes=[fig.add_subplot(s) for s in facet_slots(fig,len(models),rows,cols)]
    else:fig,ax=canvas();axes=[ax]*len(models)
    if interpolation not in ('linear','steps-post'):raise ValueError('Declare linear or steps-post interpolation')
    styles=['-','--','-.',':'];drawstyle='default' if interpolation=='linear' else interpolation
    for i,(m,ax) in enumerate(zip(models,axes)):
        sub=d[d.model==m];color=palette[m] if palette else '#35618F';style='-' if facets else styles[i]
        rgb=np.asarray(to_rgba(color)[:3]);linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
        contrast=1.05/(float(linear@[.2126,.7152,.0722])+.05)
        if contrast<3:ax.plot(sub.x,sub.y,color='#687783',linestyle=style,lw=2.5,zorder=1,drawstyle=drawstyle)
        if has_interval:ax.fill_between(sub.x,sub.lower,sub.upper,color=color,alpha=.10,linewidth=0,zorder=0,step=None if interpolation=='linear' else 'post')
        ax.plot(sub.x,sub.y,color=color,linestyle=style,label=m,lw=1.5,zorder=2,drawstyle=drawstyle)
        if facets:ax.set_title(str(m),loc='left',fontsize=10)
    labels={'ROC':('False positive rate','True positive rate'),'PR':('Recall','Precision'),'calibration':('Predicted probability','Observed fraction')}
    for ax in dict.fromkeys(axes):
        if kind!='PR':ax.plot([0,1],[0,1],':',color='#A7B2BA',lw=.8,zorder=0)
        elif prevalence is not None:ax.axhline(prevalence,ls=':',color='#87939D',lw=.8,label='Prevalence '+f'{prevalence:.1%}')
        ax.set(xlim=(0,1),ylim=(0,1),xlabel=labels[kind][0],ylabel=labels[kind][1],aspect='equal')
        ax.spines[['top','right']].set_visible(False)
        if not facets:ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(1.025,1),borderaxespad=0)
        ax.grid(color='#EDF0F2',lw=.55);ax.set_axisbelow(True)
    if has_interval:fig.text(.12,.015,interval_label,fontsize=8,color='#637381')
    return stamp(fig, data, 'curve', curve_kind=kind, threshold_order='input order',curve_mode='facets' if facets else 'overlay',model_order=models,prevalence=prevalence,interval_label=interval_label,supplied_intervals=has_interval,interpolation=interpolation)

def export_figure(fig,data,out_dir,figure_id,meta, *, source_file=None, expected_source_sha256=None):
    """Publish a complete per-figure directory by one rename on the same filesystem.

    v2 layout: out_dir/figure_id/figure_id.{svg,pdf,png,tsv,json}, *_session.txt.
    Hashes identify bytes, not validity of upstream statistics. Native plots need
    their own reviewed adapter/stamp; arbitrary untracked figures are rejected.
    """
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',figure_id): raise ValueError('Unsafe figure id')
    required={'source','palette','input_unit','experimental_unit','contrast','denominator','model','limits','filtering','uncertainty','interpretation_limit','synthetic'}
    if not required.issubset(meta): raise ValueError('Incomplete figure provenance')
    for key in required-{'synthetic','palette'}:
        if not isinstance(meta[key],str) or not meta[key].strip(): raise ValueError(f'Empty/non-text metadata: {key}')
    if not isinstance(meta['palette'],(str,dict)) or not meta['palette']: raise ValueError('Empty palette metadata')
    if 'input_hash' in meta: raise ValueError('input_hash is computed; use expected_source_sha256 for source verification')
    if type(meta['synthetic']) is not bool: raise ValueError('synthetic must be bool')
    if not isinstance(data,pd.DataFrame) or data.empty: raise ValueError('Empty data')
    raw=table_bytes(data); plotted_hash=hashlib.sha256(raw).hexdigest()
    if getattr(fig,'_omics_input_sha256',None)!=plotted_hash:
        raise ValueError('Export table does not match the renderer input; use a reviewed adapter')
    from figure_layout import optimize_guide_layout
    fig=optimize_guide_layout(fig)
    source_hash=None
    if source_file is not None:
        source_file=Path(source_file).resolve(strict=True)
        source_hash=file_sha256(source_file)
    if expected_source_sha256 is not None:
        if not re.fullmatch('[0-9a-fA-F]{64}',expected_source_sha256) or source_hash!=expected_source_sha256.lower():
            raise ValueError('Source SHA256 mismatch or missing source file')
    out=Path(out_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    dest=out/figure_id; lock=out/('.'+figure_id+'.lock'); stage=None
    extensions=['.svg','.pdf','.png','.tsv','.json','_session.txt']
    if dest.exists() or any((out/(figure_id+ext)).exists() for ext in extensions):
        raise FileExistsError('Refusing to overwrite existing v1/v2 outputs')
    # Exclusive lock prevents two exporters claiming the same figure id.
    handle=lock.open('x',encoding='utf-8')
    try:
        with handle: handle.write(str(os.getpid()))
        if dest.exists(): raise FileExistsError('Destination appeared during export')
        stage=Path(tempfile.mkdtemp(prefix='.'+figure_id+'-staging-',dir=out))
        files=[stage/(figure_id+ext) for ext in extensions]
        if meta['synthetic']:
            from figure_layout import add_software_bands
            fig=add_software_bands(fig,figure_id,fig._omics_spec.get('project_theme',{}).get('font_family','sans-serif'))
        with plt.rc_context({'svg.fonttype':'none','pdf.fonttype':42,'savefig.bbox':None}):
            for file in files[:3]: fig.savefig(file,dpi=300,facecolor='white')
        files[3].write_bytes(raw)
        files[5].write_text(f'Python {platform.python_version()}\nmatplotlib {matplotlib.__version__}\npandas {pd.__version__}\nnumpy {np.__version__}\n',encoding='utf-8')
        receipt=dict(meta,schema_version=2,figure_id=figure_id,status='RENDERED_UNREVIEWED',
                     input_hash=plotted_hash,input_hash_algorithm='SHA256',input_hash_scope='exact exported TSV bytes',
                     source_file=str(source_file) if source_file else None,source_file_sha256=source_hash,
                     figure_spec=fig._omics_spec,width_inches=float(fig.get_figwidth()),height_inches=float(fig.get_figheight()))
        fig.canvas.draw()
        receipt['layout_geometry']=[dict(axis=i,bounds=list(ax.get_position().bounds),
            xlim=list(ax.get_xlim()),ylim=list(ax.get_ylim()),xscale=ax.get_xscale(),yscale=ax.get_yscale(),
            gid=ax.get_gid(),colourbar=hasattr(ax,'_colorbar'),projection=ax.name) for i,ax in enumerate(fig.axes)]
        from indexed_alignment import audit_index_alignment
        receipt['index_alignment']=audit_index_alignment(fig)
        if receipt['index_alignment']['issues']:raise ValueError('Indexed tracks do not align in final export')
        receipt['renderer_sha256']={p.name:file_sha256(p) for p in
                                   Path(__file__).parent.glob('figure_*.py')}
        for name in ('alluvial_geometry.py','indexed_alignment.py','matrix_input.py','project_theme.py'):
            helper=Path(__file__).parent/name;receipt['renderer_sha256'][name]=file_sha256(helper)
        receipt['output_sha256']={p.name:file_sha256(p) for p in files[:4]+files[5:]}
        files[4].write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        if dest.exists(): raise FileExistsError('Destination appeared before publish')
        stage.rename(dest)
        stage=None
        return [dest/(figure_id+ext) for ext in extensions]
    finally:
        # Only remove our own uncommitted temporary directory, never user outputs.
        try:
            if stage is not None and stage.parent==out and stage.name.startswith('.'+figure_id+'-staging-'):
                shutil.rmtree(stage)
        finally:
            handle.close()
            lock.unlink(missing_ok=True)
