"""Original frozen-table visual adapters, inspired by attributed primary manuals.

No enrichment, pathway prediction, similarity computation or network fitting.
Small display-only counts (UpSet/hex bins) preserve every supplied observation.
"""
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge, PathPatch, FancyArrowPatch
from matplotlib.path import Path
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from figure_core import checked, stamp
from figure_reference import _new, _ax, _records, _types, _unique, _grid, _colorbar
from project_theme import validate_theme, group_palette, apply_project_style

def _start(theme,size=(8.5,6.2)):
    validate_theme(theme)
    return _new(size,font_family=theme['font_family'])

def _done(fig,data,kind,theme,**spec):
    stamp(fig,data,kind,analysis='none; supplied results with explicitly stated display summaries',**spec)
    return apply_project_style(fig,theme)

def _cmap(theme,signed=False):
    return LinearSegmentedColormap.from_list('project',theme['continuous']['diverging' if signed else 'sequential'])

def _ribbon(ax,a0,a1,b0,b1,color,alpha=.45):
    vertices=[a0,tuple(np.asarray(a0)*.25),tuple(np.asarray(b0)*.25),b0,b1,tuple(np.asarray(b1)*.25),tuple(np.asarray(a1)*.25),a1,a0]
    codes=[Path.MOVETO]+[Path.CURVE4]*3+[Path.LINETO]+[Path.CURVE4]*3+[Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(vertices,codes),fc=color,ec='none',alpha=alpha))

def plot_typed_network(data,theme,*,edge_label,node_area_label,relation_semantics,directed=False,shape_map=None,title='',size=(8.5,6.2)):
    """Explicit node XY/labels/types/groups/areas + edges/endpoints/weights/signs."""
    _types(data,['node','edge'])
    n=_records(data,'node',['node_id','label','entity_type','group','x','y','area'],['x','y','area']); _unique(n,['node_id'])
    e=_records(data,'edge',['source','target','weight','sign'],['weight','sign'],optional=True)
    if len(n)>250 or (n.area<=0).any() or (not e.empty and ((e.weight<=0).any() or not set(e.sign)<=set([-1,0,1]))): raise ValueError('Invalid network size, node area or edge mapping')
    if not e.empty:
        _unique(e,['source','target'])
        if not directed and pd.Series([tuple(sorted((a,b))) for a,b in zip(e.source,e.target)]).duplicated().any():raise ValueError('An undirected pair cannot be counted twice')
        if (set(e.source)|set(e.target))-set(n.node_id): raise ValueError('Unknown edge endpoint')
        if (e.source==e.target).any(): raise ValueError('Self links require an explicit different adapter')
    if not relation_semantics or not node_area_label or not edge_label: raise ValueError('Declare relationship and size meanings')
    if directed and relation_semantics in ('correlation','association','overlap'): raise ValueError('Undirected association cannot acquire causal arrows')
    shapes=shape_map or {'gene':'^','metabolite':'s','community':'o','term':'D','feature':'^','root':'s'}
    if set(n.entity_type)-set(shapes): raise ValueError('Missing entity shape mapping')
    pal=group_palette(theme,list(pd.unique(n.group))); fig=_start(theme,size); ax=_ax(fig,[.06,.12,.63,.76]); positions=n.set_index('node_id')[['x','y']].to_dict('index')
    for r in e.itertuples():
        p=positions[r.source];q=positions[r.target]; role='positive' if r.sign>0 else 'negative' if r.sign<0 else 'neutral'
        ax.add_patch(FancyArrowPatch((p['x'],p['y']),(q['x'],q['y']),arrowstyle='-|>' if directed else '-',mutation_scale=8,shrinkA=4,shrinkB=4,connectionstyle='arc3,rad=.055',color=theme['roles'][role],lw=.5+1.8*r.weight,alpha=.6,zorder=1))
    for (g,t),sub in n.groupby(['group','entity_type'],sort=False): ax.scatter(sub.x,sub.y,s=sub.area,c=pal[g],marker=shapes[t],ec=theme['roles']['border'],lw=.7,zorder=3)
    for r in n.itertuples(): ax.annotate(r.label,(r.x,r.y),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7,zorder=4)
    span=max(float(np.ptp(n.x)),float(np.ptp(n.y)),1); ax.set_xlim(n.x.min()-.17*span,n.x.max()+.17*span);ax.set_ylim(n.y.min()-.17*span,n.y.max()+.17*span);ax.set_aspect('equal');ax.axis('off');ax.set_title(title,loc='left')
    types=list(pd.unique(n.entity_type)); handles=[Line2D([],[],marker=shapes[t],ls='',mfc='white',mec=theme['roles']['border'],label=t) for t in types]
    fig.legend(handles=handles,title='Entity shape',loc='upper left',bbox_to_anchor=(.72,.90),frameon=False)
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color=pal[g],label=g) for g in pal],title='Identity colour',loc='upper left',bbox_to_anchor=(.72,.66),frameon=False)
    shown=[('positive','positive',1),('negative','negative',-1),('neutral','unsigned',0)]
    fig.legend(handles=[Line2D([],[],color=theme['roles'][r],label=l) for r,l,s in shown if s in set(e.sign)],title=edge_label,loc='upper left',bbox_to_anchor=(.72,.32),frameon=False)
    fig.text(.73,.14,node_area_label+'\nEdge width = supplied weight',fontsize=8)
    return _done(fig,data,'typed_network',theme,relation_semantics=relation_semantics,directed=directed,shape_map=shapes,node_area_label=node_area_label,edge_label=edge_label)

def plot_weighted_chord(data,theme,*,weight_label,order,title=''):
    """Nonnegative quantitative relationships: widths carry the supplied weights."""
    d=checked(data,['source','target','weight'],['weight']); _unique(d,['source','target'])
    if pd.Series([frozenset((a,b)) for a,b in zip(d.source,d.target)]).duplicated().any():
        raise ValueError('Unsigned chord pairs cannot be supplied in both directions')
    if (d.weight<=0).any() or (d.source==d.target).any() or not 2<=len(order)<=12 or len(order)!=len(set(order)) or (set(d.source)|set(d.target))!=set(order): raise ValueError('Positive weights, 2–12 complete explicit sectors and no self links required')
    pal=group_palette(theme,order); totals={s:float(d.loc[(d.source==s)|(d.target==s),'weight'].sum()) for s in order}; scale=(2*np.pi-len(order)*.10)/sum(totals.values()); starts={}; cursor=np.pi/2
    fig=_start(theme);ax=_ax(fig,[.07,.10,.72,.79]); ax.axis('off'); ax.set_aspect('equal'); ax.set(xlim=(-1.28,1.28),ylim=(-1.22,1.28));ax.set_title(title,loc='left')
    for s in order:
        start=cursor; end=start+totals[s]*scale;starts[s]=start;cursor=end+.10
        ax.add_patch(Wedge((0,0),1,np.degrees(start),np.degrees(end),width=.055,fc=pal[s],ec='white',lw=.5));mid=(start+end)/2;ax.text(1.12*np.cos(mid),1.12*np.sin(mid),s,ha='center',va='center',fontsize=9)
    offsets={s:0. for s in order}
    def point(a):return(.94*np.cos(a),.94*np.sin(a))
    for r in d.itertuples():
        a=starts[r.source]+offsets[r.source]*scale;b=starts[r.target]+offsets[r.target]*scale;w=r.weight*scale
        _ribbon(ax,point(a),point(a+w),point(b+w),point(b),pal[r.source]);offsets[r.source]+=r.weight;offsets[r.target]+=r.weight
    fig.text(.80,.65,'Ribbon width\n'+weight_label,fontsize=9);fig.text(.80,.39,'Unsigned weights\nNo inferred direction',fontsize=8)
    return _done(fig,data,'weighted_chord',theme,weight_label=weight_label,sector_order=order,directed=False)

def plot_alluvial(data,theme,*,stage_columns,weight_label,title='',orientation='horizontal',
                  stage_orders=None,path_order=None,gap_fraction=.045,path_field='path_id',
                  weight_field='weight',category_aliases=None,stage_aliases=None,color_stage=None):
    """Conserved path bands, with left-to-right or top-to-bottom stage direction.

    Full category labels and totals occupy dedicated per-stage guide lanes;
    tiny/zero bands never receive an invented minimum weight for legibility.
    """
    import textwrap
    from alluvial_geometry import layout_paths
    from matrix_input import axis_labels
    if orientation not in ('horizontal','vertical') or not isinstance(weight_label,str) or not weight_label.strip():
        raise ValueError('Declare flow orientation and the weight unit')
    ledger=layout_paths(data,stage_columns,stage_orders=stage_orders,path_order=path_order,
                        gap_fraction=gap_fraction,path_field=path_field,weight_field=weight_field)
    stages=ledger['stages'];n=len(stages);groups=list(dict.fromkeys(g for c in stages for g in ledger['stage_orders'][c]))
    pal=group_palette(theme,groups);labels=dict(zip(groups,axis_labels(groups,category_aliases,'category')))
    stage_labels=axis_labels(stages,stage_aliases,'stage');color_stage=color_stage or stages[0]
    if color_stage not in stages:raise ValueError('color_stage must be a supplied stage')
    color_by_path=data.set_index(path_field)[color_stage].to_dict()
    maximum=max(len(ledger['stage_orders'][c]) for c in stages)
    if orientation=='horizontal':
        size=(max(8.5,n*2.2),max(6.2,4.5+maximum*.36));main=[.08,.42,.87,.44]
    else:
        size=(8.5,max(7.6,n*(1+maximum*.25)));main=[.10,.12,.57,.74]
    fig=_start(theme,size);ax=_ax(fig,main);thickness=.12
    def xy(points):
        a=np.asarray(points,float)
        return a if orientation=='horizontal' else a[:,::-1]
    for node in ledger['nodes']:
        if node['weight']==0:continue
        j,lo,hi=node['stage_index'],node['lo'],node['hi']
        origin=(j-thickness/2,lo) if orientation=='horizontal' else (lo,j-thickness/2)
        width,height=(thickness,hi-lo) if orientation=='horizontal' else (hi-lo,thickness)
        patch=Rectangle(origin,width,height,fc=pal[node['category']],ec='white',lw=.6,zorder=2)
        patch.set_gid('node:'+node['stage']+':'+node['category']);ax.add_patch(patch)
    for segment in ledger['segments']:
        if segment['weight']==0:continue
        j=segment['stage_index'];lo,hi=segment['source_interval'];bl,bh=segment['target_interval']
        v=[(j+thickness/2,lo),(j+.5,lo),(j+.5,bl),(j+1-thickness/2,bl),
           (j+1-thickness/2,bh),(j+.5,bh),(j+.5,hi),(j+thickness/2,hi),(j+thickness/2,lo)]
        c=[Path.MOVETO]+[Path.CURVE4]*3+[Path.LINETO]+[Path.CURVE4]*3+[Path.CLOSEPOLY]
        patch=PathPatch(Path(xy(v),c),fc=pal[color_by_path[segment['path_id']]],ec='none',alpha=.38,zorder=0)
        patch.set_gid('flow:'+segment['path_id']+':'+str(j));ax.add_patch(patch)
    if orientation=='horizontal':
        ax.set(xlim=(-.15,n-.85),ylim=(0,ledger['extent']),ylabel=weight_label)
        ax.set_xticks(range(n),stage_labels);ax.set_yticks([])
    else:
        ax.set(xlim=(0,ledger['extent']),ylim=(n-.85,-.15),xlabel=weight_label)
        ax.set_yticks(range(n),stage_labels);ax.set_xticks([])
    ax.set_title(title,loc='left',pad=12)
    for j,col in enumerate(stages):
        bounds=[.08+j*.87/n,.12,.87/n-.01,.23] if orientation=='horizontal' else [.72,.12+(n-j-1)*.74/n,.26,.74/n-.015]
        guide=fig.add_axes(bounds);guide.axis('off')
        guide.text(0,1,stage_labels[j],va='top',weight='bold',fontsize=9)
        nodes=[x for x in ledger['nodes'] if x['stage_index']==j]
        for i,node in enumerate(nodes):
            y=.77-i*.72/max(len(nodes),1)
            guide.add_patch(Rectangle((0,y-.045),.045,.055,fc=pal[node['category']],ec='none'))
            guide.text(.065,y,textwrap.fill(labels[node['category']],22)+'  ('+f"{node['weight']:g}"+')',
                       va='center',fontsize=8,linespacing=1.1)
    fig.text(.08,.045,'Band width = '+weight_label+'; total = '+f"{ledger['total']:g}"+'; colour = '+color_stage+' identity.\nGaps carry no quantity; zero-weight paths retained in the source and ledger.',fontsize=8)
    return _done(fig,data,'alluvial',theme,stage_columns=stages,weight_label=weight_label,
                 denominator=ledger['total'],orientation=orientation,color_stage=color_stage,
                 category_aliases=labels,stage_aliases=dict(zip(stages,stage_labels)),geometry_ledger=ledger)

def plot_upset(data,theme,*,set_columns,unit_label,title=''):
    d=checked(data,['object_id']+set_columns,set_columns);_unique(d,['object_id'])
    if not 2<=len(set_columns)<=8 or len(set_columns)!=len(set(set_columns)) or not set(d[set_columns].to_numpy().ravel())<=set([0,1]):raise ValueError('Membership must be complete binary values for 2–8 distinct sets')
    patterns=d.groupby(set_columns,sort=False).size(); pats=list(patterns.index); counts=patterns.to_numpy();fig=_start(theme);bars=_ax(fig,[.17,.53,.60,.32]);mat=_ax(fig,[.17,.17,.60,.29]);right=_ax(fig,[.81,.17,.15,.29]);color=theme['roles']['primary']
    bars.bar(range(len(pats)),counts,color=color,width=.7);bars.set(xlim=(-.5,len(pats)-.5),ylabel='Exclusive intersection count');bars.set_xticks([]);bars.set_title(title,loc='left')
    for j,p in enumerate(pats):
        on=[i for i,v in enumerate(p) if v==1];mat.scatter([j]*len(set_columns),range(len(set_columns)),s=30,color='#DDE3E9')
        if on:mat.plot([j]*len(on),on,color=color,lw=1);mat.scatter([j]*len(on),on,color=color,s=35,zorder=3)
        else:mat.text(j,(len(set_columns)-1)/2, 'None',ha='center',va='center',rotation=90,fontsize=7)
    mat.set(xlim=(-.5,len(pats)-.5),ylim=(len(set_columns)-.5,-.5));mat.set_yticks(range(len(set_columns)),set_columns);mat.set_xticks([]);right.barh(range(len(set_columns)),d[set_columns].sum(),color=color);right.set(ylim=(len(set_columns)-.5,-.5),xlabel='Set count');right.set_yticks([]);fig.text(.17,.04,unit_label+'; complete membership, disjoint pattern counts; all-zero objects retained',fontsize=8)
    return _done(fig,data,'upset',theme,set_columns=set_columns,unit_label=unit_label,display_summary='Exact binary-pattern counts; inclusive set totals',intersection_counts=[dict(pattern=list(p),count=int(c)) for p,c in zip(pats,counts)])

def plot_multistate_matrix(data,theme,*,state_order,state_slots,title='',row_field='row',column_field='column',
                           row_order=None,column_order=None,row_aliases=None,column_aliases=None):
    d=checked(data,[row_field,column_field,'states']);d=d.rename(columns={row_field:'row',column_field:'column'});_unique(d,['row','column']);rows=list(pd.unique(d.row));cols=list(pd.unique(d.column))
    if row_order is not None:
        row_order=list(row_order)
        if len(row_order)!=len(set(row_order)) or set(row_order)!=set(rows):raise ValueError('row_order must cover every row')
        rows=row_order
    if column_order is not None:
        column_order=list(column_order)
        if len(column_order)!=len(set(column_order)) or set(column_order)!=set(cols):raise ValueError('column_order must cover every column')
        cols=column_order
    if len(d)!=len(rows)*len(cols) or len(state_order)!=len(set(state_order)):raise ValueError('Complete known state grid required')
    palette=group_palette(theme,list(state_slots.values()));colors={s:palette[state_slots[s]] for s in state_order};tokens={}
    for r in d.itertuples():
        values=r.states.split(';') if r.states!='None' else []
        if set(values)-set(state_order) or len(values)!=len(set(values)):raise ValueError('Unknown/duplicate state; None means measured absence, not missing')
        tokens[(r.row,r.column)]=values
    fig=_start(theme,size=(max(8.5,len(cols)*.44+4),max(6.2,len(rows)*.30+3)));ax=_ax(fig,[.16,.20,.59,.63]);ax.set(xlim=(0,len(cols)),ylim=(len(rows),0));
    for y,row in enumerate(rows):
        for x,col in enumerate(cols):
            ax.add_patch(Rectangle((x+.04,y+.04),.92,.92,fc='#F0F3F6',ec='white'))
            active=tokens[(row,col)]
            for k,s in enumerate(active):ax.add_patch(Rectangle((x+.08,y+.08+k*.84/len(active)),.84,.84/len(active),fc=colors[s],ec='none'))
    xl=[str((column_aliases or {}).get(x,x)) for x in cols];yl=[str((row_aliases or {}).get(x,x)) for x in rows]
    if len(set(xl))!=len(xl) or len(set(yl))!=len(yl):raise ValueError('Axis aliases must be unique')
    ax.set_xticks(np.arange(len(cols))+.5,xl,rotation=45,ha='right');ax.set_yticks(np.arange(len(rows))+.5,yl);ax.set_title(title,loc='left');fig.legend(handles=[Rectangle((0,0),1,1,fc=colors[s],label=s) for s in state_order],title='Supplied event states',loc='upper left',bbox_to_anchor=(.78,.84),frameon=False)
    fig.text(.16,.05,'Multiple states may coexist; grey = explicit measured None',fontsize=8)
    return _done(fig,data,'multistate_matrix',theme,state_order=state_order,state_slots=state_slots,row_field=row_field,column_field=column_field,row_order=rows,column_order=cols,row_aliases=dict(zip(rows,yl)),column_aliases=dict(zip(cols,xl)),missing_policy='Missing rows/cells rejected; explicit None only')

def plot_running_enrichment(data,theme,*,curve_groups,rank_label,title=''):
    _types(data,['running','hit','metric']);d=_records(data,'running',['group','rank','value'],['rank','value']);h=_records(data,'hit',['group','rank'],['rank']);m=_records(data,'metric',['rank','value'],['rank','value']);_unique(d,['group','rank']);_unique(h,['group','rank']);_unique(m,['rank'])
    if set(d.group)!=set(curve_groups) or set(h.group)-set(curve_groups):raise ValueError('Curve identity mismatch')
    ranges=[(tuple(d.loc[d.group==g,'rank']),g) for g in curve_groups]
    base=ranges[0][0]
    if any(r[0]!=base for r in ranges) or tuple(m['rank'])!=base or not all(a<b for a,b in zip(base,base[1:])) or not set(h['rank'])<=set(base):raise ValueError('Shared ordered rank axis required; no interpolation or fitting')
    pal=group_palette(theme,curve_groups);fig=_start(theme);top=_ax(fig,[.13,.52,.62,.32]);hits=_ax(fig,[.13,.35,.62,.12]);bottom=_ax(fig,[.13,.14,.62,.17]);
    for i,g in enumerate(curve_groups):
        q=d[d.group==g];top.plot(q['rank'],q.value,color=pal[g],label=g);q=h[h.group==g];hits.vlines(q['rank'],i,i+.75,color=pal[g],lw=.8)
    bottom.fill_between(m['rank'],0,m.value,color=theme['roles']['primary'],alpha=.25);bottom.plot(m['rank'],m.value,color=theme['roles']['primary']);top.axhline(0,color='#BBC3CB',lw=.6);top.set_ylabel('Stored running score');top.set_title(title,loc='left');hits.set_yticks(np.arange(len(curve_groups))+.35,curve_groups);hits.set_ylim(-.1,len(curve_groups));bottom.set(xlabel=rank_label,ylabel='Rank metric')
    for a in (top,hits,bottom):a.set_xlim(base[0],base[-1])
    top.set_xticks([]);hits.set_xticks([]);fig.legend(handles=[Line2D([],[],color=pal[g],label=g) for g in curve_groups],loc='upper left',bbox_to_anchor=(.79,.84),frameon=False);fig.text(.13,.035,'Supplied enrichment curves and hit positions; no enrichment calculation',fontsize=8)
    return _done(fig,data,'running_enrichment',theme,rank_label=rank_label,curve_groups=curve_groups)

def plot_rank_bump(data,theme,*,stage_order,title=''):
    d=checked(data,['group','stage','rank'],['rank']);_unique(d,['group','stage']);groups=list(pd.unique(d.group));pal=group_palette(theme,groups)
    if set(d.stage)!=set(stage_order) or len(d)!=len(groups)*len(stage_order) or (d['rank']<1).any():raise ValueError('Complete supplied positive ranks required')
    fig=_start(theme);ax=_ax(fig,[.14,.16,.58,.68]);
    for g in groups:
        q=d[d.group==g].set_index('stage').reindex(stage_order);ax.plot(range(len(stage_order)),q['rank'],color=pal[g],marker='o',label=g)
    ax.invert_yaxis();ax.set_xticks(range(len(stage_order)),stage_order);ax.set(ylabel='Stored rank (1 = highest)',title=title);fig.legend(handles=ax.get_legend_handles_labels()[0],labels=groups,loc='upper left',bbox_to_anchor=(.78,.84),frameon=False)
    return _done(fig,data,'rank_bump',theme,stage_order=stage_order,analysis_boundary='Ranks supplied; ties preserved; no rank computation')

def plot_hex_density(data,theme,*,x_label,y_label,unit_label,gridsize=24,title=''):
    d=checked(data,['object_id','x','y'],['x','y']);_unique(d,['object_id'])
    if type(gridsize)!=int or not 4<=gridsize<=100:raise ValueError('Bounded explicit bin resolution required')
    fig=_start(theme);ax=_ax(fig,[.14,.17,.60,.67]);h=ax.hexbin(d.x,d.y,gridsize=gridsize,mincnt=1,cmap=_cmap(theme),linewidths=.25);fig.colorbar(h,cax=fig.add_axes([.79,.18,.025,.63]),label='Object count per bin');ax.set(xlabel=x_label,ylabel=y_label,title=title);fig.text(.14,.035,unit_label+'; descriptive occupied-bin counts; no regression or independence claim',fontsize=8)
    return _done(fig,data,'hex_density',theme,gridsize=gridsize,unit_label=unit_label,display_summary='All supplied objects allocated to occupied hex bins')

def plot_contour_field(data,theme,*,value_label,limits,levels,x_label,y_label,title=''):
    d=checked(data,['x','y','value'],['x','y','value']);mat,ys,xs=_grid(d,'y','x','value');xs=sorted(xs);ys=sorted(ys);mat=mat.reindex(index=ys,columns=xs)
    if not limits[0]<limits[1] or len(levels)<2 or any(a>=b for a,b in zip(levels,levels[1:])) or levels[0]<limits[0] or levels[-1]>limits[1]:raise ValueError('Explicit ordered color limits and contour levels required')
    if d.value.min()<limits[0] or d.value.max()>limits[1]:raise ValueError('Field exceeds declared color limits')
    fig=_start(theme);ax=_ax(fig,[.14,.16,.61,.69]);signed=limits[0]<0<limits[1];norm=TwoSlopeNorm(0,*limits) if signed else Normalize(*limits);cf=ax.contourf(xs,ys,mat.to_numpy(),levels=levels,cmap=_cmap(theme,signed),norm=norm);lines=ax.contour(xs,ys,mat.to_numpy(),levels=levels,colors='#647481',linewidths=.4,alpha=.6);ax.clabel(lines,inline=True,fontsize=6,fmt='%.1f');_colorbar(fig,[.80,.18,.025,.63],_cmap(theme,signed),norm,value_label);ax.set(xlabel=x_label,ylabel=y_label,title=title)
    return _done(fig,data,'contour_field',theme,value_label=value_label,limits=limits,levels=levels,analysis_boundary='Complete supplied grid; no spatial model or response fitting')
