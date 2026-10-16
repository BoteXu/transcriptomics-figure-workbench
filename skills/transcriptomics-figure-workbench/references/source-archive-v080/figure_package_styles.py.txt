"""Reference-informed package displays, exclusively from frozen result channels."""
import copy
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors, ticker
from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle, Patch
from figure_core import checked
from figure_editorial import _axis, _finish, _order, validate_contract
from figure_gsea import _gsea_input
from project_theme import group_palette

INK='#243449';MUTED='#738091';GRID='#E7EBEF'
TEAL='#218C8D';CORAL='#D8795B';BLUE='#4B70A6';GOLD='#C8A34E'


def _new(theme, title, subtitle='', size=(6.7,4.3)):
    with plt.rc_context({'svg.fonttype':'none','pdf.fonttype':42,'font.family':theme['font_family']}):
        fig=plt.figure(figsize=size,facecolor='white')
    fig.text(.105,.942,title,fontsize=11.6,fontweight='bold',color=INK,va='top')
    if subtitle:fig.text(.105,.881,subtitle,fontsize=7.6,color=MUTED,va='top')
    badge=fig.text(.985,.994,'',ha='right',va='top',fontsize=5.8,color=MUTED)
    fig._software_band_artists=[badge];fig._editorial_font=theme['font_family']
    return fig


def _foot(fig, text):
    fig.text(.105,.025,'\n'.join(textwrap.wrap(text,112)),fontsize=6.3,color=MUTED,va='bottom')


def _flat_axis(ax, grid='y'):
    ax.spines[['top','right']].set_visible(False)
    for side in ['left','bottom']:ax.spines[side].set(color='#A6B0B9',linewidth=.65)
    ax.tick_params(colors=INK,labelsize=8,width=.6,length=3)
    if grid:ax.grid(axis=grid,color=GRID,lw=.55);ax.set_axisbelow(True)


def _bounds(values, limits, signed=False):
    if not isinstance(limits,(list,tuple)) or len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1]:raise ValueError('Declare finite increasing display limits')
    if signed and not limits[0]<0<limits[1]:raise ValueError('Signed scale must straddle zero')
    if (values<limits[0]).any() or (values>limits[1]).any():raise ValueError('Display limits would clip supplied results')
    return colors.TwoSlopeNorm(vmin=limits[0],vcenter=0,vmax=limits[1]) if signed else colors.Normalize(*limits)


def _cmap(theme,signed=True):
    return colors.LinearSegmentedColormap.from_list('package_continuous',theme['continuous']['diverging' if signed else 'sequential'])


def _grid(data,row,col,rows,cols):
    rr,cc=_order(data[row],rows),_order(data[col],cols)
    if data.duplicated([row,col]).any() or len(data)!=len(rr)*len(cc):raise ValueError('Complete selected grid required; missing is not zero')
    return rr,cc


def _gsea(data,theme,o):
    c,h,m,s,names=_gsea_input(data,o['curve_order'],o['ranked_universe']);mode=o.get('mode','classic')
    if mode not in ['classic','overlay','facets'] or (mode=='classic' and len(names)!=1):raise ValueError('Select a valid GSEA arrangement')
    if any(not isinstance(o.get(k),str) or not o[k] for k in ['metric_label','contrast','gene_set_version']):raise ValueError('Declare contrast, rank metric and gene-set version')
    pal=group_palette(theme,names);n=len(names);facets=mode=='facets'
    fig=_new(theme,o.get('title','Gene set enrichment'),o['contrast']+'  /  complete ranked universe: '+str(o['ranked_universe']),size=(6.6,4.7 if not facets else 4.8+.30*n))
    top_low=.49;top_height=.31
    axes=[]
    if facets:
        for i,name in enumerate(names):
            ax=_axis(fig,[.13,top_low+(n-i-1)*top_height/n,.66,top_height/n-.03]);axes.append(ax)
    else:axes=[_axis(fig,[.13,top_low,.66,top_height])]
    for i,name in enumerate(names):
        q=c[c.pathway==name];ax=axes[i] if facets else axes[0]
        if n==1:ax.fill_between(q['rank'],0,q.value,color=pal[name],alpha=.09)
        ax.plot(q['rank'],q.value,c=pal[name],lw=1.7,label=name)
        ax.axhline(0,c='#A8B2BB',lw=.65,ls=(0,(3,3)))
        ax.set_xlim(1,o['ranked_universe']);ax.tick_params(axis='x',labelbottom=False);ax.yaxis.set_major_locator(ticker.MaxNLocator(3));_flat_axis(ax,grid='y')
        if facets:ax.text(1.025,.74,name+'\nNES '+f'{s.loc[name,"NES"]:+.2f}'+'\nFDR '+f'{s.loc[name,"padj"]:.2g}',transform=ax.transAxes,fontsize=6.8,color=pal[name],va='top')
    if not facets:
        axes[0].set_ylabel('Running ES',fontsize=8.4)
        for i,name in enumerate(names):
            fig.text(.825,.79-i*.12,'\n'.join(textwrap.wrap(name,18))+'\n'+f'NES {s.loc[name,"NES"]:+.2f}\nFDR {s.loc[name,"padj"]:.2g}',fontsize=6.7,color=pal[name],va='top',linespacing=1.4)
    else:fig.text(.035,.65,'Running ES',rotation=90,color=INK,fontsize=8.4,va='center')
    hit=fig.add_axes([.13,.365,.66,.085]);hit.set(xlim=(1,o['ranked_universe']),ylim=(0,n));hit.axis('off')
    for i,name in enumerate(names):
        q=h[h.pathway==name];hit.vlines(q['rank'],n-i-.83,n-i-.12,color=pal[name],lw=.7,alpha=.55,clip_on=False)
        q=q[q.leading_edge==1];hit.vlines(q['rank'],n-i-.83,n-i-.12,color=pal[name],lw=1.5,clip_on=False)
    fig.text(.825,.405,'Gene-set hits\nBold: supplied\nleading edge',fontsize=6.5,color=MUTED,va='top',linespacing=1.5)
    bottom=_axis(fig,[.13,.16,.66,.145]);_flat_axis(bottom,grid=None)
    bottom.fill_between(m['rank'],0,m.value,where=m.value>=0,color=CORAL,alpha=.40,interpolate=True)
    bottom.fill_between(m['rank'],0,m.value,where=m.value<=0,color=BLUE,alpha=.45,interpolate=True)
    bottom.plot(m['rank'],m.value,c='#8C99A6',lw=.55);bottom.set(xlim=(1,o['ranked_universe']),xlabel='Rank in ordered dataset',ylabel=o['metric_label']);bottom.xaxis.set_major_locator(ticker.MaxNLocator(5,integer=True));bottom.yaxis.set_major_locator(ticker.MaxNLocator(3))
    labels=o.get('gene_labels',[])
    if len(labels)>6 or not set(labels)<=set(h.gene):raise ValueError('Label at most six supplied hit genes')
    for i,gene in enumerate(labels):
        row=h[h.gene==gene].iloc[0];hit.annotate(gene,(row['rank'],.90*n),xytext=(0,3+7*(i%2)),textcoords='offset points',ha='center',fontsize=6.1,color=INK)
    _foot(fig,o['gene_set_version']+'; ES, NES, adjusted probabilities and hit positions supplied unchanged.')
    return fig


def _nes(data,theme,o):
    d=checked(data,['pathway','contrast','status']);rows,cols=_grid(d,'pathway','contrast',o['pathway_order'],o['contrast_order'])
    if len(rows)>24 or len(cols)>10 or not set(d.status)<={'reported','not_tested'}:raise ValueError('Bounded NES grid and explicit test status required')
    z=checked(d[d.status=='reported'],['NES','padj','set_size'],['NES','padj','set_size']);norm=_bounds(z.NES,o['nes_limits'],True)
    maximum=o['size_max'];alpha=o.get('alpha',.05)
    if not 0<alpha<1 or not np.isfinite(maximum) or maximum<=0 or ((z.padj<0)|(z.padj>1)|(z.set_size<=0)|(z.set_size%1!=0)|(z.set_size>maximum)).any():raise ValueError('Invalid NES support values or scale')
    if d[d.status=='not_tested'][['NES','padj','set_size']].notna().any().any():raise ValueError('Untested cannot acquire invented metrics')
    fig=_new(theme,o.get('title','Enrichment across contrasts'),'Colour: normalized enrichment  /  Area: gene-set size',size=(6.8,max(3.7,.27*len(rows)+1.8)))
    ax=fig.add_axes([.35,.22,.40,.55]);cm=_cmap(theme)
    for i,p in enumerate(rows):
        ax.axhline(i,c=GRID,lw=.6,zorder=0)
        for j,c in enumerate(cols):
            q=d[(d.pathway==p)&(d.contrast==c)].iloc[0]
            if q.status=='not_tested':ax.text(j,i,'×',ha='center',va='center',color='#9AA5AE',fontsize=8)
            else:ax.scatter(j,i,s=180*q.set_size/maximum,c=[cm(norm(q.NES))],edgecolors=INK if q.padj<=alpha else '#BBC5CE',lw=1 if q.padj<=alpha else .45,zorder=2)
    ax.set_xticks(range(len(cols)),cols,rotation=30,ha='right');ax.set_yticks(range(len(rows)),['\n'.join(textwrap.wrap(r,26)) for r in rows]);ax.set(xlim=(-.5,len(cols)-.5),ylim=(len(rows)-.5,-.5));ax.tick_params(length=0,labelsize=8,pad=7)
    for sp in ax.spines.values():sp.set_visible(False)
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.82,.59,.018,.17]));cb.set_label('NES',fontsize=7.5);cb.ax.tick_params(labelsize=7)
    fig.text(.81,.48,f'Outline: FDR ≤ {alpha:g}\n×  Not tested',fontsize=6.7,color=MUTED,va='top',linespacing=1.6)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(180*k/maximum),mfc='#C8D1D9',mec='#94A3B0',label=str(int(k))) for k in [maximum/4,maximum]],title='Set size',loc='upper left',bbox_to_anchor=(.80,.32),frameon=False,fontsize=7,title_fontsize=7)
    _foot(fig,'Selected terms and contrasts retained; FDR and NES are separate supplied channels.');return fig


def _leading(data,theme,o):
    d=checked(data,['pathway','gene','member','leading_edge','value'],['member','leading_edge','value']);rows,cols=_grid(d,'pathway','gene',o['pathway_order'],o['gene_order'])
    if len(rows)>18 or len(cols)>30 or not set(d.member)<={0,1} or not set(d.leading_edge)<={0,1} or (d.leading_edge>d.member).any() or (d.groupby('gene').value.nunique()!=1).any():raise ValueError('Explicit consistent membership, subset and gene effects required')
    norm=_bounds(d.value,o['value_limits'],True);cm=_cmap(theme)
    fig=_new(theme,o.get('title','Leading-edge gene programmes'),'Outlined cells identify the supplied leading-edge subset',size=(max(6.7,.29*len(cols)+3),max(3.7,.29*len(rows)+1.8)))
    ax=fig.add_axes([.32,.30,.47,.47]);lookup=d.set_index(['pathway','gene'])
    for i,p in enumerate(rows):
        for j,g in enumerate(cols):
            q=lookup.loc[(p,g)]
            ax.add_patch(Rectangle((j,i),1,1,fc=cm(norm(q.value)) if q.member else '#F4F6F8',ec='white',lw=2))
            if q.leading_edge:ax.add_patch(Rectangle((j+.07,i+.07),.86,.86,fc='none',ec=INK,lw=.9))
    ax.set(xlim=(0,len(cols)),ylim=(len(rows),0));ax.set_xticks(np.arange(len(cols))+.5,cols,rotation=90,ha='center');ax.set_yticks(np.arange(len(rows))+.5,rows);ax.tick_params(length=0,labelsize=7.8,pad=6)
    for sp in ax.spines.values():sp.set_visible(False)
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.84,.58,.018,.18]));cb.set_label(o['value_label'],fontsize=7.2);cb.ax.tick_params(labelsize=7)
    fig.text(.83,.43,'Outline: leading edge\nGrey: nonmember',va='top',fontsize=6.7,color=MUTED,linespacing=1.7)
    _foot(fig,'Membership and gene effects supplied; no gene selection, clustering or inference.');return fig


def _ora(data,theme,o):
    d=checked(data,['term','count','query_size','padj'],['count','query_size','padj']);order=_order(d.term,o['term_order'])
    if len(d)>25 or d.term.duplicated().any() or d.query_size.nunique()!=1 or ((d['count']<=0)|(d['count']%1!=0)|(d.query_size<=0)|(d.query_size%1!=0)|(d['count']>d.query_size)|(d.padj<=0)|(d.padj>1)).any():raise ValueError('Exact ORA counts, query denominator and positive adjusted probabilities required')
    mode=o.get('mode','bubble')
    if mode not in ['bubble','lollipop']:raise ValueError('Unknown ORA view')
    d=d.set_index('term').loc[order];ratio=d['count']/d.query_size;strength=-np.log10(d.padj);maximum=o.get('significance_max',8);ratio_max=o.get('ratio_max',1)
    if not 0<ratio_max<=1 or not np.isfinite(maximum) or maximum<=0 or (ratio>ratio_max).any() or (strength>maximum).any():raise ValueError('ORA scale would clip values')
    fig=_new(theme,o.get('title','Over-represented programmes'),'Selected query n='+str(int(d.query_size.iloc[0]))+'  /  '+o['background_definition'],size=(6.6,max(3.9,.30*len(d)+1.6)))
    ax=_axis(fig,[.38,.20,.39,.57]);_flat_axis(ax,'x');ax.spines['left'].set_visible(False);y=np.arange(len(d));cm=_cmap(theme,False)
    for i in y:
        if i%2==0:ax.axhspan(i-.46,i+.46,color='#F7F9FA',zorder=0)
    if mode=='lollipop':ax.hlines(y,0,ratio,colors='#C6D4DC',lw=2.1,zorder=1)
    ax.scatter(ratio,y,s=140*d['count']/d['count'].max(),c=strength,cmap=cm,vmin=0,vmax=maximum,edgecolors='white',lw=.7,zorder=3)
    ax.set_yticks(y,['\n'.join(textwrap.wrap(t,29)) for t in order]);ax.set(xlim=(0,ratio_max),ylim=(len(d)-.5,-.5),xlabel='Gene ratio');ax.tick_params(axis='y',length=0,pad=8);ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
    cb=fig.colorbar(ScalarMappable(norm=colors.Normalize(0,maximum),cmap=cm),cax=fig.add_axes([.84,.60,.018,.17]));cb.set_label('−log10 adjusted P',fontsize=7);cb.ax.tick_params(labelsize=7)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(140*k/d['count'].max()),mfc='#A5C2CE',mec='white',label=str(int(k))) for k in [d['count'].min(),d['count'].max()]],title='Gene count',loc='upper left',bbox_to_anchor=(.82,.43),frameon=False,fontsize=7,title_fontsize=7)
    _foot(fig,'Ratio = count / selected query; background and adjusted probabilities are explicit frozen inputs.');return fig


def _ridge(data,theme,o):
    d=checked(data,['group','x','density'],['x','density']);names=list(dict.fromkeys(d.group));pal=group_palette(theme,names)
    if len(names)>12 or (d.density<0).any() or d.duplicated(['group','x']).any():raise ValueError('Bounded unique nonnegative frozen density profiles required')
    grids=[]
    for name in names:
        q=d[d.group==name];grids.append(q.x.tolist())
        if len(q)<2 or (np.diff(q.x)<=0).any():raise ValueError('Density grid must be strictly ordered')
    if any(g!=grids[0] for g in grids[1:]) or d.density.max()<=0:raise ValueError('Common density grid and positive global maximum required')
    fig=_new(theme,o.get('title','Distribution of core enrichment scores'),o['density_label'],size=(6.6,max(4.0,len(names)*.40+1.7)));ax=_axis(fig,[.35,.19,.53,.61]);scale=.78/float(d.density.max())
    for i,name in enumerate(names):
        q=d[d.group==name];y=len(names)-i-1
        ax.plot([d.x.min(),d.x.max()],[y,y],c='#DCE3E8',lw=.6)
        ax.fill_between(q.x,y,y+q.density*scale,color=pal[name],alpha=.68);ax.plot(q.x,y+q.density*scale,c=pal[name],lw=1.2)
    ax.set_yticks(np.arange(len(names)),list(reversed(names)));ax.set(xlim=(d.x.min(),d.x.max()),ylim=(-.18,len(names)),xlabel=o['x_label']);ax.tick_params(axis='y',length=0,pad=10);ax.spines['left'].set_visible(False)
    _foot(fig,'Common height scale; supplied density profiles only. No KDE or core-gene selection performed.');return fig


def _matrix(data,theme,o):
    d=checked(data,['feature','sample','value'],['value']);rows,cols=_grid(d,'feature','sample',o.get('row_order'),o.get('column_order'))
    if len(rows)>36 or len(cols)>30:raise ValueError('Use an explicitly bounded matrix panel')
    signed=o.get('scale_type','signed')=='signed';norm=_bounds(d.value,o['limits'],signed)
    fig=_new(theme,o.get('title','Frozen activity scores'),o.get('subtitle','Fixed order  /  shared scale  /  supplied scores'),size=(max(6.4,len(cols)*.29+3),max(4.0,len(rows)*.27+1.8)))
    ax=fig.add_axes([.34,.25,.43,.50]);mat=d.pivot(index='feature',columns='sample',values='value').loc[rows,cols]
    im=ax.pcolormesh(np.arange(len(cols)+1),np.arange(len(rows)+1),mat,cmap=_cmap(theme,signed),norm=norm,edgecolors='white',lw=.7)
    ax.set_xticks(np.arange(len(cols))+.5,cols,rotation=40,ha='right');ax.set_yticks(np.arange(len(rows))+.5,rows);ax.set_ylim(len(rows),0);ax.tick_params(length=0,pad=7,labelsize=8)
    for sp in ax.spines.values():sp.set_visible(False)
    annotations=o.get('column_groups')
    if annotations:
        if set(annotations)!=set(cols):raise ValueError('Every selected matrix column needs its declared annotation')
        pal=group_palette(theme,list(dict.fromkeys(annotations.values())))
        bar=fig.add_axes([.34,.775,.43,.018])
        for j,c in enumerate(cols):bar.add_patch(Rectangle((j,0),1,1,fc=pal[annotations[c]],ec='white',lw=.6))
        bar.set(xlim=(0,len(cols)),ylim=(0,1));bar.axis('off')
        fig.legend(handles=[Patch(fc=v,label=k) for k,v in pal.items()],loc='upper left',bbox_to_anchor=(.81,.48),frameon=False,fontsize=7,title='Sample group',title_fontsize=7)
    cb=fig.colorbar(im,cax=fig.add_axes([.83,.59,.017,.17]));cb.set_label(o.get('y_label','Supplied score'),fontsize=7.4);cb.ax.tick_params(labelsize=7)
    _foot(fig,'Values and identities retained. No scaling, sample clustering or upstream activity estimation.');return fig


def _volcano(data,theme,o):
    d=checked(data,['gene','log2FC','padj'],['log2FC','padj'])
    if d.gene.duplicated().any() or ((d.padj<=0)|(d.padj>1)).any():raise ValueError('Unique genes and adjusted probabilities in (0,1] required')
    alpha=o.get('alpha',.05);cutoff=o.get('effect_cutoff',1)
    if not 0<alpha<1 or not np.isfinite(cutoff) or cutoff<0:raise ValueError('Declare finite positive visual thresholds')
    y=-np.log10(d.padj);up=(d.log2FC>cutoff)&(d.padj<alpha);down=(d.log2FC< -cutoff)&(d.padj<alpha)
    fig=_new(theme,o.get('title','Differential expression'),o.get('subtitle','Frozen contrast  /  adjusted probability and effect size'));ax=_axis(fig,[.14,.18,.68,.61]);_flat_axis(ax,'y')
    ax.scatter(d.loc[~(up|down),'log2FC'],y[~(up|down)],s=8,c='#C7CED5',alpha=.55,lw=0,rasterized=True)
    ax.scatter(d.loc[down,'log2FC'],y[down],s=14,c=BLUE,alpha=.76,lw=0,rasterized=True);ax.scatter(d.loc[up,'log2FC'],y[up],s=14,c=CORAL,alpha=.8,lw=0,rasterized=True)
    for x in [-cutoff,cutoff]:ax.axvline(x,c='#ADB7BF',lw=.7,ls=(0,(3,3)))
    ax.axhline(-np.log10(alpha),c='#ADB7BF',lw=.7,ls=(0,(3,3)));ax.set(xlabel='log2 fold change',ylabel='−log10 adjusted P')
    labels=o.get('label_genes',[])
    if len(labels)>10 or not set(labels)<=set(d.gene):raise ValueError('Declare at most ten actual gene labels')
    for i,gene in enumerate(labels):
        q=d[d.gene==gene].iloc[0];ax.annotate(gene,(q.log2FC,-np.log10(q.padj)),xytext=(5 if q.log2FC>=0 else -5,7+7*(i%2)),textcoords='offset points',ha='left' if q.log2FC>=0 else 'right',fontsize=7,color=INK,bbox=dict(fc='white',ec='none',alpha=.88,pad=.7),arrowprops=dict(arrowstyle='-',color='#A8B3BC',lw=.55))
    handles=[Line2D([],[],ls='',marker='o',mfc=c,mec='none',label=t,markersize=4) for c,t in [(CORAL,'Higher ('+str(int(up.sum()))+')'),(BLUE,'Lower ('+str(int(down.sum()))+')'),('#C7CED5','Other ('+str(int((~(up|down)).sum()))+')')]]
    fig.legend(handles=handles,loc='upper right',bbox_to_anchor=(.97,.79),frameon=False,fontsize=6.8,labelspacing=.9)
    _foot(fig,'Visual thresholds only; exact supplied fold changes and adjusted probabilities. Label selection declared.');return fig


def _forest(data,theme,o):
    d=checked(data,['label','group','estimate','lower','upper'],['estimate','lower','upper'])
    if d.label.duplicated().any() or len(d)>30 or ((d.lower>d.estimate)|(d.upper<d.estimate)).any():raise ValueError('Unique effects and valid supplied intervals required')
    ratio=o.get('effect_scale','difference')=='ratio'
    if o.get('effect_scale','difference') not in ['ratio','difference']:raise ValueError('Declare ratio or difference effect scale')
    if ratio and (d.lower<=0).any():raise ValueError('Ratio intervals must be positive')
    fig=_new(theme,o.get('title','Differential effects'),o.get('interval_label','Supplied intervals; definition retained'),size=(7.2,max(3.8,len(d)*.30+1.5)));ax=_axis(fig,[.24,.19,.44,.59]);textax=fig.add_axes([.72,.19,.25,.59],sharey=ax);textax.axis('off');pal=group_palette(theme,list(dict.fromkeys(d.group)));n=len(d)
    for i,q in enumerate(d.itertuples()):
        if i%2==0:ax.axhspan(i-.46,i+.46,fc='#F4F7F9',zorder=0)
        ax.errorbar(q.estimate,i,xerr=[[q.estimate-q.lower],[q.upper-q.estimate]],fmt='o',color=pal[q.group],ms=4.7,lw=1.1,capsize=2,mec='white',mew=.5)
        textax.text(0,i,f'{q.estimate:+.2f}  [{q.lower:+.2f}, {q.upper:+.2f}]',va='center',fontsize=7.4,color=INK)
    ax.axvline(1 if ratio else 0,c='#9BA7B2',ls=(0,(3,3)),lw=.8);ax.set_yticks(range(n),d.label);ax.set_ylim(n-.5,-.5);ax.tick_params(axis='y',length=0,pad=12);ax.spines['left'].set_visible(False);ax.set_xlabel(o.get('x_label','Effect size'))
    if ratio:ax.set_xscale('log')
    textax.text(0,1.04,'Estimate [interval]',transform=textax.transAxes,fontsize=7.5,color=MUTED)
    _foot(fig,'Existing intervals only; no model fit, empirical-Bayes moderation or uncertainty estimation.');return fig


def _dot(data,theme,o):
    d=checked(data,['feature','group','fraction','value'],['fraction','value']);rows,cols=_grid(d,'feature','group',o.get('row_order'),o.get('column_order'))
    if len(rows)>35 or len(cols)>20 or ((d.fraction<0)|(d.fraction>1)).any() or o.get('value_semantics') not in ['mean_all','mean_detected','scaled','signed_effect'] or not o.get('denominator_label'):raise ValueError('Declare dot value semantics and fraction denominator')
    norm=_bounds(d.value,o['limits'],o.get('scale_type','sequential')=='signed');cm=_cmap(theme,o.get('scale_type','sequential')=='signed')
    if o.get('scale_type','sequential') not in ['signed','sequential'] or (o['value_semantics']=='signed_effect' and o.get('scale_type')!='signed'):raise ValueError('Signed effects require an explicit diverging scale')
    fig=_new(theme,o.get('title','Cell-type marker expression'),o['denominator_label'],size=(max(6.6,len(cols)*.34+3),max(4.4,len(rows)*.24+1.8)));ax=fig.add_axes([.23,.24,.51,.54])
    for i in range(len(rows)):ax.axhline(i,c=GRID,lw=.55,zorder=0)
    for i,r in enumerate(rows):
        for j,c in enumerate(cols):
            q=d[(d.feature==r)&(d.group==c)].iloc[0];ax.scatter(j,i,s=140*q.fraction,c=[cm(norm(q.value))],ec='white',lw=.35)
    ax.set_xticks(range(len(cols)),cols,rotation=60,ha='right');ax.set_yticks(range(len(rows)),rows);ax.set(xlim=(-.6,len(cols)-.4),ylim=(len(rows)-.5,-.5));ax.tick_params(length=0,labelsize=8,pad=7)
    for sp in ax.spines.values():sp.set_visible(False)
    pal=group_palette(theme,cols);bar=fig.add_axes([.23,.80,.51,.016]);bar.set(xlim=(-.5,len(cols)-.5),ylim=(0,1));bar.axis('off')
    for j,c in enumerate(cols):bar.add_patch(Rectangle((j-.5,0),1,1,fc=pal[c],ec='white',lw=.6))
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cm),cax=fig.add_axes([.83,.60,.018,.18]));cb.set_label(o['value_label'],fontsize=7.3);cb.ax.tick_params(labelsize=7)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(140*f),mfc='#A8BEC9',mec='white',label=str(int(f*100))+'%') for f in [.25,.5,1]],title='Fraction (area)',loc='upper left',bbox_to_anchor=(.80,.43),frameon=False,fontsize=7,title_fontsize=7)
    _foot(fig,'Means and fractions supplied. No expression normalization, clustering or independent-subject inference.');return fig


def _embedding(data,theme,o):
    d=checked(data,['cell_id','group','x','y'],['x','y']);names=list(dict.fromkeys(d.group));pal=group_palette(theme,names)
    if d.cell_id.duplicated().any() or len(d)>5000 or len(names)>12:raise ValueError('Unique bounded stored cell coordinates required')
    fig=_new(theme,o.get('title','Cell populations in stored UMAP'),o.get('subtitle','Frozen two-dimensional embedding; point = cell'),size=(6.3,4.6));ax=fig.add_axes([.10,.15,.66,.66])
    for name in names:
        q=d[d.group==name];ax.scatter(q.x,q.y,s=o.get('point_size',5),c=pal[name],alpha=.75,lw=0,rasterized=True)
    ax.set_aspect('equal');ax.axis('off')
    positions=o.get('label_positions',{})
    if positions and set(positions)!=set(names):raise ValueError('Stored label anchors must cover each displayed group')
    for name,position in positions.items():
        if len(position)!=2 or not np.isfinite(position).all():raise ValueError('Finite explicit label anchors required')
        ax.text(*position,name,ha='center',va='center',fontsize=8,fontweight='normal',color=INK,bbox=dict(boxstyle='round,pad=.18',fc='white',ec='none',alpha=.85))
    fig.legend(handles=[Line2D([],[],ls='',marker='o',mfc=pal[n],mec='none',markersize=4,label=n) for n in names],loc='upper left',bbox_to_anchor=(.78,.77),frameon=False,fontsize=7.1,labelspacing=1)
    prefix=o.get('axis_prefix','UMAP');ax.annotate('',xy=(.20,.055),xytext=(.04,.055),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',lw=.8,color=INK));ax.annotate('',xy=(.04,.20),xytext=(.04,.055),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',lw=.8,color=INK));ax.text(.12,.015,prefix+' 1',transform=ax.transAxes,fontsize=7,color=MUTED);ax.text(.005,.15,prefix+' 2',rotation=90,transform=ax.transAxes,fontsize=7,color=MUTED)
    _foot(fig,'Stored coordinates and explicit label anchors; no embedding fit, density estimate or donor-level inference.');return fig


def _network(data,theme,o):
    if not set(data.kind)<={'node','edge'}:raise ValueError('Only explicit nodes and edges supported')
    n=checked(data[data.kind=='node'],['node_id','label','entity_type','group','x','y','area'],['x','y','area']);e=checked(data[data.kind=='edge'],['source','target','weight','sign'],['weight','sign']);names=list(dict.fromkeys(n.group));pal=group_palette(theme,names)
    if n.node_id.duplicated().any() or len(n)>80 or (n.area<=0).any() or e.duplicated(['source','target']).any() or (e.weight<=0).any() or not set(e.sign)<={-1,0,1} or (set(e.source)|set(e.target))-set(n.node_id):raise ValueError('Explicit fixed topology, positive areas and weights required')
    directed=o.get('directed',False)
    if type(directed) is not bool or (e.source==e.target).any():raise ValueError('Explicit direction and no self loops required')
    if not directed and len({tuple(sorted((a,b))) for a,b in zip(e.source,e.target)})!=len(e):raise ValueError('Duplicate undirected edge')
    if not o.get('edge_label') or not o.get('node_area_label') or not o.get('relation_semantics'):raise ValueError('Declare network units and relation semantics')
    if directed and o['relation_semantics'] in ['correlation','association','overlap']:raise ValueError('Undirected associations cannot acquire causal arrows')
    fig=_new(theme,o.get('title','Frozen relationship network'),o['relation_semantics']+'  /  '+o['edge_label'],size=(6.8,4.9));ax=fig.add_axes([.08,.13,.69,.68]);lookup=n.set_index('node_id');style=o.get('network_style','module')
    if style not in ['module','gene_term','similarity','communication']:raise ValueError('Unknown network display arrangement')
    for q in e.itertuples():
        a,b=lookup.loc[q.source],lookup.loc[q.target];color=pal[a.group] if style=='communication' else ('#ADC0CF' if q.sign>=0 else '#D9B0A1');rad=.18 if directed else .06
        ax.add_patch(FancyArrowPatch((a.x,a.y),(b.x,b.y),connectionstyle='arc3,rad='+str(rad),arrowstyle='-|>' if directed else '-',mutation_scale=7,lw=.45+1.7*q.weight,color=color,alpha=.40,shrinkA=5,shrinkB=5,zorder=1))
    for (group,kind),q in n.groupby(['group','entity_type'],sort=False):
        ax.scatter(q.x,q.y,s=q.area,c=pal[group],marker='D' if kind=='term' else 'o',ec='white',lw=.9,zorder=3)
    for q in n.itertuples():
        dx=getattr(q,'label_dx',0);dy=getattr(q,'label_dy',.075);ha=getattr(q,'label_align','center')
        if not np.isfinite(dx) or not np.isfinite(dy):raise ValueError('Finite label offsets required')
        ax.text(q.x+dx,q.y+dy,q.label,ha=ha,va='center',fontsize=7,color=INK,zorder=4,bbox=dict(fc='white',ec='none',pad=.4,alpha=.8))
    ax.margins(.23);ax.set_aspect('equal');ax.axis('off')
    fig.legend(handles=[Line2D([],[],ls='',marker='o',mfc=pal[g],mec='white',label=g,markersize=5) for g in names],loc='upper left',bbox_to_anchor=(.79,.78),frameon=False,fontsize=6.8,labelspacing=1)
    fig.legend(handles=[Line2D([],[],color='#9EB2C0',lw=.45+1.7*w,label=f'{w:g}') for w in sorted({float(e.weight.min()),float(e.weight.max())})],title='Edge weight',loc='upper left',bbox_to_anchor=(.79,.43),frameon=False,fontsize=6.5,title_fontsize=6.5,labelspacing=1)
    if style in ['gene_term','similarity']:fig.text(.81,.49,'Diamonds: terms'+('\nCircles: genes' if style=='gene_term' else ''),fontsize=6.3,color=MUTED,va='top')
    fig.text(.81,.27,'Node area\n'+o['node_area_label'],va='top',fontsize=6.5,color=MUTED,linespacing=1.5)
    _foot(fig,'Topology, coordinates and weights supplied. No layout optimization, edge inference or causal validation.');return fig


def _module(data,theme,o):
    d=checked(data,['row_id','column_id','association','pvalue'],['association','pvalue']);rows,cols=_grid(d,'row_id','column_id',o['row_order'],o['column_order']);norm=_bounds(d.association,o['association_limits'],True)
    if len(rows)>20 or len(cols)>12 or ((d.pvalue<=0)|(d.pvalue>1)).any():raise ValueError('Bounded supplied association and probability grid required')
    fig=_new(theme,o.get('title','Module–trait relationships'),o['association_definition'],size=(6.7,max(4.2,len(rows)*.39+1.8)));ax=fig.add_axes([.28,.24,.48,.53]);mat=d.pivot(index='row_id',columns='column_id',values='association').loc[rows,cols];im=ax.pcolormesh(np.arange(len(cols)+1),np.arange(len(rows)+1),mat,cmap=_cmap(theme),norm=norm,ec='white',lw=1.2)
    for i,r in enumerate(rows):
        for j,c in enumerate(cols):
            q=d[(d.row_id==r)&(d.column_id==c)].iloc[0];col='white' if abs(q.association)>.65 else INK
            ax.text(j+.5,i+.5,f'{q.association:+.2f}\n({q.pvalue:.1g})',ha='center',va='center',fontsize=6.8,color=col,linespacing=1.4)
    ax.set(xlim=(0,len(cols)),ylim=(len(rows),0));ax.set_xticks(np.arange(len(cols))+.5,cols,rotation=35,ha='right');ax.set_yticks(np.arange(len(rows))+.5,rows);ax.tick_params(length=0,labelsize=8,pad=7)
    for sp in ax.spines.values():sp.set_visible(False)
    cb=fig.colorbar(im,cax=fig.add_axes([.83,.60,.018,.17]));cb.set_label('Association',fontsize=7.5);cb.ax.tick_params(labelsize=7)
    fig.text(.82,.45,'Cell text\nAssociation\n(probability)',va='top',fontsize=6.7,color=MUTED,linespacing=1.5)
    _foot(fig,o['probability_definition']+'; module identities and independent sample context retained.');return fig


def _survival(data,theme,o):
    if not set(data.kind)<={'step','risk','censor'}:raise ValueError('Supply step, risk and censor records')
    s=checked(data[data.kind=='step'],['group','time','survival','lower','upper'],['time','survival','lower','upper']);r=checked(data[data.kind=='risk'],['group','time','at_risk'],['time','at_risk']);c=checked(data[data.kind=='censor'],['group','time','survival'],['time','survival']);names=list(dict.fromkeys(s.group));pal=group_palette(theme,names)
    if o.get('risk_convention') not in ['start_of_period','end_of_period'] or not o.get('interval_definition') or not o.get('time_label'):raise ValueError('Declare time, interval and risk convention')
    if ((s[['survival','lower','upper']]<0)|(s[['survival','lower','upper']]>1)).any().any() or ((s.lower>s.survival)|(s.upper<s.survival)).any() or (s.time<0).any():raise ValueError('Invalid frozen survival intervals')
    times=list(dict.fromkeys(r.time))
    if names!=list(dict.fromkeys(r.group)) or r.duplicated(['group','time']).any() or len(r)!=len(names)*len(times) or times!=sorted(times) or (r.at_risk<0).any() or (r.at_risk%1!=0).any() or s.duplicated(['group','time']).any():raise ValueError('Complete ordered integer risk table required')
    if len(names)>4 or (set(c.group)-set(names)) or min(times)<s.time.min() or max(times)>s.time.max():raise ValueError('Censor/risk scope must match the selected curves')
    for name in names:
        q=s[s.group==name];risk_values=r[r.group==name]
        if q.time.iloc[0]!=0 or q.survival.iloc[0]!=1 or (np.diff(risk_values.at_risk)>0).any():raise ValueError('Survival starts at one at time zero; risk counts cannot increase')
        for point in c[c.group==name].itertuples():
            if point.time<q.time.min() or point.time>q.time.max() or not np.isclose(q[q.time<=point.time].iloc[-1].survival,point.survival):raise ValueError('Censor marks must lie on the supplied post-step curve')
    fig=_new(theme,o.get('title','Survival over follow-up'),o.get('subtitle','Frozen survival estimates with supplied intervals'),size=(6.4,5.0));ax=_axis(fig,[.14,.41,.70,.39]);_flat_axis(ax,'y')
    for name in names:
        q=s[s.group==name]
        if (np.diff(q.time)<=0).any() or (np.diff(q.survival)>1e-12).any():raise ValueError('Ordered nonincreasing supplied survival steps required')
        ax.step(q.time,q.survival,where='post',color=pal[name],lw=1.65,label=name);ax.fill_between(q.time,q.lower,q.upper,step='post',color=pal[name],alpha=.14)
        q=c[c.group==name];ax.scatter(q.time,q.survival,marker='+',c=pal[name],s=15,lw=.85)
    ax.set(xlim=(s.time.min(),s.time.max()),ylim=(0,1.025),ylabel='Survival probability');ax.set_xticks(times);ax.tick_params(labelbottom=False)
    fig.legend(handles=ax.get_legend_handles_labels()[0],labels=names,loc='upper right',bbox_to_anchor=(.94,.845),ncol=len(names),frameon=False,fontsize=7.4)
    risk=fig.add_axes([.14,.20,.70,.11]);risk.set(xlim=ax.get_xlim(),ylim=(-.5,len(names)-.5));risk.axis('off')
    for i,name in enumerate(names):
        y=len(names)-i-1;risk.text(-.04,y,name,transform=risk.get_yaxis_transform(),ha='right',va='center',color=pal[name],fontsize=7)
        for q in r[r.group==name].itertuples():risk.text(q.time,y,str(int(q.at_risk)),ha='center',va='center',fontsize=7.4,color=INK)
    risk.text(0,1.25,'Number at risk',transform=risk.transAxes,fontsize=8,color=MUTED)
    axis=fig.add_axes([.14,.15,.70,.001]);axis.set_xlim(ax.get_xlim());axis.set_xticks(times);axis.set_yticks([]);axis.set_xlabel(o['time_label'],fontsize=8);_flat_axis(axis,None);axis.spines[['left','right','top']].set_visible(False)
    _foot(fig,o['interval_definition']+'; risk convention: '+o['risk_convention']+'. No survival fit or log-rank test.');return fig


def _roc(data,theme,o):
    d=checked(data,['group','x','y'],['x','y']);names=_order(d.group,o.get('order'));pal=group_palette(theme,names)
    if ((d[['x','y']]<0)|(d[['x','y']]>1)).any().any():raise ValueError('ROC coordinates must be in [0,1]')
    fig=_new(theme,o.get('title','Discrimination on a held-out cohort'),o.get('subtitle','Stored threshold coordinates; no model fitting'),size=(6.2,4.7));ax=_axis(fig,[.16,.17,.48,.62]);_flat_axis(ax,'both')
    for i,name in enumerate(names):
        q=d[d.group==name]
        if len(q)<2 or (np.diff(q.x)<0).any() or (np.diff(q.y)<0).any():raise ValueError('Preserve monotone threshold order')
        ax.step(q.x,q.y,where='post',color=pal[name],lw=1.65,ls=['-','--',':','-.'][i%4])
    ax.plot([0,1],[0,1],c='#B2BDC6',lw=.8,ls=(0,(3,3)));ax.set(xlim=(0,1),ylim=(0,1),aspect='equal',xlabel='False-positive rate',ylabel='True-positive rate');ax.set_xticks([0,.25,.5,.75,1]);ax.set_yticks([0,.25,.5,.75,1])
    auc=o.get('auc_labels',{})
    if auc and set(auc)!=set(names):raise ValueError('Supplied AUC labels must cover every model')
    fig.legend(handles=[Line2D([],[],c=pal[n],lw=1.6,ls=['-','--',':','-.'][i%4],label=n+('\n'+str(auc[n]) if auc else '')) for i,n in enumerate(names)],loc='upper left',bbox_to_anchor=(.71,.76),frameon=False,fontsize=7.2,labelspacing=1.2)
    _foot(fig,'Curves and optional AUC text supplied by the analysis host; no AUC or uncertainty calculation.');return fig


DRAW={'gsea':_gsea,'nes':_nes,'leading':_leading,'ora':_ora,'ridge':_ridge,'heatmap':_matrix,'volcano':_volcano,'forest':_forest,'dot':_dot,'embedding':_embedding,'network':_network,'module':_module,'survival':_survival,'roc':_roc}

OPTIONS={
    'gsea':'curve_order ranked_universe mode metric_label contrast gene_set_version gene_labels',
    'nes':'pathway_order contrast_order nes_limits size_max alpha',
    'leading':'pathway_order gene_order value_limits value_label',
    'ora':'term_order mode significance_max ratio_max background_definition',
    'ridge':'density_label x_label',
    'heatmap':'row_order column_order limits scale_type column_groups y_label',
    'volcano':'alpha effect_cutoff label_genes',
    'forest':'effect_scale interval_label x_label',
    'dot':'row_order column_order value_semantics denominator_label limits scale_type value_label',
    'embedding':'point_size label_positions axis_prefix',
    'network':'directed network_style relation_semantics edge_label node_area_label',
    'module':'row_order column_order association_limits association_definition probability_definition',
    'survival':'risk_convention interval_definition time_label',
    'roc':'order auc_labels'}


def plot_package_style(data,theme,*,view,contract,options):
    """Fourteen reference-informed package display grammars; frozen tables and explicit method context."""
    validate_contract(contract)
    if view not in DRAW or not isinstance(options,dict):raise ValueError('Select a registered package view and explicit drawing options')
    if set(options)-set(OPTIONS[view].split())-{'title','subtitle'}:raise ValueError('Unknown package drawing option')
    fig=DRAW[view](data,theme,copy.deepcopy(options))
    return _finish(fig,data,'package_'+view,contract,options,theme)
