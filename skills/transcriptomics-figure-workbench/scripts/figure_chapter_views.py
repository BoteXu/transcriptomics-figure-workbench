"""Adaptive complementary panels from explicitly frozen transcriptomic summaries.

This drawing grammar does not call an analysis engine. Every curve, interval,
layout coordinate, matrix value and annotation must already be supplied.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from figure_core import checked, stamp
from project_theme import apply_project_style,group_palette


def _wrap(value, width=19):
    return '\n'.join(textwrap.wrap(str(value), width, break_long_words=False))


def _order(values):
    return list(dict.fromkeys(map(str, values)))


def _colours(theme, names):
    return group_palette(theme,names)


def _draw(ax, d, p, theme):
    kind=p['kind'];required={'curve':['series','x','y'], 'points':['series','x','y'],
        'interval':['label','x','lower','upper'], 'matrix':['label','series','value'],
        'bubble':['label','series','value','fraction'], 'embedding':['label','series','x','y'],
        'network':['label','series','x','y','target','target_x','target_y','value'],
        'stack':['label','series','value'], 'bars':['label','value'],
        'vector':['label','x','y','u','v','value']}[kind]
    numeric=[c for c in required if c in ['x','y','lower','upper','value','fraction','target_x','target_y','u','v']]
    d=checked(d,required,numeric)
    if kind in ['curve','points','embedding','network','stack','matrix','bubble']:
        names=_order(d.series)
        if 'series_order' in p:
            if len(p['series_order'])!=len(names) or set(p['series_order'])!=set(names):raise ValueError('Series order must retain every supplied category')
            names=list(p['series_order'])
        if kind not in ['matrix','bubble']:pal=_colours(theme,names)
    ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,width=.6,labelsize=10)
    ax.set_title(p['title'],loc='left',fontsize=12,fontweight='bold',pad=17)
    ax.set_xlabel(p.get('x_label',''),labelpad=8);ax.set_ylabel(p.get('y_label',''),labelpad=8)
    if kind in ['curve','points']:
        if kind=='points' and not p.get('point_unit'):raise ValueError('Declare what each point represents')
        drawstyle=p.get('drawstyle','default')
        if drawstyle not in ['default','steps-post']:raise ValueError('Use exact supplied straight segments or explicitly declared post steps')
        if d.duplicated(['series','x']).any() and kind=='curve':raise ValueError('Unique supplied curve coordinates required')
        for name in names:
            q=d[d.series==name].sort_values('x');c=pal[name]
            if kind=='curve':
                if {'lower','upper'}.issubset(q) and q[['lower','upper']].notna().all().all():
                    if not p.get('interval_definition') or ((q.lower>q.y)|(q.upper<q.y)).any():raise ValueError('Define valid supplied interval bounds')
                    if not p.get('interval_label'):raise ValueError('Supplied shaded intervals need a visible meaning')
                    ax.fill_between(q.x,q.lower,q.upper,color=c,alpha=.11,lw=0,step='post' if drawstyle=='steps-post' else None)
                ax.plot(q.x,q.y,color=c,lw=1.8,label=name,drawstyle=drawstyle)
            elif p.get('grouped_distribution',False):
                if q.x.nunique()!=1 or float(q.x.iloc[0])!=names.index(name):raise ValueError('Grouped distributions require explicit nominal group positions')
                if 'cloud_shapes' in p:
                    from figure_raincloud_geometry import draw_supplied_raincloud
                    if set(p['cloud_shapes'])!=set(names):raise ValueError('Supply one cloud shape per complete displayed group')
                    draw_supplied_raincloud(ax,names.index(name),q.y,c,p['cloud_shapes'][name],point_size=32)
                    continue
                x=names.index(name);offsets=np.linspace(-.12,.12,len(q)) if len(q)>1 else [0]
                box=ax.boxplot([q.y],positions=[x],widths=.44,patch_artist=True,showfliers=False,
                    boxprops=dict(fc=c+'28',ec=c,lw=1),medianprops=dict(color=c,lw=1.7),whiskerprops=dict(color=c,lw=1),capprops=dict(color=c,lw=1))
                ax.scatter(x+np.asarray(offsets),q.y,s=31,c=c,alpha=.9,ec='white',lw=.5,zorder=3)
            else:ax.scatter(q.x,q.y,s=17,c=c,alpha=.55,ec='none',rasterized=True,label=name)
        if p.get('grouped_distribution',False):
            ax.set_xticks(range(len(names)),[name+'\nn='+str(sum(d.series==name)) for name in names]);ax.set_xlim(-.5,len(names)-.5)
        else:ax.legend(loc='upper center',bbox_to_anchor=(.5,-.25),ncols=min(3,len(names)),frameon=False,fontsize=9,handlelength=1.3,title=('Point: '+p['point_unit']) if kind=='points' else p.get('interval_label',''),title_fontsize=9)
        ax.grid(axis='y',color='#E7EDF0',lw=.6);ax.set_axisbelow(True)
    elif kind=='interval':
        if d.label.duplicated().any() or ((d.lower>d.x)|(d.upper<d.x)).any() or not p.get('interval_definition'):raise ValueError('Unique labels and explicitly defined valid intervals required')
        y=np.arange(len(d));span=max(float(d.upper.max()-d.lower.min()),.1)
        for i,r in enumerate(d.itertuples()):
            c=theme['roles']['positive'] if r.x>=p.get('reference',0) else theme['roles']['negative']
            if i%2==0:ax.axhspan(i-.45,i+.45,color='#F2F6F7',zorder=0)
            ax.plot([r.lower,r.upper],[i,i],c=c,lw=2,zorder=2);ax.scatter(r.x,i,c=c,s=35,ec='white',lw=.5,zorder=3)
        ax.axvline(p.get('reference',0),color='#A4B4BF',ls=(0,(3,3)),lw=.8)
        ax.set_yticks(y,[_wrap(x,24) for x in d.label]);ax.invert_yaxis();ax.margins(x=.12,y=.12);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
    elif kind in ['matrix','bubble']:
        rows=_order(d.label);cols=names
        if d.duplicated(['label','series']).any() or len(d)!=len(rows)*len(cols):raise ValueError('Supply the complete unique matrix; missing values require an explicit separate panel')
        values=d.pivot(index='label',columns='series',values='value').reindex(index=rows,columns=cols).to_numpy()
        limits=p.get('limits')
        if not isinstance(limits,list) or len(limits)!=2 or limits[0]>=limits[1]:raise ValueError('Declare matrix/colour limits')
        if values.min()<limits[0]-1e-9 or values.max()>limits[1]+1e-9:raise ValueError('Colour limits may not silently clip supplied values')
        signed=limits[0]<0<limits[1]
        cmap=LinearSegmentedColormap.from_list('chapter',theme['continuous']['diverging'] if signed else theme['continuous']['sequential'])
        norm=TwoSlopeNorm(vmin=limits[0],vcenter=0,vmax=limits[1]) if signed else plt.Normalize(*limits)
        if kind=='matrix':
            art=ax.imshow(values,aspect='auto',cmap=cmap,norm=norm,interpolation='nearest')
            if len(rows)*len(cols)<=60 and p.get('show_values',True):
                value_format='.0f' if np.array_equal(values,np.round(values)) else '.2f'
                for i in range(len(rows)):
                    for j in range(len(cols)):
                        rgba=cmap(norm(values[i,j]));lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                        ax.text(j,i,format(values[i,j],value_format),ha='center',va='center',fontsize=9,color='white' if lum<.43 else '#294656')
        else:
            if ((d.fraction<0)|(d.fraction>1)).any() or not p.get('fraction_definition'):raise ValueError('Supply fractions in [0,1] and their denominator')
            xs=[cols.index(x) for x in d.series];ys=[rows.index(x) for x in d.label]
            art=ax.scatter(xs,ys,s=160*d.fraction,c=d.value,cmap=cmap,norm=norm,ec='white',lw=.4)
            ax.set(xlim=(-.6,len(cols)-.4),ylim=(len(rows)-.4,-.6));ax.set_axisbelow(True);ax.grid(color='#E5ECEF',lw=.5)
            handles=[Line2D([],[],ls='',marker='o',color='#617C8A',ms=math.sqrt(160*x),label=str(int(x*100))+'%') for x in [.25,.75]]
            ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,-.30),ncols=2,frameon=False,fontsize=9,title=p.get('size_label','Fraction'),title_fontsize=9)
        ax.set_xticks(range(len(cols)),[_wrap(x,13) for x in cols],rotation=30,ha='right');ax.set_yticks(range(len(rows)),[_wrap(x,23) for x in rows]);ax.tick_params(length=0);ax.spines[:].set_visible(False)
        cb=ax.figure.colorbar(art,ax=ax,pad=.035,fraction=.04,shrink=.82);cb.set_label(p['value_label'],fontsize=10);cb.ax.tick_params(labelsize=9,length=2)
    elif kind=='embedding':
        if d.label.duplicated().any():raise ValueError('One position per explicit object')
        for name in names:
            q=d[d.series==name];ax.scatter(q.x,q.y,c=pal[name],s=max(5,min(18,3000/len(d))),alpha=.65,ec='none',rasterized=True)
            if {'anchor_x','anchor_y'}.issubset(q) and q[['anchor_x','anchor_y']].notna().all().all():
                anchors=q[['anchor_x','anchor_y']].drop_duplicates()
                if len(anchors)!=1:raise ValueError('One explicit label anchor per category')
                ax.text(*anchors.iloc[0],_wrap(name),fontsize=10,ha='center',bbox=dict(boxstyle='round,pad=.25',fc='white',ec='none',alpha=.85))
        ax.set_aspect('equal',adjustable='box');ax.margins(.15);ax.spines[:].set_visible(False);ax.set_xticks([]);ax.set_yticks([])
        if 'coordinate_limits' in p:
            bounds=p['coordinate_limits']
            if not isinstance(bounds,list) or len(bounds)!=4 or not np.isfinite(bounds).all() or bounds[0]>=bounds[1] or bounds[2]>=bounds[3]:
                raise ValueError('Declare increasing finite x/y embedding limits')
            if d.x.min()<bounds[0] or d.x.max()>bounds[1] or d.y.min()<bounds[2] or d.y.max()>bounds[3]:
                raise ValueError('Shared embedding limits must retain every supplied point')
            ax.set(xlim=bounds[:2],ylim=bounds[2:])
        ax.legend(handles=[Line2D([],[],ls='',marker='o',ms=5,c=pal[x],label=x) for x in names],loc='upper center',bbox_to_anchor=(.5,-.10),ncols=min(3,len(names)),frameon=False,fontsize=9)
    elif kind=='network':
        if d.duplicated(['label','target']).any() or (d.value<0).any():raise ValueError('Unique explicit nonnegative edges required')
        if not p.get('edge_definition'):raise ValueError('Declare edge meaning and full selection rule')
        nodes={}
        for r in d.itertuples():
            for label,x,y in [(r.label,r.x,r.y),(r.target,r.target_x,r.target_y)]:
                if label in nodes and nodes[label]!=(x,y):raise ValueError('Inconsistent frozen network coordinates')
                nodes[label]=(x,y)
            if p.get('directed',False):
                ax.add_patch(FancyArrowPatch((r.x,r.y),(r.target_x,r.target_y),arrowstyle='-|>',mutation_scale=12,shrinkA=8,shrinkB=8,color=pal[r.series],alpha=.65,lw=.5+1.7*r.value/max(d.value.max(),1e-9),zorder=1))
            else:ax.plot([r.x,r.target_x],[r.y,r.target_y],color=pal[r.series],alpha=.22+.38*r.value/max(d.value.max(),1e-9),lw=.5+1.7*r.value/max(d.value.max(),1e-9),zorder=1)
        for label,(x,y) in nodes.items():
            ax.scatter(x,y,s=100,c='#FAFDFD',ec='#518895',lw=1.2,zorder=3);ax.annotate(_wrap(label,13),(x,y),xytext=(0,10),textcoords='offset points',ha='center',fontsize=10,zorder=4)
        ax.margins(.25);ax.set_aspect('equal');ax.spines[:].set_visible(False);ax.set_xticks([]);ax.set_yticks([])
        weights=[float(d.value.min()),float(d.value.max())]
        ax.legend(handles=[Line2D([],[],c=pal[names[0]],lw=.5+1.7*w/max(d.value.max(),1e-9),label=format(w,'.2g')) for w in weights],loc='upper center',bbox_to_anchor=(.5,-.10),ncols=2,frameon=False,title=p.get('edge_label','Supplied edge weight'),title_fontsize=9,fontsize=9)
    elif kind=='stack':
        labels=_order(d.label)
        if d.duplicated(['label','series']).any() or len(d)!=len(labels)*len(names) or (d.value<0).any():raise ValueError('Complete additive nonnegative segments required')
        if not p.get('denominator_definition'):raise ValueError('Declare the segment denominator')
        bottom=np.zeros(len(labels))
        for name in names:
            q=d[d.series==name].set_index('label').reindex(labels);ax.barh(range(len(labels)),q.value,left=bottom,color=pal[name],height=.65,label=name,ec='white',lw=.4);bottom+=q.value.to_numpy()
        ax.set_yticks(range(len(labels)),[_wrap(x) for x in labels]);ax.invert_yaxis();ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.17),ncols=min(3,len(names)),frameon=False,fontsize=9)
    elif kind=='bars':
        if d.label.duplicated().any():raise ValueError('One supplied quantity per label')
        ax.hlines(range(len(d)),0,d.value,color='#B5D4D5',lw=3);ax.scatter(d.value,range(len(d)),c='#218C8D',s=40,zorder=3)
        ax.set_yticks(range(len(d)),[_wrap(x,23) for x in d.label]);ax.invert_yaxis();ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0);ax.margins(x=.15)
    elif kind=='vector':
        if d.label.duplicated().any() or not p.get('vector_definition') or p.get('arrow_scale',0)<=0:raise ValueError('Unique coordinates and explicitly scaled supplied vectors required')
        art=ax.scatter(d.x,d.y,c=d.value,s=10,cmap='viridis',alpha=.45,rasterized=True)
        ax.quiver(d.x,d.y,d.u,d.v,color='#395E6B',angles='xy',scale_units='xy',scale=p['arrow_scale'],width=.004,alpha=.7)
        ax.set_aspect('equal');ax.spines[:].set_visible(False);ax.set_xticks([]);ax.set_yticks([])
        cb=ax.figure.colorbar(art,ax=ax,fraction=.04,pad=.035);cb.set_label(p['value_label'])


def plot_transcriptomic_chapter(data,theme,*,panels,title,scope_note,columns='auto',rows=None,presentation='classic'):
    """Draw a complete, explicitly selected analysis chapter with adaptive packing."""
    if not isinstance(panels,list) or not 1<=len(panels)<=12:raise ValueError('Select one to twelve complementary panels')
    if not title or not scope_note:raise ValueError('Declare the scientific comparison and scope')
    ids=[p['id'] for p in panels]
    if len(ids)!=len(set(ids)) or set(data.panel_id)!=set(ids):raise ValueError('Every input panel must be declared exactly once')
    kinds={'curve','points','interval','matrix','bubble','embedding','network','stack','bars','vector'}
    if any(p.get('kind') not in kinds or not p.get('title') for p in panels):raise ValueError('Use a documented typed panel')
    if presentation in ['raincloud_horizontal','raincloud_vertical']:
        from figure_study_alternatives import raincloud
        return raincloud(data,theme,panels,title,scope_note,columns,rows,presentation)
    if presentation not in ['classic','publication']:raise ValueError('Choose a documented chapter presentation')
    if presentation=='publication' and len(panels)==1 and panels[0]['kind']=='matrix' and panels[0].get('matrix_semantics') in ['design','cell_support']:
        from figure_study_publication import matrix_evidence
        return apply_project_style(matrix_evidence(data,theme,panels[0],title,scope_note),theme)
    if rows is not None and (type(rows) is not int or not 1<=rows<=12):raise ValueError('rows must be one to twelve or unspecified')
    ncols=(math.ceil(len(panels)/rows) if rows else min(2,len(panels))) if columns=='auto' else columns
    if isinstance(ncols,bool) or not isinstance(ncols,int) or not 1<=ncols<=4:raise ValueError('columns is auto or an integer from one to four')
    nrows=rows or math.ceil(len(panels)/ncols)
    if nrows*ncols<len(panels):raise ValueError('Requested rows and columns cannot contain every panel')
    max_labels=max([len(set(data.loc[data.panel_id==p['id'],'label'].dropna())) if p['kind'] in ['interval','matrix','bubble','stack','bars'] else 6 for p in panels])
    height=max(4.1,min(8.5,2.9+max_labels*.18))
    fig=plt.figure(figsize=(6*ncols,height*nrows+1.4),layout='constrained')
    if presentation=='publication':
        ph=3.0 if all(p['kind']=='points' and p.get('grouped_distribution') for p in panels) else 3.7
        fig.set_size_inches(4.6*ncols,ph*nrows+1.2)
    from figure_workbench.responsive import facet_slots
    slots=facet_slots(fig,len(panels),nrows,ncols)
    for i,p in enumerate(panels):
        ax=fig.add_subplot(slots[i]);_draw(ax,data[data.panel_id==p['id']],p,theme)
        ax.text(-.10,1.10,chr(65+i),transform=ax.transAxes,fontsize=14,fontweight='bold',color='#286A7C')
    fig.suptitle(title+'\n'+scope_note,fontsize=14,fontweight='bold')
    if presentation=='publication':
        for ax in fig.axes:
            from figure_study_publication import quiet
            quiet(ax)
    fig.get_layout_engine().set(h_pad=.18,w_pad=.30,hspace=.18,wspace=.14)
    for ax in fig.axes:ax._explicit_guide_layout=True
    stamp(fig,data,'transcriptomic_chapter',panels=panels,title=title,scope_note=scope_note,columns=columns,rows=rows,analysis_performed=False)
    return apply_project_style(fig,theme)
