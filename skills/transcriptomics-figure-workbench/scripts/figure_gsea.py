"""Dedicated GSEA/ORA display routes from exported results; no enrichment calculation."""
import textwrap
import numpy as np
from matplotlib import colors, ticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from figure_core import checked
from figure_editorial import _canvas, _axis, _finish, _order, validate_contract, INK, MUTED, GRID
from project_theme import group_palette


def _done(fig, data, theme, kind, contract, **options):
    fig._editorial_font = theme['font_family']
    return _finish(fig, data, kind, contract, options, theme)


def _required_text(**values):
    if any(not isinstance(v, str) or not v.strip() for v in values.values()):
        raise ValueError('Declare ' + ', '.join(values))


def _gsea_input(data, order, universe):
    d = checked(data, ['kind'])
    if not set(d.kind) <= {'curve', 'hit', 'metric', 'summary'}:
        raise ValueError('Only frozen curve/hit/metric/summary records are supported')
    curve = checked(d[d.kind == 'curve'], ['pathway', 'rank', 'value'], ['rank', 'value'])
    hit = checked(d[d.kind == 'hit'], ['pathway', 'rank', 'gene', 'leading_edge'], ['rank', 'leading_edge'])
    metric = checked(d[d.kind == 'metric'], ['rank', 'value'], ['rank', 'value'])
    summary = checked(d[d.kind == 'summary'], ['pathway', 'NES', 'padj', 'set_size'], ['NES', 'padj', 'set_size'])
    pathways = _order(curve.pathway, order)
    if not 1 <= len(pathways) <= 500 or type(universe) is not int or universe < 3:
        raise ValueError('Select complete pathways within the render budget and an explicit integer universe')
    if summary.pathway.duplicated().any() or set(summary.pathway) != set(pathways) or set(hit.pathway) != set(pathways):
        raise ValueError('Every selected pathway needs one summary and its actual hit positions')
    if curve.duplicated(['pathway', 'rank']).any() or hit.duplicated(['pathway', 'rank']).any() or hit.duplicated(['pathway', 'gene']).any():
        raise ValueError('Duplicate curve coordinate or hit identity')
    if not set(hit.leading_edge) <= {0, 1} or (hit['rank'] % 1 != 0).any():
        raise ValueError('Leading-edge flags must be supplied 0/1; hit ranks must be integers')
    expected = np.arange(1, universe + 1)
    if len(metric) != universe or not np.array_equal(metric['rank'], expected):
        raise ValueError('Export the complete ordered ranked metric, not only DEGs or hits')
    if ((summary.padj < 0) | (summary.padj > 1) | (summary.set_size < 1) | (summary.set_size % 1 != 0)).any():
        raise ValueError('Invalid supplied adjusted probability or intersected set size')
    for pathway in pathways:
        c, h = curve[curve.pathway == pathway], hit[hit.pathway == pathway]
        s = summary[summary.pathway == pathway].iloc[0]
        if len(c) != universe or not np.array_equal(c['rank'], expected) or not set(h['rank']) <= set(expected):
            raise ValueError('Each curve and metric must share the same complete rank axis; no interpolation')
        if len(h) != int(s.set_size) or abs(float(c.iloc[-1].value)) > 1e-6:
            raise ValueError('Hit count must equal intersected set size; supplied curve must end at zero')
        peak = float(c.loc[c.value.abs().idxmax(), 'value'])
        if peak == 0 or np.sign(peak) != np.sign(s.NES):
            raise ValueError('Supplied NES direction disagrees with the dominant running-score extremum')
    return curve, hit, metric, summary.set_index('pathway'), pathways


def plot_gsea_tracks(data, theme, *, contract, curve_order, ranked_universe,
                     metric_label, contrast, gene_set_version, mode='classic',
                     title='Gene set enrichment', show_leading_edge=True,
                     ncols='auto',nrows=None,panel_width=4.2,panel_height=3.6):
    """GSEA classic/overlay/facets: exact running ES, hit rugs, rank metric and supplied NES/FDR."""
    validate_contract(contract)
    _required_text(metric_label=metric_label, contrast=contrast, gene_set_version=gene_set_version)
    if mode not in {'classic', 'overlay', 'facets'} or type(show_leading_edge) is not bool:
        raise ValueError('Choose classic, overlay or facets and an explicit leading-edge display')
    curve, hit, metric, summary, pathways = _gsea_input(data, curve_order, ranked_universe)
    if mode == 'classic' and len(pathways) != 1:
        raise ValueError('Classic mode shows exactly one selected pathway')
    if mode=='facets':
        from figure_workbench.responsive import gsea_facets
        options=dict(ncols=ncols,nrows=nrows,panel_width=panel_width,panel_height=panel_height,metric_label=metric_label,contrast=contrast,gene_set_version=gene_set_version,ranked_universe=ranked_universe,title=title,show_leading_edge=show_leading_edge)
        fig=gsea_facets(curve,hit,metric,summary,pathways,theme,options)
        return _done(fig,data,theme,'gsea_tracks',contract,mode=mode,curve_order=pathways,**options)
    pal = group_palette(theme, pathways)
    n = len(pathways)
    fig = _canvas(theme, (7.1, 5.4 if mode != 'facets' else 5.0 + .65 * n), title)
    note = 'Contrast: ' + contrast + '  |  ' + str(ranked_universe) + ' ranked genes'
    fig.text(.13, .878, note, fontsize=7.6, color=MUTED)
    label_rows = []
    for name in pathways:
        s = summary.loc[name]
        label_rows.append(f'{name}\nNES {s.NES:+.2f}\nFDR {s.padj:.2g}  ·  n={int(s.set_size)}')
    for i, label in enumerate(label_rows):
        fig.text(.785, .80 - i * .115, '\n'.join(textwrap.wrap(label.split('\n')[0], 22)) + '\n' + '\n'.join(label.split('\n')[1:]),
                 fontsize=7.1, color=pal[pathways[i]], va='top', linespacing=1.5)
    axes = []
    if mode == 'facets':
        bottom, span, gap = .51, .30, .025
        for i, pathway in enumerate(pathways):
            ax = _axis(fig, [.13, bottom + (n-i-1)*span/n, .61, span/n-gap])
            c = curve[curve.pathway == pathway]
            ax.plot(c['rank'], c.value, color=pal[pathway], lw=1.45)
            ax.axhline(0, color='#A9B2BA', lw=.6)
            ax.tick_params(axis='x', labelbottom=False)
            ax.set_xlim(1, ranked_universe);ax.yaxis.set_major_locator(ticker.MaxNLocator(3))
            axes.append(ax)
        fig.text(.035, .66, 'Running ES', rotation=90, fontsize=9, va='center', color=INK)
    else:
        ax = _axis(fig, [.13, .52, .61, .29])
        for pathway in pathways:
            c = curve[curve.pathway == pathway]
            ax.plot(c['rank'], c.value, color=pal[pathway], lw=1.55)
        ax.axhline(0, color='#A9B2BA', lw=.6)
        ax.set(xlim=(1, ranked_universe), ylabel='Running ES')
        ax.tick_params(axis='x', labelbottom=False);axes.append(ax)
    rug = fig.add_axes([.13, .375, .61, .105])
    for i, pathway in enumerate(pathways):
        h = hit[hit.pathway == pathway]
        rug.vlines(h['rank'], n-i-1+.1, n-i-.25, color=pal[pathway], lw=.8, alpha=.6)
        if show_leading_edge:
            lead = h[h.leading_edge == 1]
            rug.vlines(lead['rank'], n-i-1+.1, n-i-.25, color=pal[pathway], lw=1.8)
    rug.set(xlim=(1, ranked_universe), ylim=(0, n));rug.axis('off')
    fig.text(.785, .40, 'Hits\nBold = supplied\nleading edge' if show_leading_edge else 'Supplied hits', fontsize=7.1, color=MUTED, linespacing=1.5)
    bottom = _axis(fig, [.13, .155, .61, .16])
    bottom.fill_between(metric['rank'], 0, metric.value, where=metric.value >= 0, color=theme['roles']['positive'], alpha=.5, interpolate=True)
    bottom.fill_between(metric['rank'], 0, metric.value, where=metric.value <= 0, color=theme['roles']['negative'], alpha=.5, interpolate=True)
    bottom.plot(metric['rank'], metric.value, color='#687681', lw=.65)
    bottom.axhline(0, color='#A9B2BA', lw=.5)
    bottom.set(xlim=(1, ranked_universe), xlabel='Rank in complete ordered list', ylabel=metric_label)
    bottom.xaxis.set_major_locator(ticker.MaxNLocator(5, integer=True))
    fig.text(.13, .042, '\n'.join(textwrap.wrap('Gene sets: '+gene_set_version+'; exact supplied scores/hits; no GSEA recomputation.', 100)), fontsize=6.8, color=MUTED)
    return _done(fig, data, theme, 'gsea_tracks', contract, mode=mode, curve_order=pathways,
                 ranked_universe=ranked_universe, metric_label=metric_label, contrast=contrast,
                 gene_set_version=gene_set_version, show_leading_edge=show_leading_edge,
                 analysis_boundary='ES, NES, adjusted probability and leading edge supplied; no inference or smoothing')


def plot_gsea_nes(data, theme, *, contract, pathway_order, contrast_order, nes_limits,
                  alpha=.05, size_max=200, title='Pathway enrichment across contrasts'):
    """Signed NES dot matrix; explicit not_tested cells and supplied FDR outlines."""
    validate_contract(contract)
    d = checked(data, ['pathway', 'contrast', 'status'])
    rows, columns = _order(d.pathway, pathway_order), _order(d.contrast, contrast_order)
    if d.duplicated(['pathway','contrast']).any() or len(d) != len(rows)*len(columns):
        raise ValueError('Complete selected pathway/contrast grid required')
    if not set(d.status) <= {'reported','not_tested'}:
        raise ValueError('Use reported or not_tested; nonsignificant is not missing')
    z = checked(d[d.status == 'reported'], ['NES','padj','set_size'], ['NES','padj','set_size'])
    if not 0 < alpha < 1 or not 0 < size_max or not nes_limits[0] < 0 < nes_limits[1]:
        raise ValueError('Declare FDR cutoff, size maximum and diverging NES limits')
    if ((z.padj < 0)|(z.padj > 1)|(z.set_size <= 0)|(z.set_size % 1 != 0)|(z.set_size > size_max)|(z.NES < nes_limits[0])|(z.NES > nes_limits[1])).any():
        raise ValueError('Metrics exceed declared NES/size/probability limits')
    if d[d.status == 'not_tested'][['NES','padj','set_size']].notna().any().any():
        raise ValueError('Untested cells cannot have invented NES/FDR/size')
    height = max(3.3, len(rows)*.33+1.5)
    fig = _canvas(theme, (max(7.1,len(columns)*.7+4),height), title);ax = _axis(fig,[.32,.24,.38,.56])
    norm = colors.TwoSlopeNorm(vmin=nes_limits[0],vcenter=0,vmax=nes_limits[1])
    cmap = colors.LinearSegmentedColormap.from_list('gsea_nes',theme['continuous']['diverging'])
    for i,p in enumerate(rows):
        for j,c in enumerate(columns):
            row = d[(d.pathway == p)&(d.contrast == c)].iloc[0]
            if row.status == 'not_tested':
                ax.text(j,i,'×',ha='center',va='center',color='#9AA6AF',fontsize=8)
            else:
                ax.scatter(j,i,s=180*row.set_size/size_max,c=[cmap(norm(row.NES))],edgecolors=INK if row.padj <= alpha else '#B4BDC5',linewidths=1.0 if row.padj <= alpha else .5)
    ax.set_xticks(range(len(columns)),columns,rotation=30,ha='right');ax.set_yticks(range(len(rows)),['\n'.join(textwrap.wrap(x,24)) for x in rows])
    ax.set(xlim=(-.5,len(columns)-.5),ylim=(len(rows)-.5,-.5));ax.tick_params(length=0,pad=7)
    for spine in ax.spines.values():spine.set_visible(False)
    from matplotlib.cm import ScalarMappable
    cbar=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=fig.add_axes([.77,.57,.018,.20]));cbar.set_label('Supplied NES',fontsize=8);cbar.ax.tick_params(labelsize=7)
    fig.text(.77,.40,f'Dark outline: FDR ≤ {alpha:g}\n×  Not tested',fontsize=7.3,color=MUTED,linespacing=1.6,va='top')
    sizes=[max(1,int(size_max/4)),int(size_max)]
    fig.legend(handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(180*k/size_max),markerfacecolor='#B4BDC5',markeredgecolor='#81909D',label=str(k)) for k in sizes],title='Set size (area)',loc='upper left',bbox_to_anchor=(.76,.26),frameon=False,fontsize=7,title_fontsize=7,labelspacing=.8)
    fig.text(.32,.045,'Selected terms; no enrichment, clustering or automatic top-term selection.',fontsize=6.8,color=MUTED)
    return _done(fig,data,theme,'gsea_nes',contract,pathway_order=rows,contrast_order=columns,nes_limits=nes_limits,alpha=alpha,size_max=size_max)


def plot_gsea_leading_edge(data, theme, *, contract, pathway_order, gene_order,
                          value_label, value_limits, title='Leading-edge membership and effect'):
    """Explicit complete gene/set membership map; missing membership is not inferred."""
    validate_contract(contract);_required_text(value_label=value_label)
    d=checked(data,['pathway','gene','member','leading_edge','value'],['member','leading_edge','value'])
    rows,cols=_order(d.pathway,pathway_order),_order(d.gene,gene_order)
    if d.duplicated(['pathway','gene']).any() or len(d)!=len(rows)*len(cols):
        raise ValueError('Complete bounded selected gene/set grid required')
    if not set(d.member)<= {0,1} or not set(d.leading_edge)<= {0,1} or (d.leading_edge>d.member).any():
        raise ValueError('Leading edge must be a supplied subset of pathway membership')
    if (d.groupby('gene').value.nunique()!=1).any() or not value_limits[0]<0<value_limits[1] or ((d.value<value_limits[0])|(d.value>value_limits[1])).any():
        raise ValueError('Consistent gene effects within declared diverging limits required')
    width=max(6.5,len(cols)*.34+3);height=max(3.4,len(rows)*.35+1.6)
    fig=_canvas(theme,(width,height),title);ax=_axis(fig,[.27,.30,.47,.47])
    cmap=colors.LinearSegmentedColormap.from_list('leading_edge',theme['continuous']['diverging']);norm=colors.TwoSlopeNorm(vmin=value_limits[0],vcenter=0,vmax=value_limits[1])
    for i,p in enumerate(rows):
        for j,g in enumerate(cols):
            row=d[(d.pathway==p)&(d.gene==g)].iloc[0]
            if row.member:
                ax.scatter(j,i,s=60 if row.leading_edge else 30,c=[cmap(norm(row.value))],edgecolors=INK if row.leading_edge else 'none',linewidths=.8)
            else:ax.scatter(j,i,s=7,c='#E5E9ED',marker='.')
    ax.set_xticks(range(len(cols)),cols,rotation=55,ha='right');ax.set_yticks(range(len(rows)),['\n'.join(textwrap.wrap(x,23)) for x in rows]);ax.set(xlim=(-.5,len(cols)-.5),ylim=(len(rows)-.5,-.5));ax.tick_params(length=0,pad=6)
    for spine in ax.spines.values():spine.set_visible(False)
    from matplotlib.cm import ScalarMappable
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=fig.add_axes([.80,.56,.018,.20]));cb.set_label(value_label,fontsize=8);cb.ax.tick_params(labelsize=7)
    fig.text(.80,.35,'Outlined = leading edge\nFilled = other member\nFaint dot = nonmember',fontsize=7.1,color=MUTED,linespacing=1.7,va='top')
    fig.text(.27,.045,'Supplied subset and gene effects; blank/unknown membership is rejected.',fontsize=6.8,color=MUTED)
    return _done(fig,data,theme,'gsea_leading_edge',contract,pathway_order=rows,gene_order=cols,value_label=value_label,value_limits=value_limits)


def plot_ora_terms(data, theme, *, contract, term_order, background_definition,
                   mode='bubble', ratio_max=1, significance_max=8,
                   title='Selected over-representation results'):
    """ORA bubble/lollipop with exact numerator/denominator, no GSEA/ORA conflation."""
    validate_contract(contract);_required_text(background_definition=background_definition)
    d=checked(data,['term','count','query_size','padj'],['count','query_size','padj']);order=_order(d.term,term_order)
    if mode not in {'bubble','lollipop'} or d.term.duplicated().any():raise ValueError('Select unique ORA terms and bubble/lollipop mode')
    if ((d['count']<=0)|(d['count']%1!=0)|(d.query_size<=0)|(d.query_size%1!=0)|(d['count']>d.query_size)|(d.padj<=0)|(d.padj>1)).any():raise ValueError('Positive exact ORA counts, query denominators and adjusted p required')
    if d.query_size.nunique()!=1 or not 0<ratio_max<=1 or not significance_max>0:raise ValueError('A shared selected-query denominator and declared scales are required')
    d=d.set_index('term').loc[order];ratio=d['count']/d.query_size;strength=-np.log10(d.padj)
    if (ratio>ratio_max).any() or (strength>significance_max).any():raise ValueError('Declared scale would clip ORA values')
    fig=_canvas(theme,(6.7,max(3.4,len(d)*.32+1.5)),title);ax=_axis(fig,[.38,.23,.35,.56]);y=np.arange(len(d))
    cmap=colors.LinearSegmentedColormap.from_list('ora',theme['continuous']['sequential']);norm=colors.Normalize(0,significance_max)
    if mode=='lollipop':ax.hlines(y,0,ratio,color='#C7D1DB',lw=1.5)
    ax.scatter(ratio,y,s=160*d['count']/d['count'].max(),c=strength,cmap=cmap,norm=norm,edgecolors='#81909D',lw=.45,zorder=3)
    ax.set_yticks(y,['\n'.join(textwrap.wrap(t,26)) for t in order]);ax.set(xlim=(0,ratio_max),ylim=(len(d)-.5,-.5),xlabel='Gene ratio (count / selected query)');ax.tick_params(axis='y',length=0,pad=6);ax.xaxis.set_major_locator(ticker.MaxNLocator(4));ax.spines['left'].set_visible(False)
    from matplotlib.cm import ScalarMappable
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=fig.add_axes([.82,.55,.018,.22]));cb.set_label('−log10 adjusted P',fontsize=8);cb.ax.tick_params(labelsize=7)
    fig.legend(handles=[Line2D([],[],ls='',marker='o',markersize=np.sqrt(160*k/d['count'].max()),markerfacecolor='#CCD4DB',markeredgecolor='#81909D',label=str(int(k))) for k in sorted(set([d['count'].min(),d['count'].max()]))],title='Count (area)',loc='upper left',bbox_to_anchor=(.80,.42),frameon=False,fontsize=7,title_fontsize=7,labelspacing=1)
    fig.text(.38,.045,'Query n='+str(int(d.query_size.iloc[0]))+'; '+ '\n'.join(textwrap.wrap(background_definition,65)),fontsize=6.8,color=MUTED)
    return _done(fig,data,theme,'ora_terms',contract,term_order=order,mode=mode,ratio_max=ratio_max,significance_max=significance_max,background_definition=background_definition)
