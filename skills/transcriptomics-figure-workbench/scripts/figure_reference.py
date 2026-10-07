"""Original frozen-table adapters for the 21 user-supplied visual references.

No fitting, PCA, SHAP calculation, Mantel test, clustering, KDE or model training.
Composite inputs use one long table with record_type; the complete table is stamped.
"""
import math
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm, to_rgba
from matplotlib.patches import Circle, Ellipse, Rectangle, PathPatch, Wedge
from matplotlib.path import Path as MPath
from matplotlib.lines import Line2D
from matplotlib.cm import ScalarMappable
from figure_core import checked, stamp, palette_check
from figure_reference_palettes import reference_cmap,semantic_color
from matrix_input import axis_labels

INK='#25313A'

def _new(size=(8,6), font_size=9, font_family='DejaVu Sans'):
    if len(size)!=2 or min(size)<=0 or font_size<=0: raise ValueError('Invalid appearance dimensions')
    with plt.rc_context({'font.family':font_family,'font.size':font_size,'axes.labelcolor':INK,
                         'xtick.color':INK,'ytick.color':INK,'text.color':INK,'svg.fonttype':'none'}):
        return plt.figure(figsize=size)

def _ax(fig, bounds, *, clean=True):
    ax=fig.add_axes(bounds)
    if clean: ax.spines[['top','right']].set_visible(False)
    ax.tick_params(length=3,width=.7,labelsize=8)
    return ax

def _records(data, kind, columns, numeric=(), *, optional=False):
    checked(data,['record_type'])
    d=data.loc[data.record_type==kind]
    if d.empty and optional: return d.copy()
    return checked(d,columns,numeric)

def _types(data, allowed):
    checked(data,['record_type'])
    bad=set(data.record_type)-set(allowed)
    if bad: raise ValueError(f'Unknown record_type: {sorted(bad)}')

def _unique(d,cols):
    if d.duplicated(cols).any(): raise ValueError(f'Duplicate keys: {cols}')

def _grid(d, row, col, value):
    _unique(d,[row,col]); rows=list(pd.unique(d[row])); cols=list(pd.unique(d[col]))
    if len(d)!=len(rows)*len(cols): raise ValueError('Incomplete grid; missing is not zero')
    return d.pivot(index=row,columns=col,values=value).reindex(index=rows,columns=cols),rows,cols

def _intervals(d,estimate='value'):
    if ((d.lower>d[estimate])|(d.upper<d[estimate])).any(): raise ValueError('Interval excludes estimate')

def _signed(d,col='r'):
    if (d[col].abs()>1).any(): raise ValueError('Correlation outside [-1,1]')

def _p(d,col='p'):
    if ((d[col]<0)|(d[col]>1)).any(): raise ValueError('Probability outside [0,1]')

def _finish(fig,data,kind,**spec):
    return stamp(fig,data,'reference_'+kind,adapter_version=1,analysis='none; frozen supplied tables',**spec)

def _colorbar(fig,bounds,cmap,norm,label,orientation='vertical'):
    cax=fig.add_axes(bounds)
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation=orientation)
    cb.set_label(label,fontsize=8); cb.ax.tick_params(labelsize=7)
    return cb

def _pack(values, *, spacing=.1, max_width=.36):
    """Deterministic density-preserving display packing; measured axis unchanged.

    Bin-width is a display parameter, not a KDE or statistic. Ties retain row order.
    Crowded bins expand to max_width; point overlaps remain possible at small size.
    """
    values=np.asarray(values,float)
    if not np.isfinite(values).all() or spacing<=0: raise ValueError('Invalid packing input')
    bins=np.floor(values/spacing).astype(int); offsets=np.zeros(len(values))
    max_count=max(int((bins==b).sum()) for b in np.unique(bins)); step=min(.045,max_width/max(1,math.ceil(max_count/2)))
    for b in np.unique(bins):
        ids=np.flatnonzero(bins==b); n=len(ids)
        ranks=np.array([0]+[v for i in range(1,(n+1)//2+1) for v in (i,-i)])[:n]
        offsets[ids]=ranks*step
    return offsets

def _curve_path(xs,ys):
    vertices=[(xs[0],ys[0])]; codes=[MPath.MOVETO]
    for i in range(len(xs)-1):
        mid=(xs[i]+xs[i+1])/2
        vertices.extend([(mid,ys[i]),(mid,ys[i+1]),(xs[i+1],ys[i+1])]); codes.extend([MPath.CURVE4]*3)
    return MPath(vertices,codes)

def plot_annular_profile(data,palette,*,value_label,area_label,value_max,area_scale=0.045,
                         connect_categories=False,curve_mode='vertices',size=(8,7),font_size=9):
    """R01/R02. Area profile and bubble ring; area in pt^2 per original unit."""
    _types(data,['profile'])
    d=_records(data,'profile',['category','series','value','area'],['value','area'])
    _unique(d,['category','series']); palette_check(d.series,palette)
    if not np.isfinite(value_max) or not np.isfinite(area_scale) or value_max<=0 or area_scale<=0 or (d[['value','area']]<0).any().any() or (d.value>value_max).any(): raise ValueError('Invalid radial/area scale')
    mat,cats,series=_grid(d,'category','series','value'); n=len(cats)
    if n<3 or len(series)>4: raise ValueError('Use 3+ categories and <=4 series')
    if curve_mode not in ('vertices','smooth_display') or (not connect_categories and curve_mode!='vertices'): raise ValueError('Invalid radial display curve')
    theta=np.pi/2-np.arange(n)*2*np.pi/n
    fig=_new(size,font_size); ax=_ax(fig,[.025,.07,.76,.84]); ax.set_aspect('equal'); ax.axis('off')
    hole=.30
    for r in np.linspace(hole,1,5): ax.add_patch(Circle((0,0),r,fill=False,color='#BEC3C6',lw=.8))
    for t,c in zip(theta,cats):
        ax.plot([hole*np.cos(t),1.045*np.cos(t)],[hole*np.sin(t),1.045*np.sin(t)],color='#B9BEC2',lw=.65)
        ax.plot([np.cos(t),1.045*np.cos(t)],[np.sin(t),1.045*np.sin(t)],color=INK,lw=1)
        ax.text(1.10*np.cos(t),1.10*np.sin(t),str(c),ha='center',va='center',fontsize=8)
    for j,s in enumerate(series):
        sub=d.set_index(['category','series']).loc[[(c,s) for c in cats]]
        r=hole+(1-hole)*sub.value.to_numpy()/value_max
        x=r*np.cos(theta); y=r*np.sin(theta)
        if connect_categories:
            if curve_mode=='smooth_display':
                points=[]
                for k in range(n):
                    t=np.linspace(0,1,20,endpoint=False); eased=t*t*(3-2*t)
                    radius=r[k]+(r[(k+1)%n]-r[k])*eased; ang=theta[k]-t*2*np.pi/n
                    points.extend(zip(radius*np.cos(ang),radius*np.sin(ang)))
                points=np.asarray(points); x,y=points[:,0],points[:,1]
            ax.fill(np.r_[x,x[0]],np.r_[y,y[0]],facecolor=palette[s],alpha=.3)
            ax.plot(np.r_[x,x[0]],np.r_[y,y[0]],color=palette[s],lw=1.7)
        else:
            ax.scatter(x,y,color=palette[s],s=12)
        ring=.90-j*.20
        ax.scatter(ring*np.cos(theta),ring*np.sin(theta),s=sub.area*area_scale,color=palette[s],alpha=.52,edgecolor=palette[s],lw=.8)
    ax.add_patch(Circle((0,0),1,fill=False,color=INK,lw=1.5,zorder=5))
    ax.add_patch(Circle((0,0),hole,facecolor='white',edgecolor=INK,lw=1.5,zorder=6))
    ax.text(0,0,value_label,ha='center',va='center',fontsize=12,zorder=7)
    for v in np.linspace(0,value_max,5)[1:]:
        r=hole+(1-hole)*v/value_max
        ax.text(.03,r,f'{v:g}',fontsize=7,va='bottom',zorder=8)
    ax.plot([0,0],[hole,1],color=INK,lw=1.1)
    ax.set(xlim=(-1.18,1.18),ylim=(-1.18,1.18))
    lg=_ax(fig,[.81,.25,.18,.46]); lg.axis('off')
    sizes=np.array([.25,.5,.75])*d.area.max()
    handles=[Line2D([],[],marker='o',ms=np.sqrt(v*area_scale),mfc='white',mec=INK,ls='',label=f'{v:g}') for v in sizes]
    l1=lg.legend(handles=handles,title=area_label,loc='upper left',frameon=False,labelspacing=1.4,fontsize=8,title_fontsize=8); lg.add_artist(l1)
    lg.legend(handles=[Rectangle((0,0),1,1,color=palette[s],label=str(s)) for s in series],title='Series',loc='lower left',frameon=False,fontsize=8,title_fontsize=8)
    return _finish(fig,data,'annular_profile',palette=palette,value_label=value_label,area_label=area_label,value_max=value_max,area_scale=area_scale,connect_categories=connect_categories,radial_zero='inner boundary',curve_mode=curve_mode,smoothing='optional bounded smoothstep connectors only; exact category vertices preserved; no intermediate observations',bubble_area='original area times area_scale')

def plot_ellipse_correlation(data,*,labels,cmap_name='ellipse_yellow_purple',size=(7,7)):
    _types(data,['correlation']); d=_records(data,'correlation',['a','b','r'],['r']); _signed(d)
    _unique(d,['a','b']); labels=list(labels); n=len(labels)
    expected={(labels[i],labels[j]) for i in range(n) for j in range(i+1,n)}
    if set(zip(d.a,d.b))!=expected: raise ValueError('Supply each ordered upper-triangle pair exactly once')
    fig=_new(size); ax=_ax(fig,[.10,.12,.76,.76],clean=False); cm=reference_cmap(cmap_name); norm=Normalize(-1,1)
    for i in range(n+1): ax.axhline(i-.5,color='#BFC3C5',lw=.7); ax.axvline(i-.5,color='#BFC3C5',lw=.7)
    for r in d.itertuples():
        i=labels.index(r.a); j=labels.index(r.b)
        ax.add_patch(Ellipse((j,i),width=.85*np.sqrt(1+r.r),height=.85*np.sqrt(1-r.r),angle=-45,fc=cm(norm(r.r)),ec='none'))
        ax.text(i,j,f'{r.r:.2f}',ha='center',va='center',fontsize=10,color=INK)
    ax.set(xlim=(-.5,n-.5),ylim=(n-.5,-.5),aspect='equal'); ax.set_xticks(range(n),labels); ax.xaxis.tick_top(); ax.set_yticks(range(n),labels); ax.tick_params(length=0,labelsize=12)
    _colorbar(fig,[.89,.12,.025,.76],cm,norm,'Correlation r')
    return _finish(fig,data,'ellipse_correlation',labels=labels,cmap=cmap_name,limits=[-1,1],numeric_color='charcoal for contrast')

def plot_signed_network(data,*,palette_name='network_teal_red',node_color='#45B0C8',size=(7,7)):
    _types(data,['node','edge'])
    nodes=_records(data,'node',['node','order'],['order']); edges=_records(data,'edge',['a','b','r'],['r'])
    _unique(nodes,['node']); _unique(nodes,['order']); _unique(edges,['a','b']); _signed(edges)
    if not set(edges.a).union(edges.b)<=set(nodes.node) or (edges.a==edges.b).any(): raise ValueError('Unknown node or self-edge')
    unordered=[tuple(sorted((str(a),str(b)))) for a,b in zip(edges.a,edges.b)]
    if len(set(unordered))!=len(unordered): raise ValueError('Repeated undirected edge')
    ns=nodes.sort_values('order').node.tolist(); theta=np.pi/2+np.arange(len(ns))*2*np.pi/len(ns)
    positions={n:np.array([np.cos(t),np.sin(t)]) for n,t in zip(ns,theta)}
    fig=_new(size); ax=_ax(fig,[.08,.18,.84,.72]); ax.axis('off'); ax.set_aspect('equal'); cm=reference_cmap(palette_name); norm=Normalize(-1,1)
    for e in edges.itertuples():
        start,end=positions[e.a],positions[e.b]; control=(start+end)*.16
        path=MPath([start,control,end],[MPath.MOVETO,MPath.CURVE3,MPath.CURVE3])
        ax.add_patch(PathPatch(path,fc='none',ec=cm(norm(e.r)),lw=1.8,alpha=.8))
    for n in ns:
        p=positions[n]; ax.scatter(*p,s=230,fc=node_color,ec='#485683',lw=1.2,zorder=3)
        ax.text(*(p*1.12),n,ha='left' if p[0]>.3 else 'right' if p[0]<-.3 else 'center',va='center',fontsize=9,weight='bold')
    ax.set(xlim=(-1.45,1.45),ylim=(-1.22,1.22))
    _colorbar(fig,[.30,.095,.40,.025],cm,norm,'Supplied signed association',orientation='horizontal')
    return _finish(fig,data,'signed_network',palette=palette_name,node_area='constant; unknown reference size encoding not inferred',edge_width='constant',node_order=ns,arrows=False)

def plot_mantel_matrix(data,*,labels,specimen_order,p_type,pearson_p_type,size=(9,7)):
    if p_type not in ('raw','adjusted') or pearson_p_type not in ('raw','adjusted'): raise ValueError('Declare p types')
    _types(data,['correlation','mantel'])
    corr=_records(data,'correlation',['a','b','r','p'],['r','p']); links=_records(data,'mantel',['specimen','target','r','p'],['r','p'])
    _signed(corr); _signed(links); _p(corr); _p(links); _unique(corr,['a','b']); _unique(links,['specimen','target'])
    labels=list(labels); specs=list(specimen_order); n=len(labels)
    expected={(labels[i],labels[j]) for i in range(n) for j in range(i+1,n)}
    if set(zip(corr.a,corr.b))!=expected or not set(links.target)<=set(labels) or not set(links.specimen)<=set(specs): raise ValueError('Incomplete/unknown matrix or link keys')
    fig=_new(size); ax=_ax(fig,[.06,.16,.72,.70]); ax.axis('off'); ax.set_aspect('equal'); cm=reference_cmap('pearson_purple_cyan'); norm=Normalize(-1,1)
    for c in corr.itertuples():
        i=labels.index(c.a); j=labels.index(c.b); x=j; y=-i
        ax.add_patch(Rectangle((x-.48,y-.48),.96,.96,fc='white',ec='#AEB4B8',lw=.5))
        w=.78*np.sqrt(abs(c.r)); ax.add_patch(Rectangle((x-w/2,y-w/2),w,w,fc=cm(norm(c.r)),ec='#70777A',lw=.5))
        star='***' if c.p<.001 else '**' if c.p<.01 else '*' if c.p<.05 else ''
        ax.text(x,y,star,ha='center',va='center',fontsize=7)
    target={l:np.array([i,-i]) for i,l in enumerate(labels)}
    source={s:np.array([-4+1.15*k,-(n*.25+k*n*.17)]) for k,s in enumerate(specs)}
    colors=[semantic_color('significant','#DF3450'),semantic_color('primary','#6C6092'),semantic_color('neutral','#91DD6F')]
    for e in links.itertuples():
        a,b=source[e.specimen],target[e.target]
        ax.add_patch(PathPatch(MPath([a,(a+b)/2+[-.4,-.55],b],[MPath.MOVETO,MPath.CURVE3,MPath.CURVE3]),ec=colors[0 if e.p<.01 else 1 if e.p<.05 else 2],fc='none',lw=.7 if abs(e.r)<.2 else 1.6 if abs(e.r)<.4 else 2.7,alpha=.9))
    for l,p in target.items(): ax.scatter(*p,s=16,color=semantic_color('primary','#3C62B5'),ec='white',lw=.3); ax.text(n+.1,p[1],l,va='center',fontsize=8); ax.text(p[0],.8,l,ha='center',rotation=90,fontsize=8)
    for s,p in source.items(): ax.scatter(*p,s=18,color=semantic_color('primary','#3C62B5')); ax.text(p[0]-.3,p[1],s,ha='right',va='center',fontsize=8)
    ax.set(xlim=(-5,n+2),ylim=(-n-.4,2))
    lg=_ax(fig,[.81,.50,.18,.35]); lg.axis('off')
    l1=lg.legend(handles=[Line2D([],[],color=c,lw=2,label=t) for c,t in zip(colors,['<0.01','0.01–0.05','>=0.05'])],title=f'Mantel {p_type} p',frameon=False,loc='upper left',fontsize=8,title_fontsize=8); lg.add_artist(l1)
    lg.legend(handles=[Line2D([],[],color=INK,lw=w,label=t) for w,t in zip([.7,1.6,2.7],['<0.2','0.2–0.4','>=0.4'])],title='Absolute Mantel r',frameon=False,loc='lower left',fontsize=8,title_fontsize=8)
    _colorbar(fig,[.85,.20,.025,.22],cm,norm,'Pearson r')
    return _finish(fig,data,'mantel_matrix',labels=labels,specimen_order=specs,p_type=p_type,pearson_p_type=pearson_p_type,area='absolute Pearson r',tests='none; supplied statistics')

def plot_parallel_trials(data,*,axis_order,axis_ranges,score_label,score_limits,size=(10,5)):
    _types(data,['trial']); d=_records(data,'trial',['trial_id','dimension','value','score'],['value','score']); _unique(d,['trial_id','dimension'])
    dims=list(axis_order)
    if set(d.dimension)!=set(dims) or len(d)!=d.trial_id.nunique()*len(dims): raise ValueError('Incomplete parallel-coordinate trials')
    if d.groupby('trial_id').score.nunique().max()!=1: raise ValueError('Score must be constant for each trial')
    if score_limits[0]>=score_limits[1] or ((d.score<score_limits[0])|(d.score>score_limits[1])).any(): raise ValueError('Invalid score limits')
    for k in dims:
        lo,hi=axis_ranges[k]
        if lo>=hi or ((d.loc[d.dimension==k,'value']<lo)|(d.loc[d.dimension==k,'value']>hi)).any(): raise ValueError('Axis range clips supplied data')
    fig=_new(size); ax=_ax(fig,[.08,.20,.82,.66]); ax.axis('off'); cm=reference_cmap('performance_blue_red',semantic='sequential'); norm=Normalize(*score_limits)
    for _,sub in d.groupby('trial_id',sort=False):
        sub=sub.set_index('dimension'); vals=[(sub.loc[k,'value']-axis_ranges[k][0])/(axis_ranges[k][1]-axis_ranges[k][0]) for k in dims]
        ax.add_patch(PathPatch(_curve_path(np.arange(len(dims)),vals),fc='none',ec=cm(norm(sub.score.iloc[0])),lw=.65,alpha=.5))
    for i,k in enumerate(dims):
        ax.plot([i,i],[0,1],color=INK,lw=.7); ax.text(i,-.05,k,ha='center',va='top',fontsize=8)
        lo,hi=axis_ranges[k]
        for y in np.linspace(0,1,5): ax.text(i-.02,y,f'{lo+y*(hi-lo):.3g}',ha='right',va='center',fontsize=7)
    ax.set(xlim=(-.1,len(dims)-.9),ylim=(-.08,1.04)); _colorbar(fig,[.93,.22,.018,.62],cm,norm,score_label)
    return _finish(fig,data,'parallel_trials',axis_order=dims,axis_ranges=axis_ranges,score_limits=list(score_limits),score_label=score_label,curve='Bezier display connectors; no fitting')

def _draw_swarm(ax,d,feature_order,cmap,limits,point_size=8):
    norm=Normalize(0,1)
    for i,f in enumerate(feature_order):
        sub=d[d.feature==f]
        offsets=_pack(sub.contribution,spacing=(limits[1]-limits[0])/80)
        ax.scatter(sub.contribution,i+offsets,c=sub.feature_value,cmap=cmap,norm=norm,s=point_size,linewidths=0,alpha=.9)
    ax.axvline(0,color='#9A9D9F',lw=1); ax.set_yticks(range(len(feature_order)),feature_order,fontsize=8)
    ax.set_ylim(len(feature_order)-.6,-.6); ax.set_xlim(limits); ax.grid(axis='y',ls=(0,(1,4)),color='#D8DDE0',lw=.5); ax.set_axisbelow(True)

def plot_contribution_swarm(data,*,feature_order,contribution_label,limits,cmap_name='shap_teal_red',size=(8,8)):
    _types(data,['contribution']); d=_records(data,'contribution',['unit_id','feature','contribution','feature_value'],['contribution','feature_value']); _unique(d,['unit_id','feature'])
    if set(d.feature)!=set(feature_order) or ((d.feature_value<0)|(d.feature_value>1)).any(): raise ValueError('Invalid feature order or normalized feature values')
    if limits[0]>=limits[1] or ((d.contribution<limits[0])|(d.contribution>limits[1])).any(): raise ValueError('Limits clip contributions')
    fig=_new(size); ax=_ax(fig,[.28,.12,.57,.77]); cm=reference_cmap(cmap_name,semantic='sequential')
    _draw_swarm(ax,d,feature_order,cm,limits); ax.set_xlabel(contribution_label)
    _colorbar(fig,[.90,.15,.018,.72],cm,Normalize(0,1),'Feature value (upstream scaled)')
    return _finish(fig,data,'contribution_swarm',feature_order=list(feature_order),limits=list(limits),cmap=cmap_name,color='supplied feature_value on [0,1]',x_label=contribution_label,packing='display offsets only')

def plot_group_beeswarm(data,palette,*,group_order,value_label,summary_label,limits,size=(9,5)):
    _types(data,['observation','summary'])
    d=_records(data,'observation',['unit_id','group','value'],['value']); summaries=_records(data,'summary',['group','value'],['value'])
    _unique(d,['unit_id']); _unique(summaries,['group']); palette_check(d.group,palette)
    if set(d.group)!=set(group_order) or set(summaries.group)!=set(group_order): raise ValueError('Group/summary mismatch')
    if limits[0]>=limits[1] or ((d.value<limits[0])|(d.value>limits[1])).any() or ((summaries.value<limits[0])|(summaries.value>limits[1])).any(): raise ValueError('Limits clip observations or summaries')
    fig=_new(size); ax=_ax(fig,[.10,.15,.86,.74])
    for i,g in enumerate(group_order):
        sub=d[d.group==g]; offset=_pack(sub.value,spacing=(limits[1]-limits[0])/75)
        ax.scatter(i+offset,sub.value,s=9,color=palette[g],lw=0,alpha=.85)
        ax.scatter(i,summaries.set_index('group').loc[g,'value'],s=42,color=INK,ec='white',lw=1,zorder=5)
    ax.set_xticks(range(len(group_order)),group_order); ax.set(xlim=(-.55,len(group_order)-.45),ylim=limits,ylabel=value_label)
    ax.grid(axis='y',color='#E1E7EA',lw=.6); ax.set_axisbelow(True)
    ax.legend(handles=[Line2D([],[],ls='',marker='o',mfc=INK,mec='white',label=summary_label)],frameon=False,loc='upper right')
    return _finish(fig,data,'group_beeswarm',palette=palette,group_order=list(group_order),limits=list(limits),summary=summary_label,value_label=value_label)

def plot_joint_reference(data,palette,*,x_label,y_label,limits,marginal_mode='density',
                         identity=False,residual_label=None,size=(8,7)):
    """R08/R12/R13. Marginals, fits/bands and box summaries are supplied, never fitted."""
    allowed=['point','marginal','density2d','fit','annotation','box','bracket']; _types(data,allowed)
    d=_records(data,'point',['unit_id','group','x','y'],['x','y']); _unique(d,['unit_id']); palette_check(d.group,palette)
    marg=_records(data,'marginal',['group','axis','coordinate','value'],['coordinate','value'])
    if marginal_mode not in ('density','bins'): raise ValueError('marginal_mode must be density or bins')
    if not set(marg.axis)<={'x','y'} or set(marg.group)!=set(d.group) or (marg.value<0).any(): raise ValueError('Invalid marginals')
    _unique(marg,['group','axis','coordinate'])
    for g in pd.unique(d.group):
        if set(marg.loc[marg.group==g,'axis'])!={'x','y'}: raise ValueError('Each group needs both marginals')
    if marginal_mode=='bins': checked(marg,['left','right'],['left','right'])
    if marginal_mode=='bins' and (marg.left>=marg.right).any(): raise ValueError('Invalid marginal bin widths')
    (xmin,xmax),(ymin,ymax)=limits
    if xmin>=xmax or ymin>=ymax or ((d.x<xmin)|(d.x>xmax)|(d.y<ymin)|(d.y>ymax)).any(): raise ValueError('Limits clip points')
    fig=_new(size); ax=_ax(fig,[.12,.14,.66,.62]); top=_ax(fig,[.12,.81,.66,.12]); side=_ax(fig,[.82,.14,.14,.62])
    density=_records(data,'density2d',['group','x','y','value'],['x','y','value'],optional=True)
    if not density.empty:
        if not set(density.group)<=set(d.group) or (density.value<0).any(): raise ValueError('Invalid supplied density grid')
        for g in pd.unique(density.group):
            sub=density[density.group==g]; mat,ys,xs=_grid(sub,'y','x','value')
            if min(mat.shape)<2 or mat.to_numpy().max()<=0: raise ValueError('Nonpositive or degenerate density grid')
            ax.contourf(xs,ys,mat.to_numpy(),levels=np.linspace(mat.to_numpy().max()*.12,mat.to_numpy().max(),5),colors=[palette[g]],alpha=.07)
    for g in pd.unique(d.group):
        sub=d[d.group==g]; ax.scatter(sub.x,sub.y,s=23,color=palette[g],alpha=.78,edgecolor='white',lw=.45,label=g)
        for dim,margax in [('x',top),('y',side)]:
            m=marg[(marg.group==g)&(marg.axis==dim)].sort_values('coordinate')
            if marginal_mode=='bins':
                if dim=='x': margax.bar(m.coordinate,m.value,width=m.right-m.left,color=palette[g],ec='#7E8488',lw=.5,alpha=.55)
                else: margax.barh(m.coordinate,m.value,height=m.right-m.left,color=palette[g],ec='#7E8488',lw=.5,alpha=.55)
            elif dim=='x': margax.fill_between(m.coordinate,0,m.value,color=palette[g],alpha=.35); margax.plot(m.coordinate,m.value,color=palette[g],lw=1)
            else: margax.fill_betweenx(m.coordinate,0,m.value,color=palette[g],alpha=.35); margax.plot(m.value,m.coordinate,color=palette[g],lw=1)
    fits=_records(data,'fit',['group','x','y','lower','upper'],['x','y','lower','upper'],optional=True)
    if not fits.empty:
        _intervals(fits,'y'); _unique(fits,['group','x']); palette_check(fits.group,palette)
        for g,sub in fits.groupby('group',sort=False):
            sub=sub.sort_values('x'); ax.fill_between(sub.x,sub.lower,sub.upper,color=palette[g],alpha=.17); ax.plot(sub.x,sub.y,color=palette[g],lw=1.8)
    if identity:
        lo=max(xmin,ymin); hi=min(xmax,ymax); ax.plot([lo,hi],[lo,hi],ls='--',color=semantic_color('accent','#E84D3B'),lw=1.6,label='Identity y = x')
    ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax),xlabel=x_label,ylabel=y_label); top.set_xlim(xmin,xmax); side.set_ylim(ymin,ymax)
    top.set_xticks([]); side.set_yticks([])
    top.set_ylabel('Count' if marginal_mode=='bins' else 'Density',fontsize=8); side.set_xlabel('Count' if marginal_mode=='bins' else 'Density',fontsize=8)
    max_x=float(marg.loc[marg.axis=='x','value'].max()); max_y=float(marg.loc[marg.axis=='y','value'].max())
    side.set_xlim(0,max_y*1.08); side.set_xticks(np.linspace(0,max_y,3)); top.set_ylim(0,max_x*1.08); top.set_yticks(np.linspace(0,max_x,3))
    from matplotlib.ticker import FormatStrFormatter
    side.xaxis.set_major_formatter(FormatStrFormatter('%.2g')); top.yaxis.set_major_formatter(FormatStrFormatter('%.2g'))
    ax.legend(frameon=False,fontsize=8,loc='upper left' if residual_label else 'lower right')
    annotation=_records(data,'annotation',['group','x','y','text'],['x','y'],optional=True)
    for row in annotation.itertuples():
        if not (0<=row.x<=1 and 0<=row.y<=1) or row.group not in palette: raise ValueError('Annotation needs group and axes-fraction position')
        ax.text(row.x,row.y,row.text,transform=ax.transAxes,ha='left',va='top',color=INK,fontsize=8,bbox=dict(boxstyle='round,pad=.45',fc='#FAFAEF',ec=palette[row.group],lw=1))
    boxes=_records(data,'box',['group','q1','median','q3','low','high'],['q1','median','q3','low','high'],optional=True)
    if not boxes.empty:
        if not residual_label or not identity: raise ValueError('Box inset requires paired-method identity plot and residual label')
        _unique(boxes,['group']); palette_check(boxes.group,palette)
        if ((boxes.low>boxes.q1)|(boxes.q1>boxes['median'])|(boxes['median']>boxes.q3)|(boxes.q3>boxes.high)).any(): raise ValueError('Invalid frozen box summary')
        ins=_ax(fig,[.47,.19,.27,.19],clean=False); order=boxes.group.tolist()
        stats=[dict(label=r.group,q1=r.q1,med=r.median,q3=r.q3,whislo=r.low,whishi=r.high,fliers=[]) for r in boxes.itertuples()]
        artists=ins.bxp(stats,orientation='horizontal',showfliers=False,patch_artist=True)
        for patch,g in zip(artists['boxes'],order): patch.set_facecolor(palette[g]); patch.set_alpha(.75)
        ins.set_title(residual_label,fontsize=8,pad=3); ins.tick_params(labelsize=6,length=2)
        brackets=_records(data,'bracket',['a','b','text'],optional=True)
        for k,b in enumerate(brackets.itertuples()):
            if b.a not in order or b.b not in order: raise ValueError('Unknown bracket group')
            ins.text(.98,.91-k*.16,f'{b.a} vs {b.b}: {b.text}',transform=ins.transAxes,ha='right',fontsize=5.5)
    elif (data.record_type=='bracket').any(): raise ValueError('Bracket requires box summaries')
    return _finish(fig,data,'joint',palette=palette,limits=[list(l) for l in limits],x_label=x_label,y_label=y_label,marginal_mode=marginal_mode,identity=identity,residual_label=residual_label,stats='all fit/density/box/annotation values supplied')

def plot_pca_reference(data,palette,*,group_order,axis_labels,limits,ellipse_label,
                       spider=False,landscape=False,size=(8,6)):
    _types(data,['point','centroid','ellipse'])
    pts=_records(data,'point',['unit_id','group','x','y'],['x','y']); centers=_records(data,'centroid',['group','x','y'],['x','y']); ell=_records(data,'ellipse',['group','x','y','width','height','angle'],['x','y','width','height','angle'])
    _unique(pts,['unit_id']); _unique(centers,['group']); _unique(ell,['group']); palette_check(pts.group,palette)
    if set(pts.group)!=set(group_order) or set(centers.group)!=set(group_order) or set(ell.group)!=set(group_order) or (ell[['width','height']]<=0).any().any(): raise ValueError('Invalid PCA groups or ellipse geometry')
    (xmin,xmax),(ymin,ymax)=limits
    if xmin>=xmax or ymin>=ymax or ((pts.x<xmin)|(pts.x>xmax)|(pts.y<ymin)|(pts.y>ymax)).any(): raise ValueError('Limits clip PCA coordinates')
    fig=_new(size); ax=_ax(fig,[.12,.14,.69,.69]); markers=['o','^','s','D','P','X']
    if len(group_order)>len(markers): raise ValueError('Facet more than 6 groups')
    if landscape:
        ax.add_patch(Rectangle((xmin,ymin),-xmin,-ymin,fc='#ECF4F8',ec='none',alpha=.65,zorder=0))
        ax.add_patch(Rectangle((0,0),xmax,ymax,fc='#FBEFEF',ec='none',alpha=.65,zorder=0))
        ax.axvline(0,color='#A6ABAE',lw=.8); ax.axhline(0,color='#A6ABAE',lw=.8)
    for i,g in enumerate(group_order):
        sub=pts[pts.group==g]; c=centers.set_index('group').loc[g]; e=ell.set_index('group').loc[g]
        if spider:
            for p in sub.itertuples(): ax.plot([c.x,p.x],[c.y,p.y],color=palette[g],alpha=.14,lw=.5)
        ax.scatter(sub.x,sub.y,s=24,color=palette[g],alpha=.80,marker=markers[i] if landscape else 'o',ec='white',lw=.4,label=g)
        ax.add_patch(Ellipse((e.x,e.y),e.width,e.height,angle=e.angle,fc='none',ec=palette[g],lw=1.6))
        if spider: ax.scatter(c.x,c.y,s=170,color=palette[g],ec='white',lw=1.8,zorder=6)
        if landscape:
            ax.plot(sub.x,np.full(len(sub),ymin+.02*(ymax-ymin)),ls='',marker='|',ms=6,color=palette[g],alpha=.25)
            ax.plot(np.full(len(sub),xmin+.02*(xmax-xmin)),sub.y,ls='',marker='_',ms=6,color=palette[g],alpha=.25)
    ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax),xlabel=axis_labels[0],ylabel=axis_labels[1]); ax.legend(loc='upper left',bbox_to_anchor=(1.02,1),frameon=False,title='Group',fontsize=8)
    fig.text(.12,.88,ellipse_label,fontsize=8,color='#697278')
    return _finish(fig,data,'pca',palette=palette,axis_labels=list(axis_labels),limits=[list(l) for l in limits],ellipse_label=ellipse_label,spider=spider,landscape=landscape,ellipse_geometry='supplied, not fitted',PCA='not computed')

def plot_state_dashboard(data,palette,*,family_order,condition_order,mean_label,program_label,size=(9,9)):
    _types(data,['embedding','state','effect','mean','program'])
    emb=_records(data,'embedding',['unit_id','family','x','y'],['x','y']); st=_records(data,'state',['state','family','order'],['order'])
    effect=_records(data,'effect',['state','condition','value','evidence'],['value','evidence']); mean=_records(data,'mean',['state','feature','value'],['value']); programs=_records(data,'program',['state','feature','value'],['value'])
    _unique(emb,['unit_id']); _unique(st,['state']); _unique(st,['order']); _unique(effect,['state','condition']); palette_check(st.state,palette)
    if set(st.family)!=set(family_order) or not set(emb.family)<=set(family_order) or set(effect.state)!=set(st.state) or set(effect.condition)!=set(condition_order) or len(effect)!=len(st)*len(condition_order): raise ValueError('Dashboard alignment mismatch')
    if (effect.evidence<0).any() or (mean.value<0).any(): raise ValueError('Invalid evidence/mean magnitude')
    states=st.sort_values('order').state.tolist(); ymap={}; cursor=0
    for fam in family_order:
        for s in states:
            if st.set_index('state').loc[s,'family']==fam: ymap[s]=cursor; cursor+=1
        cursor+=.65
    fig=_new(size); shared_height=.68; base=.16; n=cursor
    for fam in family_order:
        sids=st[st.family==fam].state.tolist(); low=min(ymap[s] for s in sids)-.5; high=max(ymap[s] for s in sids)+.5
        pos=base+shared_height*(1-(high+.2)/n); h=shared_height*(high-low)/n
        ax=_ax(fig,[.02,pos,.16,h]); ax.scatter(emb.x,emb.y,s=1,color='#D8DADA',alpha=.25,lw=0)
        sub=emb[emb.family==fam]; ax.scatter(sub.x,sub.y,s=2,color=palette[sids[0]],alpha=.55,lw=0); ax.axis('off'); ax.set_title(fam,fontsize=8,pad=2)
    effax=_ax(fig,[.44,base,.14,shared_height]); effcm=reference_cmap('expression_blue_red'); effect_bound=max(float(effect.value.abs().max()),1e-9)
    effax.scatter([list(condition_order).index(c) for c in effect.condition],[ymap[s] for s in effect.state],s=effect.evidence*3,c=effect.value,cmap=effcm,norm=TwoSlopeNorm(0,-effect_bound,effect_bound),lw=0)
    effax.set_yticks([ymap[s] for s in states],states,fontsize=6.8); effax.set_xticks(range(len(condition_order)),condition_order,rotation=45,ha='left',fontsize=7); effax.xaxis.tick_top(); effax.set(xlim=(-.6,len(condition_order)-.4),ylim=(n-.2,-.8)); effax.spines[:].set_visible(False); effax.tick_params(length=0)
    for s in states: effax.scatter(-.65,ymap[s],s=25,color=palette[s],clip_on=False)
    for source,left,width,label,cmap,norm in [(mean,.63,.14,mean_label,reference_cmap('expression_warm',semantic='sequential'),Normalize(0,max(mean.value.max(),1e-9))),(programs,.81,.17,program_label,effcm,TwoSlopeNorm(0,-max(programs.value.abs().max(),1e-9),max(programs.value.abs().max(),1e-9)))]:
        mat,rows,cols=_grid(source,'state','feature','value')
        if set(rows)!=set(states): raise ValueError('Heatmap states mismatch')
        ax=_ax(fig,[left,base,width,shared_height]); ax.axis('off')
        for r in source.itertuples(): ax.add_patch(Rectangle((cols.index(r.feature)-.5,ymap[r.state]-.5),1,1,fc=cmap(norm(r.value)),ec='none'))
        ax.set(xlim=(-.5,len(cols)-.5),ylim=(n-.2,-.8))
        for i,c in enumerate(cols): ax.text(i,-1.0,c,rotation=45,ha='right',fontsize=7)
        _colorbar(fig,[left,.078,width,.012],cmap,norm,label,orientation='horizontal')
    _colorbar(fig,[.44,.078,.14,.012],effcm,TwoSlopeNorm(0,-effect_bound,effect_bound),'Supplied log2 OR',orientation='horizontal')
    fig.text(.22,.084,'Dot area: supplied\n−log10(adjusted p)',fontsize=7)
    return _finish(fig,data,'state_dashboard',family_order=list(family_order),condition_order=list(condition_order),palette=palette,mean_label=mean_label,program_label=program_label,area='supplied negative log adjusted p',shared_state_order=states)

def plot_multiclass_contributions(data,palette,*,class_order,feature_orders,limits,size=(12,9)):
    _types(data,['contribution','share'])
    d=_records(data,'contribution',['unit_id','class','feature','contribution','feature_value'],['contribution','feature_value']); shares=_records(data,'share',['class','feature','value'],['value'])
    _unique(d,['unit_id','class','feature']); _unique(shares,['class','feature']); palette_check(shares.feature,palette)
    if len(class_order)>5 or set(d['class'])!=set(class_order) or set(shares['class'])!=set(class_order) or ((d.feature_value<0)|(d.feature_value>1)).any() or (shares.value<0).any(): raise ValueError('Invalid multiclass data')
    if limits[0]>=limits[1] or ((d.contribution<limits[0])|(d.contribution>limits[1])).any(): raise ValueError('Clipped contributions')
    if not np.allclose(shares.groupby('class').value.sum(),1,atol=1e-6): raise ValueError('Shares must sum to 1 for each class')
    fig=_new(size); cm=reference_cmap('shap_reference_rainbow',semantic='sequential')
    for k,cl in enumerate(class_order):
        row,col=divmod(k,3); left=.09+col*.32; bottom=.56-row*.43
        ax=_ax(fig,[left,bottom,.21,.32]); sub=d[d['class']==cl]; order=feature_orders[cl]
        if set(sub.feature)!=set(order): raise ValueError('Class feature order mismatch')
        _draw_swarm(ax,sub,order,cm,limits,point_size=3); ax.tick_params(labelsize=6); ax.set_title(str(cl),fontsize=9,loc='left'); ax.set_xlabel('Supplied contribution',fontsize=7)
        rose=_ax(fig,[left+.135,bottom+.03,.095,.105]); rose.axis('off'); rose.set_aspect('equal'); frac=shares[shares['class']==cl]
        angles=np.arange(len(frac))*360/len(frac)
        for a,r in zip(angles,frac.itertuples()): rose.add_patch(Wedge((0,0),np.sqrt(float(r.value))*1.75,a,a+360/len(frac),fc=palette[r.feature],ec='white',lw=.5))
        rose.set(xlim=(-1.1,1.1),ylim=(-1.1,1.1))
    ring=_ax(fig,[.76,.22,.20,.27]); ring.axis('off'); ring.set_aspect('equal')
    for k,cl in enumerate(class_order):
        sub=shares[shares['class']==cl]; start=90; radius=1.0-k*.145
        for r in sub.itertuples():
            extent=r.value*360; ring.add_patch(Wedge((0,0),radius,start-extent,start,width=.12,fc=palette[r.feature],ec='white',lw=.65)); start-=extent
    ring.set(xlim=(-1.1,1.1),ylim=(-1.1,1.1)); ring.set_title('Supplied absolute-contribution shares',fontsize=8)
    fig.legend(handles=[Rectangle((0,0),1,1,fc=palette[f],label=f) for f in pd.unique(shares.feature)],loc='lower right',bbox_to_anchor=(.98,.085),ncol=3,frameon=False,fontsize=7)
    _colorbar(fig,[.78,.938,.17,.010],cm,Normalize(0,1),'Feature value',orientation='horizontal')
    return _finish(fig,data,'multiclass_contributions',palette=palette,class_order=list(class_order),feature_orders=feature_orders,limits=list(limits),rose='equal angular sectors; area proportional to supplied share',rings='each ring is a class; angle supplied share',shares='provided upstream; not derived from points')

def plot_embedding_atlas(data,palette,stack_palette,*,atlas_order,main_order,marker_label,
                         count_label,fraction_label,radial_count_max,size=(10,15)):
    """R04 all three subfigures. Supplied tree segments are drawn, not clustered."""
    _types(data,['point','count','leaf','tree','marker'])
    pts=_records(data,'point',['unit_id','layer','group','x','y'],['x','y']); counts=_records(data,'count',['layer','group','segment','value'],['value'])
    leaves=_records(data,'leaf',['group','order'],['order']); tree=_records(data,'tree',['segment_id','x0','y0','x1','y1'],['x0','y0','x1','y1'])
    marks=_records(data,'marker',['group','feature','fraction','value'],['fraction','value'])
    _unique(pts,['unit_id']); _unique(counts,['layer','group','segment']); _unique(leaves,['group']); _unique(leaves,['order']); _unique(tree,['segment_id']); _unique(marks,['group','feature'])
    palette_check(pts.group,palette); palette_check(counts.loc[counts.layer=='atlas','segment'],stack_palette)
    if set(pts.layer)!={'atlas','main'} or set(counts.layer)!={'atlas','main'} or (counts.value<0).any() or (counts.value%1!=0).any() or ((marks.fraction<0)|(marks.fraction>1)).any() or (marks.value<0).any(): raise ValueError('Invalid atlas layers/counts/markers')
    if set(pts.loc[pts.layer=='atlas','group'])!=set(atlas_order) or set(pts.loc[pts.layer=='main','group'])!=set(main_order) or set(leaves.group)!=set(main_order) or set(marks.group)!=set(main_order): raise ValueError('Atlas group alignment mismatch')
    if radial_count_max<=0 or counts[counts.layer=='atlas'].groupby('group').value.sum().max()>radial_count_max: raise ValueError('Invalid radial count scale')
    mat,mrows,mcols=_grid(marks,'feature','group','value')
    if set(mcols)!=set(main_order): raise ValueError('Marker grid mismatch')
    # Uniform translation/scaling only: circle never changes relative geometry.
    fig=_new(size,8); ring=_ax(fig,[.025,.62,.50,.31]); ring.axis('off'); ring.set_aspect('equal')
    apts=pts[pts.layer=='atlas']; center=np.array([(apts.x.min()+apts.x.max())/2,(apts.y.min()+apts.y.max())/2]); coords=apts[['x','y']].to_numpy()-center
    display_scale=.82/max(np.linalg.norm(coords,axis=1).max(),1e-9); coords*=display_scale
    for g in atlas_order:
        mask=(apts.group==g).to_numpy(); ring.scatter(coords[mask,0],coords[mask,1],s=2,color=palette[g],alpha=.55,lw=0)
    ring.add_patch(Circle((0,0),1,fc='none',ec='#69747C',lw=.9)); angles=np.linspace(90,450,len(atlas_order),endpoint=False)
    acount=counts[counts.layer=='atlas']; segs=list(stack_palette)
    for i,(g,a) in enumerate(zip(atlas_order,angles)):
        start=1.03
        for s in segs:
            sub=acount[(acount.group==g)&(acount.segment==s)]
            if len(sub)!=1: raise ValueError('Each circular category requires every stacked segment')
            height=.50*sub.value.iloc[0]/radial_count_max
            if height>0: ring.add_patch(Wedge((0,0),start+height,a-360/len(atlas_order)*.38,a+360/len(atlas_order)*.38,width=height,fc=stack_palette[s],ec='white',lw=.2))
            start+=height
        t=np.deg2rad(a); ring.text(.95*np.cos(t),.95*np.sin(t),str(i+1),ha='center',va='center',fontsize=5,color=palette[g],weight='bold')
    ring.set(xlim=(-1.60,1.60),ylim=(-1.60,1.60)); ring.set_title('A  Embedding with aligned radial counts',loc='left',fontsize=10)
    lg=_ax(fig,[.55,.65,.43,.26]); lg.axis('off'); rows=math.ceil(len(atlas_order)/3)
    for i,g in enumerate(atlas_order):
        col,row=divmod(i,rows); x=col/3; y=1-(row+.5)/rows
        lg.scatter(x,y,s=13,color=palette[g]); lg.text(x+.025,y,f'{i+1:02d} {g}',fontsize=5.6,va='center')
    lg.set(xlim=(-.03,1),ylim=(0,1)); fig.text(.55,.62,'Radial length: '+count_label+'; zero at ring base',fontsize=7)
    main=_ax(fig,[.06,.34,.58,.23]); main.axis('off'); main.set_aspect('equal'); mp=pts[pts.layer=='main']
    for g in main_order:
        sub=mp[mp.group==g]; main.scatter(sub.x,sub.y,s=3,color=palette[g],alpha=.7,lw=0,label=g)
    main.set_title('B  Categorical embedding; fixed coordinates',loc='left',fontsize=10)
    main.legend(loc='upper left',bbox_to_anchor=(1.03,1),frameon=False,fontsize=6,ncols=1,markerscale=3)
    order=leaves.sort_values('order').group.tolist(); n=len(order)
    dend=_ax(fig,[.15,.285,.68,.045]); dend.axis('off')
    for t in tree.itertuples(): dend.plot([t.x0,t.x1],[t.y0,t.y1],color='#8A949B',lw=.7)
    dend.set_xlim(-.5,n-.5); dend.set_title('C  Supplied hierarchy, counts and marker matrix',loc='left',fontsize=9,pad=4)
    bar=_ax(fig,[.15,.22,.68,.058]); mc=counts[counts.layer=='main']
    if set(mc.group)!=set(order): raise ValueError('Count bars mismatch')
    # This adapter expects one total count record per main leaf, no hidden summation.
    _unique(mc,['group']); values=mc.set_index('group').reindex(order).value
    bar.bar(range(n),values,color=[palette[g] for g in order],width=.82); bar.set(xlim=(-.5,n-.5),ylabel=count_label); bar.set_xticks([]); bar.tick_params(labelsize=6); bar.yaxis.label.set_size(7)
    dot=_ax(fig,[.15,.10,.68,.11]); cm=reference_cmap('expression_warm',semantic='sequential'); norm=Normalize(0,max(marks.value.max(),1e-9))
    dots=dot.scatter([order.index(g) for g in marks.group],[mrows.index(f) for f in marks.feature],s=marks.fraction*45,c=marks.value,cmap=cm,norm=norm,lw=0)
    dot.set_xticks(range(n),order,rotation=90,fontsize=5.5); dot.set_yticks(range(len(mrows)),mrows,fontsize=6); dot.set(xlim=(-.5,n-.5),ylim=(len(mrows)-.5,-.5))
    _colorbar(fig,[.89,.16,.012,.10],cm,norm,marker_label)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',color='#AD3D3D',ms=np.sqrt(f*45),label=f'{f:.0%}') for f in [.25,.5,1]],title=fraction_label,loc='lower right',bbox_to_anchor=(.98,.083),frameon=False,fontsize=6,title_fontsize=6)
    return _finish(fig,data,'embedding_atlas',palette=palette,stack_palette=stack_palette,atlas_order=list(atlas_order),main_order=order,radial_count_max=radial_count_max,uniform_display_scale=float(display_scale),display_translation=center.tolist(),tree='supplied exact segments, no clustering',marker_area='supplied fraction',marker_label=marker_label,fraction_label=fraction_label,count_label=count_label)

def plot_training_dashboard(data,palette,*,selected_epoch,selection_label,loss_label,heat_label,
                            gradient_label,size=(10,6)):
    _types(data,['loss','heat','gradient','reference'])
    loss=_records(data,'loss',['series','epoch','value','lower','upper'],['epoch','value','lower','upper']); heat=_records(data,'heat',['run','epoch','value'],['epoch','value']); grad=_records(data,'gradient',['epoch','value','lower','upper'],['epoch','value','lower','upper']); reference=_records(data,'reference',['epoch','value'],['epoch','value'])
    _unique(loss,['series','epoch']); _unique(grad,['epoch']); _unique(reference,['epoch']); _intervals(loss); _intervals(grad); palette_check(loss.series,palette)
    if (grad[['lower','value','upper']]<=0).any().any() or (reference.value<=0).any(): raise ValueError('Log gradient requires positive values and bounds')
    if selected_epoch not in set(loss.epoch): raise ValueError('Selected epoch absent')
    fig=_new(size); ax=_ax(fig,[.09,.15,.61,.72])
    for g,sub in loss.groupby('series',sort=False):
        sub=sub.sort_values('epoch'); ax.fill_between(sub.epoch,sub.lower,sub.upper,color=palette[g],alpha=.16); ax.plot(sub.epoch,sub.value,color=palette[g],lw=2,label=g)
    ax.axvline(selected_epoch,color='#697780',ls='--',lw=1); chosen=loss[(loss.epoch==selected_epoch)&(loss.series==loss.series.iloc[-1])]
    epochs=sorted(loss.epoch.unique()); eticks=np.unique(np.linspace(0,len(epochs)-1,min(7,len(epochs))).astype(int)); ax.set_xticks([epochs[i] for i in eticks])
    ax.scatter(chosen.epoch,chosen.value,s=48,fc='white',ec=INK,zorder=6); ax.set(xlabel='Epoch',ylabel=loss_label,title='A  Recorded loss and uncertainty'); ax.legend(frameon=False,fontsize=8)
    mat,rs,es=_grid(heat,'run','epoch','value'); hax=_ax(fig,[.77,.61,.13,.26]); cm=reference_cmap('expression_warm',semantic='sequential')
    es=sorted(es);mat=mat.reindex(columns=es)
    epoch_values=np.asarray(es,float)
    edges=np.r_[epoch_values[0]-.5,epoch_values[0]+.5] if len(es)==1 else np.r_[epoch_values[0]-(epoch_values[1]-epoch_values[0])/2,(epoch_values[:-1]+epoch_values[1:])/2,epoch_values[-1]+(epoch_values[-1]-epoch_values[-2])/2]
    im=hax.pcolormesh(edges,np.arange(len(rs)+1)-.5,mat.to_numpy(),cmap=cm,shading='flat');hax.set_ylim(len(rs)-.5,-.5); hax.set(xlabel='Epoch',ylabel='Run',title='B'); hax.set_yticks(range(len(rs)),[str(r) for r in rs],fontsize=max(4,min(7,9-len(rs)*.12))); hax.axvline(selected_epoch,color='#54636E',ls='--',lw=.7)
    _colorbar(fig,[.92,.62,.012,.24],cm,im.norm,heat_label)
    gax=_ax(fig,[.80,.16,.18,.28]); grad=grad.sort_values('epoch'); reference=reference.sort_values('epoch'); gax.fill_between(grad.epoch,grad.lower,grad.upper,color=semantic_color('primary','#00A78D'),alpha=.20); gax.plot(grad.epoch,grad.value,color=semantic_color('primary','#00A78D'),lw=1.7); gax.plot(reference.epoch,reference.value,color=semantic_color('accent','#EDA019'),ls='--',lw=1.2); gticks=np.unique(np.linspace(0,len(grad)-1,min(5,len(grad))).astype(int)); gax.set_xticks(grad.epoch.iloc[gticks])
    fig.text(.09,.065,selection_label,fontsize=8)
    return _finish(fig,data,'training_dashboard',palette=palette,selected_epoch=selected_epoch,selection_label=selection_label,loss_label=loss_label,heat_label=heat_label,gradient_label=gradient_label,uncertainty='supplied intervals; repeated runs not independent subjects')

def plot_activity_dashboard(data,palette,*,row_order,column_order,value_label,bar_label,line_label,size=(10,7),
                            row_aliases=None,column_aliases=None,row_label_wrap=18,column_label_wrap=13,
                            row_label_mode='all'):
    _types(data,['matrix','row','top','density'])
    matrix=_records(data,'matrix',['row','column','value'],['value']); rows=_records(data,'row',['row','group']); top=_records(data,'top',['column','bar','line'],['bar','line']); density=_records(data,'density',['group','coordinate','value'],['coordinate','value'])
    _unique(rows,['row']); _unique(top,['column']); _unique(density,['group','coordinate']); palette_check(rows.group,palette)
    mat,rs,cs=_grid(matrix,'row','column','value')
    if set(rs)!=set(row_order) or set(cs)!=set(column_order) or set(rows.row)!=set(row_order) or set(top.column)!=set(column_order) or set(density.group)!=set(rows.group) or (density.value<0).any(): raise ValueError('Activity alignment mismatch')
    mat=mat.reindex(index=row_order,columns=column_order); groups=rows.set_index('row').reindex(row_order).group.tolist()
    if row_label_mode not in ('all','none'): raise ValueError("row_label_mode must be 'all' or 'none'")
    rlabels=axis_labels(row_order,row_aliases,'row'); clabels=axis_labels(column_order,column_aliases,'column')
    if row_label_wrap is not None and (type(row_label_wrap) is not int or row_label_wrap<1): raise ValueError('row_label_wrap must be a positive integer or None')
    if column_label_wrap is not None and (type(column_label_wrap) is not int or column_label_wrap<1): raise ValueError('column_label_wrap must be a positive integer or None')
    rlabels=[textwrap.fill(x,row_label_wrap) if row_label_wrap else x for x in rlabels]; clabels=[textwrap.fill(x,column_label_wrap) if column_label_wrap else x for x in clabels]
    if size==(10,7): size=(max(10,7+len(column_order)*.34+max((len(x.replace('\n','')) for x in clabels),default=0)*.025),max(7,4+len(row_order)*.16))
    fig=_new(size); ax=_ax(fig,[.10,.16,.62,.61]); cm=reference_cmap('activity_blue',semantic='sequential')
    im=ax.imshow(mat,aspect='auto',cmap=cm,vmin=float(matrix.value.min()),vmax=float(matrix.value.max())); ax.set_xticks(range(len(cs)),clabels,rotation=45,ha='right'); ax.set_yticks(range(len(row_order)),rlabels if row_label_mode=='all' else []); ax.set_xlabel('Supplied column order'); ax.set_title('A  Frozen matrix',loc='left',fontsize=10)
    strip=_ax(fig,[.04,.16,.026,.61]); strip.axis('off')
    start=0
    for stop in range(1,len(groups)+1):
        if stop==len(groups) or groups[stop]!=groups[start]:
            strip.add_patch(Rectangle((0,start-.5),1,stop-start,fc=palette[groups[start]],ec='none',antialiased=False)); start=stop
    strip.set(xlim=(0,1),ylim=(len(rs)-.5,-.5)); tops=_ax(fig,[.10,.81,.62,.10]); t=top.set_index('column').reindex(column_order); tops.bar(range(len(t)),t.bar,color=semantic_color('primary','#2CB29F'),width=.8);tops.set_xlim(-.5,len(column_order)-.5); tops.set_xticks([]); tops.set_ylabel(bar_label,fontsize=7); tops.set_title('B',loc='left',fontsize=10)
    twin=tops.twinx(); twin.plot(range(len(t)),t.line,color=semantic_color('accent','#EF4831'),lw=1.2); twin.set_ylabel(line_label,fontsize=7); twin.tick_params(labelsize=6); twin.spines['top'].set_visible(False)
    from indexed_alignment import bind_index_axes
    bind_index_axes(fig,ax,strip,'y',row_order)
    bind_index_axes(fig,ax,tops,'x',column_order)
    bind_index_axes(fig,ax,twin,'x',column_order)
    _colorbar(fig,[.75,.25,.015,.42],cm,im.norm,value_label)
    cats=list(dict.fromkeys(groups))
    for i,g in enumerate(cats):
        dy=.61/len(cats); dax=_ax(fig,[.82,.16+(len(cats)-1-i)*dy,.16,dy*.85]); sub=density[density.group==g].sort_values('coordinate'); dax.fill_between(sub.coordinate,0,sub.value,color=palette[g],alpha=.35); dax.plot(sub.coordinate,sub.value,color=palette[g],lw=1.2); dax.set_yticks([]); dax.set_title(g,loc='left',fontsize=7,pad=1)
        if i<len(cats)-1: dax.set_xticks([])
        else: dax.set_xlabel('Supplied density coordinate',fontsize=7)
    return _finish(fig,data,'activity_dashboard',palette=palette,row_order=list(row_order),column_order=list(column_order),row_aliases=dict(zip(row_order,rlabels)),column_aliases=dict(zip(column_order,clabels)),row_label_mode=row_label_mode,value_label=value_label,bar_label=bar_label,line_label=line_label,density='supplied, no KDE',top_scales='separate labelled axes')

def plot_effect_distribution_forest(data,*,row_order,panel_order,panel_labels,limits,
                                    interval_label,count_label,p_type,size=(12,9)):
    _types(data,['effect','summary'])
    effects=_records(data,'effect',['effect_id','panel','row','value'],['value']); sums=_records(data,'summary',['panel','row','value','lower','upper','count_text','p'],['value','lower','upper','p'])
    _unique(effects,['effect_id','panel']); _unique(sums,['panel','row']); _intervals(sums); _p(sums)
    if p_type not in ('raw','adjusted'): raise ValueError('Declare p type')
    if len(panel_order)!=2 or set(sums.panel)!=set(panel_order) or set(sums.row)!=set(row_order) or len(sums)!=len(panel_order)*len(row_order) or not set(effects.row)<=set(row_order) or not set(effects.panel)<=set(panel_order): raise ValueError('Forest row/panel mismatch')
    for v in [effects.value,sums.lower,sums.upper]:
        if ((v<limits[0])|(v>limits[1])).any(): raise ValueError('Forest limits clip supplied values')
    fig=_new(size); cm=reference_cmap('meta_purple_green'); norm=TwoSlopeNorm(0,limits[0],limits[1])
    for k,p in enumerate(panel_order):
        ax=_ax(fig,[.22+k*.39,.14,.37,.73]); n=len(row_order)
        for i,r in enumerate(row_order):
            if i%2: ax.axhspan(i-.5,i+.5,color='#EFEFEF',zorder=0)
            sub=effects[(effects.panel==p)&(effects.row==r)]; offset=_pack(sub.value,spacing=(limits[1]-limits[0])/100,max_width=.2)
            ax.scatter(sub.value,i+offset,s=3,c=sub.value,cmap=cm,norm=norm,alpha=.45,lw=0)
            s=sums[(sums.panel==p)&(sums.row==r)].iloc[0]
            ax.plot([s.lower,s.upper],[i,i],color='#767E83',lw=1.1,zorder=3)
            ax.scatter(s.value,i,s=55,marker='D',fc=cm(norm(s.value)) if s.p<.05 else 'white',ec=INK,lw=.8,zorder=4)
            star='***' if s.p<.001 else '**' if s.p<.01 else '*' if s.p<.05 else ''
            ax.text(limits[1]-.18,i,star,ha='right',va='center',fontsize=7)
        ax.axvline(0,ls='--',color='#8A949B',lw=.8); ax.set(xlim=limits,ylim=(n-.5,-.5),xlabel=panel_labels[p],title=str(p)); ax.set_yticks(range(n),[f'{r}  {sums[(sums.panel==p)&(sums.row==r)].count_text.iloc[0]}' for r in row_order] if k==0 else [],fontsize=7)
    fig.text(.22,.02,interval_label+'; '+count_label,fontsize=8)
    _colorbar(fig,[.67,.055,.27,.012],cm,norm,'Supplied effect value',orientation='horizontal')
    return _finish(fig,data,'effect_distribution_forest',row_order=list(row_order),panel_order=list(panel_order),panel_labels=panel_labels,limits=list(limits),interval_label=interval_label,count_label=count_label,summary='provided, not pooled by renderer',p_semantics=p_type+' supplied p; threshold glyph only')

def plot_facet_bubble_matrix(data,*,row_facets,column_facets,feature_order,window_order,
                            value_label,size=(10,8)):
    _types(data,['association']); d=_records(data,'association',['row_facet','column_facet','feature','window','r'],['window','r']); _signed(d); _unique(d,['row_facet','column_facet','feature','window'])
    if set(d.row_facet)!=set(row_facets) or set(d.column_facet)!=set(column_facets) or set(d.feature)!=set(feature_order) or set(d.window)!=set(window_order): raise ValueError('Facet category mismatch')
    expected=len(row_facets)*len(column_facets)*len(feature_order)*len(window_order)
    if len(d)!=expected: raise ValueError('Incomplete facet matrix')
    fig=_new(size); cm=reference_cmap('partial_blue_red'); norm=Normalize(-.5,.5)
    # Use the full [-1,1] domain if the supplied values exceed the reference's range.
    domain=max(.5,float(d.r.abs().max())); norm=Normalize(-domain,domain)
    w=.65/len(column_facets); h=.75/len(row_facets)
    for i,rf in enumerate(row_facets):
        for j,cf in enumerate(column_facets):
            ax=_ax(fig,[.12+j*w,.14+(len(row_facets)-1-i)*h,w-.008,h-.008],clean=False); sub=d[(d.row_facet==rf)&(d.column_facet==cf)]
            ax.scatter([list(window_order).index(v) for v in sub.window],[list(feature_order).index(v) for v in sub.feature],s=sub.r.abs()*520,c=sub.r,cmap=cm,norm=norm,ec='#555F66',lw=.7)
            ax.set(xlim=(-.6,len(window_order)-.4),ylim=(len(feature_order)-.5,-.5)); ax.set_xticks(range(len(window_order)),window_order if i==len(row_facets)-1 else [],fontsize=7); ax.set_yticks(range(len(feature_order)),feature_order if j==0 else [],fontsize=8); ax.grid(color='#E4E7E9',lw=.4); ax.set_axisbelow(True)
            if i==0: ax.set_title(cf,fontsize=10,weight='bold')
            if j==len(column_facets)-1: ax.text(1.03,.5,rf,transform=ax.transAxes,rotation=-90,ha='left',va='center',fontsize=8)
    fig.text(.39,.065,'Supplied window / condition',ha='center',fontsize=9)
    lg=_ax(fig,[.85,.61,.14,.22]); lg.axis('off'); lg.legend(handles=[Line2D([],[],ls='',marker='o',ms=np.sqrt(v*520),mfc='white',mec='#555F66',label=f'{v:g}') for v in [.1,.3,.5]],title='Absolute r (area)',frameon=False,fontsize=8,title_fontsize=8)
    _colorbar(fig,[.87,.26,.018,.26],cm,norm,value_label)
    return _finish(fig,data,'facet_bubble_matrix',row_facets=list(row_facets),column_facets=list(column_facets),feature_order=list(feature_order),window_order=list(window_order),color_limits=[-domain,domain],value_label=value_label,area='abs supplied r times 520')

def plot_strip_effects(data,palette,*,panel_order,contrast_order,up_color='#FF6A3D',down_color='#7CCD14',
                       eligibility_label,alpha=.05,fc=1,size=(10,5)):
    _types(data,['effect']); d=_records(data,'effect',['feature','panel','contrast','value','padj','jitter'],['value','padj','jitter']); _unique(d,['feature','panel','contrast']); _p(d,'padj'); palette_check(d.contrast,palette)
    if not 0<alpha<1 or fc<=0 or (d.jitter.abs()>.43).any(): raise ValueError('Invalid eligibility/jitter controls')
    if set(d.panel)!=set(panel_order) or set(d.contrast)!=set(contrast_order): raise ValueError('Strip categories mismatch')
    # Selection is a declared display operation on supplied adjusted p and effects.
    included=(d.padj<=alpha)&(d.value.abs()>=fc)
    fig=_new(size); h=max(float(d.value.abs().max())*1.12,fc*2); width=.87/len(panel_order)
    for k,p in enumerate(panel_order):
        ax=_ax(fig,[.07+k*width,.22,width-.055,.63])
        for i,c in enumerate(contrast_order):
            sub=d[(d.panel==p)&(d.contrast==c)]; eligible=sub[(sub.padj<=alpha)&(sub.value.abs()>=fc)]
            ax.axvspan(i-.44,i+.44,color='#F0F1F2',zorder=0)
            ax.scatter(i+eligible.jitter,eligible.value,s=2,c=np.where(eligible.value>0,up_color,down_color),lw=0)
            ax.add_patch(Rectangle((i-.44,-.8),.88,1.6,fc=palette[c],ec='none',zorder=3)); ax.text(i,0,c,ha='center',va='center',fontsize=6,color='white',zorder=4)
            ax.text(i,h*.90,str(int((eligible.value>0).sum())),ha='center',fontsize=7); ax.text(i,-h*.90,str(int((eligible.value<0).sum())),ha='center',fontsize=7)
        ax.set(xlim=(-.6,len(contrast_order)-.4),ylim=(-h,h),ylabel='Supplied signed effect',title=str(p)); ax.set_xticks([])
    fig.text(.07,.10,eligibility_label+f'; padj <= {alpha:g}; |effect| >= {fc:g}',fontsize=8)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',color=c,label=l) for c,l in [(up_color,'Positive eligible effect'),(down_color,'Negative eligible effect')]],loc='lower right',bbox_to_anchor=(.98,.09),frameon=False,fontsize=7)
    return _finish(fig,data,'strip_effects',palette=palette,panel_order=list(panel_order),contrast_order=list(contrast_order),alpha=alpha,fc=fc,eligibility_label=eligibility_label,included_rows=int(included.sum()),excluded_rows=int((~included).sum()),counts='eligible feature records; not inferred sample n',jitter='supplied display offset; effect unchanged')

def plot_aligned_tracks(data,palette,*,category_order,track_order,matrix_order,block_order,
                         matrix_labels,matrix_limits,count_label,size=(12,7)):
    """R22. Domain-neutral aligned bar tracks and multiple matrix strips."""
    _types(data,['count','matrix','category'])
    counts=_records(data,'count',['track','category','value'],['value']); matrices=_records(data,'matrix',['matrix','row','category','value'],['value']); categories=_records(data,'category',['category','block'])
    _unique(counts,['track','category']); _unique(matrices,['matrix','row','category']); _unique(categories,['category']); palette_check(counts.track,palette)
    if (counts.value<0).any() or (counts.value%1!=0).any() or set(counts.track)!=set(track_order) or set(counts.category)!=set(category_order) or set(categories.category)!=set(category_order) or set(categories.block)!=set(block_order) or set(matrices.matrix)!=set(matrix_order): raise ValueError('Track category mismatch')
    if len(counts)!=len(category_order)*len(track_order): raise ValueError('Incomplete count tracks')
    fig=_new(size); n=len(category_order); top=.90; height=.075
    for i,t in enumerate(track_order):
        ax=_ax(fig,[.08,top-(i+1)*height,.80,height*.84]); sub=counts[counts.track==t].set_index('category').reindex(category_order)
        ax.bar(range(n),sub.value,color=palette[t],width=.86); ax.set(xlim=(-.5,n-.5),ylabel=t); ax.set_xticks([]); ax.yaxis.label.set_size(8); ax.grid(axis='y',color='#E2E6E9',lw=.4); ax.set_axisbelow(True)
    cursor=top-len(track_order)*height-.01
    for k,m in enumerate(matrix_order):
        sub=matrices[matrices.matrix==m]; mat,rs,cs=_grid(sub,'row','category','value')
        if set(cs)!=set(category_order): raise ValueError('Matrix columns mismatch')
        lo,hi=matrix_limits[m]
        if lo>=hi or ((sub.value<lo)|(sub.value>hi)).any(): raise ValueError('Matrix limits clip values')
        mh=.13; cursor-=mh+.025
        ax=_ax(fig,[.08,cursor,.80,mh]); cmap=plt.get_cmap('RdPu' if k%2==0 else 'OrRd'); ax.imshow(mat.reindex(columns=category_order),aspect='auto',cmap=cmap,vmin=lo,vmax=hi); ax.set_yticks(range(len(rs)),rs,fontsize=7)
        ax.set_xticks(range(n),category_order,rotation=90,fontsize=6) if k==len(matrix_order)-1 else ax.set_xticks([])
        _colorbar(fig,[.90,cursor,.012,mh],cmap,Normalize(lo,hi),matrix_labels[m])
    cats=categories.set_index('category').reindex(category_order); band=_ax(fig,[.08,.23,.80,.055]); band.axis('off'); band.set(xlim=(-.5,n-.5),ylim=(0,1))
    observed_blocks=[]
    for b in block_order:
        ids=np.flatnonzero(cats.block.to_numpy()==b)
        if len(ids)==0 or not np.all(np.diff(ids)==1): raise ValueError('Each block must be contiguous in supplied category order')
        observed_blocks.extend(ids.tolist()); left=ids.min()-.5; right=ids.max()+.5; band.plot([left,left,right,right],[1,.2,.2,1],color=INK,lw=.8); band.text((left+right)/2,.05,b,ha='center',va='top',fontsize=9)
    fig.text(.01,.66,count_label,rotation=90,fontsize=9)
    return _finish(fig,data,'aligned_tracks',palette=palette,category_order=list(category_order),track_order=list(track_order),matrix_order=list(matrix_order),block_order=list(block_order),matrix_labels=matrix_labels,matrix_limits=matrix_limits,count_label=count_label,order='fixed across all panels; no clustering or species assumption')

def plot_surface_grid(data,*,axis_labels,value_label,limits,view=(32,-132),size=(9,6)):
    _types(data,['grid']); d=_records(data,'grid',['x','y','z'],['x','y','z']); mat,ys,xs=_grid(d,'y','x','z')
    if min(mat.shape)<2 or limits[0]>=limits[1] or ((d.z<limits[0])|(d.z>limits[1])).any(): raise ValueError('Degenerate surface or clipping limits')
    xs=np.asarray(xs,float); ys=np.asarray(ys,float)
    if not (np.all(np.diff(xs)>0) and np.all(np.diff(ys)>0)): raise ValueError('Grid coordinates must be supplied in ascending order')
    fig=_new(size); ax=fig.add_axes([.02,.07,.83,.83],projection='3d'); xx,yy=np.meshgrid(xs,ys); cm=reference_cmap('surface_terrain',semantic='sequential'); norm=Normalize(*limits)
    # rcount/ccount preserve every supplied grid node, no automatic subsampling.
    surf=ax.plot_surface(xx,yy,mat.to_numpy(),cmap=cm,norm=norm,rcount=len(ys),ccount=len(xs),lw=0,antialiased=True,shade=False)
    ax.set(xlabel=axis_labels[0],ylabel=axis_labels[1],zlabel=value_label,zlim=limits); ax.view_init(*view); ax.tick_params(labelsize=7); ax.set_box_aspect((1,1,.55))
    ax.set_xticks(np.linspace(xs.min(),xs.max(),5)); ax.set_yticks(np.linspace(ys.min(),ys.max(),5)); ax.set_zticks(np.linspace(limits[0],limits[1],5))
    _colorbar(fig,[.89,.17,.022,.67],cm,norm,value_label)
    return _finish(fig,data,'surface_grid',axis_labels=list(axis_labels),value_label=value_label,limits=list(limits),view=list(view),surface='supplied regular grid; no smoothing/interpolation',occlusion='3D perspective hides regions; pair with 2D map for quantitative reading')
