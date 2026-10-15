"""Additional frozen-result encodings; arithmetic below is display geometry only."""
import numpy as np
from matplotlib import colors, ticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from figure_core import checked
from figure_editorial import _axis, _canvas, _finish, _order, validate_contract, INK, MUTED, GRID
from project_theme import group_palette


def _done(fig, data, theme, kind, contract, **options):
    fig._editorial_font = theme['font_family']
    return _finish(fig, data, kind, contract, options, theme)


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Declare ' + label)
    return value


def _band_coordinates(x, values, width, bands):
    """Split linear display segments exactly at band boundaries before folding."""
    xx, vv = [], []
    thresholds = np.arange(-bands, bands+1)*width
    for i in range(len(x)-1):
        xx.append(float(x[i])); vv.append(float(values[i]))
        if values[i+1] == values[i]:continue
        fractions = sorted(float((t-values[i])/(values[i+1]-values[i])) for t in thresholds
                           if min(values[i],values[i+1]) < t < max(values[i],values[i+1]))
        for fraction in fractions:
            xx.append(float(x[i]+fraction*(x[i+1]-x[i])))
            vv.append(float(values[i]+fraction*(values[i+1]-values[i])))
    xx.append(float(x[-1])); vv.append(float(values[-1]))
    return np.asarray(xx), np.asarray(vv)


def plot_mosaic_counts(data, theme, *, contract, category_order=None, group_order=None,
                       title='Composition and sample size'):
    """Area mosaic: group width is total count; within-group height is count fraction."""
    validate_contract(contract)
    d = checked(data, ['group', 'category', 'count'], ['count'])
    groups = _order(d.group, group_order)
    categories = _order(d.category, category_order)
    if d.duplicated(['group', 'category']).any() or len(d) != len(groups)*len(categories):
        raise ValueError('Complete explicit contingency table required; missing is not zero')
    if ((d['count'] < 0) | (d['count'] % 1 != 0)).any() or len(groups) > 6 or len(categories) > 6:
        raise ValueError('Nonnegative integer counts; at most six groups/categories')
    table = d.pivot(index='category', columns='group', values='count').loc[categories, groups]
    totals = table.sum(axis=0)
    if (totals <= 0).any():
        raise ValueError('Each mosaic group needs a positive denominator')
    pal = group_palette(theme, categories)
    fig = _canvas(theme, (5.4, 3.5), _text(title, 'title'))
    ax = _axis(fig, [.13, .18, .82, .58])
    x = 0.
    ticks = []
    for group in groups:
        width = float(totals[group]/totals.sum())
        ticks.append(x+width/2)
        bottom = 0.
        for category in categories:
            fraction = float(table.loc[category, group]/totals[group])
            patch = Rectangle((x, bottom), width, fraction, facecolor=pal[category],
                              edgecolor='white', linewidth=1.5)
            patch.set_gid('mosaic:'+str(group)+':'+str(category))
            ax.add_patch(patch)
            bottom += fraction
        x += width
    ax.set(xlim=(0, 1), ylim=(0, 1), ylabel='Fraction within group')
    ax.set_xticks(ticks, [str(g)+'\n(n='+str(int(totals[g]))+')' for g in groups])
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(1))
    ax.set_yticks([0, .25, .5, .75, 1]); ax.tick_params(axis='x', length=0, pad=7)
    ax.spines['bottom'].set_visible(False)
    fig.legend(handles=[Patch(facecolor=pal[g], label=g) for g in categories],
               loc='upper left', bbox_to_anchor=(.115, .855), ncol=3, frameon=False,
               fontsize=7.5, columnspacing=1.8, handlelength=1.1)
    return _done(fig, data, theme, 'mosaic_counts', contract,
                 group_order=groups, category_order=categories,
                 geometry='Tile area = count / overall total; no gaps in data geometry',
                 zero_policy='Explicit zeros retained; zero area', denominator=int(totals.sum()))


def plot_waffle_counts(data, theme, *, contract, unit_label, columns=10,
                       category_order=None, title='Exact count composition'):
    """One square per declared count unit; no rounding or percentage apportionment."""
    validate_contract(contract); _text(unit_label, 'count unit')
    d = checked(data, ['category', 'count'], ['count'])
    categories = _order(d.category, category_order)
    if d.category.duplicated().any() or ((d['count'] < 0) | (d['count'] % 1 != 0)).any():
        raise ValueError('One explicit nonnegative integer count per category')
    total = int(d['count'].sum())
    if not 1 <= total <= 400 or type(columns) is not int or not 2 <= columns <= 25:
        raise ValueError('Use 1..400 exact units and 2..25 columns; do not round larger totals')
    pal = group_palette(theme, categories); rows = (total+columns-1)//columns
    fig = _canvas(theme, (5.1, max(2.9, min(5.5, rows*.17+1.2))), _text(title, 'title'))
    ax = fig.add_axes([.10, .23, .49, .56]); ax.set_aspect('equal')
    index = 0; counts = d.set_index('category')['count']
    for category in categories:
        for _ in range(int(counts[category])):
            row, col = divmod(index, columns)
            patch = Rectangle((col+.05, rows-row-.95), .9, .9, facecolor=pal[category], linewidth=0)
            patch.set_gid('waffle:'+str(category)); ax.add_patch(patch); index += 1
    ax.set(xlim=(0, columns), ylim=(0, rows)); ax.axis('off')
    fig.legend(handles=[Patch(facecolor=pal[g], label=f'{g}  {int(counts[g])}') for g in categories],
               loc='upper left', bbox_to_anchor=(.64, .79), frameon=False, fontsize=8,
               handlelength=1.0, labelspacing=1.1, borderaxespad=0)
    fig.text(.10, .10, '1 square = 1 '+unit_label+'  ·  total '+str(total), color=MUTED, fontsize=7.5)
    return _done(fig, data, theme, 'waffle_counts', contract, category_order=categories,
                 columns=columns, exact_tile_count=total, rounding='none', unit_label=unit_label)


def plot_horizon_series(data, theme, *, contract, band_width, bands=3, series_order=None,
                         x_label, y_label, title='Signed time-course overview'):
    """Fold signed magnitude into explicit bands; preserve a full linear reference panel."""
    validate_contract(contract); _text(x_label, 'time coordinate'); _text(y_label, 'measurement unit')
    d = checked(data, ['series', 'x', 'value'], ['x', 'value'])
    groups = _order(d.series, series_order)
    if type(bands) is not int or not 2 <= bands <= 4 or not np.isfinite(band_width) or band_width <= 0:
        raise ValueError('Declare 2..4 bands and a positive band width')
    if len(groups) > 5 or (d.value.abs() > bands*band_width).any() or d.duplicated(['series','x']).any():
        raise ValueError('No clipping/duplicate coordinates; at most five series')
    for group in groups:
        sub = d[d.series == group]
        if len(sub) < 2 or (np.diff(sub.x) <= 0).any():
            raise ValueError('Each stored series must be strictly ordered; no implicit sorting')
    pal = group_palette(theme, groups)
    negative = colors.to_rgb(theme['roles']['negative']); positive = colors.to_rgb(theme['roles']['positive'])
    shades = lambda rgb: [tuple(1-(1-v)*f for v in rgb) for f in np.linspace(.32, 1, bands)]
    neg_shades, pos_shades = shades(negative), shades(positive)
    height = max(3.9, .32*len(groups)+2.6)
    fig = _canvas(theme, (5.5, height), _text(title, 'title'))
    ref = _axis(fig, [.16, .59, .60, .22])
    extent = bands*band_width
    for group in groups:
        sub = d[d.series == group]
        ref.plot(sub.x, sub.value, color=pal[group], lw=1.1, label=group)
    ref.axhline(0, color='#A5AFB8', lw=.6); ref.set_ylim(-extent, extent)
    ref.set_ylabel(y_label, fontsize=8); ref.tick_params(labelsize=7.5)
    ref.set_title('Linear reference · same supplied values', fontsize=7.5, loc='left', color=MUTED)
    ref.legend(loc='upper left', bbox_to_anchor=(1.04, 1), frameon=False, fontsize=7, borderaxespad=0)
    xmin, xmax = float(d.x.min()), float(d.x.max())
    ref.set_xlim(xmin,xmax)
    for i, group in enumerate(groups):
        ax = fig.add_axes([.16, .18+(len(groups)-1-i)*.25/len(groups), .60, .235/len(groups)])
        sub = d[d.series == group]
        x, v = _band_coordinates(sub.x.to_numpy(),sub.value.to_numpy(),band_width,bands)
        # With interpolate=True every zero/band crossing is linear between frozen coordinates.
        for sign, palette in [(1, pos_shades), (-1, neg_shades)]:
            signed = sign*v
            for k in range(bands):
                h = np.clip(signed-k*band_width, 0, band_width)
                ax.fill_between(x, 0, h, where=signed >= k*band_width, interpolate=True,
                                color=palette[k], linewidth=0, zorder=1+k)
        ax.set(xlim=(xmin, xmax), ylim=(0, band_width))
        ax.set_yticks([]); ax.tick_params(axis='x', labelsize=7.5, length=2, color=MUTED)
        ax.text(-.025, .5, str(group), transform=ax.transAxes, ha='right', va='center', fontsize=8, color=INK)
        for spine in ax.spines.values():spine.set_visible(False)
        if i != len(groups)-1:ax.set_xticks([])
        else:ax.set_xlabel(x_label, fontsize=8, color=INK)
    fig.text(.16, .49, f'Folded bands · width {band_width:g}; darker = larger magnitude', fontsize=7.2, color=MUTED)
    fig.legend(handles=[Patch(facecolor=neg_shades[-1],label='Negative'),Patch(facecolor=pos_shades[-1],label='Positive')],
               loc='upper left', bbox_to_anchor=(.78, .44), frameon=False, fontsize=7.2, borderaxespad=0)
    return _done(fig, data, theme, 'horizon_series', contract, band_width=band_width, bands=bands,
                 series_order=groups, interpolation='Straight segments between supplied points; no smoothing',
                 linear_reference=True, clipping=False)


def plot_connected_scatter(data, theme, *, contract, x_label, y_label, series_order=None,
                            title='Joint response over time'):
    """Two supplied measurements linked in explicit step order, with start/end labels."""
    validate_contract(contract); _text(x_label, 'X measurement'); _text(y_label, 'Y measurement')
    d = checked(data, ['series', 'step', 'x', 'y'], ['step', 'x', 'y'])
    groups = _order(d.series, series_order)
    if len(groups) > 4 or d.duplicated(['series', 'step']).any():
        raise ValueError('Unique ordered steps and at most four series')
    pal = group_palette(theme, groups)
    fig = _canvas(theme, (4.9, 3.7), _text(title, 'title')); ax = _axis(fig, [.15, .24, .72, .56])
    for i, group in enumerate(groups):
        sub = d[d.series == group]
        if len(sub) < 2 or (np.diff(sub.step) <= 0).any():
            raise ValueError('Stored steps must increase; no implicit sorting')
        ax.plot(sub.x, sub.y, color=pal[group], lw=1.1, ls=['-','--','-.',':'][i], zorder=2)
        ax.scatter(sub.x, sub.y, s=15, c=pal[group], edgecolor='white', lw=.4, zorder=3)
        for which, offset in [(0, (-4,-10)), (-1, (5,7))]:
            row = sub.iloc[which]
            ax.annotate(f'{group} · {row.step:g}', (row.x, row.y), xytext=offset, textcoords='offset points',
                        fontsize=7, color=INK, ha='right' if which == 0 else 'left', clip_on=False)
        ax.scatter([sub.x.iloc[0]], [sub.y.iloc[0]], s=34, facecolors='white', edgecolors=pal[group], lw=1.1, zorder=4)
    ax.set(xlabel=x_label, ylabel=y_label); ax.margins(.18); ax.grid(color=GRID, lw=.5)
    fig.text(.15,.045,'Open marker = start; labels show supplied step',fontsize=7.2,color=MUTED)
    return _done(fig,data,theme,'connected_scatter',contract,series_order=groups,
                 order='Strict supplied step order; no fitted trajectory', interpolation='straight segments')


def plot_mirrored_bars(data, theme, *, contract, unit_label, left_group, right_group,
                       category_order=None, title='Two-group profile'):
    """Compare two nonnegative profiles around a common zero with exact numeric labels."""
    validate_contract(contract); _text(unit_label,'measurement unit')
    d=checked(data,['category','group','value'],['value']); categories=_order(d.category,category_order)
    if left_group == right_group or set(d.group)!={left_group,right_group} or (d.value<0).any():
        raise ValueError('Exactly two distinct groups and nonnegative values required')
    if d.duplicated(['category','group']).any() or len(d)!=2*len(categories) or len(categories)>18:
        raise ValueError('Complete paired category grid, at most 18 rows')
    pal=group_palette(theme,[left_group,right_group]);height=max(3.0,.27*len(categories)+1.25)
    fig=_canvas(theme,(5.25,height),_text(title,'title'));ax=_axis(fig,[.24,.19,.70,.58])
    table=d.pivot(index='category',columns='group',values='value').loc[categories]
    maximum=float(d.value.max())
    if maximum<=0:raise ValueError('All-zero comparison has no visible magnitude')
    y=np.arange(len(categories))
    for group,sign in [(left_group,-1),(right_group,1)]:
        vals=table[group].to_numpy()
        bars=ax.barh(y,sign*vals,height=.55,color=pal[group],linewidth=0)
        for index,(patch,v) in enumerate(zip(bars,vals)):
            patch.set_gid('mirror:'+str(categories[index])+':'+str(group))
            ax.text(sign*(v+maximum*.035),index,f'{v:g}',ha='right' if sign<0 else 'left',
                    va='center',fontsize=7.2,color=INK)
    ax.set(xlim=(-maximum*1.30,maximum*1.30),ylim=(len(categories)-.4,-.6),xlabel=unit_label)
    ax.set_yticks(y,categories);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
    ax.axvline(0,color='#72818D',lw=.7);ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos:f'{abs(x):g}'))
    fig.legend(handles=[Patch(facecolor=pal[g],label=g) for g in [left_group,right_group]],
               loc='upper left',bbox_to_anchor=(.23,.86),frameon=False,fontsize=7.5,ncol=2,handlelength=1.1)
    return _done(fig,data,theme,'mirrored_bars',contract,category_order=categories,
                 left_group=left_group,right_group=right_group,unit_label=unit_label,
                 sign_definition='Left reflects nonnegative magnitude; not negative biological values',common_scale=True)


def plot_genomic_rainfall(data, theme, *, contract, assembly, gap_definition,
                           chromosome_order=None, title='Genomic event spacing'):
    """Supplied genomic positions and precomputed positive gaps on a shared log scale."""
    validate_contract(contract);_text(assembly,'assembly');_text(gap_definition,'gap definition')
    d=checked(data,['variant_id','chromosome','position','gap','group'],['position','gap'])
    chroms=_order(d.chromosome,chromosome_order);groups=list(dict.fromkeys(d.group))
    if len(chroms)>4 or len(groups)>6 or d.variant_id.duplicated().any():raise ValueError('Bounded unique event table required')
    if ((d.position<=0)|(d.position%1!=0)|(d.gap<=0)|(d.gap%1!=0)).any():raise ValueError('Positive integer positions/gaps required; no silent log floor')
    for chrom in chroms:
        if (np.diff(d.loc[d.chromosome==chrom,'position'])<=0).any():raise ValueError('Positions must follow supplied chromosome order')
    pal=group_palette(theme,groups);fig=_canvas(theme,(6.0,3.25),_text(title,'title'))
    axes=[];width=.72/len(chroms);low=float(d.gap.min())/1.8;high=float(d.gap.max())*1.8
    for i,chrom in enumerate(chroms):
        ax=_axis(fig,[.13+i*width,.22,width-.045,.53]);axes.append(ax);sub=d[d.chromosome==chrom]
        for j,group in enumerate(groups):
            rows=sub[sub.group==group]
            ax.scatter(rows.position/1e6,rows.gap,s=17,color=pal[group],marker=['o','s','D','^','v','P'][j],
                       linewidths=.4,edgecolors='white',zorder=3)
        ax.set_yscale('log');ax.set_ylim(low,high);ax.grid(axis='y',color=GRID,lw=.5)
        ax.set_xlabel(str(chrom)+' position (Mb)',fontsize=8);ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
        ax.tick_params(axis='y',which='minor',length=0)
        if i:ax.tick_params(axis='y',which='both',labelleft=False,left=False);ax.spines['left'].set_visible(False)
        else:ax.set_ylabel('Supplied inter-event gap (bp)',fontsize=8)
    fig.legend(handles=[Line2D([],[],color=pal[g],marker=['o','s','D','^','v','P'][i],ls='',ms=4,label=g) for i,g in enumerate(groups)],
               loc='upper left',bbox_to_anchor=(.12,.865),frameon=False,ncol=min(3,len(groups)),fontsize=7.5)
    import textwrap
    caption=assembly+' · gaps supplied upstream; chromosome starts excluded upstream'
    fig.text(.13,.08,'\n'.join(textwrap.wrap(caption,100)),fontsize=6.8,color=MUTED,va='top',linespacing=1.3)
    return _done(fig,data,theme,'genomic_rainfall',contract,assembly=assembly,gap_definition=gap_definition,
                 chromosome_order=chroms,gap_calculation='none; source definition required',
                 coordinates='1-based supplied positions; displayed Mb',first_event_policy='excluded upstream; not inferred')
