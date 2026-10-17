# -*- coding: utf-8 -*-
"""Annotation evidence with one clear scope per page, from frozen inputs only.

An atlas shows identities and marker specificity. A subgroup page shows one
declared identity, all its selected markers on unchanged coordinates, and the
same markers against every supplied comparison identity. No marker discovery,
scaling, embedding, density estimation or inferential analysis occurs here.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from figure_core import checked, stamp
from project_theme import group_palette, apply_project_style
from figure_workbench.responsive import grid_shape, canvas_budget, facet_slots

INK = '#283F4B'
MUTED = '#687B85'
LIGHT = '#DFE5E8'


def _coordinates(ax, emb):
    xx = emb.x.max() - emb.x.min(); yy = emb.y.max() - emb.y.min()
    if min(xx, yy) <= 0:
        raise ValueError('Both stored coordinate dimensions must have positive range')
    ax.set(xlim=(emb.x.min()-.07*xx, emb.x.max()+.07*xx),
           ylim=(emb.y.min()-.07*yy, emb.y.max()+.07*yy))
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([]); ax.set_yticks([]); ax.spines[:].set_visible(False)
    # One coordinate key per panel preserves orientation without heavy axes.
    for end in [(0.17, .025), (.025, .17)]:
        ax.annotate('', xy=end, xytext=(.025, .025), xycoords='axes fraction',
                    arrowprops=dict(arrowstyle='-', lw=.65, color='#91A0A8'))


def _heading(ax, letter, title):
    text = ax.text(0, 1.07, letter+'  '+title, transform=ax.transAxes,
                   ha='left', va='bottom', color=INK, fontsize=11,
                   fontweight='bold', clip_on=False)
    text._panel_heading = True


def _dot(ax, dots, groups, markers, limits, cmap, focus, pal):
    ax.set(xlim=(-.6, len(markers)-.4), ylim=(len(groups)-.5, -.5))
    if focus is not None:
        y = groups.index(focus)
        ax.axhspan(y-.43, y+.43, color=pal[focus], alpha=.08, zorder=0)
    for y in range(len(groups)):
        ax.axhline(y, color='#EDF0F2', lw=.65, zorder=0)
    ax.scatter([markers.index(x) for x in dots.feature],
               [groups.index(x) for x in dots.group],
               s=130*dots.fraction, c=dots.value, cmap=cmap,
               norm=Normalize(*limits), edgecolors='none', zorder=2)
    ax.set_xticks(range(len(markers)), markers,
                  rotation=90 if len(markers)>6 else 35,
                  ha='center' if len(markers)>6 else 'right')
    ax.set_yticks(range(len(groups)), groups)
    ax.tick_params(length=0, pad=5, labelsize=9.5)
    ax.spines[:].set_visible(False)
    for tick in ax.get_yticklabels():
        if tick.get_text()==focus:
            tick.set_color(pal[focus]); tick.set_fontweight('bold')


def plot_annotation_evidence(data, theme, *, mode, title, expression_label,
                             detection_definition, expression_limits,
                             marker_order, focus_group=None, group_order=None,
                             ncols='auto', nrows=None, panel_width=3.25,
                             panel_height=3.15):
    """Separate annotation atlas and per-subgroup multi-marker reading pages.

    record_type=embedding: object_id, group, x, y (one row/cell).
    record_type=marker_dot: feature, group, value, fraction, feature_group.
    record_type=feature_map (subgroup): object_id, feature, x, y, value.
    record_type=embedding_label (atlas): group, x, y, label (one/group).
    Expression values are supplied on one explicit common nonnegative scale;
    no quantile clipping or gene-wise rescaling is applied for appearance.
    """
    if mode not in ['atlas', 'subgroup']:
        raise ValueError('Choose atlas or subgroup evidence')
    for label in [title, expression_label, detection_definition]:
        if not isinstance(label, str) or not label.strip() or len(label)>220:
            raise ValueError('Bounded explicit title, expression units and detection definition required')
    if not isinstance(marker_order, (list, tuple)) or not marker_order or len(marker_order)!=len(set(marker_order)):
        raise ValueError('Explicit unique marker order required; do not auto-select markers')
    if len(marker_order) > (48 if mode=='atlas' else 12):
        raise ValueError('Use complete additional reading pages for more markers')
    if len(expression_limits)!=2 or not np.isfinite(expression_limits).all() or expression_limits[0]!=0 or expression_limits[1]<=0:
        raise ValueError('Declare common nonnegative expression limits beginning at zero')
    allowed = {'embedding', 'marker_dot', 'embedding_label'} | ({'feature_map'} if mode=='subgroup' else set())
    if set(data.record_type)-allowed:
        raise ValueError('Supply only channels displayed on this page; keep response in its companion')
    emb = checked(data[data.record_type=='embedding'], ['object_id','group','x','y'], ['x','y'])
    if emb.empty or emb.object_id.duplicated().any():
        raise ValueError('Unique supplied cell identities and complete frozen coordinates required')
    names = list(emb.group.unique()) if group_order is None else list(group_order)
    if len(names)!=len(set(names)) or set(names)!=set(emb.group):
        raise ValueError('Group order must retain every comparison identity exactly once')
    pal = group_palette(theme, names)
    dots = checked(data[data.record_type=='marker_dot'],
                   ['feature','group','value','fraction','feature_group'], ['value','fraction'])
    if set(dots.feature)!=set(marker_order) or set(dots.group)!=set(names) or dots.duplicated(['feature','group']).any() or len(dots)!=len(names)*len(marker_order):
        raise ValueError('Complete selected-marker by all-identity specificity grid required')
    if ((dots.fraction<0)|(dots.fraction>1)|(dots.value<0)|(dots.value>expression_limits[1])).any():
        raise ValueError('Detection fractions or expression values outside declared limits')
    if (dots.groupby('feature').feature_group.nunique()!=1).any() or set(dots.feature_group)-set(names):
        raise ValueError('Every selected marker requires one declared identity assignment')
    features = None
    if mode=='subgroup':
        if focus_group not in names or set(dots.feature_group)!={focus_group}:
            raise ValueError('All selected markers must be explicitly assigned to this focus group')
        features = checked(data[data.record_type=='feature_map'],
                           ['object_id','feature','x','y','value'], ['x','y','value'])
        if set(features.feature)!=set(marker_order) or features.duplicated(['object_id','feature']).any():
            raise ValueError('Supply each selected marker exactly once per cell')
        if ((features.value<0)|(features.value>expression_limits[1])).any():
            raise ValueError('Do not clip expression to improve colour contrast')
        for gene, q in features.groupby('feature', sort=False):
            if set(q.object_id)!=set(emb.object_id):
                raise ValueError('Every feature retains every background and target cell')
            q = q.set_index('object_id').loc[emb.object_id]
            if not np.array_equal(q[['x','y']].to_numpy(),emb[['x','y']].to_numpy()):
                raise ValueError('All feature maps must preserve exact embedding coordinates')
    elif focus_group is not None:
        raise ValueError('Use subgroup mode for a focus identity')
    anchors = data[data.record_type=='embedding_label']
    if mode=='atlas':
        anchors = checked(anchors, ['group','x','y','label'], ['x','y'])
        if anchors.group.duplicated().any() or set(anchors.group)!=set(names):
            raise ValueError('Supply one reviewed label anchor per identity')
    else:
        if not anchors.empty:
            raise ValueError('Subgroup pages do not use whole-atlas text anchors')
    count = 2 if mode=='atlas' else 2+len(marker_order)
    requested = (2 if mode=='atlas' else 3) if ncols=='auto' and nrows is None else ncols
    rows, cols = grid_shape(count, requested, nrows)
    # A long group name or larger specificity matrix grows its own text lane.
    group_lane = max(.75, max(len(str(n)) for n in names)*.065)
    cell_height = max(panel_height, .32*len(names)+1.2)
    if mode=='atlas' and cols==2:
        widths = [3.5, max(5.65, len(marker_order)*.22+group_lane+.5)]
        width = sum(widths)+.9; height = cell_height+2.0
        ratios = widths
    else:
        width = cols*max(panel_width,group_lane+2.1)+.5
        height = rows*cell_height+1.95; ratios = None
    if cols==1:height+=1.1
    header=1.75 if cols==1 else 1.2
    footer=1.72 if cols==1 else 1.12
    fig = plt.figure(figsize=canvas_budget(width,height))
    options=dict(left=.065,right=.97,top=1-header/height,
                 bottom=footer/height,hspace=.58,wspace=.48)
    if ratios is not None:
        gs=fig.add_gridspec(rows,cols,width_ratios=ratios,**options)
        slots=[gs[i//cols,i%cols] for i in range(count)]
    else:
        slots=facet_slots(fig,count,rows,cols,**options)
    cmap = LinearSegmentedColormap.from_list('annotation_expression', ['#E8ECEE','#80B2AE','#146D77','#123F5D'])
    shown_title=textwrap.fill(title,30,break_long_words=False) if cols==1 else title
    fig.text(.065, 1-.23/height, shown_title, fontsize=14, fontweight='bold',color=INK,va='top')
    subtitle = 'Identity and cross-population marker evidence' if mode=='atlas' else (
        focus_group+'  /  '+str(sum(emb.group==focus_group))+' of '+str(len(emb))+' displayed cells  /  '+str(len(marker_order))+' selected markers')
    subtitle_y=.23+len(shown_title.splitlines())*.23+.12
    fig.text(.065,1-subtitle_y/height,textwrap.fill(subtitle,38) if cols==1 else subtitle,
             fontsize=10,color=MUTED,va='top')
    panels=[]
    for i in range(count):
        ax=fig.add_subplot(slots[i]); panels.append(ax)
        if i==0:
            _coordinates(ax,emb)
            if mode=='atlas':
                for group in names:
                    q=emb[emb.group==group]
                    ax.scatter(q.x,q.y,s=8,color=pal[group],alpha=.8,ec='none',rasterized=True)
                for row in anchors.itertuples():
                    ax.text(row.x,row.y,row.label,color=pal[row.group],ha='center',va='center',fontsize=10,
                            bbox=dict(fc='white',ec='none',alpha=.85,pad=1.5))
            else:
                q=emb[emb.group==focus_group]
                ax.scatter(emb.x,emb.y,s=7,color=LIGHT,ec='none',rasterized=True)
                ax.scatter(q.x,q.y,s=9,color=pal[focus_group],alpha=.9,ec='none',rasterized=True)
            _heading(ax,'A','Cell identities' if mode=='atlas' else 'Population location')
        elif i==1:
            _dot(ax,dots,names,list(marker_order),expression_limits,cmap,focus_group,pal)
            _heading(ax,'B','Marker specificity')
        else:
            gene=marker_order[i-2];q=features[features.feature==gene].sort_values('value',kind='stable')
            _coordinates(ax,emb)
            ax.scatter(q.x,q.y,s=7,c=q.value,cmap=cmap,norm=Normalize(*expression_limits),ec='none',rasterized=True)
            _heading(ax,chr(65+i),gene)
    # Shared guides have a reserved bottom lane directly under the data panels.
    cax=fig.add_axes([.15 if cols==1 else .67,.43/height,.70 if cols==1 else .26,.075/height])
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(*expression_limits),cmap=cmap),cax=cax,orientation='horizontal')
    cb.set_label(textwrap.fill(expression_label,28) if cols==1 else expression_label,fontsize=9.5,labelpad=2);cb.ax.tick_params(labelsize=9)
    legend=fig.legend(handles=[Line2D([],[],ls='',marker='o',color='#527F89',
                        ms=math.sqrt(130*p),label=str(int(p*100))+'%') for p in [.25,.5,1]],
                      title='Cells detected',loc='lower left',bbox_to_anchor=(.065,(.96 if cols==1 else .25)/height),
                      ncols=3,frameon=False,fontsize=9.5,title_fontsize=9.5,
                      handletextpad=.35,columnspacing=1.1,borderaxespad=0)
    legend._page_fixed_anchor=True
    stamp(fig,data,'annotation_evidence',mode=mode,focus_group=focus_group,
          marker_order=list(marker_order),comparison_groups=names,
          all_cells_retained=True,expression_limits=list(expression_limits),
          detection_definition=detection_definition,coordinates_refitted=False,
          layout={'rows':rows,'columns':cols},scientific_acceptance=False)
    for ax in fig.axes:ax._explicit_guide_layout=True
    fig=apply_project_style(fig,theme)
    fig.texts[0].set_fontsize(14)
    # Restoring deliberate hierarchy after the common typography adapter is
    # appearance only. It prevents generic notes from flattening panel headings.
    for ax in panels:
        for t in ax.texts:
            if getattr(t,'_panel_heading',False):t.set_fontsize(11);t.set_fontweight('bold')
    return fig
