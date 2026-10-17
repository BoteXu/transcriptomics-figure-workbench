"""Linked ORA/GSEA views with explicit gene support and unchanged supplied results."""
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize,TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from figure_core import checked,stamp
from project_theme import apply_project_style,group_palette

def _label(x,width=24):return '\n'.join(textwrap.wrap(str(x),width,break_long_words=False))

def plot_enrichment_story(data,theme,*,mode,title,background_definition,gene_set_version,selection_definition,support_contrast,tested_size,query_size=None,nes_limits=(-3,3),gene_effect_limits=(-3,3),columns='auto'):
    """Prefer linked effect/ratio, probability, count and exact gene-support channels."""
    if mode not in ['ora','gsea_comparison','gene_support']:raise ValueError('Choose ora, gsea_comparison or gene_support')
    if not all(isinstance(x,str) and x.strip() for x in [title,background_definition,gene_set_version,selection_definition,support_contrast]):raise ValueError('Declare background, sets, selection, support contrast and question')
    terms=checked(data[data.record_type=='term'],['term','contrast','family','padj'],['padj'])
    if terms.duplicated(['term','contrast']).any() or ((terms.padj<=0)|(terms.padj>1)).any():raise ValueError('Unique valid enrichment summaries required; FDR zero needs an explicit numerical floor upstream')
    if type(tested_size) is not int or tested_size<1:raise ValueError('Declare the actual positive tested/ranked universe size')
    if mode!='gsea_comparison':
        terms=checked(terms,['count','ratio'],['count','ratio'])
        if type(query_size) is not int or not 1<=query_size<=tested_size or ((terms['count']<1)|(terms['count']%1!=0)|(terms['count']>query_size)).any() or not np.allclose(terms.ratio,terms['count']/query_size,rtol=1e-8,atol=1e-12):raise ValueError('GeneRatio must equal exact overlap count / declared query size within the actual tested universe')
    elif query_size is not None:raise ValueError('A preranked GSEA is not an ORA query-list test')
    if (terms.groupby('term').family.nunique()!=1).any():raise ValueError('Stable explicit theme assignment required')
    names=list(terms.term.unique());contrasts=list(terms.contrast.unique());families=list(terms.family.unique());palette=theme['palette_colors']
    if support_contrast not in contrasts:raise ValueError('Gene support must name an explicitly supplied contrast')
    if len(families)>len(palette):raise ValueError('Sufficient family colours required')
    pal=group_palette(theme,families);cols=2 if columns=='auto' else columns
    if type(cols)!=int or cols not in [1,2]:raise ValueError('Use auto, one or two columns')
    n=2;height=max(5.8,len(names)*.42+2.6)
    fig=plt.figure(figsize=(12 if cols==2 else 8,height*(2 if cols==1 else 1)),layout='constrained');gs=fig.add_gridspec(1 if cols==2 else 2,cols)
    a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[0,1] if cols==2 else gs[1,0])
    cmap=LinearSegmentedColormap.from_list('enrichment_strength',['#DCECEE','#4B9F9B','#246173'])
    for ax in [a,b]:ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,labelsize=10)
    if mode=='ora':
        if len(contrasts)!=1:raise ValueError('ORA ratio view selects one explicit contrast; use separate scoped chapters for other contrasts')
        maximum=max(float((-np.log10(terms.padj)).max()),1);norm=Normalize(0,maximum)
        for i,r in enumerate(terms.itertuples()):
            a.axhspan(i-.43,i+.43,color=pal[r.family],alpha=.035)
            a.plot([0,r.ratio],[i,i],c=pal[r.family],lw=2,alpha=.5)
        art=a.scatter(terms.ratio,range(len(names)),s=24+220*terms['count']/terms['count'].max(),c=-np.log10(terms.padj),cmap=cmap,norm=norm,ec='white',lw=.8,zorder=3)
        for i,r in enumerate(terms.itertuples()):a.annotate(str(int(r.count))+' hits',(r.ratio,i),xytext=(9,0),textcoords='offset points',va='center',fontsize=9,color='#466170')
        a.set_yticks(range(len(names)),[_label(x) for x in names]);a.invert_yaxis();a.set_xlabel('Supplied GeneRatio');a.set_xlim(0,float(terms.ratio.max())*1.35);a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
        cb=fig.colorbar(art,ax=a,fraction=.04,pad=.04,shrink=.6);cb.set_label('-log10 supplied FDR',fontsize=10);cb.ax.tick_params(labelsize=9)
        a.set_title('A  Enrichment, support and themes',loc='left',fontsize=12,fontweight='bold',pad=16)
    elif mode=='gsea_comparison':
        z=checked(terms,['NES'],['NES'])
        if len(z)!=len(names)*len(contrasts):raise ValueError('Complete selected term-by-contrast grid required')
        if len(nes_limits)!=2 or not nes_limits[0]<0<nes_limits[1] or ((z.NES<nes_limits[0])|(z.NES>nes_limits[1])).any():raise ValueError('Declare common NES limits containing all selected results')
        norm=TwoSlopeNorm(vmin=nes_limits[0],vcenter=0,vmax=nes_limits[1]);cm=LinearSegmentedColormap.from_list('nes',theme['continuous']['diverging'])
        size=30+50*(-np.log10(z.padj)).to_numpy();xs=[contrasts.index(x) for x in z.contrast];ys=[names.index(x) for x in z.term]
        art=a.scatter(xs,ys,s=size,c=z.NES,cmap=cm,norm=norm,ec='white',lw=.7,zorder=3)
        nonsig=z.padj>.05
        a.scatter(np.array(xs)[nonsig],np.array(ys)[nonsig],s=8,c='white',zorder=4)
        a.set_xticks(range(len(contrasts)),[_label(x,14) for x in contrasts],rotation=25,ha='right');a.set_yticks(range(len(names)),[_label(x) for x in names]);a.set(xlim=(-.6,len(contrasts)-.4),ylim=(len(names)-.4,-.6));a.grid(color='#E5EDF0',lw=.6);a.set_axisbelow(True);a.spines[:].set_visible(False)
        cb=fig.colorbar(art,ax=a,fraction=.04,pad=.04,shrink=.65);cb.set_label('Supplied NES',fontsize=10);cb.ax.tick_params(labelsize=9)
        a.legend(handles=[Line2D([],[],marker='o',ls='',c='#7795A0',ms=np.sqrt(30+50*x),label=str(x)) for x in [1,3]],title='Size: -log10 FDR\nWhite centre: FDR > 0.05',title_fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.26),ncols=2,frameon=False,fontsize=9)
        a.set_title('A  Direction across contrasts',loc='left',fontsize=12,fontweight='bold',pad=16)
    else:
        if len(contrasts)!=1:raise ValueError('Select one explicit contrast for the gene-support view')
        a.barh(range(len(names)),terms['count'],height=.6,color=[pal[x] for x in terms.family]);a.set_yticks(range(len(names)),[_label(x) for x in names]);a.invert_yaxis();a.set_xlabel('Supplied overlap gene count');a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0);a.set_title('A  Complete selected term support',loc='left',fontsize=12,fontweight='bold',pad=16)
    membership=checked(data[data.record_type=='membership'],['term','gene','member'],['member'])
    genes=list(membership.gene.unique())
    if set(membership.term)!=set(names) or membership.duplicated(['term','gene']).any() or len(membership)!=len(names)*len(genes) or not set(membership.member)<={0,1}:raise ValueError('Complete explicit binary gene-term membership required, including absent edges')
    effects=checked(data[data.record_type=='gene'],['gene','effect'],['effect'])
    if effects.gene.duplicated().any() or set(effects.gene)!=set(genes):raise ValueError('Exactly one supplied gene effect for every displayed support gene required')
    effect=effects.set_index('gene').effect
    if len(gene_effect_limits)!=2 or not gene_effect_limits[0]<0<gene_effect_limits[1] or ((effect<gene_effect_limits[0])|(effect>gene_effect_limits[1])).any():raise ValueError('Declare gene-effect limits containing every selected gene')
    norm=TwoSlopeNorm(vmin=gene_effect_limits[0],vcenter=0,vmax=gene_effect_limits[1]);cm=LinearSegmentedColormap.from_list('gene_effect',theme['continuous']['diverging'])
    m=membership.set_index(['term','gene']);xx=[];yy=[];vv=[]
    for i,t in enumerate(names):
        for j,g in enumerate(genes):
            if m.loc[(t,g),'member']==1:xx.append(j);yy.append(i);vv.append(effect[g])
    for i,t in enumerate(names):b.axhspan(i-.43,i+.43,color=pal[terms[terms.term==t].family.iloc[0]],alpha=.035)
    art=b.scatter(xx,yy,c=vv,s=110,cmap=cm,norm=norm,ec='white',lw=.5,zorder=3)
    b.set_xticks(range(len(genes)),genes,rotation=60,ha='right');b.set_yticks(range(len(names)),[_label(x) for x in names]);b.set(xlim=(-.7,len(genes)-.3),ylim=(len(names)-.4,-.6));b.tick_params(length=0);b.spines[:].set_visible(False);b.grid(color='#E8EEF0',lw=.5);b.set_axisbelow(True)
    cb=fig.colorbar(art,ax=b,fraction=.04,pad=.04,shrink=.65);cb.set_label('Supplied gene log2 effect',fontsize=10);cb.ax.tick_params(labelsize=9)
    b.set_title('B  Selected gene support\n'+support_contrast,loc='left',fontsize=12,fontweight='bold',pad=16)
    b.legend(handles=[Patch(fc=c,alpha=.3,label=x) for x,c in pal.items()],loc='upper center',bbox_to_anchor=(.5,-.31),ncols=min(2,len(pal)),frameon=False,fontsize=9,title='Theme bands',title_fontsize=9)
    fig.suptitle(title+'\n'+background_definition+' · '+gene_set_version,fontsize=14,fontweight='bold')
    fig.get_layout_engine().set(h_pad=.20,w_pad=.30,hspace=.25,wspace=.20)
    for ax in fig.axes:ax._explicit_guide_layout=True
    stamp(fig,data,'enrichment_story',mode=mode,background_definition=background_definition,gene_set_version=gene_set_version,selection_definition=selection_definition,support_contrast=support_contrast,tested_size=tested_size,query_size=query_size,nes_limits=nes_limits,gene_effect_limits=gene_effect_limits,columns=columns,complete_selected_membership=True,analysis_performed=False)
    return apply_project_style(fig,theme)
