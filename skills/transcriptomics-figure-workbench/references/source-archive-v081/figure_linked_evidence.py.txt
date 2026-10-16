"""Display supplied membership, paired cell metrics and hierarchy records.

No enrichment, correlations, clustering, network inference or docking occurs.
Orders, metrics and all relationships are frozen inputs, not inferred from a
visually similar example. Quantitative and categorical channels stay separate.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle, PathPatch, Wedge
from matplotlib.path import Path
from figure_core import checked
from figure_method_extensions import _records, _types, _unique, _new, _axis, _finish, _cmap, _limits
from project_theme import group_palette


def plot_membership_ribbons(data,theme,*,member_order,term_order,block_slots,effect_limits,
                            significance_limits,ratio_max,ratio_definition,title=''):
    _types(data,['member','term','link'])
    m=_records(data,'member',['member_id','effect'],['effect']);_unique(m,['member_id'])
    t=_records(data,'term',['term_id','label','block','ratio','padj','count'],['ratio','padj','count']);_unique(t,['term_id'])
    e=_records(data,'link',['member_id','term_id']);_unique(e,['member_id','term_id'])
    if not ratio_definition or len(member_order)>40 or len(term_order)>14 or set(member_order)!=set(m.member_id) or set(term_order)!=set(t.term_id) or len(set(member_order))!=len(member_order) or len(set(term_order))!=len(term_order):raise ValueError('Explicit unique bounded member/term orders required')
    if (set(e.member_id)-set(m.member_id)) or (set(e.term_id)-set(t.term_id)) or set(t.block)-set(block_slots):raise ValueError('Unknown member, term or block')
    if (t.padj<=0).any() or (t.padj>1).any() or (t.ratio<0).any() or (t.ratio>ratio_max).any() or ratio_max<=0:raise ValueError('Declared ratios and probabilities outside limits')
    counts=e.groupby('term_id').member_id.nunique()
    if any(float(r.count)!=counts.get(r.term_id,0) for r in t.itertuples()):raise ValueError('Term count disagrees with displayed membership')
    en=_limits(m.effect,effect_limits,signed=True);sn=_limits(-np.log10(t.padj),significance_limits)
    pal=group_palette(theme,list(block_slots.values())); cmap=_cmap(theme,True);scmap=_cmap(theme)
    fig=_new(theme,(14,7));a=fig.add_axes([.09,.18,.35,.69]);names=fig.add_axes([.46,.18,.20,.69]);dots=_axis(fig,[.68,.18,.17,.69])
    my={v:1-(i+.5)/len(member_order) for i,v in enumerate(member_order)};ty={v:1-(i+.5)/len(term_order) for i,v in enumerate(term_order)}
    effects=m.set_index('member_id').effect.to_dict(); terms=t.set_index('term_id')
    for r in e.itertuples():
        verts=[(.04,my[r.member_id]),(.39,my[r.member_id]),(.61,ty[r.term_id]),(.98,ty[r.term_id])]
        a.add_patch(PathPatch(Path(verts,[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4]),fc='none',ec=cmap(en(effects[r.member_id])),lw=.8,alpha=.55))
    for mid in member_order:
        a.text(.0,my[mid],mid,ha='right',va='center',fontsize=8)
    for tid in term_order:
        r=terms.loc[tid];y=ty[tid];color=pal[block_slots[r.block]]
        names.add_patch(Rectangle((0,y-.036),.025,.072,fc=color,ec='none'))
        names.text(.045,y,r.label,va='center',fontsize=8)
        dots.scatter([r.ratio],[y],s=230*r['count']/max(t['count']),c=[scmap(sn(-np.log10(r.padj)))],ec='white',lw=.5)
    for ax in [a,names,dots]:ax.set_ylim(0,1)
    for ax in [a,names]:ax.set_xlim(0,1);ax.axis('off')
    dots.set(xlim=(0,ratio_max*1.15),xlabel='Supplied ratio');dots.set_yticks([])
    sizes=sorted(set(int(v) for v in t['count']))
    if len(sizes)>3:sizes=[sizes[0],sizes[len(sizes)//2],sizes[-1]]
    handles=[dots.scatter([],[],s=230*v/max(t['count']),color='#687584',label=str(v)) for v in sizes]
    fig.legend(handles=handles,title='Member count (area)',loc='upper left',bbox_to_anchor=(.67,.985),ncols=len(sizes),frameon=False,fontsize=8,title_fontsize=8,columnspacing=.7)
    fig.colorbar(plt.cm.ScalarMappable(norm=sn,cmap=scmap),cax=fig.add_axes([.89,.55,.015,.24]),label='-log10 adjusted p')
    fig.colorbar(plt.cm.ScalarMappable(norm=en,cmap=cmap),cax=fig.add_axes([.89,.20,.015,.24]),label='Member effect')
    fig.text(.09,.94,title,fontsize=12,weight='bold');fig.text(.09,.08,'Equal-width lines = explicit membership. Dot area = displayed member count. '+ratio_definition,fontsize=8)
    return _finish(fig,data,theme,'membership_ribbons',member_order=member_order,term_order=term_order,block_slots=block_slots,effect_limits=effect_limits,significance_limits=significance_limits,ratio_max=ratio_max,ratio_definition=ratio_definition)


def plot_split_metric_matrix(data,theme,*,row_order,column_order,row_slots,association_limits,
                            significance_limits,association_definition,probability_definition,title=''):
    d=checked(data,['row_id','column_id','association','pvalue'],['association','pvalue']);_unique(d,['row_id','column_id'])
    if not association_definition or not probability_definition or len(row_order)!=len(set(row_order)) or len(column_order)!=len(set(column_order)) or set(row_order)!=set(d.row_id) or set(column_order)!=set(d.column_id) or len(d)!=len(row_order)*len(column_order) or set(row_order)!=set(row_slots):raise ValueError('Complete declared matrix/order and two metric definitions required')
    if (d.pvalue<=0).any() or (d.pvalue>1).any():raise ValueError('Supplied probabilities must be in (0,1]')
    an=_limits(d.association,association_limits,signed=True);pn=_limits(-np.log10(d.pvalue),significance_limits)
    pal=group_palette(theme,list(row_slots.values()));fig=_new(theme,(9,6));ax=fig.add_axes([.15,.26,.57,.59]);lookup=d.set_index(['row_id','column_id'])
    for i,row in enumerate(row_order):
        ax.add_patch(Rectangle((-.15,i),.08,1,fc=pal[row_slots[row]],ec='white',lw=.5,clip_on=False))
        for j,col in enumerate(column_order):
            r=lookup.loc[(row,col)]
            ax.add_patch(Polygon([(j,i),(j+1,i),(j,i+1)],fc=_cmap(theme)(pn(-np.log10(r.pvalue))),ec='white',lw=.5))
            ax.add_patch(Polygon([(j+1,i),(j+1,i+1),(j,i+1)],fc=_cmap(theme,True)(an(r.association)),ec='white',lw=.5))
    ax.set(xlim=(0,len(column_order)),ylim=(len(row_order),0));ax.set_xticks(np.arange(len(column_order))+.5,column_order,rotation=35,ha='right');ax.set_yticks(np.arange(len(row_order))+.5,row_order);ax.tick_params(length=0)
    fig.colorbar(plt.cm.ScalarMappable(norm=pn,cmap=_cmap(theme)),cax=fig.add_axes([.79,.58,.025,.23]),label='Upper: -log10 p')
    fig.colorbar(plt.cm.ScalarMappable(norm=an,cmap=_cmap(theme,True)),cax=fig.add_axes([.79,.27,.025,.23]),label='Lower: association')
    fig.text(.15,.93,title,fontsize=12,weight='bold');fig.text(.15,.07,'Two independent color keys; probability is not correlation magnitude. Supplied results only.',fontsize=8)
    return _finish(fig,data,theme,'split_metric_matrix',row_order=row_order,column_order=column_order,row_slots=row_slots,association_limits=association_limits,significance_limits=significance_limits,association_definition=association_definition,probability_definition=probability_definition)


def _tree(data,leaf_order):
    _types(data,['leaf','merge']);leaves=_records(data,'leaf',['node_id','group']);merges=_records(data,'merge',['node_id','left','right','height'],['height'])
    _unique(leaves,['node_id']);_unique(merges,['node_id'])
    if len(leaves)<2 or len(leaves)>100 or len(leaf_order)!=len(set(leaf_order)) or set(leaf_order)!=set(leaves.node_id) or len(merges)!=len(leaves)-1 or set(leaves.node_id)&set(merges.node_id):raise ValueError('Unique leaves and a full binary supplied hierarchy required')
    positions={v:i+.5 for i,v in enumerate(leaf_order)};heights={v:0. for v in leaf_order};desc={v:{i} for i,v in enumerate(leaf_order)};used=[]
    for r in merges.itertuples():
        if r.left not in positions or r.right not in positions or r.left==r.right or r.height<=max(heights[r.left],heights[r.right]):raise ValueError('Hierarchy order, height or child invalid')
        branch=desc[r.left]|desc[r.right]
        if desc[r.left]&desc[r.right] or max(branch)-min(branch)+1!=len(branch):raise ValueError('Declared leaf order crosses hierarchy branches')
        positions[r.node_id]=(positions[r.left]+positions[r.right])/2;heights[r.node_id]=r.height;desc[r.node_id]=branch;used.extend([r.left,r.right])
    if len(used)!=len(set(used)) or len(desc[merges.iloc[-1].node_id])!=len(leaves):raise ValueError('Hierarchy is disconnected or reuses a child')
    return leaves,merges,positions,heights


def plot_hierarchy_tracks(data,theme,*,leaf_order,height_definition,title=''):
    l,m,x,h=_tree(data,leaf_order)
    if not height_definition:raise ValueError('Merge-height meaning required')
    pal=group_palette(theme,list(l.group.unique()));fig=_new(theme,(11,5.6));ax=_axis(fig,[.09,.32,.68,.52]);strip=fig.add_axes([.09,.22,.68,.065])
    for r in m.itertuples():ax.plot([x[r.left],x[r.left],x[r.right],x[r.right]],[h[r.left],r.height,r.height,h[r.right]],c=theme['roles']['border'],lw=.8)
    for i,id_ in enumerate(leaf_order):strip.add_patch(Rectangle((i,0),1,1,fc=pal[l.set_index('node_id').loc[id_,'group']],ec='white',lw=.25))
    ax.set(xlim=(0,len(l)),ylabel=height_definition,title=title);ax.set_xticks([]);strip.set(xlim=(0,len(l)),ylim=(0,1));strip.set_xticks(np.arange(len(l))+.5,leaf_order,rotation=90,fontsize=7);strip.set_yticks([])
    fig.legend(handles=[Line2D([],[],lw=6,c=c,label=g) for g,c in pal.items()],bbox_to_anchor=(.80,.80),loc='upper left',frameon=False)
    fig.text(.09,.06,'Given hierarchy, fixed leaf order and categorical strip; no clustering performed.',fontsize=8)
    return _finish(fig,data,theme,'hierarchy_tracks',leaf_order=leaf_order,height_definition=height_definition)


def plot_radial_hierarchy(data,theme,*,leaf_order,height_definition,metric_limits,metric_definition,
                          outer_definition,area_definition,label_ids=(),title=''):
    l,m,x,h=_tree(data,leaf_order);l=checked(l,['metric','outer_value','area_value'],['metric','outer_value','area_value'])
    if (l.outer_value<0).any() or ((l.area_value<0)|(l.area_value>1)).any() or not all([height_definition,metric_definition,outer_definition,area_definition]) or set(label_ids)-set(l.node_id) or len(label_ids)>15:raise ValueError('Explicit radial numeric channels and bounded labels required')
    signed=metric_limits[0]<0<metric_limits[1]
    norm=_limits(l.metric,metric_limits,signed=signed);cm=_cmap(theme,signed);maxh=max(h.values());n=len(l);angles={v:2*np.pi*x[v]/n for v in x};radius={v:.80-.62*h[v]/maxh for v in h}
    fig=_new(theme,(9,8));ax=fig.add_axes([.03,.12,.73,.77]);ax.set_aspect('equal');ax.axis('off')
    for r in m.itertuples():
        a,b=angles[r.left],angles[r.right];rr=radius[r.node_id];theta=np.linspace(a,b,40)
        ax.plot(rr*np.cos(theta),rr*np.sin(theta),c='#BCC6CF',lw=.6)
        for ch in [r.left,r.right]:a=angles[ch];ax.plot([rr*np.cos(a),radius[ch]*np.cos(a)],[rr*np.sin(a),radius[ch]*np.sin(a)],c='#BCC6CF',lw=.6)
    lookup=l.set_index('node_id');maximum=max(float(l.outer_value.max()),1e-12)
    for id_ in leaf_order:
        a=angles[id_];r=lookup.loc[id_];color=cm(norm(r.metric));ax.scatter([.85*np.cos(a)],[.85*np.sin(a)],s=12+120*r.area_value,c=[color],ec='white',lw=.3,zorder=3)
        half=180/n*.85;angle=np.degrees(a);ax.add_patch(Wedge((0,0),1.02+.20*r.outer_value/maximum,angle-half,angle+half,width=.20*r.outer_value/maximum,fc=color,ec='none',alpha=.75))
        if id_ in label_ids:ax.annotate(id_,(.86*np.cos(a),.86*np.sin(a)),xytext=(.98*np.cos(a),.98*np.sin(a)),textcoords='data',ha='left' if np.cos(a)>0 else 'right',va='center',fontsize=8,arrowprops=dict(arrowstyle='-',color=color,lw=.6))
    ax.set(xlim=(-1.35,1.35),ylim=(-1.35,1.35),title=title)
    fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.83,.53,.023,.27]),label=metric_definition)
    fig.text(.82,.34,'Point area:\n'+area_definition,fontsize=8);fig.text(.82,.21,'Outer height:\n'+outer_definition,fontsize=8)
    fig.text(.07,.05,'Frozen hierarchy; no target ranking or binding prediction. Distances and channels use their supplied definitions.',fontsize=8)
    return _finish(fig,data,theme,'radial_hierarchy',leaf_order=leaf_order,height_definition=height_definition,metric_limits=metric_limits,metric_definition=metric_definition,outer_definition=outer_definition,area_definition=area_definition,label_ids=list(label_ids),area_mapping='12 + 120 * supplied area_value')


def plot_stacked_values(data,theme,*,object_order,segment_order,value_definition,additivity_definition,title=''):
    d=checked(data,['object_id','segment','value'],['value']);_unique(d,['object_id','segment'])
    if not value_definition or not additivity_definition or (d.value<0).any() or set(object_order)!=set(d.object_id) or set(segment_order)!=set(d.segment) or len(set(object_order))!=len(object_order) or len(set(segment_order))!=len(segment_order) or len(d)!=len(object_order)*len(segment_order):raise ValueError('Complete nonnegative additive quantity grid and explicit orders required')
    pal=group_palette(theme,segment_order);fig=_new(theme,(11,5.6));ax=_axis(fig,[.10,.27,.67,.57]);base=np.zeros(len(object_order))
    for s in segment_order:
        values=d[d.segment==s].set_index('object_id').loc[object_order,'value'].to_numpy();ax.bar(range(len(values)),values,bottom=base,color=pal[s],label=s,width=.78,ec='white',lw=.4);base+=values
    ax.set_xticks(range(len(object_order)),object_order,rotation=90,fontsize=7);ax.set(ylabel=value_definition,title=title)
    fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.81,.80),loc='upper left',frameon=False);fig.text(.10,.06,additivity_definition,fontsize=8)
    return _finish(fig,data,theme,'stacked_values',object_order=object_order,segment_order=segment_order,value_definition=value_definition,additivity_definition=additivity_definition,normalization='none; input quantities retained')
