"""Complete responsive reading pages for dense frozen drawing components.

Positions, matrices, surfaces, intervals and contribution values are supplied.
No model, clustering, surface fitting, structure prediction or analysis occurs.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LinearSegmentedColormap
from matplotlib.patches import Rectangle,Wedge,Polygon,FancyBboxPatch,FancyArrowPatch
from figure_core import stamp
from figure_workbench.responsive import grid_shape,facet_slots,canvas_budget


def multiclass_page(data,d,shares,palette,classes,orders,limits,columns,rows,size):
    from figure_reference import _new,_draw_swarm,_finish,reference_cmap
    nr,nc=grid_shape(len(classes)+1,columns,rows)
    max_features=max(map(len,orders.values()));panel_height=max(3.4,.20*max_features+1)
    width=max(8,nc*4.4+1.0) if tuple(size)==(12,9) else float(size[0])
    height=nr*panel_height+1.9
    fig=_new(canvas_budget(width,height));slots=facet_slots(fig,len(classes)+1,nr,nc,left=.13,right=.97,bottom=1.0/height,top=1-1.15/height,wspace=.8,hspace=.6)
    cm=reference_cmap('shap_reference_rainbow',semantic='sequential')
    for k,cl in enumerate(classes):
        ax=fig.add_subplot(slots[k]);sub=d[d['class']==cl]
        if set(sub.feature)!=set(orders[cl]):raise ValueError('Class feature order mismatch')
        _draw_swarm(ax,sub,orders[cl],cm,limits,point_size=7)
        ax.set_title(f'{cl} · {sub.unit_id.nunique()} supplied units',loc='left',fontsize=9);ax.set_xlabel('Supplied prediction contribution',fontsize=8);ax.tick_params(labelsize=8)
        ax.spines[['top','right']].set_visible(False);ax._explicit_guide_layout=True
    summary=fig.add_subplot(slots[-1]);summary.set_title('Supplied contribution shares',loc='left',fontsize=9)
    features=list(dict.fromkeys(shares.feature));bottom=np.zeros(len(classes))
    for feature in features:
        values=np.array([float(shares[(shares['class']==cl)&(shares.feature==feature)].value.iloc[0]) if ((shares['class']==cl)&(shares.feature==feature)).any() else 0 for cl in classes])
        summary.barh(range(len(classes)),values,left=bottom,color=palette[feature],label=feature,height=.65,ec='white',lw=.5);bottom+=values
    summary.set(xlim=(0,1),ylim=(len(classes)-.5,-.5),xlabel='Fraction of supplied absolute contribution')
    summary.set_yticks(range(len(classes)),classes,fontsize=8);summary.set_xticks([0,.5,1],['0','50%','100%']);summary.tick_params(labelsize=8);summary.spines[['top','right']].set_visible(False)
    # The complete identity key owns a bottom lane; it never overlays points.
    legend_rows=math.ceil(len(features)/max(1,nc*3));legend_height=.22*legend_rows+.25
    old_height=height;height+=legend_height;fig.set_size_inches(width,height)
    scale=old_height/height
    for ax in fig.axes:
        b=ax.get_position();ax.set_position([b.x0,(b.y0*old_height+legend_height)/height,b.width,b.height*scale]);ax._explicit_guide_layout=True
    handles,labels=summary.get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.14/height),ncols=max(1,nc*3),frameon=False,fontsize=8)
    cax=fig.add_axes([.73,1-.4/height,.20,.075/height]);fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,1),cmap=cm),cax=cax,orientation='horizontal',label='Supplied feature value');cax.tick_params(labelsize=7);cax._explicit_guide_layout=True
    fig.text(.13,(legend_height+.35)/height,'Frozen upstream contributions; feature order is supplied. Shares are not inferred from plotted points.',fontsize=8)
    fig._responsive_facets=dict(rows=nr,columns=nc,panels=len(classes)+1)
    return _finish(fig,data,'multiclass_contributions',palette=palette,class_order=list(classes),feature_orders=orders,limits=list(limits),presentation='reading',columns=nc,rows=nr,shares='complete supplied values; 100% per class',rose='classic option retains polar shares')


def process_page(data,palette,nodes,edges,paths,matrices,surfaces,peaks,counts,surface_order,bar_groups,stages,geometry_label,count_label,columns,rows,width):
    from figure_reference import _new,_grid
    nr,nc=grid_shape(8,columns,rows)
    width=width or max(11,nc*4.5+.8);lower_height=nr*3.2;diagram_height=4.4;height=lower_height+diagram_height+1.9
    fig=_new(canvas_budget(width,height));body=fig.add_axes([.07,(lower_height+1.1)/height,.86,diagram_height/height]);body.axis('off');body.set(xlim=(0,100),ylim=(0,100))
    for n in nodes.itertuples():
        # Identity pills occupy their own visual layer: decorative paths must
        # not pass through the label, while transparent backdrop containers
        # stay behind the supplied process geometry.
        pill=n.group=='Paper'
        body.add_patch(FancyBboxPatch((n.x,n.y),n.width,n.height,boxstyle='round,pad=.4,rounding_size=2',fc='white' if n.group=='Backdrop' else palette[n.group],ec='#AABCC5' if n.group=='Backdrop' else '#64717A',lw=.7,alpha=.98 if pill else .7,zorder=4 if pill else 1));body.text(n.x+n.width/2,n.y+n.height/2,n.text,ha='center',va='center',fontsize=8,zorder=5)
    for e in edges.itertuples():body.add_patch(FancyArrowPatch((e.x0,e.y0),(e.x1,e.y1),arrowstyle='->',mutation_scale=9,color='#7F919C',lw=.8,ls=e.line_style,connectionstyle='arc3,rad=.08'))
    for _,obj in paths.groupby('object_id',sort=False):
        obj=obj.sort_values('order');color=palette[obj.group.iloc[0]]
        if obj['shape'].iloc[0]=='ribbon':body.plot(obj.x,obj.y,color=color,lw=1.5,alpha=.9)
        else:body.add_patch(Polygon(obj[['x','y']].to_numpy(),fc=color,ec='#6B8795',lw=.6,alpha=.8))
    body.set_title('A  Supplied process geometry · schematic coordinates',loc='left',fontsize=11,pad=8)
    slots=facet_slots(fig,8,nr,nc,left=.08,right=.93,bottom=1.0/height,top=(lower_height+.45)/height,hspace=.9,wspace=.65)
    for i,sid in enumerate(surface_order):
        sub=surfaces[surfaces.surface_id==sid];mat,ys,xs=_grid(sub,'y','x','z');xx,yy=np.meshgrid(xs,ys)
        if min(mat.shape)<2 or not np.all(np.diff(xs)>0) or not np.all(np.diff(ys)>0):raise ValueError('Surface requires ordered complete supplied grid')
        ax=fig.add_subplot(slots[i],projection='3d');cm=LinearSegmentedColormap.from_list('supplied_surface_'+str(i),['#E5EEF1',palette[['Module','Object','Accent'][i%3]]]);norm=Normalize(float(sub.z.min()),float(sub.z.max()))
        ax.plot_surface(xx,yy,mat.to_numpy(),cmap=cm,norm=norm,rcount=len(ys),ccount=len(xs),lw=0,shade=False,alpha=.95)
        for p in peaks[peaks.surface_id==sid].itertuples():ax.scatter(p.x,p.y,p.z,s=30,marker='D',c=palette[p.group],ec='#263D4A',lw=.5)
        ax.set(xlabel='Supplied X',ylabel='Supplied Y',zlabel='Value');ax.view_init(30,-55);ax.set_title(chr(66+i)+'  '+str(sid),loc='left',fontsize=9)
        ax.tick_params(labelsize=7,pad=0);ax.xaxis.label.set_fontsize(8);ax.yaxis.label.set_fontsize(8);ax.zaxis.label.set_fontsize(8);ax._explicit_guide_layout=True
    cm=LinearSegmentedColormap.from_list('supplied_matrix',['#F1F5F6',palette['Accent'],palette['Highlight']])
    for i,mid in enumerate(sorted(matrices.matrix_id.unique())):
        sub=matrices[matrices.matrix_id==mid];mat,rs,cs=_grid(sub,'row','column','value');ax=fig.add_subplot(slots[i+3]);im=ax.imshow(mat,cmap=cm,vmin=0,vmax=1,aspect='auto');ax.set_title(chr(69+i)+f'  Supplied matrix {int(mid)+1}',loc='left',fontsize=9);ax.set_xticks(range(len(cs)),cs,fontsize=7);ax.set_yticks(range(len(rs)),rs,fontsize=7);ax.set(xlabel='Column',ylabel='Row');ax.spines[:].set_visible(False)
        if ((sub.value<0)|(sub.value>1)).any():raise ValueError('Matrix normalized value must be in [0,1]')
        ax.set_xticklabels([f'{float(v):g}' for v in cs]);ax.set_yticklabels([f'{float(v):g}' for v in rs])
        cb=fig.colorbar(im,ax=ax,fraction=.04,pad=.04,label='Supplied normalized value');cb.ax.tick_params(labelsize=7);ax._explicit_guide_layout=True;cb.ax._explicit_guide_layout=True
    for i,bg in enumerate(bar_groups):
        ax=fig.add_subplot(slots[i+6]);sub=counts[counts.bar_group==bg];cats=list(dict.fromkeys(sub.category));base=np.zeros(len(cats))
        for s in stages:
            q=sub[sub.stage==s].set_index('category').reindex(cats)
            if q.value.isna().any():raise ValueError('Incomplete stage counts')
            ax.barh(range(len(cats)),q.value,left=base,color=palette[s],height=.68,label=s,ec='white',lw=.5)
            from matplotlib.colors import to_rgb
            ink='white' if np.dot(to_rgb(palette[s]),[.2126,.7152,.0722])<.47 else '#253C49'
            for j,v in enumerate(q.value):
                if v>0:ax.text(base[j]+v/2,j,str(int(v)),va='center',ha='center',fontsize=7,color=ink)
            base+=q.value.to_numpy()
        ax.set_yticks(range(len(cats)),cats,fontsize=8);ax.set(xlabel=count_label,title=chr(72+i)+'  '+str(bg),ylim=(len(cats)-.5,-.5));ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8);ax._explicit_guide_layout=True
    fig.legend(*ax.get_legend_handles_labels(),loc='lower right',bbox_to_anchor=(.96,.05/height),frameon=False,ncols=len(stages),fontsize=8)
    fig.text(.08,.38/height,textwrap.fill(geometry_label+'; frozen schematic objects and supplied landscapes, no prediction or scoring.',max(60,int(width*10))),fontsize=8)
    fig._responsive_facets=dict(rows=nr,columns=nc,panels=9,full_width_components=1)
    return stamp(fig,data,'reference_process_dashboard',palette=palette,surface_order=list(surface_order),bar_group_order=list(bar_groups),stage_order=list(stages),geometry_label=geometry_label,count_label=count_label,presentation='reading',columns=nc,rows=nr,width=width,analysis='none; all scientific geometry and numerical values supplied',adapter_version=2)
