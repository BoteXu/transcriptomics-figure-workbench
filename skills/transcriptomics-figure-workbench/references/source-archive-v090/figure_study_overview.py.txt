"""Compact transcriptomic main figures from supplied result channels only."""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,TwoSlopeNorm,LinearSegmentedColormap
from matplotlib.lines import Line2D
from figure_core import checked,stamp
from project_theme import group_palette,apply_project_style
from figure_workbench.responsive import grid_shape,facet_slots,canvas_budget


def plot_transcriptomic_overview(data,theme,*,assay,contrast,independent_unit,denominator,
                                matrix_label='Row z-score',panels=None,labels=(),alpha=.05,fc=1,
                                embedding_axes=None,panel_titles=None,
                                ncols='auto',nrows=None,panel_width=3.9,panel_height=3.6):
    """A coherent main figure; complete companion results remain independently exported.

    Mixed record_type table: embedding, de, matrix/enrichment for bulk;
    embedding, marker_dot, composition and de for single_cell. All summaries,
    coordinates, probabilities and annotations must already exist upstream.
    """
    choices={'bulk':['embedding','de','matrix','enrichment'],'single_cell':['embedding','marker_dot','composition','de']}
    if assay not in choices or not 0<alpha<1 or not np.isfinite(fc) or fc<=0:raise ValueError('Declare assay and valid display thresholds')
    if any(not isinstance(v,str) or not v.strip() for v in [contrast,independent_unit,denominator,matrix_label]):raise ValueError('Complete contrast, unit, denominator and matrix scale required')
    d=checked(data,['record_type']);selected=list(panels or choices[assay])
    if not selected or len(selected)!=len(set(selected)) or set(selected)-set(choices[assay]) or set(d.record_type)-set(choices[assay]):raise ValueError('Choose unique supported whole panels')
    if set(selected)-set(d.record_type):raise ValueError('A selected overview channel is missing; never invent its result')
    embedding_axes=embedding_axes or (['UMAP 1','UMAP 2'] if assay=='single_cell' else ['PC1','PC2'])
    if not isinstance(embedding_axes,(tuple,list)) or len(embedding_axes)!=2 or any(not isinstance(s,str) or not s.strip() for s in embedding_axes):raise ValueError('Two explicit embedding axis labels required')
    panel_titles={} if panel_titles is None else panel_titles
    if not isinstance(panel_titles,dict) or set(panel_titles)-set(selected) or any(not isinstance(s,str) or not s.strip() for s in panel_titles.values()):raise ValueError('Title overrides must identify selected complete panels')
    rows,cols=grid_shape(len(selected),ncols,nrows)
    # A panel owns its complete label, legend and colour-key lanes. Constrained
    # layout cannot reserve these reliably for heterogeneous transcriptomic
    # panels and can collapse the axes before text measurement.
    tick_pt=theme['design']['tick_pt']
    panel_heights=[]
    for kind in selected:
        q=d[d.record_type==kind]
        lines=q.feature.nunique() if kind in ['matrix','marker_dot'] else 0
        # Complete categorical rows need a real physical text lane; only the
        # row containing a dense matrix grows, not the unrelated PCA panel.
        panel_heights.append(max(panel_height+(.35 if kind=='composition' else 0),lines*(tick_pt+3)*1.05/72+1.42))
    row_heights=[max(panel_heights[r*cols:(r+1)*cols],default=panel_height) for r in range(rows)]
    heading='\n'.join([textwrap.fill(contrast,max(24,int(cols*panel_width*9))),textwrap.fill(independent_unit,max(24,int(cols*panel_width*9)))])
    heading_height=.20+len(heading.splitlines())*max(theme['design']['note_pt'],9)*1.2/72
    fig=plt.figure(figsize=canvas_budget(cols*panel_width,sum(row_heights)+heading_height))
    slots=facet_slots(fig,len(selected),rows,cols,left=0,right=1,
                      bottom=.08/fig.get_figheight(),top=1-heading_height/fig.get_figheight(),
                      wspace=0,hspace=0,height_ratios=row_heights)
    axes=[];counts={};semantic={}
    positive=theme['roles']['positive'];negative=theme['roles']['negative'];neutral='#C7CED3'
    sequential=LinearSegmentedColormap.from_list('study_magnitude',theme['continuous']['sequential'])
    diverging=LinearSegmentedColormap.from_list('study_signed',theme['continuous']['diverging'])
    def validate_grid(q,a,b):
        if q.duplicated([a,b]).any() or len(q)!=q[a].nunique()*q[b].nunique():raise ValueError('An explicitly complete unique overview grid is required')
    for index,(kind,slot) in enumerate(zip(selected,slots)):
        box=slot.get_position(fig)
        left=1.48 if kind=='enrichment' else .58
        right=.62 if kind in ['matrix','marker_dot','enrichment'] else .16
        bottom=1.05 if kind in ['marker_dot','composition'] else .70 if kind=='matrix' else .55
        top=1.4 if kind=='composition' and 'embedding' not in selected else .72
        x=box.x0+left/fig.get_figwidth();y=box.y0+bottom/fig.get_figheight()
        w=box.width-(left+right)/fig.get_figwidth();h=box.height-(bottom+top)/fig.get_figheight()
        if min(w*fig.get_figwidth(),h*fig.get_figheight())<1.2:raise ValueError('Panel is too small for complete overview guides; enlarge or reflow')
        ax=fig.add_axes([x,y,w,h]);axes.append(ax);q=d[d.record_type==kind].copy();counts[kind]=len(q)
        def color_key(artist,label):
            cax=fig.add_axes([x+w+.10/fig.get_figwidth(),y,.075/fig.get_figwidth(),h])
            cb=fig.colorbar(artist,cax=cax);cb.set_label(label,fontsize=8)
            cb.ax.tick_params(labelsize=7.5)
            return cb
        ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8)
        if kind=='embedding':
            q=checked(q,['object_id','group','x','y'],['x','y'])
            if q.object_id.duplicated().any():raise ValueError('Unique supplied coordinate identities required')
            names=list(q.group.unique());pal=group_palette(theme,names)
            for name in names:
                z=q[q.group==name];ax.scatter(z.x,z.y,s=10 if len(q)>100 else 27,c=pal[name],alpha=.78,ec='none',label=name,rasterized=len(q)>500)
            ax.set(xlabel=embedding_axes[0],ylabel=embedding_axes[1])
            if assay=='single_cell':ax.set_aspect('equal',adjustable='box')
            ax.legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.01),ncols=3 if len(names)>2 else len(names),fontsize=7.5,handletextpad=.3,columnspacing=.7,borderaxespad=0)
            title='Cell identity' if assay=='single_cell' else 'Sample architecture'
            semantic[kind]='Only supplied coordinates and annotations; no embedding, ellipse or annotation inference'
        elif kind=='de':
            q=checked(q,['gene','log2FC','padj'],['log2FC','padj'])
            if q.gene.duplicated().any() or ((q.padj<=0)|(q.padj>1)).any():raise ValueError('Unique DE results and adjusted probabilities in (0,1] required')
            status=np.where((q.padj<=alpha)&(q.log2FC>=fc),'Up',np.where((q.padj<=alpha)&(q.log2FC<=-fc),'Down','Other'))
            for name,color in [('Other',neutral),('Down',negative),('Up',positive)]:
                z=q[status==name];ax.scatter(z.log2FC,-np.log10(z.padj),s=6 if name=='Other' else 11,c=color,alpha=.28 if name=='Other' else .85,ec='none',label=name+' ('+str(len(z))+')',rasterized=True)
            for cut in [-fc,fc]:ax.axvline(cut,color='#9CA9B3',lw=.7,ls=(0,(3,3)))
            ax.axhline(-np.log10(alpha),color='#9CA9B3',lw=.7,ls=(0,(3,3)))
            if len(labels)>6 or len(set(labels))!=len(labels) or set(labels)-set(q.gene):raise ValueError('At most six explicitly supplied existing overview gene labels')
            for z in q[q.gene.isin(labels)].itertuples():ax.annotate(z.gene,(z.log2FC,-np.log10(z.padj)),xytext=(3,4),textcoords='offset points',fontsize=8)
            ax.legend(frameon=False,loc='lower left',bbox_to_anchor=(0,1.01),ncols=3,fontsize=7.5,handletextpad=.2,columnspacing=.6,borderaxespad=0)
            ax.set(xlabel='log2 fold change',ylabel='−log10 adjusted P')
            title='Donor-level pseudobulk' if assay=='single_cell' else 'Differential response'
            semantic[kind]={'alpha':alpha,'absolute_log2FC':fc,'unit':independent_unit,'all_results_retained':True}
        elif kind=='matrix':
            q=checked(q,['feature','sample','value'],['value']);validate_grid(q,'feature','sample')
            rr=list(q.feature.unique());cc=list(q['sample'].unique());mat=q.pivot(index='feature',columns='sample',values='value').reindex(index=rr,columns=cc)
            extent=max(abs(q.value.min()),abs(q.value.max()),1e-9)
            im=ax.imshow(mat,aspect='auto',cmap=diverging,norm=TwoSlopeNorm(vmin=-extent,vcenter=0,vmax=extent),interpolation='nearest')
            ax.set_xticks(range(len(cc)),cc,rotation=90,fontsize=7.5);ax.set_yticks(range(len(rr)),rr,fontsize=7.5)
            ax.tick_params(length=0);ax.spines[:].set_visible(False)
            if 'sample_group' in q and q.sample_group.notna().any():
                if q.sample_group.isna().any() or (q.groupby('sample').sample_group.nunique()!=1).any():raise ValueError('Complete, consistent sample-group annotations required')
                from matplotlib.patches import Rectangle,Patch
                annotation=q.drop_duplicates('sample').set_index('sample').reindex(cc).sample_group;ap=group_palette(theme,list(annotation.unique()))
                for j,g in enumerate(annotation):ax.add_patch(Rectangle((j-.5,1.015),1,.035,transform=ax.get_xaxis_transform(),fc=ap[g],ec='white',lw=.3,clip_on=False))
                ax.legend(handles=[Patch(color=c,label=g) for g,c in ap.items()],ncols=len(ap),frameon=False,fontsize=7.5)
            color_key(im,matrix_label)
            title='Prespecified expression program';semantic[kind]='Supplied matrix, order and scale; no clustering, rescaling or feature selection'
        elif kind=='enrichment':
            q=checked(q,['term','score','padj','count'],['score','padj','count'])
            if q.term.duplicated().any() or ((q.padj<=0)|(q.padj>1)).any() or (q['count']<1).any() or ((q.score<0)|(q.score>1)).any():raise ValueError('Complete unique supplied ORA terms, fractions, counts and adjusted probabilities required')
            yy=np.arange(len(q));strength=-np.log10(q.padj);norm=Normalize(0,max(strength.max(),1e-9))
            ax.hlines(yy,0,q.score,colors='#CAD4DB',lw=1.4)
            dots=ax.scatter(q.score,yy,s=90*q['count']/q['count'].max(),c=strength,cmap=sequential,norm=norm,ec='#5F7482',lw=.4,zorder=3)
            ax.set_yticks(yy,[textwrap.fill(str(t),17,break_long_words=False) for t in q.term],fontsize=7.5);ax.invert_yaxis();ax.set(xlim=(0,q.score.max()*1.18),xlabel='Gene ratio')
            from matplotlib.ticker import PercentFormatter,MaxNLocator
            ax.xaxis.set_major_locator(MaxNLocator(4));ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
            color_key(dots,'−log10 FDR')
            levels=sorted(set([int(q['count'].min()),int(q['count'].max())]))
            ax.legend(handles=[Line2D([],[],ls='',marker='o',color='#668392',ms=np.sqrt(90*v/q['count'].max()),label=str(v)+' genes') for v in levels],loc='lower left',bbox_to_anchor=(0,1.01),ncols=2,frameon=False,fontsize=7.5,borderaxespad=0)
            title='Functional context';semantic[kind]='Separate supplied ratio, overlap-count area and adjusted probability; no enrichment calculation'
        elif kind=='marker_dot':
            q=checked(q,['feature','group','value','fraction'],['value','fraction']);validate_grid(q,'feature','group')
            if ((q.fraction<0)|(q.fraction>1)|(q.value<0)).any():raise ValueError('Supplied nonnegative mean expression and bounded detection fractions required')
            rr=list(q.feature.unique());cc=list(q.group.unique())
            im=ax.scatter([cc.index(v) for v in q.group],[rr.index(v) for v in q.feature],s=q.fraction*80,c=q.value,cmap=sequential,ec='none')
            ax.set_xticks(range(len(cc)),[str(v) for v in cc],rotation=90,fontsize=7.5);ax.set_yticks(range(len(rr)),rr,fontsize=7.5);ax.set(ylim=(len(rr)-.5,-.5),xlim=(-.5,len(cc)-.5));ax.tick_params(length=0)
            color_key(im,'Mean over all cells')
            ax.legend(handles=[Line2D([],[],ls='',marker='o',color='#668392',ms=np.sqrt(80*v),label=str(int(v*100))+'% detected') for v in [.25,1]],loc='lower left',bbox_to_anchor=(0,1.01),ncols=2,frameon=False,fontsize=7.5,borderaxespad=0)
            title='Marker specificity';semantic[kind]='Supplied means and fractions; denominator is all cells per annotation; no marker testing'
        elif kind=='composition':
            q=checked(q,['sample','category','count','condition'],['count']);validate_grid(q,'sample','category')
            if (q['count']<0).any() or (q['count']%1!=0).any() or (q.groupby('sample')['count'].sum()<=0).any() or (q.groupby('sample').condition.nunique()!=1).any():raise ValueError('Complete nonnegative integer counts and one condition per donor required')
            rr=list(q['sample'].unique());cc=list(q.category.unique());mat=q.pivot(index='sample',columns='category',values='count').reindex(index=rr,columns=cc);fractions=mat.div(mat.sum(axis=1),axis=0);bottom=np.zeros(len(rr));pal=group_palette(theme,cc)
            for category in cc:ax.bar(range(len(rr)),fractions[category],bottom=bottom,width=.84,color=pal[category]);bottom+=fractions[category]
            ax.set_xticks(range(len(rr)),rr,rotation=90,fontsize=7.5);ax.set(ylim=(0,1),ylabel='Fraction of cells per donor')
            from matplotlib.ticker import PercentFormatter
            ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
            condition=q.drop_duplicates('sample').set_index('sample').reindex(rr).condition;cp=group_palette(theme,list(condition.unique()))
            ax.scatter(range(len(rr)),np.full(len(rr),1.035),c=[cp[c] for c in condition],marker='s',s=20,clip_on=False)
            handles=[Line2D([],[],ls='',marker='s',color=color,label=name) for name,color in cp.items()]
            if 'embedding' in selected:
                embedding_groups=set(d.loc[d.record_type=='embedding','group'])
                if set(cc)!=embedding_groups:raise ValueError('A shared cell-type key requires exactly matching supplied annotation identities')
                ax.set_xlabel('Cell-type colours: panel '+chr(65+selected.index('embedding')))
            else:handles += [Line2D([],[],ls='',marker='s',color=pal[c],label=c) for c in cc]
            ax.legend(handles=handles,loc='lower left',bbox_to_anchor=(0,1.08),ncols=2,frameon=False,fontsize=7.5,borderaxespad=0)
            title='Donor composition';semantic[kind]='Each bar is one donor; proportions are descriptive closure of all supplied counts; no group test'
        legend=ax.get_legend()
        if legend is not None:
            legend.set_bbox_to_anchor((x,box.y1-.30/fig.get_figheight()),transform=fig.transFigure)
            legend.set_loc('upper left');legend._page_fixed_anchor=True
        panel_heading=fig.text(box.x0+.13/fig.get_figwidth(),box.y1-.08/fig.get_figheight(),
                 chr(65+index)+'  '+panel_titles.get(kind,title),ha='left',va='top',fontsize=10,fontweight='bold')
        panel_heading._panel_heading=True
    fig.suptitle(heading,fontsize=10,y=1-.04/fig.get_figheight())
    stamp(fig,data,'transcriptomic_overview',assay=assay,selected_panels=selected,omitted_channels=sorted(set(d.record_type)-set(selected)),input_rows_by_panel=counts,semantics=semantic,contrast=contrast,independent_unit=independent_unit,denominator=denominator,layout={'rows':rows,'columns':cols},scientific_acceptance=False)
    return apply_project_style(fig,theme)
