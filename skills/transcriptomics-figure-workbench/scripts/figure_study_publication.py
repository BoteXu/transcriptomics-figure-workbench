"""Publication extensions for existing frozen-result renderers.

Only descriptive display arithmetic is performed: counts, fractions and order.
No model, density, embedding, uncertainty or enrichment is fitted here.
"""
import math,textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize,TwoSlopeNorm,to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch,Rectangle
from matplotlib.ticker import PercentFormatter,MaxNLocator
from figure_core import stamp
from project_theme import group_palette

INK='#294553';MUTED='#6B808A';GRID='#E5ECEF'


def quiet(ax,grid=None):
    ax.spines[['top','right']].set_visible(False)
    for s in ['left','bottom']:ax.spines[s].set_color('#B3C2C9');ax.spines[s].set_linewidth(.7)
    ax.tick_params(colors=INK,labelsize=10,length=3,width=.6)
    if grid:ax.grid(axis=grid,color=GRID,lw=.6);ax.set_axisbelow(True)


def lock(fig):
    for ax in fig.axes:
        ax._explicit_guide_layout=True
        for text in [ax.title,ax.xaxis.label,ax.yaxis.label,*ax.texts,*ax.get_xticklabels(),*ax.get_yticklabels()]:
            if text.get_color() in ['black','k','#000000']:text.set_color(INK)
    return fig


def heading(fig,title,subtitle='',x=.07):
    fig.text(x,.963,title,ha='left',va='top',fontsize=15,color=INK,fontweight='bold')
    if subtitle:fig.text(x,.917,subtitle,ha='left',va='top',fontsize=10,color=MUTED)


def qc_grid(data,theme,title,cloud_shapes,observation_unit):
    from figure_raincloud_geometry import draw_supplied_raincloud
    groups=list(data.group.unique());metrics=list(data.metric.unique()) if 'metric' in data else ['Expression']
    if len(groups)>6:raise ValueError('Use scoped QC pages beyond six conditions')
    facets=[]
    for group in groups:
        samples=list(data.loc[data.group==group,'sample'].unique())
        chunks=math.ceil(len(samples)/8)
        for indices in np.array_split(np.arange(len(samples)),chunks):facets.append((group,[samples[int(i)] for i in indices]))
    nc=min(3,len(groups));blocks=math.ceil(len(facets)/nc);nr=len(metrics)*blocks
    fig=plt.figure(figsize=(max(7.5,4.15*nc),1.25+2.7*nr))
    heading(fig,title,str(data['sample'].nunique())+' samples · complete supplied observations · shared metric axes')
    gs=fig.add_gridspec(nr,nc,left=.09,right=.98,bottom=.14,top=.77 if nr==1 else min(.86,1-1.3/fig.get_figheight()),hspace=.78,wspace=.18)
    for mi,metric in enumerate(metrics):
        d=data if 'metric' not in data else data[data.metric==metric];vmin=float(d.value.min());vmax=float(d.value.max());pad=max((vmax-vmin)*.1,.01)
        for gi,(group,samples) in enumerate(facets):
            row=mi*blocks+gi//nc;col=gi%nc;a=fig.add_subplot(gs[row,col]);quiet(a,'y')
            q=d[(d.group==group)&d['sample'].isin(samples)];pal=group_palette(theme,groups)
            for i,s in enumerate(samples):
                vals=q.loc[q['sample']==s,'value'].to_numpy()
                if metric not in cloud_shapes or s not in cloud_shapes[metric]:raise ValueError('Every QC sample requires its own frozen cloud')
                draw_supplied_raincloud(a,i,vals,pal[group],cloud_shapes[metric][s],point_size=7)
            a.set(xlim=(-.55,len(samples)-.5),ylim=(vmin-pad,vmax+pad))
            a.set_xticks(range(len(samples)),[s+'\n'+str(sum(q['sample']==s)) for s in samples],rotation=0)
            a.set_xlabel(observation_unit.capitalize()+' per sample',fontsize=10)
            if col==0:a.set_ylabel(metric)
            else:a.tick_params(labelleft=False)
            a.set_title(group+' · '+str(len(samples))+' samples',loc='left',color=pal[group],fontweight='bold',pad=11)
    stamp(fig,data,'integrated_qc',mode='qc',display_summary_only=True,cloud_definition='supplied per-metric/sample; no density fit',observation_unit=observation_unit,condition_facets=True,all_observations=True)
    return lock(fig)


def coverage(data,theme,title,label):
    names=list(data.group.unique());pal=group_palette(theme,names);n=len(data);height=max(4,1.75+.29*n)
    fig=plt.figure(figsize=(8,height));heading(fig,title,str(n)+' supplied units · all counts retained')
    a=fig.add_axes([.15,.17,.64,.61]);quiet(a,'x');y=np.arange(n);maximum=float(data.value.max())
    for i,r in enumerate(data.itertuples()):
        c=pal[r.group];a.barh(i,r.value,color=c,alpha=.16,height=.57,lw=0)
        a.plot([0,r.value],[i,i],c=c,alpha=.55,lw=1.5);a.scatter(r.value,i,s=36,c=c,ec='white',lw=.7,zorder=3)
        a.annotate(format(r.value,',g'),(r.value,i),xytext=(8,0),textcoords='offset points',va='center',color=c,fontweight='bold')
    a.set_yticks(y,data.sample_id);a.invert_yaxis();a.set(xlim=(0,maximum*1.18),xlabel=label);a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
    fig.legend(handles=[Patch(fc=pal[g],label=g+' · '+str(sum(data.group==g))) for g in names],loc='upper right',bbox_to_anchor=(.98,.85),ncols=len(names),frameon=False)
    stamp(fig,data,'integrated_unit_profile',mode='unit_profile',all_units_retained=True,count_units=label)
    return lock(fig)


def enrichment(data,theme,mode,title,contrast,tested,query,nes_limits,effect_limits):
    t=data[data.record_type=='term'];names=list(t.term.unique());families=list(t.family.unique());pal=group_palette(theme,families)
    width=max(8.9,max(map(len,names))*.064+7.1);height=max(4.4,2.25+.37*len(names));fig=plt.figure(figsize=(width,height))
    heading(fig,title,contrast+' · '+('ranked genes '+str(tested) if query is None else str(query)+' query genes / '+str(tested)+' tested genes'),.045)
    bottom=1.15/height;top=1-1.22/height;body=top-bottom
    if mode!='gene_support':
        a=fig.add_axes([.265,bottom,.36,body]);meta=fig.add_axes([.68,bottom,.29,body],sharey=a);meta.axis('off')
        a.set_ylim(len(names)-.5,-.5);a.set_yticks(range(len(names)),[textwrap.fill(x,27) for x in names]);a.tick_params(axis='y',length=0,pad=13);quiet(a,'x');a.spines['left'].set_visible(False)
        score=t.NES.to_numpy() if mode=='gsea_comparison' else t.ratio.to_numpy()
        cmap=LinearSegmentedColormap.from_list('publication_strength',['#B8D8D4','#438F91','#22576D']);strength=max(float((-np.log10(t.padj)).max()),1)
        for i,r in enumerate(t.itertuples()):
            if i%2==0:
                for ax in [a,meta]:ax.axhspan(i-.5,i+.5,fc='#F1F6F7',zorder=0)
            c=(theme['roles']['positive'] if score[i]>=0 else theme['roles']['negative']) if mode=='gsea_comparison' else cmap(float(-np.log10(r.padj)/strength))
            a.plot([0,score[i]],[i,i],color=c,alpha=.35,lw=2,zorder=1);a.scatter(score[i],i,s=72,fc=c if r.padj<=.05 else 'white',ec=c,lw=1.1,zorder=3)
            a.scatter(-.045,i,marker='s',s=20,c=pal[r.family],transform=a.get_yaxis_transform(),clip_on=False)
            first=f'{r.NES:+.2f}' if mode=='gsea_comparison' else str(int(r.count))
            meta.text(.02,i,first,va='center',color=INK);meta.text(.37,i,format(r.padj,'.3g'),va='center',color=INK);meta.text(.70,i,r.family.removesuffix(' theme'),va='center',color=MUTED)
        a.set_title('Normalized enrichment score' if mode=='gsea_comparison' else 'Overlap / query gene ratio',loc='left',pad=20,fontweight='bold',color=INK)
        for x,label in [(.02,'NES' if mode=='gsea_comparison' else 'Genes'),(.37,'FDR'),(.70,'Theme')]:meta.text(x,1.055,label,transform=meta.transAxes,color=MUTED,fontweight='bold')
        if mode=='gsea_comparison':a.axvline(0,c='#A4B9C1',ls=(0,(2,3)),lw=.8);a.set_xlim(*nes_limits);a.set_xlabel('NES · positive and negative direction');a.xaxis.set_major_locator(MaxNLocator(5))
        else:
            a.set_xlim(0,max(score)*1.12);a.xaxis.set_major_locator(MaxNLocator(4));a.xaxis.set_major_formatter(PercentFormatter(1,decimals=0));a.set_xlabel('Gene ratio')
            cax=fig.add_axes([.265,.085,.30,.017]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,strength),cmap=cmap),cax=cax,orientation='horizontal');cb.set_label('−log10 FDR');cb.ax.tick_params(length=2)
        fig.text(.68,.27/height,'Filled: FDR ≤ 0.05\nOpen: FDR > 0.05',color=MUTED,fontsize=9)
    else:
        m=data[data.record_type=='membership'];genes=list(m.gene.unique());effects=data[data.record_type=='gene'].set_index('gene').effect.loc[genes]
        matrix=m.pivot(index='term',columns='gene',values='member').loc[names,genes]
        a=fig.add_axes([.27,bottom,.40,body]);a.set(xlim=(-.5,len(genes)-.5),ylim=(len(names)-.5,-.5));a.set_yticks(range(len(names)),[textwrap.fill(x,27) for x in names]);a.set_xticks(range(len(genes)),genes,rotation=0)
        a.tick_params(length=0,pad=10);a.spines[:].set_visible(False)
        cmap=LinearSegmentedColormap.from_list('publication_effect',theme['continuous']['diverging']);norm=TwoSlopeNorm(vmin=effect_limits[0],vcenter=0,vmax=effect_limits[1])
        for i in range(len(names)):
            for j,g in enumerate(genes):
                member=bool(matrix.iloc[i,j]);a.add_patch(Rectangle((j-.44,i-.39),.88,.78,fc=cmap(norm(effects[g])) if member else '#F0F4F5',ec='white',lw=.8))
                a.text(j,i,'●' if member else '–',ha='center',va='center',fontsize=11,color=INK if member else '#A8B7BF')
        a.set_title('Selected gene membership',loc='left',pad=23,fontweight='bold',color=INK)
        meta=fig.add_axes([.73,bottom,.23,body],sharey=a);meta.axis('off')
        for i,r in enumerate(t.itertuples()):meta.text(.0,i,str(int(r.count)),va='center',color=INK);meta.text(.4,i,format(r.padj,'.3g'),va='center',color=MUTED)
        meta.text(0,1.06,'Overlap',transform=meta.transAxes,fontweight='bold',color=MUTED);meta.text(.4,1.06,'FDR',transform=meta.transAxes,fontweight='bold',color=MUTED)
        for j,g in enumerate(genes):a.text(j,-.82,f'{effects[g]:+.2f}',ha='center',color=INK,fontweight='bold')
        cax=fig.add_axes([.73,.105,.22,.016]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal');cb.set_label('Gene log2 effect');cb.set_ticks([effect_limits[0],0,effect_limits[1]])
        fig.text(.27,.28/height,'Top: gene effects · ● member · – absent',color=MUTED,fontsize=9)
    stamp(fig,data,'enrichment_story',mode=mode,support_contrast=contrast,tested_size=tested,query_size=query,presentation='publication',selected_membership_in_companion=mode!='gene_support',complete_selected_membership=True,analysis_performed=False)
    return lock(fig)


def annotated_matrix(data,mat,groups,blocks,group_colors,block_colors,*,value_label,title,scale_type,colors,xlabels,ylabels,correlation=False):
    from indexed_alignment import bind_index_axes
    nr,nc=mat.shape;width=max(7.1,nc*.32+2.2);height=width*1.18 if correlation else max(5.8,nr*.215+2.1)
    fig=plt.figure(figsize=(width,height));heading(fig,title,'Unique sample pairs' if correlation else str(nr)+' selected features · '+str(nc)+' samples')
    left=.17;right=.95;bottom=.21;top=.79
    ax=fig.add_axes([left,bottom,right-left,top-bottom]);strip=fig.add_axes([left,top+.015,right-left,.018]);side=fig.add_axes([left-.02,bottom,.012,top-bottom])
    values=mat.to_numpy();extent=max(float(np.abs(values).max()),1e-9)
    if correlation:
        if list(mat.index)!=list(mat.columns) or not np.array_equal(values,values.T):raise ValueError('A triangular correlation view requires exactly symmetric ordered samples')
        if (np.abs(values)>1).any() or not np.allclose(np.diag(values),1,rtol=0,atol=1e-12):raise ValueError('Correlation coefficients require bounds [-1, 1] and a unit diagonal')
        display=np.ma.masked_where(np.triu(np.ones_like(values,dtype=bool),0),values)
    else:
        if scale_type!='signed' and values.min()<0:raise ValueError('A nonnegative sequential matrix cannot clip negative values; use a signed scale')
        display=values
    cmap=LinearSegmentedColormap.from_list('publication_matrix',colors);norm=TwoSlopeNorm(vmin=-extent,vcenter=0,vmax=extent) if scale_type=='signed' else Normalize(float(values.min()) if correlation else 0,float(values.max()))
    im=ax.imshow(display,cmap=cmap,norm=norm,aspect='auto',interpolation='nearest');ax.spines[:].set_visible(False)
    ax.set_xticks(range(nc),xlabels,rotation=45,ha='right');ax.set_yticks(range(nr),ylabels);ax.tick_params(length=0,pad=10);ax.tick_params(axis='y',pad=17)
    strip.imshow(np.array([[to_rgba(group_colors[g]) for g in groups]]),aspect='auto');strip.axis('off');side.imshow(np.array([[to_rgba(block_colors[g])] for g in blocks]),aspect='auto');side.axis('off')
    bind_index_axes(fig,ax,strip,'x',list(mat.columns));bind_index_axes(fig,ax,side,'y',list(mat.index))
    if correlation and nr<=18:
        for i in range(nr):
            for j in range(i):ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',fontsize=8.2,color='white' if norm(values[i,j])>.65 else INK)
    for i in range(1,nr):
        if blocks.iloc[i]!=blocks.iloc[i-1]:ax.axhline(i-.5,c='white',lw=2)
    for i in range(1,nc):
        if groups.iloc[i]!=groups.iloc[i-1]:ax.axvline(i-.5,c='white',lw=2)
    cax=fig.add_axes([.46,.077,.39,.017]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label(value_label,labelpad=4);cb.ax.tick_params(length=2)
    handles=[Patch(fc=group_colors[g],label=g) for g in dict.fromkeys(groups)]
    if not correlation:handles += [Patch(fc=block_colors[g],label=g) for g in dict.fromkeys(blocks)]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.165,.885),ncols=2 if correlation else 4,frameon=False,handlelength=1.0,columnspacing=1.4)
    if correlation:
        ax.text(.98,.98,'Unique pairs · diagonal r = 1 omitted',transform=ax.transAxes,ha='right',va='top',color=MUTED)
        summaries=[];g=list(groups)
        for name in dict.fromkeys(g):
            vals=[values[i,j] for i in range(nr) for j in range(i) if g[i]==g[j]==name]
            if vals:summaries.append((name,vals))
        vals=[values[i,j] for i in range(nr) for j in range(i) if g[i]!=g[j]]
        if vals:summaries.append(('Between groups',vals))
        for i,(name,vals) in enumerate(summaries):ax.text(.98,.87-i*.11,name+'  '+str(len(vals))+' pairs\nmedian '+format(np.median(vals),'.2f')+' · range '+format(min(vals),'.2f')+'–'+format(max(vals),'.2f'),transform=ax.transAxes,ha='right',va='top',color=MUTED,fontsize=8.5)
    return lock(fig)


def composition(data,palette,types_palette,cloud_shapes,unit_label,ncols='auto',nrows=None,panel_width=2.8,panel_height=2.9):
    from figure_workbench.responsive import grid_shape,facet_slots
    from figure_raincloud_geometry import draw_supplied_raincloud
    types=list(data.celltype.unique());groups=list(data.group.unique());samples=list(data['sample'].unique());rows,cols=grid_shape(len(types),ncols,nrows)
    width=max(8.8,cols*panel_width,len(samples)*.36+4.4);height=4.3+rows*panel_height
    fig=plt.figure(figsize=(width,height));heading(fig,'Cell composition across donors','One independent donor per bar and point · denominator: all supplied cells within that donor')
    if rows>2:
        fig.texts[0].set_y(1-.23/height);fig.texts[1].set_y(1-.65/height)
    a=fig.add_axes([.09,1-3.25/height,.85,1.55/height]);quiet(a);bottom=np.zeros(len(samples));mat=data.pivot(index='sample',columns='celltype',values='count').loc[samples,types];total=mat.sum(axis=1)
    for t in types:
        v=mat[t].to_numpy()/total.to_numpy();a.bar(range(len(samples)),v,bottom=bottom,color=types_palette[t],width=.82,ec='white',lw=.35);bottom+=v
    a.set(xlim=(-.7,len(samples)-.3),ylim=(0,1),ylabel='Within-donor\ncell fraction');a.yaxis.set_major_formatter(PercentFormatter(1));a.set_xticks(range(len(samples)),samples,rotation=45,ha='right')
    cond=data.drop_duplicates('sample').set_index('sample').loc[samples,'group'];a.scatter(range(len(samples)),[1.055]*len(samples),s=26,marker='s',c=[palette[x] for x in cond],clip_on=False)
    for g in groups:
        indices=[i for i,s in enumerate(samples) if cond[s]==g]
        a.text(float(np.mean(indices)),1.14,g+' · '+str(len(indices))+' donors',transform=a.get_xaxis_transform(),ha='center',color=palette[g],fontweight='bold')
    fig.legend(handles=[Patch(fc=types_palette[t],label=t) for t in types],loc='upper left',bbox_to_anchor=(.09,1-1.12/height),ncols=min(5,len(types)),frameon=False)
    for i,(t,slot) in enumerate(zip(types,facet_slots(fig,len(types),rows,cols,left=.09,right=.96,bottom=.085,top=1-4.1/height,hspace=.55,wspace=.30))):
        ax=fig.add_subplot(slot);quiet(ax,'y');q=data[data.celltype==t]
        for gi,g in enumerate(groups):
            part=q[q.group==g];vals=(part['count']/part['sample'].map(total)).to_numpy()
            draw_supplied_raincloud(ax,gi,vals,palette[g],cloud_shapes[t][g],point_size=23)
        ax.set_xticks(range(len(groups)),[g+'\nn='+str(sum(q.group==g)) for g in groups]);ax.set(xlim=(-.5,len(groups)-.45),ylim=(0,min(1,max(.05,float((data['count']/data['sample'].map(total)).max())*1.14))))
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_title(t,loc='left',fontweight='bold',color=types_palette[t]);ax.set_ylabel('Donor cell fraction' if i%cols==0 else '')
        if i%cols:ax.tick_params(labelleft=False)
    stamp(fig,data,'composition_panels',presentation='publication',all_donors=True,all_celltypes=True,denominator='all supplied celltype counts within each donor; no pooling',clouds='supplied shapes; no KDE or inferential intervals',unit_label=unit_label)
    return lock(fig)


def matrix_evidence(data,theme,p,title,scope):
    labels=list(data.label.unique());cols=list(data.series.unique());mat=data.pivot(index='label',columns='series',values='value').loc[labels,cols];v=mat.to_numpy()
    if len(data)!=len(labels)*len(cols) or data.duplicated(['label','series']).any():raise ValueError('A complete unique evidence matrix is required')
    design=p['matrix_semantics']=='design'
    if design and not set(np.unique(v))<={0,1}:raise ValueError('Binary design indicators only')
    if not design and ((v<0).any() or (v%1!=0).any()):raise ValueError('Cell support requires exact nonnegative integers')
    nr,nc=v.shape;fig=plt.figure(figsize=(max(7.6,nc*.45+3),max(4.7,nr*.30+2)))
    heading(fig,title,scope)
    a=fig.add_axes([.22,.25,.58,.55]);a.spines[:].set_visible(False);a.tick_params(length=0,pad=9)
    if design:
        a.set(xlim=(-.5,nc-.5),ylim=(nr-.5,-.5));a.set_xticks(range(nc),cols);a.set_yticks(range(nr),labels)
        for i in range(nr):
            for j in range(nc):a.scatter(j,i,s=135,marker='s',fc=theme['roles']['primary'] if v[i,j] else '#EDF3F5',ec='white',lw=1);a.text(j,i,str(int(v[i,j])),ha='center',va='center',color='white' if v[i,j] else '#71858F')
        a.grid(axis='y',color=GRID,lw=.4);a.set_axisbelow(True)
        if not p.get('reference_definition'):raise ValueError('State the design reference coding explicitly')
        fig.text(.22,.15,'Reference: '+p['reference_definition']+'; 0 = absent, 1 = present',fontsize=9,color=MUTED)
    else:
        cmap=LinearSegmentedColormap.from_list('support',theme['continuous']['sequential']);im=a.imshow(v,cmap=cmap,vmin=0,vmax=v.max(),aspect='auto')
        for i in range(nr):
            for j in range(nc):a.text(j,i,str(int(v[i,j])),ha='center',va='center',color='white' if v[i,j]>.65*v.max() else INK)
        a.set_yticks(range(nr),labels)
        aliases=p.get('column_aliases',{});a.set_xticks(range(nc),[aliases.get(x,x)+'\n'+str(int(v[:,j].sum())) for j,x in enumerate(cols)])
        fig.text(.22,.14,'Donor ID / cells per donor',color=MUTED,fontsize=9)
        for i in range(nr):a.text(1.04,i/(-nr)+1-.5/nr,str(int(v[i].sum())),transform=a.transAxes,va='center',color=theme['roles']['primary'],fontweight='bold')
        fig.text(.83,.825,'Total',fontsize=10,color=MUTED)
        cax=fig.add_axes([.55,.085,.25,.016]);cb=fig.colorbar(im,cax=cax,orientation='horizontal');cb.set_label('Cells per donor / identity')
    annotations=p.get('sample_annotations')
    if annotations:
        ids=labels if design else cols
        if set(annotations)!=set(ids) or any(set(x)!={'condition','batch'} for x in annotations.values()):raise ValueError('Complete explicit condition/batch annotations required')
        conditions=list(dict.fromkeys(annotations[x]['condition'] for x in ids));pal=group_palette(theme,conditions)
        if design:
            for i,x in enumerate(ids):a.scatter(-.18,i,c=pal[annotations[x]['condition']],marker='s',s=27,transform=a.get_yaxis_transform(),clip_on=False)
        else:
            pos=a.get_position();strip=fig.add_axes([pos.x0,pos.y1+.018,pos.width,.016]);strip.imshow(np.array([[to_rgba(pal[annotations[x]['condition']]) for x in ids]]),aspect='auto');strip.axis('off')
        fig.legend(handles=[Patch(fc=pal[x],label=x) for x in conditions],loc='upper right',bbox_to_anchor=(.86,.90),ncols=len(conditions),frameon=False)
    stamp(fig,data,'transcriptomic_chapter',panels=[p],title=title,scope_note=scope,presentation='publication',analysis_performed=False,all_matrix_cells_retained=True)
    return lock(fig)


def batch_coverage(data,theme,title,identities,identity_order=None):
    if set(identities)!=set(data.cell_id) or data.cell_id.duplicated().any():raise ValueError('Reviewed identity mapping must match every displayed cell exactly')
    groups=list(data.group.unique());types=list(dict.fromkeys(identities.values())) if identity_order is None else list(identity_order)
    if len(types)!=len(set(types)) or set(types)!=set(identities.values()):raise ValueError('Identity order must retain every mapped cell category')
    pal=group_palette(theme,groups);tp=group_palette(theme,types);n=len(groups)
    if n>6:raise ValueError('Use scoped batch pages beyond six batches')
    nc=min(3,n);nr=math.ceil(n/nc);fig=plt.figure(figsize=(max(8,nc*3),nr*2.8+3.35));heading(fig,title,'Stored coordinates · all cells retained in every background')
    gs=fig.add_gridspec(nr,nc,left=.06,right=.97,bottom=.43,top=.82,hspace=.33,wspace=.14)
    bounds=[data.x.min(),data.x.max(),data.y.min(),data.y.max()]
    for i,g in enumerate(groups):
        a=fig.add_subplot(gs[i//nc,i%nc]);q=data[data.group==g];a.scatter(data.x,data.y,s=6,c='#DEE6E9',ec='none',rasterized=True);a.scatter(q.x,q.y,s=11,c=pal[g],ec='white',lw=.15,alpha=.85,rasterized=True)
        a.set_aspect('equal',adjustable='box');a.set(xlim=(bounds[0]-.2,bounds[1]+.2),ylim=(bounds[2]-.2,bounds[3]+.2));a.axis('off');a.set_title(g+' · '+str(len(q))+' cells',loc='left',fontweight='bold',color=pal[g])
    a=fig.add_axes([.18,.15,.68,.17]);quiet(a,'x');a.set_yticks(range(n),groups);bottom=np.zeros(n)
    for t in types:
        count=np.array([sum(identities[c]==t for c in data.loc[data.group==g,'cell_id']) for g in groups]);a.barh(range(n),count,left=bottom,color=tp[t],ec='white',lw=.4,height=.55);bottom+=count
    a.set(xlabel='All retained cells per batch');a.invert_yaxis();a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
    for i,count in enumerate(bottom):a.text(count+5,i,str(int(count)),va='center',color=MUTED)
    a.set_xlim(0,bottom.max()*1.12);fig.legend(handles=[Patch(fc=tp[t],label=t) for t in types],loc='upper left',bbox_to_anchor=(.17,.405),ncols=min(5,len(types)),frameon=False)
    stamp(fig,data,'integrated_batch_facets',mode='batch_facets',identity_mapping='explicit reviewed mapping for every cell',all_background_cells=True,embedding_refitted=False)
    return lock(fig)
