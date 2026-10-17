"""Integrated presentation of explicit frozen result channels; no fitting.

Ellipses, density shapes, embedding labels and histogram bins are supplied.
Counts/proportions are checked as display summaries, never treated as inference.
"""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Ellipse,Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.ticker import MaxNLocator,PercentFormatter
from figure_core import checked,stamp
from project_theme import group_palette,apply_project_style


def _clean(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(labelsize=9,length=3,width=.6)


def _axis(fig,box):
    ax=fig.add_axes(box);_clean(ax);return ax


def _inside(fig,box,relative):
    x,y,w,h=box;u,v,a,b=relative
    return _axis(fig,[x+u*w,y+v*h,a*w,b*h])


def _bins(data,kind,groups):
    q=checked(data[data.record_type==kind],['group','left','right','count'],['left','right','count'])
    if set(q.group)!=set(groups) or ((q.right<=q.left)|(q['count']<0)|(q['count']%1!=0)).any() or q.duplicated(['group','left','right']).any():raise ValueError('Complete unique nonnegative frozen histogram bins required')
    grid=None
    for name in groups:
        z=q[q.group==name].sort_values('left');pairs=list(zip(z.left,z.right))
        if grid is None:grid=pairs
        if pairs!=grid or any(abs(a[1]-b[0])>1e-8 for a,b in zip(pairs,pairs[1:])):raise ValueError('Group histograms require the same complete contiguous bins')
    return q


def _marginals(fig,box,data,points,pal,xfield,yfield,*,xkind,ykind,stacked=False):
    core=_inside(fig,box,[0,0,.78,.77]);top=_inside(fig,box,[0,.82,.78,.18]);right=_inside(fig,box,[.84,0,.16,.77])
    for kind,field,ax,horizontal in [(xkind,xfield,top,False),(ykind,yfield,right,True)]:
        bins=_bins(data,kind,pal);bottom=None
        for name,color in pal.items():
            z=bins[bins.group==name].sort_values('left');source=points[points.group==name]
            if int(z['count'].sum())!=len(source):raise ValueError('Frozen marginal count differs from complete point scope')
            observed=np.histogram(source[field],bins=np.r_[z.left.to_numpy(),z.right.iloc[-1]])[0]
            if not np.array_equal(observed,z['count'].to_numpy()):raise ValueError('Frozen bins do not match the declared points')
            values=z['count'].to_numpy(float) if stacked else z['count'].to_numpy(float)/max(len(source),1)
            if bottom is None:bottom=np.zeros(len(z))
            if stacked:
                if horizontal:ax.barh(z.left,values,height=z.right-z.left,left=bottom,color=color,align='edge',lw=0)
                else:ax.bar(z.left,values,width=z.right-z.left,bottom=bottom,color=color,align='edge',lw=0)
                bottom+=values
            else:
                edges=np.r_[z.left,z.right.iloc[-1]]
                ax.stairs(values,edges,orientation='horizontal' if horizontal else 'vertical',fill=True,color=color,alpha=.18,lw=.9)
                ax.stairs(values,edges,orientation='horizontal' if horizontal else 'vertical',color=color,lw=1.1)
        ax.spines[:].set_visible(False);ax.tick_params(length=0)
        if horizontal:
            ax.tick_params(labelleft=False,labelbottom=True)
            maximum=max(float(bottom.max()) if stacked else float(bins.groupby('group')['count'].apply(lambda z:z.max()/max(z.sum(),1)).max()),.01)
            ax.set_xlim(0,maximum*1.08);ax.set_xticks([0,maximum])
            if not stacked:ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
            else:ax.xaxis.set_major_formatter(lambda x,pos:format(x,'.0f'))
            ax.set_xlabel('Count' if stacked else 'Within\ngroup',fontsize=9)
        else:
            ax.tick_params(labelbottom=False);ax.yaxis.set_major_locator(MaxNLocator(2))
            if not stacked:ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
            ax.set_ylabel('Genes' if stacked else '%',fontsize=9)
    core._linked_marginals=(top,right)
    return core,top,right


def _pca_panel(fig,box,data,theme,axes_labels,ellipse_definition):
    d=checked(data[data.record_type=='embedding'],['object_id','group','x','y'],['x','y'])
    if d.object_id.duplicated().any():raise ValueError('One PCA position per explicit independent sample required')
    pal=group_palette(theme,list(d.group.unique()))
    ax,top,right=_marginals(fig,box,data,d,pal,'x','y',xkind='pca_x_bin',ykind='pca_y_bin')
    e=checked(data[data.record_type=='ellipse'],['group','x','y','width','height','angle','coverage'],['x','y','width','height','angle','coverage'])
    if not ellipse_definition or e.group.duplicated().any() or set(e.group)!=set(pal) or ((e.width<=0)|(e.height<=0)|(e.coverage<=0)|(e.coverage>=1)).any():raise ValueError('Complete supplied ellipse geometry and explicit interpretation required')
    if any((d.group==g).sum()<3 for g in e.group):raise ValueError('Do not display group ellipses with fewer than three supplied samples')
    for row in e.itertuples():
        ax.add_patch(Ellipse((row.x,row.y),row.width,row.height,angle=row.angle,facecolor=pal[row.group]+'20',edgecolor=pal[row.group],lw=1.2,zorder=1))
    ax.axhline(0,color='#E0E7EA',lw=.7,zorder=0);ax.axvline(0,color='#E0E7EA',lw=.7,zorder=0)
    for name,color in pal.items():
        q=d[d.group==name];ax.scatter(q.x,q.y,c=color,s=49,ec='white',lw=.6,zorder=3,label=name+'  n='+str(len(q)))
    ax.autoscale_view();ax.margins(.12);top.set_xlim(ax.get_xlim());right.set_ylim(ax.get_ylim())
    ax.set(xlabel=axes_labels[0],ylabel=axes_labels[1]);ax.set_zorder(2)
    return ax


def _volcano_panel(fig,box,data,theme,labels=(),alpha=.05,fc=1):
    d=checked(data[data.record_type=='de'],['gene','log2FC','padj'],['log2FC','padj']).copy()
    if d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any() or not 0<alpha<1 or fc<=0:raise ValueError('Complete unique DE results and explicit valid display thresholds required')
    d['group']=np.where((d.padj<=alpha)&(d.log2FC>=fc),'Up',np.where((d.padj<=alpha)&(d.log2FC<=-fc),'Down','Other'))
    d['strength']=-np.log10(d.padj)
    pal={'Other':'#CFD6DB','Down':theme['roles']['negative'],'Up':theme['roles']['positive']}
    ax,top,right=_marginals(fig,box,data,d,pal,'log2FC','strength',xkind='de_x_bin',ykind='de_y_bin',stacked=True)
    for name,color in pal.items():
        q=d[d.group==name];ax.scatter(q.log2FC,q.strength,c=color,s=6 if name=='Other' else 15,alpha=.32 if name=='Other' else .87,ec='none',zorder=1 if name=='Other' else 3,rasterized=True)
    for cut in [-fc,fc]:ax.axvline(cut,color='#9BAAB4',lw=.7,ls=(0,(3,3)))
    ax.axhline(-np.log10(alpha),color='#9BAAB4',lw=.7,ls=(0,(3,3)))
    if len(labels)>12 or set(labels)-set(d.gene):raise ValueError('Select at most twelve explicitly existing gene labels')
    annotations=[]
    for index,row in enumerate(d[d.gene.isin(labels)].itertuples()):
        dx=-7 if row.log2FC<0 else 7;dy=9+(index%2)*12
        annotations.append(ax.annotate(row.gene,(row.log2FC,row.strength),xytext=(dx,dy),textcoords='offset points',ha='right' if dx<0 else 'left',fontsize=9,color='#293D48',arrowprops=dict(arrowstyle='-',lw=.6,color='#8698A3'),bbox=dict(boxstyle='round,pad=.12',fc='white',ec='none',alpha=.8)))
    ax.set(xlabel='log2 fold change',ylabel='−log10 adjusted P');ax.margins(x=.13,y=.12)
    top.set_xlim(ax.get_xlim());right.set_ylim(ax.get_ylim())
    fig.canvas.draw();accepted=[]
    for annotation in annotations:
        dx,dy=annotation.get_position()
        for offset in [0,14,-14,28,-28,42,-42,56,-56,70,-70]:
            annotation.set_position((dx,dy+offset));fig.canvas.draw()
            # Measure the text only: connector extents may legitimately cross.
            box=annotation.get_bbox_patch().get_window_extent(fig.canvas.get_renderer()).expanded(1.08,1.12)
            if not any(box.overlaps(previous) for previous in accepted):accepted.append(box);break
        else:raise ValueError('Selected gene labels require a wider panel or fewer explicit labels')
    return ax,{name:int((d.group==name).sum()) for name in pal}


def _dot_panel(fig,box,data,theme):
    d=checked(data[data.record_type=='marker_dot'],['feature','group','value','fraction','feature_group'],['value','fraction'])
    if d.duplicated(['feature','group']).any() or len(d)!=d.feature.nunique()*d.group.nunique() or ((d.fraction<0)|(d.fraction>1)|(d.value<0)).any():raise ValueError('Complete marker mean/fraction grid required')
    if (d.groupby('feature').feature_group.nunique()!=1).any():raise ValueError('Each marker requires an explicit consistent supplied annotation block')
    names=list(d.group.unique());pal=group_palette(theme,names);features=list(d.feature.unique())
    # Explicit supplied block membership supplies order; this is not clustering.
    features=sorted(features,key=lambda v:(names.index(d[d.feature==v].feature_group.iloc[0]),features.index(v)))
    ax=_inside(fig,box,[0,0,.91,.90]);cax=_inside(fig,box,[.95,0,.025,.90])
    cmap=LinearSegmentedColormap.from_list('marker_mean',['#E1EBED','#245E78'])
    artist=ax.scatter([features.index(v) for v in d.feature],[names.index(v) for v in d.group],s=90*d.fraction,c=d.value,cmap=cmap,ec='none')
    ax.set(ylim=(len(names)-.5,-.5),xlim=(-.5,len(features)-.5));ax.set_yticks(range(len(names)),names);ax.set_xticks(range(len(features)),features,rotation=90,fontsize=9);ax.tick_params(length=0)
    from matplotlib.patches import Rectangle
    for j,gene in enumerate(features):
        block=d[d.feature==gene].feature_group.iloc[0]
        if block not in pal:raise ValueError('Marker block must name a supplied annotation identity')
        ax.add_patch(Rectangle((j-.5,1.025),1,.045,transform=ax.get_xaxis_transform(),fc=pal[block],ec='white',lw=.3,clip_on=False))
    for boundary in np.cumsum([sum(d.drop_duplicates('feature').feature_group==n) for n in names])[:-1]:ax.axvline(boundary-.5,color='#E1E7EA',lw=.8,zorder=0)
    ax.spines[:].set_visible(False);cb=fig.colorbar(artist,cax=cax);cb.set_label('Supplied mean expression',fontsize=9);cb.ax.tick_params(labelsize=9)
    return ax


def _annotation_atlas(data,theme,title,include_response=False,feature_columns='auto'):
    emb=checked(data[data.record_type=='embedding'],['object_id','group','x','y'],['x','y'])
    if emb.object_id.duplicated().any():raise ValueError('Annotation atlas requires unique cells with fixed coordinates')
    names=list(emb.group.unique());pal=group_palette(theme,names)
    anchors=checked(data[data.record_type=='embedding_label'],['group','x','y','label'],['x','y'])
    if anchors.group.duplicated().any() or set(anchors.group)!=set(names):raise ValueError('Supply one reviewed label anchor per annotation')
    features=checked(data[data.record_type=='feature_map'],['object_id','feature','x','y','value'],['x','y','value'])
    if features.duplicated(['object_id','feature']).any():raise ValueError('Duplicate cell-feature coordinates')
    maps=list(features.feature.unique())
    if not 1<=len(maps)<=16:raise ValueError('Choose one to sixteen explicit representative markers; use a reading edition beyond that')
    for gene,q in features.groupby('feature',sort=False):
        if set(q.object_id)!=set(emb.object_id):raise ValueError('Every selected feature map retains all cells')
        merged=q.set_index('object_id').loc[emb.object_id];np.testing.assert_allclose(merged[['x','y']].to_numpy(),emb[['x','y']].to_numpy(),rtol=0,atol=0)
    if feature_columns!='auto' and (type(feature_columns) is not int or not 1<=feature_columns<=8):raise ValueError('Use auto or one to eight feature columns')
    cols=min(5,len(maps)) if feature_columns=='auto' else feature_columns
    rows=int(np.ceil(len(maps)/cols));height=6.9+rows*1.65+(3.4 if include_response else 0)
    fig=plt.figure(figsize=(9.7,height));fig.suptitle(title,fontsize=13,fontweight='bold',y=.98)
    # Regions use physical inches, so additional marker rows grow the canvas.
    def box(x,y,w,h):return [x/9.7,y/height,w/9.7,h/height]
    upper=height-4.95
    ax=_axis(fig,box(.58,upper,3.65,3.8));ax.set(xlabel='Stored UMAP 1',ylabel='Stored UMAP 2');ax.set_aspect('equal',adjustable='box')
    for name,color in pal.items():
        q=emb[emb.group==name];ax.scatter(q.x,q.y,s=11,c=color,ec='none',alpha=.78,rasterized=True)
    for row in anchors.itertuples():
        label=ax.text(row.x,row.y,row.label,ha='center',va='center',fontsize=10,color=pal[row.group],fontweight='bold');label.set_path_effects([pe.withStroke(linewidth=3.5,foreground='white')])
    ax.set_title('A  Subpopulations',loc='left',fontsize=11,fontweight='bold',pad=14)
    dot=_dot_panel(fig,box(5.05,upper+.55,4.1,2.85),data,theme);dot.set_title('B  Marker specificity',loc='left',fontsize=11,fontweight='bold',pad=25)
    dot.legend(handles=[Line2D([],[],ls='',marker='o',color='#627E8D',ms=np.sqrt(90*p),label=str(int(p*100))+'% detected') for p in [.25,.75]],loc='upper center',bbox_to_anchor=(.5,-.36),ncols=2,frameon=False,fontsize=9)
    baseline=(3.9 if include_response else .55)
    cmap=LinearSegmentedColormap.from_list('feature_signal',['#E4EBED','#2A827F','#133D56']);limits=(float(features.value.min()),float(features.value.max()))
    xlim=ax.get_xlim();ylim=ax.get_ylim();fw=8.65/cols
    for i,gene in enumerate(maps):
        row,col=divmod(i,cols);occupied=min(cols,len(maps)-row*cols);shift=(cols-occupied)*fw/2
        a=_axis(fig,box(.62+shift+col*fw,baseline+(rows-1-row)*1.65,fw-.18,1.35));q=features[features.feature==gene].sort_values('value',kind='stable')
        artist=a.scatter(q.x,q.y,c=q.value,s=5,cmap=cmap,vmin=limits[0],vmax=limits[1],ec='none',rasterized=True);a.set(xlim=xlim,ylim=ylim);a.set_aspect('equal',adjustable='box');a.set_xticks([]);a.set_yticks([]);a.spines[:].set_visible(False);a.set_title(gene,fontsize=10,fontweight='bold')
    fig.text(.06,(baseline+rows*1.65+.13)/height,'C  Representative markers · identical coordinates and shared scale',fontsize=11,fontweight='bold')
    cax=_axis(fig,box(7.4,.10,1.75,.075));cb=fig.colorbar(artist,cax=cax,orientation='horizontal');cb.set_label('Supplied expression',fontsize=9);cb.ax.tick_params(labelsize=9)
    if include_response:
        comp=checked(data[data.record_type=='composition'],['sample','category','count','condition'],['count'])
        rr=list(comp['sample'].unique());cc=list(comp.category.unique())
        if set(cc)!=set(names) or comp.duplicated(['sample','category']).any() or len(comp)!=len(rr)*len(cc) or (comp['count']<0).any():raise ValueError('Complete donor-by-annotation counts required')
        mat=comp.pivot(index='sample',columns='category',values='count').reindex(index=rr,columns=cc);den=mat.sum(axis=1)
        if (den<=0).any():raise ValueError('Positive donor denominators required')
        a=_axis(fig,box(.70,.85,3.6,2.1));bottom=np.zeros(len(rr))
        for name in cc:v=mat[name]/den;a.bar(range(len(rr)),v,bottom=bottom,color=pal[name],width=.82);bottom+=v
        a.set_xticks(range(len(rr)),rr,rotation=90,fontsize=9);a.set(ylim=(0,1),ylabel='Within-donor cell fraction');a.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
        cond=comp.drop_duplicates('sample').set_index('sample').loc[rr,'condition'];cp=group_palette(theme,list(cond.unique()))
        a.scatter(range(len(rr)),np.repeat(1.035,len(rr)),c=[cp[v] for v in cond],s=18,marker='s',clip_on=False)
        legend=a.legend(handles=[Patch(color=c,label=g) for g,c in cp.items()],loc='lower left',bbox_to_anchor=(.70/9.7,3.10/height),bbox_transform=fig.transFigure,ncols=2,frameon=False,fontsize=9);legend._page_fixed_anchor=True
        heading=fig.text(.70/9.7,3.57/height,'D  Donor composition',fontsize=11,fontweight='bold');heading._panel_heading=True
        v,counts=_volcano_panel(fig,box(5.20,.85,3.7,2.25),data,theme,labels=())
        heading=fig.text(5.20/9.7,3.57/height,'E  Myeloid donor response',fontsize=11,fontweight='bold');heading._panel_heading=True
    for a in fig.axes:a._explicit_guide_layout=True
    stamp(fig,data,'integrated_annotation_atlas',annotation_inferred=False,embedding_refitted=False,selected_markers=maps,all_cells_retained=True,shared_feature_scale=limits,includes_donor_response=include_response,scientific_acceptance=False)
    return fig


def plot_integrated_view(data,theme,*,mode,title,axis_labels=None,ellipse_definition=None,labels=(),alpha=.05,fc=1,feature_columns='auto',cloud_shapes=None,observation_unit=None,presentation='auto',group_counts=None,expression_limits=None,identity_by_cell=None,identity_order=None):
    """Prefer a compatible information-rich view; all extra scientific channels are supplied."""
    if mode not in ['pca','volcano','annotation_atlas','single_cell_main','qc','marker_dot','batch_facets','effect_table','ma','unit_profile']:raise ValueError('Choose a documented integrated presentation')
    if not isinstance(title,str) or not title.strip():raise ValueError('State the comparison')
    if presentation not in ['auto','publication','classic']:raise ValueError('Choose auto, publication or classic presentation')
    if mode=='qc' and cloud_shapes is not None and presentation!='classic':
        d=checked(data,['cell_id','sample','group','value'],['value'])
        if not observation_unit or (d.groupby('sample').group.nunique()!=1).any():raise ValueError('Explicit QC count units and stable sample groups required')
        from figure_study_publication import qc_grid
        return apply_project_style(qc_grid(d,theme,title,cloud_shapes,observation_unit),theme)
    if mode=='unit_profile' and presentation!='classic':
        d=checked(data,['sample_id','group','value'],['value'])
        if d.sample_id.duplicated().any() or (d.value<0).any() or not axis_labels:raise ValueError('Unique samples and explicit count units required')
        from figure_study_publication import coverage
        return apply_project_style(coverage(d,theme,title,axis_labels[0]),theme)
    if mode=='batch_facets' and identity_by_cell is not None and presentation!='classic':
        from figure_study_publication import batch_coverage
        d=checked(data,['cell_id','group','x','y'],['x','y'])
        return apply_project_style(batch_coverage(d,theme,title,identity_by_cell,identity_order),theme)
    if mode in ['annotation_atlas','single_cell_main']:
        return apply_project_style(_annotation_atlas(data,theme,title,mode=='single_cell_main',feature_columns),theme)
    fig=plt.figure(figsize=(8.0,6.7));fig.suptitle(title,fontsize=13,fontweight='bold',y=.97)
    if presentation!='classic' and mode in ['pca','volcano','ma']:
        fig.set_size_inches(8.5,6.7);fig._suptitle.set(x=.12,ha='left',color='#294553')
    if mode=='pca':
        ax=_pca_panel(fig,[.12,.29,.75,.53],data,theme,axis_labels or ['PC1','PC2'],ellipse_definition)
        points=data[data.record_type=='embedding']
        # Sample identity is essential for a small QC plot. Keep every supplied
        # point; labels are display annotations and never a new PCA fit.
        if len(points)<=24:
            for row in points.itertuples():
                ax.annotate(str(row.object_id),(row.x,row.y),xytext=(5,5),
                    textcoords='offset points',fontsize=8,color='#4D626D',
                    bbox=dict(fc='white',ec='none',alpha=.8,pad=.5))
        groups=list(data[data.record_type=='embedding'].group.unique());pal=group_palette(theme,groups)
        fig.legend(handles=[Patch(fc=pal[g],label=g+' · n='+str(sum((data.record_type=='embedding')&(data.group==g)))) for g in groups],loc='upper center',bbox_to_anchor=(.5,.92),ncols=len(groups),frameon=False,fontsize=10)
        var=checked(data[data.record_type=='pc_variance'],['component','percent'],['percent'])
        if var.component.duplicated().any() or (var.percent<0).any() or abs(var.percent.sum()-100)>1e-6:raise ValueError('Supply a complete explained-variance profile summing to 100%')
        a=_axis(fig,[.12,.09,.57,.11]);a.bar(range(len(var)),var.percent,color=['#218C8D' if i<2 else '#D6E0E5' for i in range(len(var))],width=.7);a.set_xticks(range(len(var)),var.component,fontsize=9);a.set_ylabel('Variance %',fontsize=9)
        if presentation=='classic':fig.text(.74,.115,textwrap.fill(ellipse_definition,24),fontsize=9,color='#5D707C',va='center')
        else:
            fig.text(.74,.14,'PC1 + PC2\n'+format(var.percent.iloc[:2].sum(),'.1f')+'% variance',fontsize=10,color='#356678')
            fig.text(.12,.025,textwrap.fill(ellipse_definition,105),fontsize=8.5,color='#6B808A')
    elif mode=='volcano':
        ax,counts=_volcano_panel(fig,[.12,.20,.75,.64],data,theme,labels,alpha,fc)
        colors={'Other':'#AAB6BE','Down':theme['roles']['negative'],'Up':theme['roles']['positive']};total=sum(counts.values())
        fig.legend(handles=[Patch(color=colors[g],label=g+'  '+str(n)+' ('+format(n/total,'.1%')+')') for g,n in counts.items()],loc='upper center',bbox_to_anchor=(.5,.93),ncols=3,frameon=False,fontsize=9)
        fig.text(.12,.06,'All '+format(total,',')+' tested genes · stacked counts · FDR ≤ '+str(alpha)+' and |log2FC| ≥ '+str(fc),fontsize=9,color='#5D707C')
    elif mode=='ma':
        d=checked(data[data.record_type=='ma'],['feature_id','status','average','effect'],['average','effect']).copy();d['group']=d.status
        if d.feature_id.duplicated().any() or set(d.status)-{'other','down','up'}:raise ValueError('Complete unique MA results and supplied tested statuses required')
        pal={'other':'#CFD6DB','down':theme['roles']['negative'],'up':theme['roles']['positive']}
        ax,top,right=_marginals(fig,[.12,.20,.75,.64],data,d,pal,'average','effect',xkind='ma_x_bin',ykind='ma_y_bin',stacked=True)
        for g,c in pal.items():
            q=d[d.group==g];ax.scatter(q.average,q.effect,s=6 if g=='other' else 14,c=c,alpha=.3 if g=='other' else .85,ec='none',rasterized=True)
        ax.axhline(0,color='#9BAAB4',lw=.8);ax.set(xlabel='Average log2 expression',ylabel='log2 fold change');top.set_xlim(ax.get_xlim());right.set_ylim(ax.get_ylim())
        fig.legend(handles=[Patch(color=c,label=g+' · '+str(sum(d.group==g))) for g,c in pal.items()],loc='upper center',bbox_to_anchor=(.5,.92),ncols=3,frameon=False,fontsize=9)
        fig.text(.12,.06,'All '+format(len(d),',')+' tested genes · stored effects and complete marginal counts',fontsize=9,color='#6B808A')
    elif mode=='qc':
        d=checked(data,['cell_id','sample','group','value'],['value']);metrics=list(data.metric.unique()) if 'metric' in data else ['Expression'];fig.set_size_inches(9,max(3.5,3*len(metrics)))
        if observation_unit is not None and (not isinstance(observation_unit,str) or not observation_unit.strip()):raise ValueError('Declare the observation unit displayed in QC sample counts')
        if (d.groupby('sample').group.nunique()!=1).any():raise ValueError('Explicit consistent sample-group annotation required')
        palette=group_palette(theme,list(d.group.unique()))
        for j,metric in enumerate(metrics):
            q=d if 'metric' not in data else data[data.metric==metric];samples=list(q['sample'].unique());a=fig.add_subplot(len(metrics),1,j+1);_clean(a)
            for i,s in enumerate(samples):
                z=q[q['sample']==s].value.to_numpy();color=palette[q[q['sample']==s].group.iloc[0]]
                if cloud_shapes is not None:
                    from figure_raincloud_geometry import draw_supplied_raincloud
                    if set(cloud_shapes)!=set(metrics) or set(cloud_shapes[metric])!=set(samples):raise ValueError('Supply frozen cloud geometry for every displayed metric and sample')
                    draw_supplied_raincloud(a,i,z,color,cloud_shapes[metric][s],point_size=5)
                else:
                    a.scatter(i-.22+(np.arange(len(z))*.61803398875%1)*.18,z,s=2.5,alpha=.20,color=color,ec='none',rasterized=True)
                    a.boxplot([z],positions=[i+.10],widths=.30,patch_artist=True,showfliers=False,medianprops=dict(color='#334E5C',lw=1),boxprops=dict(fc=color+'55',ec=color,lw=.8),whiskerprops=dict(color=color,lw=.8),capprops=dict(color=color,lw=.8))
            a.set_xticks(range(len(samples)),[s+'\n'+(str(sum(q['sample']==s))+' '+observation_unit if observation_unit else 'n='+str(sum(q['sample']==s))) for s in samples],rotation=45,ha='right');a.set_ylabel(metric);a.set_title(title if len(metrics)==1 else metric,loc='left',fontsize=11,fontweight='bold')
        fig.suptitle('');fig.tight_layout(pad=1.5,h_pad=2)
        fig.legend(handles=[Patch(color=c,label=g) for g,c in palette.items()],loc='upper right',bbox_to_anchor=(.98,1),ncols=len(palette),frameon=False,fontsize=9)
    elif mode=='marker_dot':
        fig.set_size_inches(max(8,data.feature.nunique()*.35+2),4.5);a=_dot_panel(fig,[.14,.31,.76,.48],data,theme)
        if presentation!='classic':
            fig._suptitle.set(x=.14,ha='left',color='#294553')
            features=[x.get_text() for x in a.get_xticklabels()];names=list(data.group.unique());pal=group_palette(theme,names)
            assignments=data.drop_duplicates('feature').set_index('feature').feature_group
            for g in names:
                indices=[j for j,f in enumerate(features) if assignments[f]==g]
                if indices:a.text(float(np.mean(indices)),1.12,textwrap.fill(g,14),transform=a.get_xaxis_transform(),ha='center',color=pal[g],fontsize=9)
        if group_counts is not None:
            names=list(data.group.unique())
            if set(group_counts)!=set(names) or any(type(v) is not int or v<1 for v in group_counts.values()):raise ValueError('Explicit positive cell counts for every identity required')
            a.set_yticklabels([g+'  ·  '+str(group_counts[g]) for g in names])
        if expression_limits is not None:
            if len(expression_limits)!=2 or expression_limits[0]!=0 or expression_limits[1]<data.value.max():raise ValueError('Common expression scale must retain every supplied value')
            a.collections[0].set_clim(*expression_limits)
        a.legend(handles=[Line2D([],[],ls='',marker='o',color='#627E8D',ms=np.sqrt(90*p),label=str(int(p*100))+'% detected') for p in [.25,.75]],loc='upper center',bbox_to_anchor=(.5,-.40),ncols=2,frameon=False,fontsize=9)
    elif mode=='batch_facets':
        d=checked(data,['cell_id','group','x','y'],['x','y']);groups=list(d.group.unique());pal=group_palette(theme,groups);cols=min(3,len(groups));rows=int(np.ceil(len(groups)/cols));fig.set_size_inches(cols*3.1,rows*3.1+.6)
        for i,g in enumerate(groups):
            a=fig.add_subplot(rows,cols,i+1);q=d[d.group==g];a.scatter(d.x,d.y,s=5,color='#E0E6EA',ec='none',rasterized=True);a.scatter(q.x,q.y,s=7,c=pal[g],ec='none',alpha=.8,rasterized=True);a.set_aspect('equal',adjustable='box');a.spines[:].set_visible(False);a.set_xticks([]);a.set_yticks([]);a.set_title(g+' · '+str(len(q))+' cells ('+format(len(q)/len(d),'.1%')+')',fontsize=10)
    elif mode=='effect_table':
        d=checked(data,['label','estimate','lower','upper'],['estimate','lower','upper'])
        if d.label.duplicated().any() or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():raise ValueError('Unique supplied effects and valid bounds required')
        # One aligned reading table: identity, interval, numerical estimate.
        # A small four-row forest should not inherit a large scatter canvas.
        fig.clear();height=1.65+.34*len(d);width=7.7
        fig.set_size_inches(width,height);body=.34*len(d)
        a=_axis(fig,[.18,.68/height,.43,body/height]);y=np.arange(len(d))
        label_ax=_axis(fig,[.055,.68/height,.105,body/height])
        number_ax=_axis(fig,[.65,.68/height,.31,body/height])
        for axis in [a,label_ax,number_ax]:axis.set_ylim(len(d)-.5,-.5)
        for axis in [label_ax,number_ax]:axis.set_xlim(0,1);axis.axis('off')
        fig.text(.055,1-.17/height,textwrap.fill(title,74),fontsize=13,fontweight='bold',color='#283F4B',va='top')
        if axis_labels:fig.text(.055,1-.46/height,str(axis_labels[0]),fontsize=9,color='#687E88',va='top')
        header=(.68+body+.13)/height
        for x,text in [(.055,'Gene'),(.18,'log2 fold change'),(.65,'Estimate [95% interval]')]:
            fig.text(x,header,text,fontsize=9.5,fontweight='bold',color='#617A86')
        for i,row in enumerate(d.itertuples()):
            c=theme['roles']['positive'] if row.estimate>0 else theme['roles']['negative']
            if i%2==0:
                for axis in [a,label_ax,number_ax]:axis.axhspan(i-.5,i+.5,fc='#EDF4F5',ec='none',zorder=0)
            a.plot([row.lower,row.upper],[i,i],c=c,lw=2.4,alpha=.65,zorder=2,solid_capstyle='round')
            a.scatter([row.estimate],[i],c=c,s=43,ec='white',lw=.75,zorder=3)
            label_ax.text(0,i,str(row.label),fontsize=10,va='center',color='#294650')
            number_ax.text(.03,i,f'{row.estimate:+.2f}  [{row.lower:+.2f}, {row.upper:+.2f}]',fontsize=9.5,va='center',color='#294650')
        a.axvline(0,color='#91A4AE',lw=.8,ls=(0,(2,3)),zorder=1)
        a.set_yticks([]);a.spines[['left','top','right']].set_visible(False)
        a.spines['bottom'].set_color('#B9C8CE');a.tick_params(axis='x',labelsize=9)
        a.xaxis.set_major_locator(MaxNLocator(5));a.margins(x=.14)
        fig.text(.18,.18/height,'Points: supplied estimates  ·  Lines: supplied 95% intervals',fontsize=9,color='#687E88')
        for axis in fig.axes:axis._explicit_guide_layout=True
    elif mode=='unit_profile':
        d=checked(data,['sample_id','group','value'],['value'])
        if d.sample_id.duplicated().any() or (d.value<0).any() or not axis_labels:raise ValueError('Unique samples and explicit nonnegative count units required')
        fig.set_size_inches(7.5,max(4.5,len(d)*.31+1.5));a=_axis(fig,[.19,.16,.65,.65]);pal=group_palette(theme,list(d.group.unique()));yy=np.arange(len(d))
        for i,row in enumerate(d.itertuples()):
            a.axhspan(i-.45,i+.45,color=pal[row.group],alpha=.045,zorder=0);a.hlines(i,0,row.value,color=pal[row.group],alpha=.35,lw=2);a.scatter(row.value,i,c=pal[row.group],s=40,ec='white',lw=.6,zorder=2);a.text(row.value+max(d.value)*.025,i,format(row.value,'g'),fontsize=9,va='center',color='#3E5663')
        a.set_yticks(yy,d.sample_id);a.invert_yaxis();a.set(xlim=(0,max(d.value)*1.15),xlabel=axis_labels[0]);a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
        fig.legend(handles=[Patch(color=c,label=g) for g,c in pal.items()],loc='upper center',bbox_to_anchor=(.5,.91),ncols=len(pal),frameon=False,fontsize=9)
    stamp(fig,data,'integrated_'+mode,mode=mode,display_summary_only=True,ellipse_definition=ellipse_definition,scientific_acceptance=False)
    if presentation!='classic':
        from figure_study_publication import lock
        lock(fig)
    return apply_project_style(fig,theme)
