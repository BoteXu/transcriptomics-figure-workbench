# -*- coding: utf-8 -*-
"""Aligned enrichment evidence; supplied statistics and membership stay fixed."""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter, MaxNLocator
from figure_core import checked, stamp
from project_theme import apply_project_style, group_palette
from figure_workbench.responsive import canvas_budget
INK = '#283F4B'
MUTED = '#687B85'

def _label(value, width=26):
    return textwrap.fill(str(value), width, break_long_words=False)

def plot_enrichment_story(data, theme, *, mode, title, background_definition,
                          gene_set_version, selection_definition, support_contrast,
                          tested_size, query_size=None, nes_limits=(-3, 3),
                          gene_effect_limits=(-3, 3), columns='auto',presentation='auto'):
    """Linked ORA/GSEA and complete selected gene support on aligned term rows.

    Two columns share exact row geometry and one term-label lane. One column
    repeats labels on each complete reading panel. Theme colours are annotation,
    never a replacement for FDR, NES or the explicit membership definition.
    """
    if mode not in ['ora', 'gsea_comparison', 'gene_support']:
        raise ValueError('Choose ora, gsea_comparison or gene_support')
    if not all(isinstance(x, str) and x.strip() for x in
               [title, background_definition, gene_set_version, selection_definition, support_contrast]):
        raise ValueError('Declare background, sets, selection, support contrast and question')
    if set(data.record_type)-{'term', 'membership', 'gene'}:
        raise ValueError('Only displayed enrichment, membership and gene channels are allowed')
    terms = checked(data[data.record_type=='term'], ['term', 'contrast', 'family', 'padj'], ['padj'])
    if terms.empty or terms.duplicated(['term', 'contrast']).any() or ((terms.padj<=0)|(terms.padj>1)).any():
        raise ValueError('Unique valid enrichment summaries required; FDR zero needs an explicit numerical floor upstream')
    if type(tested_size) is not int or tested_size<1:
        raise ValueError('Declare the actual positive tested/ranked universe size')
    if mode!='gsea_comparison':
        terms = checked(terms, ['count', 'ratio'], ['count', 'ratio'])
        if (type(query_size) is not int or not 1<=query_size<=tested_size
            or ((terms['count']<1)|(terms['count']%1!=0)|(terms['count']>query_size)).any()
            or not np.allclose(terms.ratio, terms['count']/query_size, rtol=1e-8, atol=1e-12)):
            raise ValueError('GeneRatio must equal exact overlap count / declared query size within the actual tested universe')
    elif query_size is not None:
        raise ValueError('A preranked GSEA is not an ORA query-list test')
    if (terms.groupby('term').family.nunique()!=1).any():
        raise ValueError('Stable explicit theme assignment required')
    names = list(terms.term.unique()); contrasts = list(terms.contrast.unique())
    families = list(terms.family.unique())
    if support_contrast not in contrasts:
        raise ValueError('Gene support must name an explicitly supplied contrast')
    if len(families)>len(theme['palette_colors']):
        raise ValueError('Sufficient family colours required')
    pal = group_palette(theme, families)
    cols = 2 if columns=='auto' else columns
    if type(cols) is not int or cols not in [1, 2]:
        raise ValueError('Use auto, one or two columns')
    if mode!='gsea_comparison' and len(contrasts)!=1:
        raise ValueError('Select one explicit contrast; use scoped chapters for other contrasts')
    z = None
    if mode=='gsea_comparison':
        z = checked(terms, ['NES'], ['NES'])
        if len(z)!=len(names)*len(contrasts):
            raise ValueError('Complete selected term-by-contrast grid required')
        if len(nes_limits)!=2 or not nes_limits[0]<0<nes_limits[1] or ((z.NES<nes_limits[0])|(z.NES>nes_limits[1])).any():
            raise ValueError('Declare common NES limits containing all selected results')
    membership = checked(data[data.record_type=='membership'], ['term', 'gene', 'member'], ['member'])
    genes = list(membership.gene.unique())
    if (not genes or set(membership.term)!=set(names) or membership.duplicated(['term', 'gene']).any()
        or len(membership)!=len(names)*len(genes) or not set(membership.member)<={0, 1}):
        raise ValueError('Complete explicit binary gene-term membership required, including absent edges')
    effects = checked(data[data.record_type=='gene'], ['gene', 'effect'], ['effect'])
    if effects.gene.duplicated().any() or set(effects.gene)!=set(genes):
        raise ValueError('Exactly one supplied gene effect for every displayed support gene required')
    effect = effects.set_index('gene').effect
    if (len(gene_effect_limits)!=2 or not gene_effect_limits[0]<0<gene_effect_limits[1]
        or ((effect<gene_effect_limits[0])|(effect>gene_effect_limits[1])).any()):
        raise ValueError('Declare gene-effect limits containing every selected gene')
    if presentation not in ['auto','publication','classic']:raise ValueError('Choose auto, publication or classic enrichment presentation')
    if len(contrasts)==1 and (presentation=='publication' or (presentation=='auto' and float(membership.member.mean())<.2 and columns=='auto')):
        from figure_study_publication import enrichment
        fig=enrichment(data,theme,mode,title,support_contrast,tested_size,query_size,nes_limits,gene_effect_limits)
        fig._omics_spec.update(background_definition=background_definition,gene_set_version=gene_set_version,selection_definition=selection_definition,term_order=names,gene_order=genes)
        return apply_project_style(fig,theme)
    label_lane = max(2.0, max(len(line) for x in names for line in _label(x).splitlines())*.073)
    left_width = max(3.1, len(contrasts)*.65) if z is not None else 3.15
    right_width = max(2.5, len(genes)*.38)
    row_height = max(.36, .22*max(len(_label(x).splitlines()) for x in names))
    body = max(2.6, len(names)*row_height)
    key_rows = math.ceil(len(families)/(3 if cols==1 else 5))
    footer = 2.2 + key_rows*.23 + (.5 if z is not None else 0)
    header = 1.8 if cols==1 else 1.5
    between = 2.05 if mode!='gene_support' else 1.25
    width = label_lane+left_width+right_width+1.1 if cols==2 else label_lane+max(left_width, right_width)+.55
    height = header+body+footer if cols==2 else header+2*body+footer+between
    fig = plt.figure(figsize=canvas_budget(width, height))
    left = label_lane/width
    if cols==2:
        available = 1-left-.04; gap=.48/width
        aw = (available-gap)*left_width/(left_width+right_width); bw = available-gap-aw
        a = fig.add_axes([left, footer/height, aw, body/height])
        b = fig.add_axes([left+aw+gap, footer/height, bw, body/height], sharey=a)
    else:
        aw = bw = 1-left-.05
        a = fig.add_axes([left, (footer+body+between)/height, aw, body/height])
        b = fig.add_axes([left, footer/height, bw, body/height])
    headings = []
    for ax in [a,b]:
        ax.set_ylim(len(names)-.5, -.5); ax.set_yticks(range(len(names)), [_label(x) for x in names])
        ax.tick_params(axis='y', length=0, pad=17); ax.spines[:].set_visible(False)
        for i, name in enumerate(names):
            family = terms.loc[terms.term==name, 'family'].iloc[0]
            ax.axhspan(i-.46, i+.46, fc=pal[family], alpha=.055, zorder=0)
        if ax is a or cols==1:
            ax.scatter(np.full(len(names), -.028), range(len(names)),
                       c=[pal[terms.loc[terms.term==x, 'family'].iloc[0]] for x in names],
                       s=22, marker='s', transform=ax.get_yaxis_transform(), clip_on=False, zorder=4)
    if cols==2:b.tick_params(axis='y', labelleft=False)
    sequential = LinearSegmentedColormap.from_list('enrichment_strength', ['#DCECEE', '#4B9F9B', '#246173'])
    left_art = None
    if mode=='ora':
        maximum = max(float((-np.log10(terms.padj)).max()), 1)
        for i,row in enumerate(terms.itertuples()):a.plot([0,row.ratio],[i,i],c='#BAC8CE',lw=1.2,zorder=1)
        left_art = a.scatter(terms.ratio, range(len(names)), s=24+180*terms['count']/terms['count'].max(),
            c=-np.log10(terms.padj),cmap=sequential,norm=Normalize(0,maximum),ec='white',lw=.8,zorder=3)
        for i,row in enumerate(terms.itertuples()):
            a.annotate(str(int(row.count)),(row.ratio,i),xytext=(10,0),textcoords='offset points',va='center',color=MUTED)
        a.set_xlim(0,float(terms.ratio.max())*1.27);a.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
        a.set_xlabel('Gene ratio',labelpad=9)
        a.text(0,1.025,'Numbers: overlap gene count',transform=a.transAxes,color=MUTED)
        left_title='A  Pathway enrichment';left_key=r'$-\log_{10}$ FDR'
    elif mode=='gsea_comparison':
        xs=z.NES.to_numpy() if len(contrasts)==1 else [contrasts.index(x) for x in z.contrast];ys=[names.index(x) for x in z.term]
        sizes=30+50*(-np.log10(z.padj)).to_numpy()
        left_art=a.scatter(xs,ys,s=sizes,c=z.NES,
            cmap=LinearSegmentedColormap.from_list('nes',theme['continuous']['diverging']),
            norm=TwoSlopeNorm(vmin=nes_limits[0],vcenter=0,vmax=nes_limits[1]),ec='white',lw=.7,zorder=3)
        nonsig=z.padj>.05
        a.scatter(np.array(xs)[nonsig],np.array(ys)[nonsig],s=8,c='white',zorder=4)
        if len(contrasts)==1:
            for x,y in zip(xs,ys):a.plot([0,x],[y,y],c='#BFCED3',lw=1.2,zorder=1)
            a.axvline(0,c='#AABAC2',lw=.8,ls=(0,(3,3)))
            a.set_xlim(*nes_limits);a.xaxis.set_major_locator(MaxNLocator(5));a.set_xlabel('Normalized enrichment score (NES)',labelpad=9)
            left_title='A  Pathway direction and magnitude'
        else:
            a.set_xticks(range(len(contrasts)),[_label(x,14) for x in contrasts],rotation=30,ha='right')
            a.set_xlim(-.6,len(contrasts)-.4);left_title='A  Direction across contrasts'
        left_key='NES'
    else:
        a.barh(range(len(names)),terms['count'],height=.48,color=[pal[x] for x in terms.family],alpha=.85)
        a.set_xlabel('Overlap gene count',labelpad=9);a.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=5))
        left_title='A  Pathway support'
    headings.append(a.set_title(left_title,loc='left',fontweight='bold',pad=28,color=INK))
    matrix=membership.pivot(index='term',columns='gene',values='member').loc[names,genes]
    values=np.tile(effect.loc[genes].to_numpy(),(len(names),1))
    b.imshow(np.zeros_like(values),cmap=LinearSegmentedColormap.from_list('empty_membership',['#F1F4F5','#F1F4F5']),
             aspect='auto',interpolation='none',extent=(-.5,len(genes)-.5,len(names)-.5,-.5),zorder=0)
    right_art=b.imshow(np.ma.masked_where(matrix.to_numpy()==0,values),
        cmap=LinearSegmentedColormap.from_list('gene_effect',theme['continuous']['diverging']),
        norm=TwoSlopeNorm(vmin=gene_effect_limits[0],vcenter=0,vmax=gene_effect_limits[1]),aspect='auto',interpolation='none',zorder=2)
    for i in range(len(names)):
        for j in range(len(genes)):
            if matrix.iloc[i,j]==1:
                b.add_patch(Rectangle((j-.48,i-.48),.96,.96,fill=False,ec='#94A8B2',lw=.55,zorder=3))
    b.set_xticks(range(len(genes)),genes,rotation=60 if len(genes)<=6 else 90,ha='right' if len(genes)<=6 else 'center')
    b.tick_params(axis='x',length=0,pad=7)
    b.set_xticks(np.arange(len(genes)+1)-.5,minor=True);b.set_yticks(np.arange(len(names)+1)-.5,minor=True)
    b.grid(which='minor',color='white',lw=1.2);b.tick_params(which='minor',length=0)
    a.tick_params(which='minor',length=0)
    b.set_ylim(len(names)-.5,-.5)
    b.text(0,1.025,'Outlined: member; pale: absent',transform=b.transAxes,color=MUTED)
    headings.append(b.set_title('B  Selected gene membership',loc='left',fontweight='bold',pad=28,color=INK))
    for index,(ax,art,label) in enumerate([(a,left_art,left_key if left_art is not None else ''),(b,right_art,'Gene log2 effect')]):
        if art is None:continue
        box=ax.get_position(); yy=box.y0-(.90 if index==1 or z is not None else .78)/height
        cax=fig.add_axes([box.x0+.04*box.width,yy,box.width*.80,.075/height])
        cb=fig.colorbar(art,cax=cax,orientation='horizontal');cb.set_label(label,labelpad=3);cb.ax.tick_params(length=3)
    title_text=fig.text(.045,1-.24/height,_label(title,90 if cols==2 else 48),color=INK,va='top',fontweight='bold')
    caption='Gene effects: '+support_contrast+'  /  '+('ranked universe: '+str(tested_size) if query_size is None else 'query: '+str(query_size)+'  /  tested: '+str(tested_size))
    fig.text(.045,1-.77/height,_label(caption,100 if cols==2 else 55),color=MUTED,va='top')
    legend=fig.legend(handles=[Patch(fc=pal[x],label=x) for x in families],loc='lower left',bbox_to_anchor=(.045,.22/height),
        frameon=False,ncols=min(5 if cols==2 else 3,len(families)),columnspacing=1.4,handlelength=1.0,handletextpad=.5,borderaxespad=0)
    legend._page_fixed_anchor=True
    if z is not None:
        size_key=fig.legend(handles=[Line2D([],[],ls='',marker='o',color='#7795A0',
            ms=math.sqrt(30+50*v),label=str(v)) for v in [1,3]],
            title='Dot area: -log10 FDR; white centre: FDR > 0.05',
            loc='lower left',bbox_to_anchor=(.045,(.27+key_rows*.23)/height),
            ncols=2,frameon=False,borderaxespad=0)
        size_key._page_fixed_anchor=True
    stamp(fig,data,'enrichment_story',mode=mode,background_definition=background_definition,gene_set_version=gene_set_version,
        selection_definition=selection_definition,support_contrast=support_contrast,tested_size=tested_size,query_size=query_size,
        nes_limits=nes_limits,gene_effect_limits=gene_effect_limits,columns=cols,complete_selected_membership=True,
        term_order=names,gene_order=genes,linked_term_rows=cols==2,absent_membership='pale cell',analysis_performed=False)
    for ax in fig.axes:ax._explicit_guide_layout=True
    fig=apply_project_style(fig,theme);title_text.set_fontsize(theme['design']['title_pt']+2)
    for heading in headings:heading.set_fontsize(theme['design']['title_pt']);heading.set_fontweight('bold')
    return fig
