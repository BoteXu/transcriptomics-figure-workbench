"""WGCNA/hdWGCNA diagnostics and evidence views from frozen server results.

No soft-power selection, correlation, clustering, TOM, modules or hubs are fitted.
"""
import math,textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap,TwoSlopeNorm,to_rgba
from matplotlib.lines import Line2D
from figure_core import checked,stamp
from project_theme import group_palette,apply_project_style

def _label(x,n=22):return '\n'.join(textwrap.wrap(str(x),n,break_long_words=False))
def _clean(ax):
    ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,labelsize=10)
def _grid(data,a,b):
    if data.duplicated([a,b]).any() or len(data)!=data[a].nunique()*data[b].nunique():raise ValueError('Complete unique selected grid required')
def _context(c):
    required={'network_type','correlation_method','independent_unit','independent_n','module_version','source_version','selection'}
    if not isinstance(c,dict) or set(c)!=required or any(not isinstance(c[k],str) or not c[k].strip() for k in required-{'independent_n'}):raise ValueError('Complete frozen network and source context required')
    if c['network_type'] not in ['signed','unsigned','signed hybrid'] or type(c['independent_n']) is not int or c['independent_n']<1 or c['independent_unit'].casefold() in ['cell','cells','gene','genes','metacell','metacells','unknown']:raise ValueError('Declare the actual network type and biological independent units; genes/metacells do not increase donor n')

def _dual(fig,columns):
    cols=2 if columns=='auto' else columns
    if cols not in [1,2]:raise ValueError('Two complementary diagnostics support one or two columns')
    if cols==1:fig.set_size_inches(7,10)
    return fig.subplots(1 if cols==2 else 2,cols,squeeze=False).ravel()

def _tree(data,order):
    leaves=checked(data[data.record_type=='leaf'],['node_id','module','dynamic_module']);merges=checked(data[data.record_type=='merge'],['node_id','left','right','height'],['height'])
    if order is None:order=leaves.node_id.tolist()
    if len(order)<2 or len(order)>50000 or len(order)!=len(set(order)) or set(order)!=set(leaves.node_id) or leaves.node_id.duplicated().any() or merges.node_id.duplicated().any() or len(merges)!=len(leaves)-1 or set(leaves.node_id)&set(merges.node_id):raise ValueError('Complete unique leaves, merges and exact frozen leaf order required')
    x={g:i+.5 for i,g in enumerate(order)};h={g:0. for g in order};span={g:(i,i) for i,g in enumerate(order)};used=set();segments=[]
    for r in merges.itertuples():
        if r.left not in x or r.right not in x or r.left==r.right or r.left in used or r.right in used or r.node_id in x or r.height<=max(h[r.left],h[r.right]):raise ValueError('Invalid tree child, reuse, merge order or height')
        a,b=span[r.left],span[r.right]
        if a[1]+1!=b[0] and b[1]+1!=a[0]:raise ValueError('Frozen leaf order crosses tree branches')
        segments.extend([[(x[r.left],h[r.left]),(x[r.left],r.height)],[(x[r.left],r.height),(x[r.right],r.height)],[(x[r.right],r.height),(x[r.right],h[r.right])]])
        x[r.node_id]=(x[r.left]+x[r.right])/2;h[r.node_id]=r.height;span[r.node_id]=(min(a[0],b[0]),max(a[1],b[1]));used.update([r.left,r.right])
    if span[merges.iloc[-1].node_id]!=(0,len(order)-1):raise ValueError('Disconnected frozen hierarchy')
    return leaves.set_index('node_id').loc[order],segments,order

def plot_wgcna_view(data,theme,*,mode,title,context,leaf_order=None,module_order=None,selected_power=None,fit_reference=None,probability_kind='adjusted',coefficient_semantics='signed',matrix_definition='TOM',track_labels=('Dynamic modules','Merged modules'),columns='auto',preservation_guides=None,label_genes=(),value_limits=(-3,3)):
    """Dedicated network diagnostics, identities and result meanings; adaptive facets."""
    _context(context)
    modes={'soft_threshold','module_dendrogram','sample_tree','module_trait','membership_significance','tom','eigengene_network','eigengene_profiles','hub_connectivity','preservation','metacell_qc','module_activity'}
    if mode not in modes or not title:raise ValueError('Choose a documented WGCNA view and state the question')
    if coefficient_semantics not in ['signed','absolute'] or probability_kind not in ['raw','adjusted']:raise ValueError('Declare coefficient and probability semantics')
    if columns!='auto' and (type(columns) is not int or not 1<=columns<=6):raise ValueError('Use auto or one to six columns')
    if mode in ['sample_tree','module_dendrogram','module_trait','tom','eigengene_network','hub_connectivity'] and columns not in ['auto',1]:raise ValueError('This is one complete view; compose independent views for more columns')
    if module_order is not None and (not isinstance(module_order,(list,tuple)) or len(module_order)!=len(set(module_order)) or 'module' not in data or set(module_order)!=set(data.module.dropna())):raise ValueError('Module order must include every selected input module exactly once')
    fig=plt.figure(figsize=(10,6),layout='constrained')
    if mode=='soft_threshold':
        d=checked(data,['power','signed_fit','mean_connectivity'],['power','signed_fit','mean_connectivity'])
        if d.power.duplicated().any() or ((d.power<=0)|(d.power%1!=0)|(d.signed_fit<-1)|(d.signed_fit>1)|(d.mean_connectivity<0)).any() or selected_power not in set(d.power):raise ValueError('Supply valid candidate powers and an explicitly preselected observed power')
        if fit_reference is not None and (not isinstance(fit_reference,(int,float)) or not -1<=fit_reference<=1):raise ValueError('Declare the optional fit reference')
        axes=_dual(fig,columns)
        for ax,field,label in [(axes[0],'signed_fit','Supplied signed scale-free fit'),(axes[1],'mean_connectivity','Supplied mean connectivity')]:
            _clean(ax);q=d.sort_values('power');ax.plot(q.power,q[field],c='#B7CBD1',lw=1);ax.scatter(q.power,q[field],c='#218C8D',s=38,ec='white',lw=.5)
            chosen=q[q.power==selected_power];ax.scatter(chosen.power,chosen[field],c=theme['roles']['positive'],s=85,ec='white',lw=.8,zorder=4);ax.axvline(selected_power,c='#9AB2BA',lw=.8,ls='--');ax.set(xlabel='Candidate soft power',ylabel=label)
            ax.set_xticks(q.power if len(q)<=15 else q.power.iloc[::2]);ax.set_title('Topology fit' if field=='signed_fit' else 'Network connectivity',loc='left',fontsize=12,fontweight='bold')
        if fit_reference is not None:axes[0].axhline(fit_reference,c='#B48D70',lw=.9,ls='--')
        fig.legend(handles=[Line2D([],[],marker='o',ls='',c=theme['roles']['positive'],label='Preselected power '+str(selected_power)+' / no automatic selection')],loc='outside lower center',frameon=False,fontsize=10)
    elif mode in ['module_dendrogram','sample_tree']:
        l,segments,order=_tree(data,leaf_order);gs=fig.add_gridspec(3,1,height_ratios=[7,.45,.45],hspace=.04);ax=fig.add_subplot(gs[0]);_clean(ax)
        if len(track_labels)!=2 or mode=='sample_tree' and len(order)>context['independent_n']:raise ValueError('Two named tracks and valid sample independent n required')
        ax.add_collection(LineCollection(segments,colors='#6E8591',linewidths=.7,rasterized=len(order)>2000));ax.autoscale_view();ax.set(xlim=(0,len(order)),ylim=(0,max(float(data.height.dropna().max()),.1)*1.05),ylabel='Supplied merge height');ax.set_xticks([])
        identities=list(dict.fromkeys(l.dynamic_module.tolist()+l.module.tolist()));pal=group_palette(theme,identities)
        for i,field in enumerate(['dynamic_module','module']):
            a=fig.add_subplot(gs[i+1]);a.imshow(np.array([[to_rgba(pal[x]) for x in l[field]]]),aspect='auto',extent=(0,len(order),0,1));a.set_yticks([.5],[track_labels[i]]);a.tick_params(length=0);a.spines[:].set_visible(False)
            if i==1 and len(order)<=35:a.set_xticks(np.arange(len(order))+.5,order,rotation=90)
            else:a.set_xticks([])
        fig.legend(handles=[Line2D([],[],lw=6,c=c,label=x) for x,c in pal.items()],loc='outside lower center',ncols=min(5,len(pal)),frameon=False,fontsize=10)
    elif mode=='module_trait':
        d=checked(data,['module','trait','r','probability','n'],['r','probability','n']);_grid(d,'module','trait')
        if ((d.r.abs()>1)|(d.probability<0)|(d.probability>1)|(d.n<3)|(d.n%1!=0)|(d.n>context['independent_n'])).any():raise ValueError('Valid coefficients, probabilities and actual effective independent n required')
        modules=module_order or d.module.drop_duplicates().tolist();traits=d.trait.drop_duplicates().tolist()
        if set(modules)!=set(d.module) or len(modules)!=len(set(modules)):raise ValueError('Exact selected modules required')
        fig.set_size_inches(max(7,len(traits)*1.5+3),max(4.5,len(modules)*.7+2));ax=fig.subplots();_clean(ax);m=d.pivot(index='module',columns='trait',values='r').reindex(index=modules,columns=traits)
        cmap=LinearSegmentedColormap.from_list('module_trait',theme['continuous']['diverging']);im=ax.imshow(m,cmap=cmap,vmin=-1,vmax=1,aspect='auto')
        lookup=d.set_index(['module','trait']);prefix='q' if probability_kind=='adjusted' else 'p'
        for i,mo in enumerate(modules):
            for j,tr in enumerate(traits):
                r=lookup.loc[(mo,tr)];rgba=cmap((r.r+1)/2);luminance=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2];ax.text(j,i,f'{r.r:+.2f}\n{prefix} {r.probability:.2g} · n={int(r.n)}',ha='center',va='center',fontsize=10,color='white' if luminance<.43 else '#244858')
        ax.set_xticks(range(len(traits)),[_label(x,16) for x in traits]);ax.set_yticks(range(len(modules)),modules);ax.tick_params(length=0);ax.spines[:].set_visible(False);fig.colorbar(im,ax=ax,shrink=.75,label='Supplied '+context['correlation_method']+' r')
    elif mode in ['tom','eigengene_network']:
        d=checked(data,['a','b','value'],['value']);_grid(d,'a','b');order=leaf_order or d.a.drop_duplicates().tolist()
        if len(order)!=len(set(order)) or set(d.a)!=set(order) or set(d.b)!=set(order):raise ValueError('Exactly matching row/column IDs and frozen order required')
        matrix=d.pivot(index='a',columns='b',values='value').reindex(index=order,columns=order).to_numpy()
        if not np.allclose(matrix,matrix.T,atol=1e-8):raise ValueError('WGCNA TOM/eigengene matrices must be explicitly symmetric')
        if mode=='tom':
            if matrix_definition not in ['TOM','adjacency','1 - TOM'] or (matrix<0).any() or (matrix>1).any():raise ValueError('Declare TOM, adjacency or 1 - TOM with actual [0,1] values')
            cmap=LinearSegmentedColormap.from_list('tom',['#F5FAF8','#B9D8D0','#318481','#24546B']);limits=(0,1)
        else:
            if np.abs(matrix).max()>1:raise ValueError('Valid eigengene correlations required')
            cmap=LinearSegmentedColormap.from_list('me',theme['continuous']['diverging']);limits=(-1,1);matrix_definition='Eigengene correlation'
        fig.set_size_inches(max(6,min(16,4+len(order)*.16)),max(5,min(16,3+len(order)*.16)));ax=fig.subplots();im=ax.imshow(matrix,cmap=cmap,vmin=limits[0],vmax=limits[1],interpolation='nearest');show=len(order)<=35
        ax.set_xticks(range(len(order)) if show else [],order if show else [],rotation=90);ax.set_yticks(range(len(order)) if show else [],order if show else []);ax.tick_params(length=0);ax.spines[:].set_visible(False);fig.colorbar(im,ax=ax,shrink=.7,label='Supplied '+matrix_definition)
    elif mode=='membership_significance':
        d=checked(data,['gene','module','kME','GS'],['kME','GS'])
        if d.duplicated(['gene','module']).any() or (d[['kME','GS']].abs()>1).any().any() or coefficient_semantics=='absolute' and (d[['kME','GS']]<0).any().any():raise ValueError('Declare signed or upstream absolute MM/GS; no automatic absolute-value conversion')
        modules=module_order or d.module.drop_duplicates().tolist();pal=group_palette(theme,modules);cols=min(3,len(modules)) if columns=='auto' else columns;rows=math.ceil(len(modules)/cols);fig.set_size_inches(cols*3.7,rows*3.8+1)
        from figure_workbench.responsive import facet_slots
        slots=facet_slots(fig,len(modules),rows,cols)
        if set(label_genes)-set(d.gene) or len(label_genes)>12:raise ValueError('Select at most twelve actual gene labels')
        for i,m in enumerate(modules):
            ax=fig.add_subplot(slots[i]);_clean(ax);q=d[d.module==m];ax.scatter(q.kME,q.GS,c=pal[m],s=15,alpha=.55,ec='none',rasterized=True);ax.set(xlabel='Supplied '+coefficient_semantics+' kME / MM',ylabel='Supplied '+coefficient_semantics+' GS',xlim=(0 if coefficient_semantics=='absolute' else -1,1),ylim=(0 if coefficient_semantics=='absolute' else -1,1));ax.set_title(m+' · '+str(len(q))+' genes',loc='left',fontsize=11,fontweight='bold')
            for r in q[q.gene.isin(label_genes)].itertuples():ax.annotate(r.gene,(r.kME,r.GS),xytext=(5,5),textcoords='offset points',fontsize=9)
    elif mode=='eigengene_profiles':
        d=checked(data,['unit','module','group','value'],['value'])
        if d.duplicated(['unit','module']).any() or d.unit.nunique()>context['independent_n']:raise ValueError('One frozen donor-level eigengene per explicit unit/module required')
        modules=module_order or d.module.drop_duplicates().tolist();groups=d.group.drop_duplicates().tolist();pal=group_palette(theme,groups);cols=min(3,len(modules)) if columns=='auto' else columns;rows=math.ceil(len(modules)/cols);fig.set_size_inches(cols*3.6,rows*3.8+1)
        from figure_workbench.responsive import facet_slots
        slots=facet_slots(fig,len(modules),rows,cols)
        for j,m in enumerate(modules):
            ax=fig.add_subplot(slots[j]);_clean(ax);q=d[d.module==m]
            for i,g in enumerate(groups):
                z=q[q.group==g];ax.boxplot([z.value],positions=[i],widths=.38,patch_artist=True,showfliers=False,boxprops=dict(fc=pal[g]+'40',ec=pal[g]),medianprops=dict(c=pal[g]));xx=i+((np.arange(len(z))*.618%1)-.5)*.23;ax.scatter(xx,z.value,c=pal[g],s=30,ec='white',lw=.4,zorder=3)
            ax.set_xticks(range(len(groups)),groups);ax.set_ylabel('Supplied oriented eigengene');ax.set_title(m,loc='left',fontweight='bold',fontsize=11)
    elif mode=='hub_connectivity':
        d=checked(data,['gene','module','kWithin','kME'],['kWithin','kME'])
        if d.gene.duplicated().any() or (d.kWithin<0).any() or (d.kME.abs()>1).any():raise ValueError('Exact preselected genes and valid supplied connectivity/MM required')
        pal=group_palette(theme,d.module.drop_duplicates().tolist());fig.set_size_inches(8,max(4,len(d)*.38+1.6));ax=fig.subplots();_clean(ax)
        for i,r in enumerate(d.itertuples()):ax.hlines(i,0,r.kWithin,colors=pal[r.module],lw=2,alpha=.55);ax.scatter(r.kWithin,i,c=pal[r.module],s=50,ec='white',lw=.5);ax.annotate(f'kME {r.kME:+.2f}',(r.kWithin,i),xytext=(8,0),textcoords='offset points',va='center',fontsize=10)
        ax.set_yticks(range(len(d)),d.gene);ax.invert_yaxis();ax.set_xlim(0,d.kWithin.max()*1.35);ax.set_xlabel('Supplied intramodular connectivity kWithin');ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
    elif mode=='preservation':
        d=checked(data,['module','size','Zsummary','medianRank'],['size','Zsummary','medianRank'])
        if d.module.duplicated().any() or ((d['size']<1)|(d['size']%1!=0)|(d.medianRank<=0)).any():raise ValueError('Unique module size, Zsummary and medianRank required')
        pal=group_palette(theme,d.module.tolist());axes=_dual(fig,columns)
        for ax,col,label in [(axes[0],'Zsummary','Supplied preservation Zsummary'),(axes[1],'medianRank','Supplied medianRank / lower is stronger')]:
            _clean(ax)
            for r in d.itertuples():ax.scatter(r.size,getattr(r,col),s=65,c=pal[r.module],ec='white',lw=.6,label=r.module)
            ax.set(xlabel='Module size / genes',ylabel=label)
        if preservation_guides is not None:
            if not isinstance(preservation_guides,(list,tuple)) or any(not isinstance(x,(int,float)) for x in preservation_guides):raise ValueError('Explicit source-defined preservation guides required')
            for v in preservation_guides:axes[0].axhline(v,c='#ADBFC6',lw=.8,ls='--')
        fig.legend(*axes[0].get_legend_handles_labels(),loc='outside lower center',ncols=min(5,len(d)),frameon=False,fontsize=10)
    elif mode=='metacell_qc':
        d=checked(data,['metacell','donor','celltype','n_cells','n_shared'],['n_cells','n_shared'])
        if d.metacell.duplicated().any() or ((d.n_cells<1)|(d.n_shared<0)|(d.n_shared>d.n_cells)|(d.n_cells%1!=0)|(d.n_shared%1!=0)).any() or d.donor.nunique()>context['independent_n']:raise ValueError('Explicit donor-nested metacells, actual counts and overlap required')
        pal=group_palette(theme,d.celltype.drop_duplicates().tolist());donors=d.donor.drop_duplicates().tolist();axes=_dual(fig,columns)
        for a in axes:_clean(a)
        for i,donor in enumerate(donors):
            q=d[d.donor==donor];bottom=0
            for celltype,c in pal.items():n=int((q.celltype==celltype).sum());axes[0].barh(i,n,left=bottom,color=c,height=.65,label=celltype if i==0 else None);bottom+=n
        axes[0].set_yticks(range(len(donors)),donors);axes[0].invert_yaxis();axes[0].set_xlabel('Supplied metacells per donor')
        for g,c in pal.items():q=d[d.celltype==g];axes[1].scatter(q.n_cells,q.n_shared/q.n_cells,c=c,s=27,alpha=.65,ec='white',lw=.4)
        axes[1].set(xlabel='Cells per metacell',ylabel='Shared cells / constituent cells',ylim=(-.02,1.02));fig.legend(*axes[0].get_legend_handles_labels(),loc='outside lower center',ncols=min(5,len(pal)),frameon=False,fontsize=10)
    elif mode=='module_activity':
        d=checked(data,['cell','module','x','y','value'],['x','y','value'])
        if d.duplicated(['cell','module']).any():raise ValueError('Unique stored cell/module activity values required')
        modules=module_order or d.module.drop_duplicates().tolist();ref=d[d.module==modules[0]].set_index('cell')[['x','y']].sort_index()
        for m in modules:
            q=d[d.module==m].set_index('cell')[['x','y']].sort_index()
            if not q.index.equals(ref.index) or not np.array_equal(q.to_numpy(),ref.to_numpy()):raise ValueError('All module maps require the same cells and exact stored coordinates')
        if len(value_limits)!=2 or not all(np.isfinite(x) for x in value_limits) or not value_limits[0]<0<value_limits[1] or ((d.value<value_limits[0])|(d.value>value_limits[1])).any():raise ValueError('A common declared signed activity scale containing every value is required')
        cols=min(3,len(modules)) if columns=='auto' else columns;rows=math.ceil(len(modules)/cols);fig.set_size_inches(cols*3.5,rows*3.5+1);axes=[];cmap=LinearSegmentedColormap.from_list('module_activity',theme['continuous']['diverging'])
        from figure_workbench.responsive import facet_slots
        slots=facet_slots(fig,len(modules),rows,cols)
        for i,m in enumerate(modules):
            ax=fig.add_subplot(slots[i]);q=d[d.module==m];art=ax.scatter(q.x,q.y,c=q.value,cmap=cmap,vmin=value_limits[0],vmax=value_limits[1],s=8,ec='none',rasterized=True);ax.set_aspect('equal',adjustable='box');ax.spines[:].set_visible(False);ax.set_xticks([]);ax.set_yticks([]);ax.set_title(m,fontsize=11,fontweight='bold');axes.append(ax)
        fig.colorbar(art,ax=axes,shrink=.7,label='Supplied oriented module activity')
    fig.suptitle(title+'\n'+context['network_type']+' network · '+str(context['independent_n'])+' '+context['independent_unit']+' · frozen results',fontsize=14,fontweight='bold')
    fig.get_layout_engine().set(h_pad=.18,w_pad=.25,hspace=.16,wspace=.14)
    for ax in fig.axes:ax._explicit_guide_layout=True
    stamp(fig,data,'wgcna_'+mode,mode=mode,title=title,context=context,leaf_order=leaf_order,module_order=module_order,selected_power=selected_power,fit_reference=fit_reference,probability_kind=probability_kind,coefficient_semantics=coefficient_semantics,matrix_definition=matrix_definition,track_labels=track_labels,columns=columns,preservation_guides=preservation_guides,label_genes=list(label_genes),analysis_performed=False)
    return apply_project_style(fig,theme)
