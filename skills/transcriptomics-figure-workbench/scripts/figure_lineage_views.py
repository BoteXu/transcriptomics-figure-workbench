"""Frozen cluster flow and trajectory geometry. No clustering or trajectory fit."""
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from figure_core import checked,stamp
from project_theme import apply_project_style,group_palette

def plot_lineage_view(data,theme,*,mode,title,definition,level_order=None,root_id=None,value_limits=(0,1),columns='auto'):
    """Show actual lineage/flow identities, quantities and coordinate meanings."""
    if mode not in ['cluster_tree','trajectory'] or not title or not definition:raise ValueError('Declare a supported view, scientific question and source meaning')
    if columns!='auto' and (type(columns) is not int or columns not in [1,2]):raise ValueError('Use auto, one or two columns')
    cols=2 if columns=='auto' else columns
    fig=plt.figure(figsize=(10 if cols==2 else 7,5.8 if cols==2 else 10.5),layout='constrained');axes=fig.subplots(1 if cols==2 else 2,cols,squeeze=False).flat;ax,b=list(axes)
    for a in [ax,b]:a.spines[['top','right']].set_visible(False);a.tick_params(labelsize=10)
    if mode=='cluster_tree':
        nodes=checked(data[data.record_type=='node'],['node','level','x','n'],['x','n']);edges=checked(data[data.record_type=='edge'],['source','target','n'],['n'])
        if nodes.node.duplicated().any() or edges.duplicated(['source','target']).any() or ((nodes.n<=0)|(nodes.n%1!=0)).any() or ((edges.n<=0)|(edges.n%1!=0)).any():raise ValueError('Unique positive integer node and cell-flow counts required')
        levels=level_order or nodes.level.drop_duplicates().tolist()
        if len(levels)<2 or len(levels)!=len(set(levels)) or set(levels)!=set(nodes.level):raise ValueError('Complete explicit ordered resolutions required')
        lookup=nodes.set_index('node');pal=group_palette(theme,levels)
        if len(set(nodes.groupby('level').n.sum()))!=1:raise ValueError('Each resolution must retain the same complete cell count')
        for r in edges.itertuples():
            if r.source not in lookup.index or r.target not in lookup.index:raise ValueError('Every flow endpoint must exist')
            s=lookup.loc[r.source];t=lookup.loc[r.target];i=levels.index(s.level);j=levels.index(t.level)
            if j!=i+1 or r.n>min(s.n,t.n):raise ValueError('Flows connect adjacent declared resolutions with valid counts')
            prop=r.n/t.n;arrow=FancyArrowPatch((s.x,-i),(t.x,-j),arrowstyle='-|>',mutation_scale=9,lw=.6+3*r.n/nodes.n.max(),color=pal[s.level],alpha=.2+.65*prop,shrinkA=14,shrinkB=14,connectionstyle='arc3,rad=0')
            ax.add_patch(arrow)
        for r in nodes.itertuples():
            i=levels.index(r.level)
            if i and int(edges[edges.target==r.node].n.sum())!=int(r.n):raise ValueError('Incoming flows must account for every target cell')
            if i<len(levels)-1 and int(edges[edges.source==r.node].n.sum())!=int(r.n):raise ValueError('Outgoing flows must account for every source cell')
            ax.scatter(r.x,-i,s=120+500*r.n/nodes.n.max(),c=pal[r.level],ec='white',lw=1.1,zorder=3);ax.annotate(r.node+'\nn='+str(int(r.n)),(r.x,-i),xytext=(0,18),textcoords='offset points',ha='center',fontsize=10,zorder=5,bbox=dict(fc='white',ec='none',alpha=.92,pad=1.5))
        ax.set(yticks=-np.arange(len(levels)),yticklabels=levels,xlim=(nodes.x.min()-.5,nodes.x.max()+.5),ylim=(-len(levels)+.5,.7));ax.set_xticks([]);ax.spines[:].set_visible(False);ax.set_title('A  Complete flow across resolutions',loc='left',fontsize=12,fontweight='bold')
        for i,level in enumerate(levels):
            q=nodes[nodes.level==level];bottom=0
            for r in q.itertuples():b.barh(i,r.n,left=bottom,color=pal[level],alpha=.4+.5*(list(q.node).index(r.node)+1)/len(q),height=.55,ec='white',lw=1);b.text(bottom+r.n/2,i,str(int(r.n)),ha='center',va='center',fontsize=10);bottom+=r.n
        b.set(yticks=range(len(levels)),yticklabels=levels,xlabel='Cells / same complete denominator');b.invert_yaxis();b.set_title('B  Cluster sizes at each resolution',loc='left',fontsize=12,fontweight='bold')
        fig.text(.5,.005,'Node area: 120 + 500 n/max(n) pt² · edge width: .6 + 3 n/max(node n) · opacity: .2 + .65 incoming fraction',ha='center',fontsize=9)
    else:
        cells=checked(data[data.record_type=='cell'],['cell','branch','x','y','pseudotime','donor'],['x','y','pseudotime']);nodes=checked(data[data.record_type=='node'],['node','x','y'],['x','y']);edges=checked(data[data.record_type=='edge'],['source','target'])
        if cells.cell.duplicated().any() or nodes.node.duplicated().any() or edges.duplicated(['source','target']).any() or root_id not in set(nodes.node):raise ValueError('Unique cells, frozen graph and explicit root required')
        if len(value_limits)!=2 or not np.isfinite(value_limits).all() or value_limits[0]>=value_limits[1] or ((cells.pseudotime<value_limits[0])|(cells.pseudotime>value_limits[1])).any():raise ValueError('Common explicit pseudotime limits must contain every cell')
        branches=cells.branch.drop_duplicates().tolist();pal=group_palette(theme,branches);lookup=nodes.set_index('node')
        for a in [ax,b]:
            for r in edges.itertuples():
                if r.source not in lookup.index or r.target not in lookup.index:raise ValueError('Every graph node must exist')
                s=lookup.loc[r.source];t=lookup.loc[r.target];a.plot([s.x,t.x],[s.y,t.y],c='#4C6879',lw=1.6,zorder=3)
            root=lookup.loc[root_id];a.scatter(root.x,root.y,marker='*',s=150,c='#DCA95A',ec='white',lw=.7,zorder=5);a.annotate('Root: '+root_id,(root.x,root.y),xytext=(0,-20),textcoords='offset points',ha='center',fontsize=10)
            a.set_aspect('equal',adjustable='box');a.spines[:].set_visible(False);a.set_xticks([]);a.set_yticks([])
        for group in branches:q=cells[cells.branch==group];ax.scatter(q.x,q.y,s=max(5,min(20,4000/len(cells))),c=pal[group],ec='none',alpha=.65,rasterized=True,label=group)
        art=b.scatter(cells.x,cells.y,c=cells.pseudotime,s=max(5,min(20,4000/len(cells))),cmap='viridis',vmin=value_limits[0],vmax=value_limits[1],ec='none',alpha=.8,rasterized=True)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,-.08),ncols=min(3,len(branches)),frameon=False,fontsize=10);fig.colorbar(art,ax=b,shrink=.7,label='Supplied pseudotime / not clock time');ax.set_title('A  Branch identity and frozen graph',loc='left',fontsize=12,fontweight='bold');b.set_title('B  Progression on identical cells',loc='left',fontsize=12,fontweight='bold')
    fig.suptitle(title+'\nFrozen display input · no inference',fontsize=14,fontweight='bold');fig.get_layout_engine().set(h_pad=.20,w_pad=.25,wspace=.12,hspace=.2)
    for a in fig.axes:a._explicit_guide_layout=True
    stamp(fig,data,'lineage_'+mode,mode=mode,title=title,definition=definition,level_order=level_order,root_id=root_id,value_limits=value_limits,columns=columns,analysis_performed=False)
    return apply_project_style(fig,theme)
