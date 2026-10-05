"""Optional, newly authored figure variants. No inference or implicit selection."""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from figure_core import checked, palette_check, stamp, canvas

INK = '#28323C'
COLORS = {'Down': '#35618F', 'Up': '#B84E35', 'Below cutoffs': '#BFC5CB'}

def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Explicit nonempty axis/denominator description required')

def plot_volcano_editorial(data, *, labels=(), alpha=.05, fc=1):
    d = checked(data, ['gene', 'log2FC', 'padj'], ['log2FC', 'padj'])
    if d.gene.duplicated().any() or ((d.padj <= 0) | (d.padj > 1)).any():
        raise ValueError('Unique genes and padj in (0,1] required')
    if not (0 < alpha < 1 and np.isfinite(fc) and fc > 0):
        raise ValueError('Invalid thresholds')
    labels = list(labels)
    if len(set(labels)) != len(labels) or not set(labels).issubset(d.gene):
        raise ValueError('Labels must be unique, explicitly supplied existing genes')
    if any(len(str(x)) > 24 for x in labels):
        raise ValueError('Long labels need a separate annotation layout')
    d['evidence'] = -np.log10(d.padj)
    d['status'] = np.where((d.padj <= alpha) & (d.log2FC >= fc), 'Up',
                   np.where((d.padj <= alpha) & (d.log2FC <= -fc), 'Down', 'Below cutoffs'))
    chosen = d[d.gene.isin(labels)]
    if any(sum((chosen.log2FC < 0) == side) > 6 for side in [True, False]):
        raise ValueError('At most six labels per side; use a companion table for more')
    fig, ax = canvas(); fig.set_size_inches(7.8, 4.8)
    extent = max(d.log2FC.abs().max(), fc * 1.3)
    top = max(d.evidence.max(), -np.log10(alpha)) * 1.18
    ax.axhline(-np.log10(alpha), color='#929AA1', ls='--', lw=.7)
    for x in [-fc, fc]: ax.axvline(x, color='#929AA1', ls='--', lw=.7)
    handles = []
    for status in ['Below cutoffs', 'Down', 'Up']:
        sub = d[d.status == status]
        ax.scatter(sub.log2FC, sub.evidence, s=15 if status == 'Below cutoffs' else 25,
                   c=COLORS[status], marker='o', alpha=.45 if status == 'Below cutoffs' else .9,
                   linewidths=0, rasterized=True)
        handles.append(Line2D([], [], ls='', marker='o', color=COLORS[status],
                              label=f'{status} ({len(sub)})'))
    for sign in [-1, 1]:
        sub = chosen[(chosen.log2FC < 0) == (sign < 0)].sort_values('evidence')
        positions = np.linspace(top * .44, top * .88, len(sub))
        for row, y in zip(sub.itertuples(), positions):
            ax.annotate(str(row.gene), xy=(row.log2FC, row.evidence),
                        xytext=(sign * extent * 1.17, y), ha='right' if sign < 0 else 'left',
                        va='center', color=INK, fontsize=9, fontweight='normal',
                        arrowprops=dict(arrowstyle='-', lw=.6, color='#B8C1C7'))
            ax.scatter([row.log2FC], [row.evidence], s=42, facecolors='none', edgecolors='#B8C1C7', lw=.7)
    ax.set(xlim=(-extent * 1.75, extent * 1.75), ylim=(-top * .02, top),
           xlabel='log2 fold change', ylabel='-log10(adjusted p)',
           title=f'Labels supplied explicitly | FDR <= {alpha:g}; |log2FC| >= {fc:g}')
    ticks = np.linspace(-extent, extent, 5)
    ax.set_xticks(ticks, [f'{x:.1f}' for x in ticks]); ax.tick_params(axis='x', labelsize=9)
    ax.legend(handles=handles, frameon=True, framealpha=1, edgecolor='none', facecolor='white',
              loc='upper center', ncols=3, fontsize=8)
    return stamp(fig, data, 'volcano_editorial', alpha=alpha, fc=fc, labels=labels,
                 label_layout='fixed side lanes; points unchanged', palette=COLORS,
                 point_count=len(d), status_counts=d.status.value_counts().to_dict())

def plot_volcano_marginal(data, *, labels=(), alpha=.05, fc=1, x_bins=42, y_bins=36):
    """Circular-point volcano with count histograms of the same displayed genes."""
    d = checked(data, ['gene', 'log2FC', 'padj'], ['log2FC', 'padj'])
    if d.gene.duplicated().any() or ((d.padj <= 0) | (d.padj > 1)).any():
        raise ValueError('Unique genes and padj in (0,1] required')
    if not (0 < alpha < 1 and np.isfinite(fc) and fc > 0):
        raise ValueError('Invalid thresholds')
    if not (isinstance(x_bins, int) and isinstance(y_bins, int) and
            8 <= x_bins <= 200 and 8 <= y_bins <= 200):
        raise ValueError('Histogram bins must be integers in [8,200]')
    labels = list(labels)
    if len(set(labels)) != len(labels) or not set(labels).issubset(d.gene):
        raise ValueError('Labels must be unique, explicitly supplied existing genes')
    if len(labels) > 6 or any(len(str(x)) > 24 for x in labels):
        raise ValueError('At most six short labels; use a companion table for more')
    d['evidence'] = -np.log10(d.padj)
    d['status'] = np.where((d.padj <= alpha) & (d.log2FC >= fc), 'Up',
                   np.where((d.padj <= alpha) & (d.log2FC <= -fc), 'Down', 'Below cutoffs'))
    palette = {'Down': '#9AC65B', 'Up': '#E58B7D', 'Below cutoffs': '#92999D'}
    order = ['Below cutoffs', 'Down', 'Up']
    extent = max(float(d.log2FC.abs().max()) * 1.08, fc * 1.3)
    top = max(float(d.evidence.max()) * 1.04, float(-np.log10(alpha)) * 1.3)
    fig = plt.figure(figsize=(8.1, 7.3), layout='constrained')
    grid = fig.add_gridspec(2, 2, width_ratios=[5.2, 1.25],
                            height_ratios=[1.15, 5.2], wspace=.035, hspace=.035)
    ax_top = fig.add_subplot(grid[0, 0])
    ax = fig.add_subplot(grid[1, 0], sharex=ax_top)
    ax_right = fig.add_subplot(grid[1, 1], sharey=ax)
    ax_key = fig.add_subplot(grid[0, 1]); ax_key.axis('off')
    fig._omics_axes = {'main': ax, 'top_histogram': ax_top,
                       'right_histogram': ax_right, 'legend': ax_key}
    ax.axhline(-np.log10(alpha), color='#8C9398', ls=(0, (4, 4)), lw=1)
    for x in (-fc, fc):
        ax.axvline(x, color='#8C9398', ls=(0, (4, 4)), lw=1)
    for status in order:
        sub = d[d.status == status]
        ax.scatter(sub.log2FC, sub.evidence, marker='o',
                   s=13 if status == 'Below cutoffs' else 19,
                   color=palette[status], alpha=.46 if status == 'Below cutoffs' else .8,
                   linewidths=0, rasterized=True)
    x_edges = np.linspace(-extent, extent, x_bins + 1)
    y_edges = np.linspace(0, top, y_bins + 1)
    ax_top.hist([d.loc[d.status == s, 'log2FC'] for s in order], bins=x_edges,
                stacked=True, color=[palette[s] for s in order],
                edgecolor='#BBC3C8', linewidth=.45)
    ax_right.hist([d.loc[d.status == s, 'evidence'] for s in order], bins=y_edges,
                  stacked=True, orientation='horizontal',
                  color=[palette[s] for s in order], edgecolor='#BBC3C8', linewidth=.45)
    for row in d[d.gene.isin(labels)].itertuples():
        ax.scatter([row.log2FC], [row.evidence], s=52, facecolors='none',
                   edgecolors='#B8C1C7', linewidths=1, zorder=5)
        ax.annotate(str(row.gene), xy=(row.log2FC, row.evidence),
                    xytext=(9 if row.log2FC >= 0 else -9, 8), textcoords='offset points',
                    ha='left' if row.log2FC >= 0 else 'right', fontsize=9,
                    color='#52616C', fontweight='semibold',
                    arrowprops=dict(arrowstyle='-', color='#B8C1C7', lw=.7))
    ax.set(xlim=(-extent, extent), ylim=(0, top),
           xlabel='log2 fold change', ylabel='-log10(adjusted p)')
    ax.grid(color='#E8EBED', lw=.65); ax.set_axisbelow(True)
    for side in ('top', 'right'): ax.spines[side].set_visible(False)
    for marginal in (ax_top, ax_right):
        marginal.spines[['top', 'right']].set_visible(False)
        marginal.grid(False)
    ax_top.tick_params(axis='x', labelbottom=False, bottom=False)
    ax_top.tick_params(axis='y', labelleft=False, left=False)
    ax_right.tick_params(axis='y', labelleft=False, left=False)
    ax_right.tick_params(axis='x', labelbottom=False, bottom=False)
    ax_top.set_ylabel('Gene count / bin', fontsize=8)
    ax_right.set_xlabel('Gene count / bin', fontsize=8)
    handles = [Line2D([], [], ls='', marker='o', markersize=6,
                      color=palette[s], label=f'{s}  {sum(d.status == s):,}') for s in order]
    ax_key.legend(handles=handles, title='FDR <= %.2g; |log2FC| >= %g' % (alpha, fc),
                  loc='center', frameon=False, fontsize=8, title_fontsize=8,
                  handletextpad=.25, borderaxespad=0)
    return stamp(fig, data, 'volcano_marginal', alpha=alpha, fc=fc,
                 labels=labels, palette=palette, point_marker='circle',
                 point_count=len(d), status_counts=d.status.value_counts().to_dict(),
                 histogram_universe='all displayed genes; stacked categories',
                 x_histogram_bins=x_bins, y_histogram_bins=y_bins,
                 x_limits=[-extent, extent], y_limits=[0, top])

def plot_enrichment_lollipop(data, *, score_type, denominator_label, count_label):
    d = checked(data, ['term', 'score', 'padj', 'count'], ['score', 'padj', 'count'])
    _text(denominator_label); _text(count_label)
    if score_type not in ('NES', 'GeneRatio'): raise ValueError('score_type must be NES or GeneRatio')
    if d.term.duplicated().any() or len(d) > 20: raise ValueError('Unique terms, at most 20 per panel; explicitly subset upstream')
    if ((d.padj <= 0) | (d.padj > 1)).any() or ((d['count'] < 1) | (d['count'] % 1 != 0)).any():
        raise ValueError('padj in (0,1] and positive integer counts required')
    if score_type == 'GeneRatio' and ((d.score < 0) | (d.score > 1)).any():
        raise ValueError('GeneRatio must be a fraction')
    fig, ax = canvas(); fig.set_size_inches(8.4, max(4.6, len(d) * .43 + 1.6))
    y = np.arange(len(d)); evidence = -np.log10(d.padj)
    cmap = LinearSegmentedColormap.from_list('evidence', ['#CAD9E8', '#3F7CA6', '#173F70'])
    norm = Normalize(0, max(evidence.max(), 1e-9))
    ax.axvline(0, lw=.8, color='#929AA1')
    ax.hlines(y, 0, d.score, color='#D9E1E7', lw=2, zorder=1)
    area_max = 170
    dots = ax.scatter(d.score, y, c=evidence, cmap=cmap, norm=norm,
                      s=d['count'] / d['count'].max() * area_max, edgecolors=INK, lw=.45, zorder=2)
    ax.set_yticks(y, [textwrap.fill(str(x), 31) for x in d.term]); ax.invert_yaxis()
    ax.set(xlabel=score_type, title=denominator_label)
    if score_type == 'GeneRatio':
        from matplotlib.ticker import PercentFormatter
        ax.set_xlim(0, max(d.score.max() * 1.15, .05)); ax.xaxis.set_major_formatter(PercentFormatter(1))
    else: ax.margins(x=.16)
    ax.grid(axis='x', color='#EDF0F2', lw=.7); ax.set_axisbelow(True)
    fig.colorbar(dots, ax=ax, label='-log10(FDR)', fraction=.04, pad=.04)
    breaks = np.unique(np.rint(np.linspace(d['count'].min(), d['count'].max(), 3))).astype(int)
    handles = [ax.scatter([], [], s=x/d['count'].max()*area_max, color='#6B8EA9', edgecolors=INK,
                          lw=.45, label=str(x)) for x in breaks]
    ax.legend(handles=handles, title=count_label, frameon=False, loc='upper left',
              bbox_to_anchor=(1.22, 1), fontsize=8, title_fontsize=8)
    return stamp(fig, data, 'enrichment_lollipop', score_type=score_type,
                 denominator_label=denominator_label, count_label=count_label,
                 color='-log10(FDR); sequential; zero included', area='count; zero anchored',
                 selection='all supplied rows; first appearance order', score_baseline=0)

def plot_composition_panels(data, palette, *, unit_label, y_max=1):
    d = checked(data, ['sample', 'group', 'celltype', 'count'], ['count']); _text(unit_label)
    palette_check(d.group, palette)
    if d.duplicated(['sample', 'celltype']).any() or ((d['count'] < 0) | (d['count'] % 1 != 0)).any():
        raise ValueError('Unique sample/celltype rows and nonnegative integer counts required')
    if d.groupby('sample', sort=False).group.nunique().max() != 1:
        raise ValueError('Sample group assignment is inconsistent')
    types = list(pd.unique(d.celltype)); groups = list(pd.unique(d.group))
    if len(d) != d['sample'].nunique() * len(types): raise ValueError('Explicit complete sample x celltype grid required, including zeros')
    if len(types) > 12 or len(groups) > 4: raise ValueError('Split large panels explicitly; do not hide categories')
    denom = d.groupby('sample', sort=False)['count'].transform('sum')
    if (denom <= 0).any(): raise ValueError('Zero denominator')
    d['fraction'] = d['count'] / denom
    if not (np.isfinite(y_max) and 0 < y_max <= 1 and y_max >= d.fraction.max()):
        raise ValueError('Shared y_max must include all fractions and be in (0,1]')
    ncols = min(3, len(types)); nrows = int(np.ceil(len(types) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(max(5.2, ncols*2.65), nrows*2.7+1),
                             squeeze=False, sharey=True, layout='constrained')
    samples = {g: list(pd.unique(d.loc[d.group == g, 'sample'])) for g in groups}
    offsets = {s: x for g in groups for s, x in zip(samples[g], np.linspace(-.13, .13, len(samples[g])) if len(samples[g])>1 else [0])}
    markers = ['o', 's', '^', 'D']
    for ax, celltype in zip(axes.flat, types):
        sub = d[d.celltype == celltype]
        for i, g in enumerate(groups):
            z = sub[sub.group == g]
            ax.scatter([i+offsets[s] for s in z['sample']], z.fraction, color=palette[g],
                       marker=markers[i], s=32, edgecolors='white', lw=.35, zorder=3)
        ax.set_xticks(range(len(groups)), [f'{textwrap.fill(str(g), 12)}\nn={len(samples[g])}' for g in groups], fontsize=8)
        ax.set(title=str(celltype), ylim=(0, y_max*1.04), xlim=(-.5, len(groups)-.5))
        ticks=np.linspace(0, y_max, 5); ax.set_yticks(ticks, [f'{t*100:g}%' for t in ticks])
        ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', color='#E8EDF1', lw=.7)
    for ax in list(axes.flat)[len(types):]: ax.set_visible(False)
    fig.supylabel('Fraction of all supplied cells per sample\nEach point = '+unit_label, fontsize=10)
    fig.suptitle('Each point = '+unit_label, fontsize=11)
    return stamp(fig, data, 'composition_panels', palette=palette, unit_label=unit_label,
                 denominator='all supplied celltype counts per sample; no pooling', shared_y_max=y_max,
                 sample_n={str(g):len(samples[g]) for g in groups}, inference='none',
                 sample_order_offsets=offsets, marker_by_group={str(g):markers[i] for i,g in enumerate(groups)})

def plot_sample_distribution(data, palette, y_label):
    d = checked(data, ['sample_id', 'group', 'value'], ['value']); _text(y_label)
    if d.sample_id.duplicated().any(): raise ValueError('One row per independent unit required')
    palette_check(d.group, palette); groups = list(pd.unique(d.group))
    if len(groups)>6: raise ValueError('Split more than six groups into panels')
    fig, ax = canvas(); fig.set_size_inches(7.1, 4.8)
    from matplotlib.patches import Rectangle
    for i, g in enumerate(groups):
        vals = d.loc[d.group == g, 'value'].to_numpy()
        # Display-only, deterministic horizontal offsets; values are untouched.
        offsets = np.linspace(-.15, .15, len(vals)) if len(vals)>1 else np.array([0.])
        ax.scatter(i+offsets, vals, c=palette[g], s=34, edgecolors='white', lw=.4, zorder=3)
        if len(vals)>=5:
            q1, median, q3 = np.quantile(vals, [.25, .5, .75], method='linear')
            ax.add_patch(Rectangle((i+.25, q1), .16, q3-q1, facecolor=palette[g], alpha=.2, edgecolor=INK))
            ax.hlines(median, i+.23, i+.43, color=INK, lw=1.5)
    ax.set_xticks(range(len(groups)), [f'{textwrap.fill(str(g), 18)}\nn={sum(d.group==g)}' for g in groups])
    ax.set(xlim=(-.5, len(groups)-.4), ylabel=y_label, title='All observations + median / IQR (summary only when n >= 5)')
    ax.grid(axis='y', color='#EDF0F2', lw=.7); ax.set_axisbelow(True)
    return stamp(fig, data, 'sample_distribution', palette=palette, y_label=y_label,
                 summary='median and Q1-Q3; linear quantiles; only n>=5; not CI',
                 offsets='deterministic horizontal first-appearance offsets; not a density estimate',
                 sample_n={str(g):int(sum(d.group==g)) for g in groups}, inference='none')
