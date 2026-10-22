"""Alternative publication compositions of supplied transcriptomic results.

Coordinates, scores, cloud geometry and annotation evidence remain frozen.
Only display counts, ordering and empirical quantiles are used; no fitting.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import MaxNLocator
from figure_core import checked, stamp
from project_theme import group_palette, apply_project_style
from figure_workbench.responsive import grid_shape, facet_slots, canvas_budget

INK='#263E4B'; MUTED='#627983'; GRID='#E8EEF0'


def _axis(fig, rect):
    a=fig.add_axes(rect);a.spines[['top','right']].set_visible(False)
    a.spines[['bottom','left']].set_color('#BBCBD1')
    a.tick_params(labelsize=9,colors=INK,length=3,width=.6)
    return a


def _head(fig,title,subtitle):
    h=fig.get_figheight();width=max(30,int(fig.get_figwidth()*10))
    fig.text(.07,1-.23/h,textwrap.fill(title,width),fontsize=15,fontweight='bold',color=INK,va='top')
    fig.text(.07,1-.64/h,textwrap.fill(subtitle,width+20),fontsize=9.5,color=MUTED,va='top')


def _finish(fig,data,theme,family,**options):
    for a in fig.axes:a._explicit_guide_layout=True
    stamp(fig,data,'transcriptomic_alternative',family=family,**options,
          inference_performed=False,scientific_acceptance=False)
    return apply_project_style(fig,theme)


def _note(fig,text):
    fig.text(.07,.18/fig.get_figheight(),textwrap.fill(text,max(45,int(fig.get_figwidth()*13))),fontsize=8.5,color=MUTED,va='bottom')


def pca(data,theme,title,axis_labels,ellipse_definition,presentation,ncols='auto',nrows=None,panel_width=4.5,panel_height=4.0):
    d=checked(data[data.record_type=='embedding'],['object_id','group','x','y'],['x','y'])
    e=checked(data[data.record_type=='ellipse'],['group','x','y','width','height','angle'],['x','y','width','height','angle'])
    names=list(d.group.unique());pal=group_palette(theme,names)
    if d.object_id.duplicated().any() or not ellipse_definition or not axis_labels or len(axis_labels)!=2:raise ValueError('Unique PCA samples, exact axes and ellipse meaning required')
    if set(e.group)!=set(names) or e.group.duplicated().any() or ((e.width<=0)|(e.height<=0)).any() or any(sum(d.group==g)<3 for g in names):raise ValueError('Complete valid supplied ellipse geometry and at least three samples per group required')
    if 'coverage' in e:
        e=checked(e,['coverage'],['coverage'])
        if ((e.coverage<=0)|(e.coverage>=1)).any():raise ValueError('Supplied coverage must be between zero and one; never infer coverage')
    var=data[data.record_type=='pc_variance']
    if not var.empty:var=checked(var,['component','percent'],['percent'])
    if not var.empty and (var.component.duplicated().any() or (var.percent<0).any() or abs(var.percent.sum()-100)>1e-6):raise ValueError('Complete supplied variance profile must sum to 100%')
    facets=presentation=='facets';rows,cols=grid_shape(len(names),ncols,nrows) if facets else (1,1)
    if not facets and (nrows is not None or ncols!='auto'):raise ValueError('Use facets for PCA row/column requests')
    width=max(9.8,cols*panel_width+.8) if facets else max(10.2,panel_width*2.3)
    height=1.7+rows*panel_height+(1.3 if facets else .3)
    fig=plt.figure(figsize=canvas_budget(width,height));_head(fig,title,str(len(d))+' supplied observations · colour + shape identity · frozen contours and coordinates')
    markers=['o','s','^','D','P','X'];bounds=[d.x.min(),d.x.max(),d.y.min(),d.y.max()]
    # Retain complete contour extents as well as all observations.
    rx=max(abs(e.width).max(),abs(e.height).max())/2
    lo=min(bounds[0],float((e.x-rx).min()));hi=max(bounds[1],float((e.x+rx).max()));yl=min(bounds[2],float((e.y-rx).min()));yh=max(bounds[3],float((e.y+rx).max()))
    def score(ax,focus=None):
        if focus is not None:ax.scatter(d.x,d.y,c='#DCE5E8',s=21,ec='none',zorder=1)
        for i,g in enumerate(names):
            if focus is not None and g!=focus:continue
            q=d[d.group==g];r=e[e.group==g].iloc[0]
            ax.add_patch(Ellipse((r.x,r.y),r.width,r.height,angle=r.angle,fc=pal[g]+'16',ec=pal[g],lw=1.2,zorder=1))
            ax.scatter(q.x,q.y,c=pal[g],marker=markers[i%6],s=48,ec='white',lw=.7,zorder=3)
            if len(d)<=18:
                for item in q.itertuples():ax.annotate(str(item.object_id),(item.x,item.y),xytext=(5,6),textcoords='offset points',fontsize=8,color=INK)
        ax.axhline(0,c=GRID,lw=.7,zorder=0);ax.axvline(0,c=GRID,lw=.7,zorder=0)
        ax.set(xlim=(lo-.12,hi+.12),ylim=(yl-.12,yh+.12),xlabel=axis_labels[0],ylabel=axis_labels[1]);ax.xaxis.set_major_locator(MaxNLocator(5));ax.yaxis.set_major_locator(MaxNLocator(5))
    if facets:
        for i,(g,slot) in enumerate(zip(names,facet_slots(fig,len(names),rows,cols,left=.09,right=.96,bottom=1.15/height,top=1-1.85/height,wspace=.80,hspace=.42))):
            ax=fig.add_subplot(slot);score(ax,g);ax.set_title(g+' · n='+str(sum(d.group==g)),loc='left',color=pal[g],fontweight='bold',pad=12)
        _note(fig,ellipse_definition+' All other samples remain in the grey background; limits match across panels.')
    else:
        from figure_integrated_views import _marginals
        has_marginals={'pca_x_bin','pca_y_bin'}<=set(data.record_type)
        compact=var.empty and not has_marginals
        if has_marginals:
            ax,top,right=_marginals(fig,[.09,.20,.57,.57],data,d,pal,'x','y',xkind='pca_x_bin',ykind='pca_y_bin');score(ax);top.set_xlim(ax.get_xlim());right.set_ylim(ax.get_ylim())
        else:
            ax=_axis(fig,[.09,.22,.86 if compact else .47,.55]);score(ax)
        if not compact:
            a=_axis(fig,[.74,.43,.21,.30]);a.spines[:].set_visible(False);a.set_xticks([]);a.set_yticks([])
            a.text(0,1.08,'Displayed support',transform=a.transAxes,fontsize=11,fontweight='bold',color=INK)
            for i,g in enumerate(names):a.text(0,.93-i*.20,g,transform=a.transAxes,color=pal[g],fontweight='bold');a.text(.98,.93-i*.20,str(sum(d.group==g))+' / '+str(len(d)),ha='right',transform=a.transAxes,color=INK)
        if not var.empty:
            a=_axis(fig,[.74,.20,.21,.15]);a.bar(range(len(var)),var.percent,color=[theme['roles']['primary'] if i<2 else '#D7E3E6' for i in range(len(var))],width=.65)
            ticks=sorted(set([0,min(1,len(var)-1),len(var)//2,len(var)-1]));a.set_xticks(ticks,[var.component.iloc[k] for k in ticks],fontsize=8);a.set_ylabel('Variance %',fontsize=9);a.set_title('Complete supplied variance',loc='left',fontsize=10)
        _note(fig,ellipse_definition+(' Complete variance profile not supplied; the original axis definitions are retained.' if var.empty else ' No PCA or ellipse fitting.'))
    handles=[Line2D([],[],marker=markers[i%6],ls='',c=pal[g],ms=6,label=g+' · n='+str(sum(d.group==g))) for i,g in enumerate(names)]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.07,1-.93/height),ncols=min(4,len(names)),frameon=False,fontsize=9)
    return _finish(fig,data,theme,'pca',presentation=presentation,all_samples_retained=True,ellipse_definition=ellipse_definition,layout={'rows':rows,'columns':cols})


def volcano(data,theme,title,labels,alpha,fc,presentation,panel_width=4.5,panel_height=4.0):
    from figure_integrated_views import _volcano_panel
    d=checked(data[data.record_type=='de'],['gene','log2FC','padj'],['log2FC','padj']).copy()
    if d.empty or d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any() or not 0<alpha<1 or fc<=0:raise ValueError('Complete tested genes and valid thresholds required')
    if len(labels)>12 or set(labels)-set(d.gene) or not labels:raise ValueError('Select one to twelve explicit genes for the evidence register')
    width=max(11.4,2.55*panel_width);height=max(6.8,panel_height+2.8)+(1.7 if presentation=='landscape' else 0)
    fig=plt.figure(figsize=canvas_budget(width,height));_head(fig,title,'Complete tested universe · '+format(len(d),',')+' genes · FDR ≤ '+str(alpha)+' and |log2FC| ≥ '+str(fc))
    baseline=.32 if presentation=='landscape' else .19;span=.47 if presentation=='landscape' else .60
    ax,counts=_volcano_panel(fig,[.075,baseline,.59,span],data,theme,labels,alpha,fc)
    a=_axis(fig,[.75,baseline,.21,span*.82]);a.axis('off');a.set_ylim(len(labels)-.5,-1.0);a.set_xlim(0,1)
    a.text(0,-.7,'Selected evidence',fontsize=11,fontweight='bold',color=INK)
    for i,g in enumerate(labels):
        r=d[d.gene==g].iloc[0];c=theme['roles']['positive'] if r.log2FC>=0 else theme['roles']['negative']
        a.axhspan(i-.43,i+.43,fc='#EFF4F5' if i%2==0 else 'white',ec='none')
        a.text(.02,i-.10,g,fontsize=10,fontweight='bold',color=c);a.text(.02,i+.20,f'log2FC {r.log2FC:+.2f}   FDR {r.padj:.2g}',fontsize=9,color=MUTED)
    colors={'Other':'#B8C4CB','Down':theme['roles']['negative'],'Up':theme['roles']['positive']}
    fig.legend(handles=[Patch(fc=colors[g],label=g+'  '+str(n)+' / '+str(len(d))+' ('+format(n/len(d),'.1%')+')') for g,n in counts.items()],loc='upper left',bbox_to_anchor=(.07,1-.92/height),ncols=3,frameon=False,fontsize=9)
    if presentation=='landscape':
        q=d.sort_values('log2FC',kind='stable');a=_axis(fig,[.09,.115,.86,.12]);a.scatter(np.arange(1,len(q)+1),q.log2FC,s=4,c=[colors['Up'] if p<=alpha and v>=fc else colors['Down'] if p<=alpha and v<=-fc else colors['Other'] for v,p in zip(q.log2FC,q.padj)],ec='none',rasterized=True)
        a.axhline(0,c='#A9BDC6',lw=.7);a.set(xlim=(1,len(q)),xlabel='Every tested gene, ordered by supplied effect',ylabel='log2FC');a.xaxis.set_major_locator(MaxNLocator(5,integer=True))
    _note(fig,'All genes and their supplied adjusted probabilities retained; side register is the explicitly selected label set. Stacked marginal counts are checked against the complete points.')
    return _finish(fig,data,theme,'volcano',presentation=presentation,all_tested_genes=len(d),selected_genes=list(labels),thresholds={'FDR':alpha,'absolute_log2FC':fc})


def gsea(data,theme,contract,curve_order,ranked_universe,metric_label,contrast,gene_set_version,title,presentation,ncols='auto',nrows=None,panel_width=4.8,panel_height=4.7,show_leading_edge=True):
    from figure_gsea import _gsea_input
    from figure_editorial import validate_contract
    validate_contract(contract)
    if not all(isinstance(x,str) and x.strip() for x in [metric_label,contrast,gene_set_version]):raise ValueError('Declare ranked metric, contrast and gene-set version')
    curve,hit,metric,summary,names=_gsea_input(data,curve_order,ranked_universe);pal=group_palette(theme,names)
    if presentation=='cards':rows,cols=grid_shape(len(names),ncols,nrows)
    else:
        if ncols not in ['auto',1] or nrows is not None:raise ValueError('Aligned GSEA uses one common rank axis; use cards for arbitrary rows/columns')
        rows,cols=len(names),1
    height=1.85+rows*panel_height if presentation=='cards' else 3.2+len(names)*1.55;width=max(8.8,cols*max(5.4,panel_width)+.9) if presentation=='cards' else max(10,panel_width*2.1)
    fig=plt.figure(figsize=canvas_budget(width,height));_head(fig,title,contrast+' · '+str(ranked_universe)+' ranked genes · '+gene_set_version)
    if presentation=='cards':slots=facet_slots(fig,len(names),rows,cols,left=.09,right=.96,bottom=1.05/height,top=1-1.25/height,wspace=1.0,hspace=.36)
    else:slots=None
    for i,name in enumerate(names):
        c=curve[curve.pathway==name];h=hit[hit.pathway==name];s=summary.loc[name];lead=h[h.leading_edge==1]
        if slots:
            rect=slots[i].get_position(fig);x,y,w,hh=rect.x0,rect.y0,rect.width,rect.height
            ax=_axis(fig,[x,y+hh*.49,w,hh*.40]);rug=_axis(fig,[x,y+hh*.34,w,hh*.09]);met=_axis(fig,[x,y+hh*.08,w,hh*.19])
            ax.set_title(textwrap.fill(name,max(23,int(w*width*10)))+f'\nNES {s.NES:+.2f}   FDR {s.padj:.2g}   set n={int(s.set_size)}',loc='left',color=pal[name],fontsize=10.5,fontweight='bold',pad=9)
            ax.set_ylabel('Running ES',fontsize=9);met.set_ylabel(metric_label,fontsize=8)
            met.fill_between(metric['rank'],metric.value,0,color='#C4D7DE',alpha=.7);met.plot(metric['rank'],metric.value,c='#657F8C',lw=.7);met.set(xlim=(1,ranked_universe),xlabel='Rank in complete ordered list');met.xaxis.set_major_locator(MaxNLocator(4,integer=True))
        else:
            hh=1.55/height;y=1-(1.3+(i+1)*1.55)/height;ax=_axis(fig,[.09,y+.18/height,.60,1.04/height]);rug=_axis(fig,[.09,y,.60,.13/height]);ax.set_ylabel('ES',fontsize=9)
            ax.text(1.05,.90,textwrap.fill(name,26)+f'\nNES {s.NES:+.2f}\nFDR {s.padj:.2g} · n={int(s.set_size)}\nLeading {len(lead)} / {len(h)}',transform=ax.transAxes,va='top',fontsize=9,color=pal[name],linespacing=1.6)
        ax.plot(c['rank'],c.value,c=pal[name],lw=1.75);ax.fill_between(c['rank'],c.value,0,color=pal[name],alpha=.12);ax.axhline(0,c='#A2B5BE',lw=.65);ax.set_xlim(1,ranked_universe);ax.tick_params(labelbottom=False);ax.yaxis.set_major_locator(MaxNLocator(3))
        rug.vlines(h['rank'],0,1,color=pal[name],lw=.7,alpha=.35)
        if show_leading_edge:rug.vlines(lead['rank'],0,1,color=pal[name],lw=1.4)
        rug.set(xlim=(1,ranked_universe),ylim=(0,1));rug.axis('off')
        if slots:fig.text(x,y+hh*.29,'Leading hits: '+str(len(lead))+' / '+str(len(h))+(' · bold rug' if show_leading_edge else ' · emphasis off'),color=MUTED,fontsize=8,va='center')
    if presentation=='aligned':
        met=_axis(fig,[.09,1.0/height,.60,.70/height]);met.fill_between(metric['rank'],metric.value,0,color='#CEDFE3');met.plot(metric['rank'],metric.value,c='#657F8C',lw=.8);met.set(xlim=(1,ranked_universe),xlabel='Rank in complete ordered list',ylabel=metric_label);met.xaxis.set_major_locator(MaxNLocator(5,integer=True))
    _note(fig,'Complete running scores, hit positions, supplied leading-edge flags and ranked metric. No recomputation or interpolation; full gene identities remain in the exact TSV.')
    return _finish(fig,data,theme,'gsea',presentation=presentation,curve_order=names,ranked_universe=ranked_universe,gene_set_version=gene_set_version,complete_tracks=True,layout={'rows':rows,'columns':cols})


def raincloud(data,theme,panels,title,scope_note,columns,rows,presentation):
    from figure_raincloud_geometry import draw_supplied_raincloud
    if any(p['kind']!='points' or not p.get('grouped_distribution') or not p.get('point_unit') or 'cloud_shapes' not in p for p in panels):raise ValueError('Raincloud alternatives require all observations, count units and supplied cloud geometry per panel')
    nr,nc=grid_shape(len(panels),min(2,len(panels)) if columns=='auto' else columns,rows)
    horizontal=presentation=='raincloud_horizontal';width=max(8.8,nc*5.6+.6);height=1.75+nr*(3.4 if horizontal else 3.65)
    fig=plt.figure(figsize=canvas_budget(width,height));_head(fig,title,scope_note)
    for p,slot in zip(panels,facet_slots(fig,len(panels),nr,nc,left=.12,right=.96,bottom=.65/height,top=1-1.25/height,hspace=.50,wspace=1.0)):
        q=checked(data[data.panel_id==p['id']],['series','x','y'],['x','y']);groups=p.get('series_order',list(q.series.unique()));pal=group_palette(theme,groups)
        if set(groups)!=set(q.series) or len(groups)!=len(set(groups)) or set(p['cloud_shapes'])!=set(groups):raise ValueError('Complete unique group order and clouds required')
        a=fig.add_subplot(slot);a.spines[['top','right']].set_visible(False);a.tick_params(labelsize=9,length=2,colors=INK)
        for i,g in enumerate(groups):draw_supplied_raincloud(a,i,q.loc[q.series==g,'y'].to_numpy(),pal[g],p['cloud_shapes'][g],point_size=23,orientation='horizontal' if horizontal else 'vertical')
        if horizontal:a.set_yticks(range(len(groups)),[g+' · n='+str(sum(q.series==g)) for g in groups]);a.set(xlabel=p['y_label'],ylim=(len(groups)-.5,-.55));a.grid(axis='x',c=GRID,lw=.6)
        else:a.set_xticks(range(len(groups)),[g+'\nn='+str(sum(q.series==g)) for g in groups]);a.set(ylabel=p['y_label'],xlim=(-.55,len(groups)-.5));a.grid(axis='y',c=GRID,lw=.6)
        a.set_axisbelow(True);a.set_title(p['title'],loc='left',fontweight='bold',fontsize=11,color=INK,pad=12)
        a.text(0,1.01,p['point_unit'],transform=a.transAxes,fontsize=8,color=MUTED,va='bottom')
    _note(fig,'Every point retained. Cloud geometry is supplied; thin box = empirical quartiles and median of the displayed observations. No density or inferential interval fitted.')
    return _finish(fig,data,theme,'raincloud',presentation=presentation,all_observations=True,point_units=[p['point_unit'] for p in panels],layout={'rows':nr,'columns':nc})


def marker(data,theme,mode,title,expression_label,detection_definition,expression_limits,marker_order,focus_group,group_order,ncols,nrows,panel_width,panel_height,composition):
    from figure_annotation_views import plot_annotation_evidence,_coordinates,_dot
    # Reuse the complete canonical scientific channel checks, then compose anew.
    probe=plot_annotation_evidence(data,theme,mode=mode,title=title,expression_label=expression_label,detection_definition=detection_definition,expression_limits=expression_limits,marker_order=marker_order,focus_group=focus_group,group_order=group_order,ncols='auto',composition='evidence')
    plt.close(probe)
    if mode!='subgroup':raise ValueError('Marker alternatives require one subgroup and complete marker channels')
    emb=data[data.record_type=='embedding'];dots=data[data.record_type=='marker_dot'];features=data[data.record_type=='feature_map'];names=list(emb.group.unique()) if group_order is None else list(group_order);pal=group_palette(theme,names)
    strip=composition=='strips'
    if strip and ncols not in ['auto',1]:raise ValueError('Strips require one complete marker per row; use paired_cards for multiple columns')
    columns=1 if strip else (2 if ncols=='auto' and nrows is None else ncols);nr,nc=grid_shape(len(marker_order),columns,nrows)
    step=max(2.65 if strip else 3.15,panel_height);h=step-.85
    context_extra=.075*max(map(len,marker_order)) if len(marker_order)>6 else 0
    width=max(11.7 if strip else nc*6.3+1,panel_width*(3.25 if strip else nc*1.95));height=5.7+context_extra+nr*step;fig=plt.figure(figsize=canvas_budget(width,height))
    _head(fig,title,focus_group+' · '+str(sum(emb.group==focus_group))+' / '+str(len(emb))+' cells · '+str(len(marker_order))+' markers · '+str(len(names))+' comparison identities')
    cmap=LinearSegmentedColormap.from_list('marker_signal',['#E7EDEF','#91BEB8','#227F83','#123F58']);norm=Normalize(*expression_limits)
    a=_axis(fig,[.07,1-3.45/height,.29,2.2/height]);_coordinates(a,emb);a.scatter(emb.x,emb.y,c='#DCE5E8',s=5,ec='none',rasterized=True);q=emb[emb.group==focus_group];a.scatter(q.x,q.y,c=pal[focus_group],s=8,ec='none',rasterized=True);a.set_title('A  Population location',loc='left',fontsize=11,fontweight='bold')
    a=_axis(fig,[.48,1-3.35/height,.45,1.85/height]);_dot(a,dots,names,marker_order,expression_limits,cmap,focus_group,pal);a.set_title('B  All-identity specificity',loc='left',fontsize=11,fontweight='bold',pad=14)
    for index,gene in enumerate(marker_order):
        row,col=divmod(index,nc);cw=.89/nc;in_row=min(nc,len(marker_order)-row*nc);x=.07+(col+(nc-in_row)/2)*cw;bottom=height-4.45-context_extra-row*step-h
        a=_axis(fig,[x,bottom/height,cw*(.35 if strip else .37),h/height]);_coordinates(a,emb);q=features[features.feature==gene].sort_values('value',kind='stable');a.scatter(q.x,q.y,c=q.value,cmap=cmap,norm=norm,s=6,ec='none',rasterized=True);a.set_title(gene,loc='left',fontsize=11,fontweight='bold',pad=8)
        part=dots[dots.feature==gene].set_index('group').loc[names];focus=part.loc[focus_group]
        a.text(0,-.07,f'Target: {focus.fraction:.0%} detected · mean {focus.value:.2f}',transform=a.transAxes,fontsize=8,color=MUTED)
        b=_axis(fig,[x+cw*(.53 if strip else .62),bottom/height,cw*(.43 if strip else .33),h/height]);yy=np.arange(len(names));b.axhspan(names.index(focus_group)-.42,names.index(focus_group)+.42,fc=pal[focus_group]+'18',ec='none')
        b.hlines(yy,0,part.value,colors='#D7E3E7',lw=2);b.scatter(part.value,yy,s=90*part.fraction,c=part.value,cmap=cmap,norm=norm,ec='white',lw=.45,zorder=3);b.set(ylim=(len(names)-.5,-.5),xlim=expression_limits,xlabel='Supplied mean');b.set_yticks(yy,[textwrap.fill(g,13) for g in names],fontsize=8);b.spines['left'].set_visible(False);b.tick_params(axis='y',length=0);b.xaxis.set_major_locator(MaxNLocator(3));b.set_title('Across all identities',loc='left',fontsize=9,color=MUTED)
    cax=fig.add_axes([.71,.95/height,.23,.08/height]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal');cb.set_label(expression_label,fontsize=9);cb.ax.tick_params(labelsize=8)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',color='#527F89',ms=math.sqrt(90*p),label=str(int(p*100))+'%') for p in [.25,.5,1]],title='Cells detected',loc='lower left',bbox_to_anchor=(.07,.60/height),ncols=3,frameon=False,fontsize=9,title_fontsize=9)
    _note(fig,detection_definition+'; all feature maps share the same coordinates, expression limits and complete comparison identities.')
    return _finish(fig,data,theme,'subgroup_markers',composition=composition,focus_group=focus_group,marker_order=list(marker_order),all_cells_retained=True,expression_limits=list(expression_limits),layout={'marker_rows':nr,'marker_columns':nc})
