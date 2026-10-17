"""Original display adapters for composition, position, hierarchy and uncertainty.

All scientific results, orders, registrations and intervals are supplied. Small
coordinate conversions and layout validations do not fit an analysis model.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from figure_core import checked
from project_theme import group_palette
from figure_method_extensions import _unique,_records,_types,_new,_axis,_finish,_cmap,_limits


def plot_ternary_composition(data,theme,*,components,denominator_definition,title=''):
    if len(components)!=3 or len(set(components))!=3:raise ValueError('Exactly three distinct component columns required')
    d=checked(data,['object_id','group',*components],components);_unique(d,['object_id']);v=d[components].to_numpy()
    if (v<0).any() or (v>1).any() or not np.allclose(v.sum(axis=1),1,rtol=0,atol=1e-8) or not denominator_definition:raise ValueError('Supplied three fractions must sum to one; no automatic normalization')
    pal=group_palette(theme,list(pd.unique(d.group)));height=np.sqrt(3)/2
    fig=_new(theme,(8,5.8));ax=fig.add_axes([.08,.17,.66,.66]);ax.set_aspect('equal');ax.axis('off');ax.set(xlim=(-.09,1.09),ylim=(-.10,height+.10))
    vertices=np.array([[.5,height],[0,0],[1,0]]);ax.add_patch(Polygon(vertices,fill=False,ec=theme['roles']['border'],lw=1.1))
    for fraction in [.2,.4,.6,.8]:
        for k in range(3):
            others=[j for j in range(3) if j!=k];a=vertices[k]*fraction+vertices[others[0]]*(1-fraction);b=vertices[k]*fraction+vertices[others[1]]*(1-fraction)
            ax.plot([a[0],b[0]],[a[1],b[1]],c='#DCE2E7',lw=.55,zorder=0)
        ax.text(fraction, -.036,f'{fraction:.1f}',ha='center',fontsize=8,color='#647480')
    xy=v@vertices
    for g in pal:
        ix=(d.group==g).to_numpy();ax.scatter(xy[ix,0],xy[ix,1],c=pal[g],s=26,ec='white',lw=.4,label=g,alpha=.80)
    for k,(x,y) in enumerate(vertices):ax.text(x,y+(.06 if k==0 else -.09),components[k],ha='center',fontsize=10)
    fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.78,.84),loc='upper left',frameon=False);fig.text(.08,.91,title,fontsize=11,weight='bold');fig.text(.08,.065,'Three supplied fractions; composition closure is not a correlation or causal model.',fontsize=8)
    return _finish(fig,data,theme,'ternary_composition',components=components,denominator_definition=denominator_definition,normalization='none; fractions supplied',coordinate_map='barycentric affine map, not dimension reduction')


def plot_genome_overview(data,theme,*,chromosome_order,chromosome_lengths,segment_slots,assembly,coordinate_definition,thresholds,title=''):
    d=checked(data,['variant_id','chromosome','position','pvalue'],['position','pvalue']);_unique(d,['variant_id'])
    if len(chromosome_order)!=len(set(chromosome_order)) or set(chromosome_order)!=set(d.chromosome) or set(chromosome_lengths)!=set(chromosome_order) or set(segment_slots)!=set(chromosome_order):raise ValueError('Complete explicit segment order, lengths and colour slots required')
    if not assembly or not coordinate_definition or ((d.pvalue<=0)|(d.pvalue>1)|(d.position<0)).any() or any(not np.isfinite(v) or v<=0 for v in chromosome_lengths.values()):raise ValueError('Explicit assembly/position definition and positive probabilities required')
    pal=group_palette(theme,list(dict.fromkeys(segment_slots.values())));offset={};cursor=0;gap=max(chromosome_lengths.values())*.025;centers=[]
    for c in chromosome_order:
        q=d[d.chromosome==c]
        if q.position.max()>chromosome_lengths[c]:raise ValueError('Position exceeds supplied segment length')
        offset[c]=cursor;centers.append(cursor+chromosome_lengths[c]/2);cursor+=chromosome_lengths[c]+gap
    fig=_new(theme,(10,4.6));ax=_axis(fig,[.09,.22,.69,.62])
    for c in chromosome_order:
        q=d[d.chromosome==c];ax.scatter(q.position+offset[c],-np.log10(q.pvalue),c=pal[segment_slots[c]],s=11,ec='none')
    for label,p in thresholds.items():
        if not np.isfinite(p) or not 0<p<=1:raise ValueError('Threshold probabilities must be supplied explicitly')
        ax.axhline(-np.log10(p),ls='--',lw=.8,c=theme['roles']['border'])
    ax.set(xticks=centers,xticklabels=chromosome_order,xlabel='Supplied segment position',ylabel='-log10(supplied p)',title=title,xlim=(-gap,cursor))
    fig.text(.82,.75,'Supplied thresholds\n'+'\n'.join(f'{k}: {v:g}' for k,v in thresholds.items()),fontsize=8)
    fig.text(.09,.065,assembly+'; no testing, clumping or automatic lead-variant selection.',fontsize=8)
    return _finish(fig,data,theme,'genome_association_overview',chromosome_order=chromosome_order,chromosome_lengths=chromosome_lengths,segment_slots=segment_slots,assembly=assembly,coordinate_definition=coordinate_definition,thresholds=thresholds,offsets=offset)


def plot_locus_tracks(data,theme,*,position_limits,chromosome,assembly,coordinate_definition,ld_reference,ld_definition,recombination_unit,title=''):
    _types(data,['association','gene','recombination'])
    a=_records(data,'association',['variant_id','position','pvalue'],['position','pvalue']);g=_records(data,'gene',['gene_id','start','end','strand','lane'],['start','end','lane']);r=_records(data,'recombination',['position','rate'],['position','rate'])
    _unique(a,['variant_id']);_unique(g,['gene_id']);_unique(r,['position']);lo,hi=position_limits
    if not np.isfinite([lo,hi]).all() or hi<=lo or not all([chromosome,assembly,coordinate_definition,ld_definition,recombination_unit]) or ld_reference not in set(a.variant_id):raise ValueError('Explicit region, units, assembly and LD reference required')
    if ((a.pvalue<=0)|(a.pvalue>1)|(a.position<lo)|(a.position>hi)).any() or ((g.start<lo)|(g.end>hi)|(g.end<=g.start)|(g.lane<0)|(g.lane%1!=0)).any() or set(g.strand)-set(['+','-']) or ((r.position<lo)|(r.position>hi)|(r.rate<0)).any() or (np.diff(r.position)<=0).any():raise ValueError('Invalid supplied region coordinates, spans or probability')
    if 'ld_r2' not in a:raise ValueError('LD column required; unavailable values must remain missing')
    ld=pd.to_numeric(a.ld_r2,errors='raise');known=ld.notna()
    if ((ld[known]<0)|(ld[known]>1)).any():raise ValueError('LD r2 outside [0,1]')
    if len(g)>30:raise ValueError('Split crowded gene tracks; do not shrink labels')
    fig=_new(theme,(9,6.9));ax=_axis(fig,[.12,.54,.62,.29]);rate=_axis(fig,[.12,.35,.62,.12]);genes=fig.add_axes([.12,.16,.62,.12]);cm=_cmap(theme,False)
    ax.scatter(a.position[known],-np.log10(a.pvalue[known]),c=ld[known],cmap=cm,vmin=0,vmax=1,s=25,ec='white',lw=.35)
    ax.scatter(a.position[~known],-np.log10(a.pvalue[~known]),c=theme['roles']['neutral'],s=24,marker='x',lw=.7)
    lead=a[a.variant_id==ld_reference];ax.scatter(lead.position,-np.log10(lead.pvalue),marker='D',s=62,facecolors='none',edgecolors=theme['roles']['border'],lw=1.1)
    for axis in [ax,rate,genes]:axis.set_xlim(lo,hi)
    ax.set(ylabel='-log10(supplied p)',xticks=[],title=title);rate.plot(r.position,r.rate,c=theme['roles']['border'],lw=1.1);rate.set(ylabel=recombination_unit,xticks=[])
    for row in g.itertuples():
        genes.plot([row.start,row.end],[row.lane]*2,c=theme['roles']['primary'],lw=3);mid=(row.start+row.end)/2;direction=1 if row.strand=='+' else -1
        genes.annotate('',xy=(mid+direction*(hi-lo)*.018,row.lane),xytext=(mid-direction*(hi-lo)*.018,row.lane),arrowprops=dict(arrowstyle='->',color=theme['roles']['border'],lw=.7))
        genes.text(mid,row.lane+.24,row.gene_id,ha='center',fontsize=8)
    genes.set(ylim=(-.4,g.lane.max()+.8),yticks=[],xlabel=chromosome+' / supplied position');genes.spines[['top','right','left']].set_visible(False)
    cb=fig.add_axes([.80,.59,.023,.23]);fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,1),cmap=cm),cax=cb,label='Supplied LD r2')
    fig.text(.79,.46,'Reference\n'+ld_reference+'\nGrey x: LD unavailable',fontsize=8);fig.text(.12,.055,assembly+'; supplied gene spans, no exon structure or colocalization inferred.',fontsize=8)
    return _finish(fig,data,theme,'local_association_tracks',position_limits=list(position_limits),chromosome=chromosome,assembly=assembly,coordinate_definition=coordinate_definition,ld_reference=ld_reference,ld_definition=ld_definition,recombination_unit=recombination_unit,missing_ld='grey x; never zero-imputed')


def plot_funnel_result(data,theme,*,reference_estimate,effect_definition,precision_definition,guide_definition,title=''):
    _types(data,['study','guide']);d=_records(data,'study',['study_id','group','estimate','se'],['estimate','se']);q=_records(data,'guide',['guide_id','estimate','se'],['estimate','se']);_unique(d,['study_id'])
    if (d.se<=0).any() or (q.se<0).any() or not np.isfinite(reference_estimate) or not all([effect_definition,precision_definition,guide_definition]):raise ValueError('Positive supplied SE and explicit reference/guide meaning required')
    pal=group_palette(theme,list(pd.unique(d.group)));fig=_new(theme,(8.2,5.0));ax=_axis(fig,[.12,.21,.60,.62])
    for name,g in q.groupby('guide_id',sort=False):ax.plot(g.estimate,g.se,c=theme['roles']['border'],ls='--',lw=.9,label=name)
    for name,g in d.groupby('group',sort=False):ax.scatter(g.estimate,g.se,c=pal[name],s=29,ec='white',lw=.4,label=name)
    ax.axvline(reference_estimate,c=theme['roles']['neutral'],lw=.8);ax.invert_yaxis();ax.set(xlabel=effect_definition,ylabel=precision_definition,title=title)
    fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.77,.83),loc='upper left',frameon=False,fontsize=8)
    fig.text(.12,.07,'Supplied guide geometry; asymmetry alone does not establish publication bias.',fontsize=8)
    return _finish(fig,data,theme,'funnel_supplied_results',reference_estimate=reference_estimate,effect_definition=effect_definition,precision_definition=precision_definition,guide_definition=guide_definition,model_fit='none; no pooling, Egger test or trim-and-fill')


def plot_hierarchy_partition(data,theme,*,root_id,quantity_definition,title=''):
    d=checked(data,['node_id','parent_id','group','value','x0','y0','x1','y1'],['value','x0','y0','x1','y1']);_unique(d,['node_id']);lookup=d.set_index('node_id')
    if root_id not in lookup.index or (d.value<=0).any() or ((d.x1<=d.x0)|(d.y1<=d.y0)).any() or not quantity_definition:raise ValueError('Unique positive-weight nodes with supplied rectangles required')
    root=lookup.loc[root_id];area0=(root.x1-root.x0)*(root.y1-root.y0)
    if sum(~d.parent_id.isin(d.node_id))!=1 or root.parent_id in set(d.node_id):raise ValueError('One declared root and known parents required')
    leaves=[]
    for node in d.itertuples():
        path=set();current=node.node_id
        while current!=root_id:
            if current in path or current not in lookup.index:raise ValueError('Cycle or disconnected hierarchy')
            path.add(current);current=lookup.loc[current,'parent_id']
        area=(node.x1-node.x0)*(node.y1-node.y0)
        if not np.isclose(area/area0,node.value/root.value,rtol=1e-7,atol=1e-9):raise ValueError('Supplied rectangle area must encode supplied quantity exactly')
        children=d[d.parent_id==node.node_id]
        if children.empty:leaves.append(node.node_id);continue
        if not np.isclose(children.value.sum(),node.value):raise ValueError('Children must partition the parent quantity')
        previous=[]
        for c in children.itertuples():
            if c.x0<node.x0 or c.x1>node.x1 or c.y0<node.y0 or c.y1>node.y1:raise ValueError('Child outside parent rectangle')
            if any(min(c.x1,p.x1)>max(c.x0,p.x0)+1e-10 and min(c.y1,p.y1)>max(c.y0,p.y0)+1e-10 for p in previous):raise ValueError('Overlapping sibling areas')
            previous.append(c)
    pal=group_palette(theme,list(pd.unique(lookup.loc[leaves,'group'])));fig=_new(theme,(8.3,5.8));ax=fig.add_axes([.08,.22,.64,.61]);ax.axis('off');ax.set(xlim=(root.x0,root.x1),ylim=(root.y0,root.y1))
    for row in sorted(d.itertuples(),key=lambda r:r.node_id not in leaves):
        leaf=row.node_id in leaves;ax.add_patch(Rectangle((row.x0,row.y0),row.x1-row.x0,row.y1-row.y0,fc=pal[row.group] if leaf else 'none',ec='white' if leaf else theme['roles']['border'],lw=1.4 if leaf else 1.0,alpha=.58 if leaf else 1))
        if leaf:ax.text((row.x0+row.x1)/2,(row.y0+row.y1)/2,f'{row.node_id}\n{row.value:g} ({row.value/root.value:.0%})',ha='center',va='center',fontsize=9)
        elif row.node_id!=root_id:ax.text(row.x0+.02*(root.x1-root.x0),row.y1-.02*(root.y1-root.y0),row.node_id,ha='left',va='top',fontsize=9,weight='bold')
    fig.text(.08,.92,title,fontsize=11,weight='bold');fig.text(.77,.73,'Leaf areas\nencode supplied\nadditive quantities.\nParent outlines\nencode hierarchy.',fontsize=9);fig.text(.08,.08,quantity_definition+'; supplied layout, not a new clustering.',fontsize=8)
    return _finish(fig,data,theme,'hierarchy_area_partition',root_id=root_id,quantity_definition=quantity_definition,area_encoding='leaf and parent area proportional to supplied quantity; nested values not double-counted')


def plot_uncertainty_fan(data,theme,*,coverage_order,interval_definition,x_label,y_label,title=''):
    d=checked(data,['group','x','coverage','center','lower','upper'],['x','coverage','center','lower','upper']);_unique(d,['group','x','coverage'])
    if len(coverage_order)!=len(set(coverage_order)) or coverage_order!=sorted(coverage_order) or set(coverage_order)!=set(d.coverage) or not all(0<c<1 for c in coverage_order) or not interval_definition:raise ValueError('Explicit ordered interval coverage levels required')
    if ((d.lower>d.center)|(d.upper<d.center)).any():raise ValueError('Invalid supplied interval')
    pal=group_palette(theme,list(pd.unique(d.group)));fig=_new(theme,(8.4,5.2));ax=_axis(fig,[.12,.21,.60,.63]);n=len(coverage_order)
    for group,q in d.groupby('group',sort=False):
        xs=list(pd.unique(q.x))
        if xs!=sorted(xs) or len(q)!=len(xs)*n or (q.groupby('x').center.nunique()!=1).any():raise ValueError('Complete ordered x x coverage grid with a common center required')
        lo=q.pivot(index='x',columns='coverage',values='lower').reindex(columns=coverage_order);hi=q.pivot(index='x',columns='coverage',values='upper').reindex(columns=coverage_order)
        if (np.diff(lo,axis=1)>1e-10).any() or (np.diff(hi,axis=1)<-1e-10).any():raise ValueError('Higher-coverage intervals must contain lower-coverage intervals')
        for j,c in reversed(list(enumerate(coverage_order))):ax.fill_between(xs,lo[c],hi[c],color=pal[group],alpha=.08+.16*(n-j)/n,lw=0)
        med=q.drop_duplicates('x');ax.plot(med.x,med.center,c=pal[group],lw=1.6,label=group)
    ax.set(xlabel=x_label,ylabel=y_label,title=title);fig.legend(*ax.get_legend_handles_labels(),bbox_to_anchor=(.76,.84),loc='upper left',frameon=False)
    fig.legend(handles=[Patch(fc=theme['roles']['primary'],alpha=.08+.16*(n-j)/n,label=f'{c:.0%}') for j,c in enumerate(coverage_order)],title='Supplied intervals',bbox_to_anchor=(.76,.58),loc='upper left',frameon=False)
    fig.text(.12,.07,interval_definition+'; no new forecast or interval estimation.',fontsize=8)
    return _finish(fig,data,theme,'nested_uncertainty_fan',coverage_order=coverage_order,interval_definition=interval_definition,x_label=x_label,y_label=y_label,center='same supplied center across interval levels')


def plot_spatial_overlay(data,theme,*,mode,pixel_size,physical_unit,background_definition,value_limits=None,value_label='Supplied value',title=''):
    _types(data,['pixel','spot']);b=_records(data,'pixel',['x','y','red','green','blue'],['x','y','red','green','blue']);s=_records(data,'spot',['object_id','group','x','y','radius'],['x','y','radius']);_unique(b,['x','y']);_unique(s,['object_id'])
    if mode not in ['categorical','continuous'] or not np.isfinite(pixel_size) or pixel_size<=0 or not physical_unit or not background_definition:raise ValueError('Explicit overlay mode, registered pixel scale and background required')
    xs=sorted(pd.unique(b.x));ys=sorted(pd.unique(b.y))
    if xs!=list(range(len(xs))) or ys!=list(range(len(ys))) or len(b)!=len(xs)*len(ys) or ((b[['red','green','blue']]<0)|(b[['red','green','blue']]>1)).any().any():raise ValueError('Complete origin-zero integer pixel grid with RGB values in [0,1] required')
    if (s.radius<=0).any() or (s.x-s.radius<-.5).any() or (s.x+s.radius>len(xs)-.5).any() or (s.y-s.radius<-.5).any() or (s.y+s.radius>len(ys)-.5).any():raise ValueError('Physical spot disks must stay inside the registered image')
    im=np.stack([b.pivot(index='y',columns='x',values=c).reindex(index=ys,columns=xs).to_numpy() for c in ['red','green','blue']],axis=-1)
    pal=group_palette(theme,list(pd.unique(s.group)));fig=_new(theme,(8,5.6));ax=fig.add_axes([.09,.19,.62,.64]);ax.imshow(im,origin='upper',extent=(-.5,len(xs)-.5,len(ys)-.5,-.5),interpolation='nearest');cm=_cmap(theme,False)
    norm=None
    if mode=='continuous':
        vals=checked(s,['value'],['value']);norm=_limits(vals.value,value_limits)
    for row in s.itertuples():ax.add_patch(Circle((row.x,row.y),row.radius,fc=pal[row.group] if mode=='categorical' else cm(norm(row.value)),ec='white',lw=.45,alpha=.88))
    ax.set_aspect('equal');ax.set(title=title,xticks=[],yticks=[]);ax.spines[:].set_visible(False)
    bar=max(1,int(len(xs)*.2));y=len(ys)-1.8;x=1;ax.plot([x,x+bar],[y,y],color=theme['roles']['border'],lw=1.5);ax.text(x+bar/2,y-.8,f'{bar*pixel_size:g} {physical_unit}',ha='center',va='bottom',fontsize=8,color=theme['roles']['border'])
    if mode=='categorical':fig.legend(handles=[Patch(fc=pal[g],label=g) for g in pal],bbox_to_anchor=(.76,.82),loc='upper left',frameon=False)
    else:
        cb=fig.add_axes([.79,.39,.023,.39]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cm),cax=cb,label=value_label)
    fig.text(.09,.07,'Registered physical disks on supplied RGB background; no alignment or segmentation fit.',fontsize=8)
    return _finish(fig,data,theme,'registered_spatial_'+mode,mode=mode,pixel_size=pixel_size,physical_unit=physical_unit,background_definition=background_definition,value_limits=value_limits,value_label=value_label,coordinate_definition='supplied registered pixel centers, origin upper; disks use input radii in pixel coordinates')
