"""Original process/landscape/result layout. Draw supplied geometry only.

Does not design biological sequences, predict structures, optimize binding,
score candidates or assign experimental validation. Synthetic glyphs are schematic.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import FancyBboxPatch,Polygon,FancyArrowPatch
from matplotlib.lines import Line2D
from figure_core import stamp,palette_check
from figure_reference import _new,_ax,_types,_records,_unique,_grid

def plot_process_dashboard(data,palette,*,surface_order,bar_group_order,stage_order,
                           geometry_label,count_label,size=(12,9)):
    _types(data,['node','edge','path','matrix','surface','landmark','count'])
    nodes=_records(data,'node',['node_id','x','y','width','height','group','text'],['x','y','width','height']); edges=_records(data,'edge',['edge_id','x0','y0','x1','y1','line_style'],['x0','y0','x1','y1']); paths=_records(data,'path',['object_id','order','x','y','group','shape'],['order','x','y']); matrices=_records(data,'matrix',['matrix_id','row','column','value'],['row','column','value']); surfaces=_records(data,'surface',['surface_id','x','y','z'],['x','y','z']); peaks=_records(data,'landmark',['surface_id','landmark','x','y','z','group'],['x','y','z']); counts=_records(data,'count',['bar_group','category','stage','value'],['value'])
    _unique(nodes,['node_id']); _unique(edges,['edge_id']); _unique(paths,['object_id','order']); _unique(peaks,['surface_id','landmark']); _unique(counts,['bar_group','category','stage'])
    if len(surface_order)!=3 or len(set(surface_order))!=3 or len(bar_group_order)!=2 or len(set(bar_group_order))!=2 or len(set(stage_order))!=len(stage_order): raise ValueError('Layout requires three distinct surfaces and two distinct count groups')
    if set(matrices.matrix_id)!={0,1,2} or set(peaks.surface_id)-set(surface_order): raise ValueError('Three numbered matrices and known landmark surfaces required')
    for _,obj in paths.groupby('object_id',sort=False):
        if obj.group.nunique()!=1 or obj['shape'].nunique()!=1: raise ValueError('Each geometry has one group and shape')
    palette_check(nodes.group,palette); palette_check(paths.group,palette); palette_check(peaks.group,palette); palette_check(counts.stage,palette)
    if (nodes[['width','height']]<=0).any().any() or (counts.value<0).any() or (counts.value%1!=0).any() or set(surfaces.surface_id)!=set(surface_order) or set(counts.bar_group)!=set(bar_group_order) or set(counts.stage)!=set(stage_order): raise ValueError('Invalid process dimensions/categories/counts')
    if not set(edges.line_style)<={'solid','dashed','dotted'} or not set(paths['shape'])<={'ribbon','outline'}: raise ValueError('Unknown geometry/style')
    fig=_new(size); body=_ax(fig,[.045,.18,.69,.70]); body.axis('off'); body.set(xlim=(0,100),ylim=(0,100))
    for n in nodes.itertuples():
        body.add_patch(FancyBboxPatch((n.x,n.y),n.width,n.height,boxstyle='round,pad=.4,rounding_size=2',fc=palette[n.group],ec='#64717A',lw=.8,alpha=.85)); body.text(n.x+n.width/2,n.y+n.height/2,n.text,ha='center',va='center',fontsize=8)
    for e in edges.itertuples(): body.add_patch(FancyArrowPatch((e.x0,e.y0),(e.x1,e.y1),arrowstyle='->',mutation_scale=9,color='#828B91',lw=.8,ls=e.line_style,connectionstyle='arc3,rad=.08'))
    for _,obj in paths.groupby('object_id',sort=False):
        obj=obj.sort_values('order'); color=palette[obj.group.iloc[0]]
        if obj['shape'].iloc[0]=='ribbon': body.plot(obj.x,obj.y,color=color,lw=1.4,alpha=.8)
        else: body.add_patch(Polygon(obj[['x','y']].to_numpy(),fc=color,ec='#708EA3',lw=.6,alpha=.88))
    for matrix_id in np.unique(matrices.matrix_id):
        sub=matrices[matrices.matrix_id==matrix_id]; mat,rs,cs=_grid(sub,'row','column','value')
        x=20+int(matrix_id)*24; y=29; cm=LinearSegmentedColormap.from_list('matrix',['#EAECEF',palette['Accent'],palette['Highlight']]); norm=Normalize(0,1)
        if ((sub.value<0)|(sub.value>1)).any(): raise ValueError('Candidate matrices require declared normalized [0,1] values')
        for r in sub.itertuples(): body.add_patch(Polygon([[x+r.column,y+r.row],[x+r.column+1,y+r.row],[x+r.column+1,y+r.row+1],[x+r.column,y+r.row+1]],fc=cm(norm(r.value)),ec='#67717A',lw=.25))
        body.text(x+len(cs)/2,y-2,f'Matrix {int(matrix_id)+1}',fontsize=7,ha='center')
    body.text(0,102,'a  Process nodes, fixed geometry and aligned candidates',fontsize=11,weight='bold')
    body.text(0,9,'c  Supplied object geometries with direct labels',fontsize=10,weight='bold')
    fig.text(.045,.09,geometry_label,fontsize=8,color='#65747D')
    for i,surface_id in enumerate(surface_order):
        sub=surfaces[surfaces.surface_id==surface_id]; mat,ys,xs=_grid(sub,'y','x','z')
        if min(mat.shape)<2 or not np.all(np.diff(xs)>0) or not np.all(np.diff(ys)>0): raise ValueError('Surface requires ordered regular grid')
        ax=fig.add_axes([.77,.66-i*.19,.21,.16],projection='3d'); xx,yy=np.meshgrid(xs,ys); color=palette[['Module','Object','Accent'][i%3]]; cm=LinearSegmentedColormap.from_list('landscape',['#F3F6F6',color]); ax.plot_surface(xx,yy,mat.to_numpy(),cmap=cm,rcount=len(ys),ccount=len(xs),lw=0,alpha=.9,shade=False)
        for p in peaks[peaks.surface_id==surface_id].itertuples(): ax.scatter(p.x,p.y,p.z,s=20,marker='D',c=palette[p.group],ec=INK,lw=.45)
        ax.set_axis_off(); ax.view_init(30,-55); ax.set_title(surface_id,fontsize=8,pad=-1)
    fig.text(.77,.89,'b  Supplied value landscapes',fontsize=10,weight='bold')
    for i,bg in enumerate(bar_group_order):
        ax=_ax(fig,[.64+i*.18,.14,.155,.16]); sub=counts[counts.bar_group==bg]; cats=list(dict.fromkeys(sub.category)); bottom=np.zeros(len(cats))
        if len(sub)!=len(cats)*len(stage_order): raise ValueError('Incomplete stage bars')
        for stage in stage_order:
            d=sub[sub.stage==stage].set_index('category').reindex(cats); ax.bar(range(len(cats)),d.value,bottom=bottom,width=.65,color=palette[stage],ec='#54636F',lw=.4)
            for j,v in enumerate(d.value):
                if v>0: ax.text(j,bottom[j]+v/2,str(int(v)),ha='center',va='center',fontsize=6)
            bottom+=d.value.to_numpy()
        ax.set_xticks(range(len(cats)),cats,fontsize=6); ax.set_ylabel(count_label,fontsize=7); ax.set_title(bg,fontsize=8); ax.tick_params(labelsize=6)
    fig.legend(handles=[Line2D([],[],ls='',marker='s',color=palette[s],label=s) for s in stage_order],loc='lower right',bbox_to_anchor=(.985,.073),frameon=False,ncols=2,fontsize=6)
    fig.text(.64,.32,'d  Supplied stage counts',fontsize=10,weight='bold')
    return stamp(fig,data,'reference_process_dashboard',palette=palette,surface_order=list(surface_order),bar_group_order=list(bar_group_order),stage_order=list(stage_order),geometry_label=geometry_label,count_label=count_label,analysis='none; no scoring/design/prediction/validation inferred',adapter_version=1)

INK='#25313A'
