"""Analysis-specific companions from frozen network/program result tables.

No networks, layouts, modules, tests, intervals, densities or trajectories are fit.
Geometry, counts and probabilities must come from explicitly selected results.
"""
import math
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, PathPatch
from matplotlib.path import Path
from figure_core import checked, stamp
from project_theme import group_palette, apply_project_style
from figure_wgcna_views import _context, _tree

MODES = ('module_size', 'hub_network', 'module_overlap', 'connectivity_change',
         'module_effects', 'module_enrichment', 'module_expression',
         'module_dynamics', 'stability', 'trait_scatter', 'projection', 'program_profile',
         'preservation_attributes', 'topology')


def _label(value, width=22):
    return '\n'.join(textwrap.wrap(str(value), width, break_long_words=False))


def _clean(ax, grid=None):
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(length=3, labelsize=10)
    if grid:
        ax.grid(axis=grid, color='#E7ECED', lw=.65, zorder=0)
        ax.set_axisbelow(True)


def _order(values, supplied):
    actual = list(dict.fromkeys(values))
    if supplied is None:
        return actual
    if not isinstance(supplied, (list, tuple)) or len(supplied) != len(set(supplied)) or set(supplied) != set(actual):
        raise ValueError('Order must contain every explicitly selected identity exactly once')
    return list(supplied)


def _facets(fig, n, columns, height=3.6, width=4.2):
    from figure_workbench.responsive import facet_slots
    cols = min(3, n) if columns == 'auto' else columns
    if cols > n:
        raise ValueError('Requested columns exceed the number of actual panels')
    rows = math.ceil(n / cols)
    fig.set_size_inches(cols * width, rows * height + .9)
    slots = facet_slots(fig, n, rows, cols)
    return [fig.add_subplot(slot) for slot in slots]


def _unique(d, keys):
    if d.duplicated(keys).any():
        raise ValueError('Duplicate scientific identity: ' + ', '.join(keys))


def _integers(d, cols, minimum=0):
    if ((d[cols] < minimum) | (d[cols] % 1 != 0)).any().any():
        raise ValueError('Actual nonnegative integer counts required: ' + ', '.join(cols))


def _prob(d, key='q'):
    if ((d[key] < 0) | (d[key] > 1)).any():
        raise ValueError('Probabilities must be finite and within [0,1]')


def _interval(d):
    if ((d.lower > d.estimate) | (d.estimate > d.upper)).any():
        raise ValueError('Supplied intervals must contain the supplied estimate')


def _cloud(ax, values, position, shape, color):
    if not isinstance(shape, dict) or set(shape) != {'grid', 'width', 'n', 'definition'}:
        raise ValueError('A frozen cloud needs grid, width, actual n and its upstream definition')
    grid = np.asarray(shape['grid'], dtype=float)
    width = np.asarray(shape['width'], dtype=float)
    if (not isinstance(shape['definition'], str) or not shape['definition'].strip()
        or type(shape['n']) is not int or shape['n'] != len(values) or len(grid) < 3
        or grid.shape != width.shape or not np.isfinite(grid).all() or not np.isfinite(width).all()
        or (np.diff(grid) <= 0).any() or (width < 0).any() or width.max() <= 0
        or grid.min() > min(values) or grid.max() < max(values)):
        raise ValueError('Cloud support, count or finite ordered geometry does not match observed units')
    if ax is not None:
        ax.fill_betweenx(grid, position - .12 - .34 * width / width.max(), position - .12,
                         color=color, alpha=.28, lw=.7, edgecolor=color, zorder=1)
    return grid


def plot_coexpression_evidence(data, theme, *, mode, title, context, definition,
                              module_order=None, columns='auto', value_label='Oriented module eigengene',
                              value_limits=None, label_genes=(), edge_semantics=None,
                              directed=False, cloud_shapes=None):
    """Coexpression, pathway/regulon and donor-level companions with exact result semantics."""
    if isinstance(context, dict) and 'network_type' in context:
        _context(context)
    else:
        required = {'independent_unit', 'independent_n', 'method_version', 'source_version', 'selection'}
        if (not isinstance(context, dict) or set(context) != required
            or any(not isinstance(context[k], str) or not context[k].strip() for k in required - {'independent_n'})
            or type(context['independent_n']) is not int or context['independent_n'] < 1
            or context['independent_unit'].casefold() in ['cell', 'cells', 'gene', 'genes', 'metacell', 'metacells', 'unknown']):
            raise ValueError('Explicit method/source versions, selection and independent biological support required')
    if mode not in MODES or not isinstance(title, str) or not title.strip() or not isinstance(definition, str) or not definition.strip():
        raise ValueError('Declare a supported mode, a question and the upstream result definition')
    if columns != 'auto' and (type(columns) is not int or not 1 <= columns <= 6):
        raise ValueError('Use auto or an explicit one to six columns')
    single = mode in ('module_size', 'hub_network', 'module_overlap', 'stability', 'topology')
    if single and columns not in ('auto', 1):
        raise ValueError('This is one complete view; use a composition for additional views')
    if not isinstance(value_label, str) or not value_label.strip():
        raise ValueError('Declare the numerical measurement and its units')
    fig = plt.figure(figsize=(10, 6), layout='constrained')
    attached_tracks = []
    topology_axes = None
    if mode == 'module_size':
        d = checked(data, ['module', 'genes', 'assigned'], ['genes', 'assigned'])
        _unique(d, ['module']); _integers(d, ['genes'], 1)
        if not d.assigned.isin([0, 1]).all():
            raise ValueError('Assigned must distinguish modules (1) from unassigned genes (0)')
        modules = _order(d.module, module_order); d = d.set_index('module').loc[modules]
        palette = group_palette(theme, modules)
        fig.set_size_inches(9, max(3.6, .44 * len(d) + 1.7)); ax = fig.subplots(); _clean(ax, 'x')
        for i, (module, row) in enumerate(d.iterrows()):
            c = palette[module] if row.assigned else '#ADB9C0'
            ax.barh(i, row.genes, height=.58, color=c, alpha=.85)
            ax.text(row.genes, i, '  ' + f'{int(row.genes):,}' + (' · unassigned' if not row.assigned else ''), va='center', fontsize=11, color='#395665')
        ax.set_yticks(range(len(d)), modules); ax.invert_yaxis(); ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
        ax.set(xlabel='Genes in the supplied module partition', xlim=(0, d.genes.max() * 1.42))
    elif mode == 'hub_network':
        if 'record_type' not in data or not set(data.record_type) <= {'node', 'edge'}:
            raise ValueError('Declare node and edge records')
        n = checked(data[data.record_type == 'node'], ['gene', 'module', 'x', 'y', 'kME'], ['x', 'y', 'kME'])
        e = checked(data[data.record_type == 'edge'], ['source', 'target', 'weight'], ['weight'])
        _unique(n, ['gene']); _unique(e, ['source', 'target'])
        if type(directed) is not bool or not isinstance(edge_semantics, str) or not edge_semantics.strip():
            raise ValueError('Declare edge evidence and its direction; coexpression is not PPI or regulation')
        if (n.kME.abs() > 1).any() or (e.weight <= 0).any() or (e.source == e.target).any() or (set(e.source) | set(e.target)) - set(n.gene):
            raise ValueError('Valid supplied nodes, positive weights and matching nonself edges required')
        if not directed and len({tuple(sorted((str(a), str(b)))) for a, b in zip(e.source, e.target)}) != len(e):
            raise ValueError('An undirected edge may only appear once')
        if len(label_genes) != len(set(label_genes)) or len(label_genes) > 30 or set(label_genes) - set(n.gene):
            raise ValueError('Select at most thirty actual labels, without duplicates')
        modules = _order(n.module, module_order); palette = group_palette(theme, modules); nodes = n.set_index('gene')
        fig.set_size_inches(9.2, 6.4); ax = fig.subplots()
        for row in e.itertuples():
            a, b = nodes.loc[row.source], nodes.loc[row.target]
            color = palette[a.module] if a.module == b.module else '#AEBCC3'
            patch = FancyArrowPatch((a.x, a.y), (b.x, b.y), arrowstyle='-|>' if directed else '-',
                                    mutation_scale=11, shrinkA=9, shrinkB=9,
                                    connectionstyle='arc3,rad=.08', lw=.5 + 1.7 * row.weight / e.weight.max(), color=color, alpha=.25, zorder=1)
            ax.add_patch(patch)
        for module in modules:
            q = n[n.module == module]
            ax.scatter(q.x, q.y, s=35 + 170 * q.kME.abs(), color=palette[module], alpha=.9, edgecolors='white', lw=.8, label=module, zorder=3)
        for row in n[n.gene.isin(label_genes)].itertuples():
            ax.annotate(row.gene, (row.x, row.y), xytext=(7, 7), textcoords='offset points', fontsize=10, color='#355365', zorder=5)
        ax.margins(.18); ax.set_aspect('equal', adjustable='box'); ax.axis('off')
        ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), frameon=False, title='Supplied identities', markerscale=.7, fontsize=10)
        fig.text(.5, .02, f'{len(n)} selected nodes · {len(e)} supplied edges · point area scaled by |kME|', ha='center', fontsize=10, color='#647885')
    elif mode == 'module_overlap':
        d = checked(data, ['reference', 'query', 'count'], ['count']); _unique(d, ['reference', 'query']); _integers(d, ['count'])
        refs = _order(d.reference, module_order); queries = list(dict.fromkeys(d['query']))
        if len(d) != len(refs) * len(queries) or d['count'].sum() <= 0:
            raise ValueError('Supply the full selected intersection grid, including explicit zero counts')
        palette = group_palette(theme, refs); total = d['count'].sum(); gap = .025 * total
        left = {r: int(d.loc[d.reference == r, 'count'].sum()) for r in refs}; right = {r: int(d.loc[d['query'] == r, 'count'].sum()) for r in queries}
        if min(left.values()) <= 0 or min(right.values()) <= 0:
            raise ValueError('Each displayed partition must contain at least one gene')
        fig.set_size_inches(10, max(5.5, .65 * max(len(refs), len(queries)) + 1.9)); ax = fig.subplots()
        yl = {}; yr = {}; pos = 0
        for key in refs: yl[key] = pos; pos += left[key] + gap
        pos = 0
        for key in queries: yr[key] = pos; pos += right[key] + gap
        lc = yl.copy(); rc = yr.copy()
        for a in refs:
            for b in queries:
                size = float(d.loc[(d.reference == a) & (d['query'] == b), 'count'].iloc[0])
                if size == 0: continue
                y0, y1 = lc[a], rc[b]
                vertices = [(0, y0), (.4, y0), (.6, y1), (1, y1), (1, y1 + size), (.6, y1 + size), (.4, y0 + size), (0, y0 + size), (0, y0)]
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
                ax.add_patch(PathPatch(Path(vertices, codes), facecolor=palette[a], alpha=.38, edgecolor='none'))
                lc[a] += size; rc[b] += size
        for keys, starts, sizes, x in [(refs, yl, left, 0), (queries, yr, right, 1)]:
            for key in keys:
                ax.plot([x, x], [starts[key], starts[key] + sizes[key]], lw=10, color=palette.get(key, '#B4C1C8'), solid_capstyle='butt')
                ax.text(x + (-.04 if x == 0 else .04), starts[key] + sizes[key] / 2, f'{key}  ·  {sizes[key]:,}', va='center', ha='right' if x == 0 else 'left', fontsize=11)
        ax.set(xlim=(-.25, 1.25), ylim=(-gap, total + max(len(refs), len(queries)) * gap)); ax.invert_yaxis(); ax.axis('off')
        ax.set_title('Reference partition                         Query partition', fontsize=11, pad=14)
    elif mode == 'connectivity_change':
        d = checked(data, ['gene', 'module', 'k_reference', 'k_query', 'estimate', 'lower', 'upper'], ['k_reference', 'k_query', 'estimate', 'lower', 'upper'])
        _unique(d, ['gene']); _interval(d)
        if (d[['k_reference', 'k_query']] < 0).any().any(): raise ValueError('Connectivity must be nonnegative')
        modules = _order(d.module, module_order); palette = group_palette(theme, modules); axes = _facets(fig, 2, columns, height=max(4, .31 * len(d)), width=5)
        a, b = axes; _clean(a); _clean(b, 'x'); upper = float(d[['k_reference', 'k_query']].to_numpy().max()) * 1.12
        a.plot([0, upper], [0, upper], color='#ABBAC3', ls='--', lw=1)
        for module in modules:
            q = d[d.module == module]; a.scatter(q.k_reference, q.k_query, s=52, color=palette[module], edgecolors='white', lw=.7, label=module)
        a.set(xlabel='Reference connectivity', ylabel='Query connectivity', xlim=(0, upper), ylim=(0, upper)); a.set_title('Same selected genes', loc='left', fontweight='bold', fontsize=12)
        a.legend(frameon=False, fontsize=10)
        for i, row in enumerate(d.itertuples()):
            b.plot([row.lower, row.upper], [i, i], color=palette[row.module], lw=2.2)
            b.scatter(row.estimate, i, s=45, c=palette[row.module], ec='white', lw=.6, zorder=3)
        b.axvline(0, c='#9EAEB8', ls='--', lw=1); b.set_yticks(range(len(d)), d.gene); b.invert_yaxis(); b.spines['left'].set_visible(False); b.tick_params(axis='y', length=0)
        b.set_xlabel(value_label); b.set_title('Supplied effects and intervals', loc='left', fontweight='bold', fontsize=12)
    elif mode == 'module_effects':
        d = checked(data, ['module', 'contrast', 'estimate', 'lower', 'upper', 'q', 'n'], ['estimate', 'lower', 'upper', 'q', 'n'])
        _unique(d, ['module', 'contrast']); _interval(d); _prob(d); _integers(d, ['n'], 1)
        if (d.n > context['independent_n']).any(): raise ValueError('Effective independent n exceeds declared support')
        modules = _order(d.module, module_order); contrasts = list(dict.fromkeys(d.contrast)); palette = group_palette(theme, modules)
        if len(d) != len(modules) * len(contrasts): raise ValueError('Explicit complete module/contrast grid required')
        axes = _facets(fig, len(contrasts), columns, height=max(3.6, .43 * len(modules) + 1.3), width=5.6)
        low, high = min(0, d.lower.min()), max(0, d.upper.max()); span = max(high - low, .1)
        for ax, contrast in zip(axes, contrasts):
            q = d[d.contrast == contrast].set_index('module').loc[modules]; _clean(ax, 'x')
            for i, (module, row) in enumerate(q.iterrows()):
                if i % 2 == 0: ax.axhspan(i - .43, i + .43, color='#F3F6F6', zorder=0)
                ax.plot([row.lower, row.upper], [i, i], c=palette[module], lw=2.4, solid_capstyle='round')
                ax.scatter(row.estimate, i, s=58, c=palette[module], ec='white', lw=.8, zorder=3)
                ax.text(high + .10 * span, i, f'q {row.q:.2g} · n={int(row.n)}', fontsize=10, va='center', color='#536C7A')
            ax.axvline(0, c='#9FAEB8', ls='--', lw=1); ax.set_yticks(range(len(modules)), [_label(m,20) for m in modules]); ax.invert_yaxis(); ax.set_ylim(len(modules) - .5, -.5)
            ax.set_xlim(low - .08 * span, high + .53 * span); ax.set_xlabel(_label(value_label,32)); ax.set_title(_label(contrast, 34), loc='left', fontweight='bold', fontsize=12); ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
    elif mode == 'module_enrichment':
        required = ['module', 'term', 'overlap', 'query_size', 'term_size', 'universe', 'q']
        d = checked(data, required, required[2:]); _unique(d, ['module', 'term']); _integers(d, required[2:-1]); _prob(d)
        if ((d.overlap > d.query_size) | (d.overlap > d.term_size) | (d.query_size > d.universe) | (d.term_size > d.universe) | (d.query_size < 1) | (d.term_size < 1) | (d.overlap < d.query_size + d.term_size - d.universe)).any():
            raise ValueError('Explicit tested universe, query and term counts must bound all overlaps')
        if d.groupby('module').query_size.nunique().max() != 1 or d.universe.nunique() != 1:
            raise ValueError('Each module needs one tested query size and this comparison needs one common universe')
        modules = _order(d.module, module_order); palette = group_palette(theme, modules); terms = list(dict.fromkeys(d.term))
        fig.set_size_inches(max(7, .9 * len(modules) + 4.5), max(4, .50 * len(terms) + 2)); ax = fig.subplots(); _clean(ax)
        strength = -np.log10(np.maximum(d.q, 1e-300)); norm = Normalize(0, max(2, float(strength.max()))); cmap = LinearSegmentedColormap.from_list('program_q', ['#DDECE6', '#529D93', '#285B77'])
        for i, module in enumerate(modules):
            q = d[d.module == module]
            for row in q.itertuples():
                j = terms.index(row.term); sc = ax.scatter(i, j, s=950 * row.overlap / row.query_size, c=[-math.log10(max(row.q, 1e-300))], cmap=cmap, norm=norm, edgecolors='white', lw=.7)
                ax.text(i + .17, j, str(int(row.overlap)), va='center', fontsize=9, color='#3A5B68')
        ax.set_xticks(range(len(modules)), modules); ax.set_yticks(range(len(terms)), [_label(t, 31) for t in terms]); ax.invert_yaxis(); ax.set_xlim(-.55, len(modules) - .35); ax.spines[:].set_visible(False); ax.tick_params(length=0)
        ax.set_xlabel('Module · numerals show supporting gene counts')
        ax.legend(handles=[ax.scatter([],[],s=950*p,c='#84ADA5',ec='white',lw=.7,label=f'{p:.0%}') for p in [.05,.15,.30]],
                  title='Overlap / tested module genes',loc='upper center',bbox_to_anchor=(.5,-.17),ncols=3,frameon=False,fontsize=10)
        fig.colorbar(sc, ax=ax, shrink=.65, label='−log10 supplied adjusted P')
    elif mode == 'module_expression':
        d = checked(data, ['record_type', 'module', 'unit', 'gene', 'group', 'value'], ['value'])
        if not set(d.record_type) <= {'gene', 'eigengene'}: raise ValueError('Supply gene and oriented eigengene records')
        _unique(d, ['record_type', 'module', 'unit', 'gene'])
        if d.unit.nunique() > context['independent_n'] or d.groupby('unit').group.nunique().max() != 1:
            raise ValueError('Units must retain stable group identity and fit declared donor support')
        modules = _order(d.module, module_order); groups = list(dict.fromkeys(d.group)); palette = group_palette(theme, groups)
        cols = min(2, len(modules)) if columns == 'auto' else columns
        if cols > len(modules): raise ValueError('More columns than modules')
        rows = math.ceil(len(modules) / cols); fig.set_size_inches(cols * 5.1, rows * 4.8 + 1)
        from figure_workbench.responsive import facet_slots
        slots = facet_slots(fig, len(modules), rows, cols)
        cmap = LinearSegmentedColormap.from_list('frozen_expression', theme['continuous']['diverging'])
        limits = value_limits
        if not limits or len(limits) != 2 or not all(np.isfinite(limits)) or limits[0] >= limits[1] or ((d[d.record_type == 'gene'].value < limits[0]) | (d[d.record_type == 'gene'].value > limits[1])).any():
            raise ValueError('Declare a common scale containing every supplied scaled gene value; drawing never standardizes')
        units = list(dict.fromkeys(d.unit))
        for module, slot in zip(modules, slots):
            q = d[d.module == module]; g = q[q.record_type == 'gene']; me = q[q.record_type == 'eigengene']; genes = list(dict.fromkeys(g.gene))
            if len(g) != len(units) * len(genes) or set(g.unit) != set(units) or len(me) != len(units) or set(me.unit) != set(units):
                raise ValueError('Complete selected gene-by-unit matrix and exactly one eigengene per unit required')
            inner = slot.subgridspec(3, 1, height_ratios=[.18, 2.4, 1.1], hspace=.08)
            track = fig.add_subplot(inner[0]); heat = fig.add_subplot(inner[1]); profile = fig.add_subplot(inner[2])
            ordered = g.pivot(index='gene', columns='unit', values='value').reindex(index=genes, columns=units)
            lookup = me.set_index('unit').loc[units]; track.imshow(np.array([[plt.matplotlib.colors.to_rgba(palette[x]) for x in lookup.group]]), aspect='auto'); track.axis('off'); track.set_title(module, loc='left', fontweight='bold', fontsize=12)
            im = heat.imshow(ordered, cmap=cmap, vmin=limits[0], vmax=limits[1], aspect='auto'); heat.set_xticks([]); heat.set_yticks(range(len(genes)), genes); heat.tick_params(length=0, labelsize=9); heat.spines[:].set_visible(False)
            attached_tracks.append((track,heat))
            profile.bar(range(len(units)), lookup.value, color=[palette[x] for x in lookup.group], width=.8); profile.axhline(0, c='#A7B7BF', lw=.7); _clean(profile)
            step = max(1, math.ceil(len(units) / 12)); profile.set_xticks(range(0, len(units), step), units[::step], rotation=90); profile.set_xlim(-.5, len(units) - .5); profile.set_ylabel('Eigengene', fontsize=10)
            fig.colorbar(im, ax=[heat, profile], shrink=.65, label=value_label)
        fig.legend(handles=[Line2D([], [], c=c, lw=5, label=g) for g, c in palette.items()], loc='outside lower center', ncols=len(groups), frameon=False, fontsize=10)
    elif mode == 'module_dynamics':
        d = checked(data, ['module', 'branch', 'position', 'estimate', 'lower', 'upper', 'n'], ['position', 'estimate', 'lower', 'upper', 'n']); _unique(d, ['module', 'branch', 'position']); _interval(d); _integers(d, ['n'], 1)
        if (d.n > context['independent_n']).any(): raise ValueError('Effective independent n exceeds declared support')
        modules = _order(d.module, module_order); branches = list(dict.fromkeys(d.branch)); palette = group_palette(theme, branches); axes = _facets(fig, len(modules), columns)
        low,high=float(d.lower.min()),float(d.upper.max());pad=max((high-low)*.06,.05)
        for ax, module in zip(axes, modules):
            _clean(ax, 'y')
            for branch in branches:
                q = d[(d.module == module) & (d.branch == branch)].sort_values('position')
                if len(q) < 2: raise ValueError('Every selected module/branch needs at least two supplied positions')
                ax.fill_between(q.position, q.lower, q.upper, color=palette[branch], alpha=.16, lw=0); ax.plot(q.position, q.estimate, c=palette[branch], lw=2.3, label=branch)
            ax.set(xlabel='Supplied time / progression coordinate', ylabel=value_label,ylim=(low-pad,high+pad)); ax.set_title(module, loc='left', fontsize=12, fontweight='bold')
        fig.legend(*axes[0].get_legend_handles_labels(), loc='outside lower center', ncols=min(5, len(branches)), frameon=False, fontsize=10)
    elif mode == 'stability':
        d = checked(data, ['module', 'setting', 'estimate', 'lower', 'upper', 'n_resamples'], ['estimate', 'lower', 'upper', 'n_resamples']); _unique(d, ['module', 'setting']); _interval(d); _integers(d, ['n_resamples'], 1)
        if ((d.lower < 0) | (d.upper > 1)).any(): raise ValueError('Stability intervals must be in [0,1]')
        modules = _order(d.module, module_order); settings = list(dict.fromkeys(d.setting)); palette = group_palette(theme, modules)
        if len(d) != len(modules) * len(settings): raise ValueError('Complete module/setting grid required; missing is not zero')
        fig.set_size_inches(max(7, len(settings) * 1.1 + 3), 5); ax = fig.subplots(); _clean(ax, 'y')
        for j, module in enumerate(modules):
            q = d[d.module == module].set_index('setting').loc[settings]; x = np.arange(len(settings)) + (j - (len(modules) - 1) / 2) * .035
            ax.plot(x, q.estimate, c=palette[module], lw=1.4, alpha=.8); ax.errorbar(x, q.estimate, yerr=[q.estimate - q.lower, q.upper - q.estimate], fmt='o', color=palette[module], lw=1, capsize=2, ms=5, mec='white', mew=.5, label=module)
        ax.set_xticks(range(len(settings)), [_label(x, 14) for x in settings]); ax.set(xlabel='Prespecified upstream sensitivity setting', ylabel=value_label, ylim=(-.03, 1.03)); ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), frameon=False, fontsize=10)
    elif mode == 'trait_scatter':
        d = checked(data, ['module', 'unit', 'group', 'trait', 'eigengene'], ['trait', 'eigengene']); _unique(d, ['module', 'unit'])
        if d.unit.nunique() > context['independent_n'] or d.groupby('unit').group.nunique().max() != 1 or d.groupby('unit').trait.nunique().max() != 1:
            raise ValueError('Stable donor identities, traits and group assignments required')
        modules = _order(d.module, module_order); palette = group_palette(theme, list(dict.fromkeys(d.group))); axes = _facets(fig, len(modules), columns)
        for ax, module in zip(axes, modules):
            _clean(ax); q = d[d.module == module]
            for group, color in palette.items():
                z = q[q.group == group]; ax.scatter(z.trait, z.eigengene, c=color, s=42, alpha=.8, ec='white', lw=.6, label=group); ax.plot(z.trait, np.full(len(z), .018), '|', c=color, ms=5, transform=ax.get_xaxis_transform())
            ax.set(xlabel=value_label, ylabel='Supplied oriented eigengene'); ax.set_title(module + ' · n=' + str(len(q)), loc='left', fontsize=12, fontweight='bold')
            low,high=float(d.eigengene.min()),float(d.eigengene.max());pad=max((high-low)*.08,.05);ax.set_ylim(low-pad,high+pad)
        fig.legend(*axes[0].get_legend_handles_labels(), loc='outside lower center', ncols=min(5, len(palette)), frameon=False, fontsize=10)
    elif mode == 'projection':
        d = checked(data, ['module', 'cohort', 'retained_genes', 'tested_genes', 'estimate', 'lower', 'upper', 'n'], ['retained_genes', 'tested_genes', 'estimate', 'lower', 'upper', 'n']); _unique(d, ['module', 'cohort']); _interval(d); _integers(d, ['retained_genes', 'tested_genes', 'n'])
        if ((d.tested_genes < 1) | (d.n < 1) | (d.retained_genes > d.tested_genes) | (d.lower < -1) | (d.upper > 1) | (d.n > context['independent_n'])).any(): raise ValueError('Declared gene coverage, valid correlations and effective n required')
        modules = _order(d.module, module_order); palette = group_palette(theme, modules); axes = _facets(fig, 2, columns, height=max(3.1, len(d) * .40), width=5.4)
        a, b = axes; _clean(a, 'x'); _clean(b, 'x')
        for i, row in enumerate(d.itertuples()):
            a.barh(i, row.retained_genes / row.tested_genes, height=.58, color=palette[row.module], alpha=.8); a.text(row.retained_genes / row.tested_genes, i, f'  {int(row.retained_genes)}/{int(row.tested_genes)}', va='center', fontsize=10)
            b.plot([row.lower, row.upper], [i, i], c=palette[row.module], lw=2.3); b.scatter(row.estimate, i, s=48, c=palette[row.module], ec='white', lw=.6); b.text(1.05, i, f'n={int(row.n)}', va='center', fontsize=10)
        labels=[r.module + ' · ' + r.cohort for r in d.itertuples()]
        for ax in axes: ax.set_yticks(range(len(d)), labels); ax.set_ylim(len(d)-.5,-.5); ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
        a.set(xlabel='Retained / tested reference genes', xlim=(0, 1.36)); b.set(xlabel=value_label, xlim=(-1.05, 1.38)); b.axvline(0, c='#9EAFB9', lw=1, ls='--')
    elif mode == 'program_profile':
        d = checked(data, ['module', 'unit', 'group', 'value'], ['value']); _unique(d, ['module', 'unit'])
        if d.unit.nunique() > context['independent_n'] or d.groupby('unit').group.nunique().max() != 1: raise ValueError('Each independent unit must have one stable group identity')
        modules = _order(d.module, module_order); groups = list(dict.fromkeys(d.group)); palette = group_palette(theme, groups); axes = _facets(fig, len(modules), columns, width=4)
        if cloud_shapes is None: raise ValueError('Raincloud default requires frozen cloud shapes; drawing never fits density')
        if set(cloud_shapes) != set(modules): raise ValueError('Cloud keys must cover exactly the selected programs')
        if value_limits is not None and (len(value_limits) != 2 or not all(np.isfinite(value_limits)) or value_limits[0] >= value_limits[1] or ((d.value < value_limits[0]) | (d.value > value_limits[1])).any()):
            raise ValueError('The declared measurement limits must contain every observed value')
        grids=[]
        for module in modules:
            observed=d[d.module==module]
            if not isinstance(cloud_shapes[module],dict) or set(cloud_shapes[module])!=set(observed.group):raise ValueError('Cloud keys must cover exactly the observed groups')
            for group,shape in cloud_shapes[module].items():grids.append(_cloud(None,observed.loc[observed.group==group,'value'].to_numpy(),0,shape,'#000000'))
        grid_low=min(float(g.min()) for g in grids);grid_high=max(float(g.max()) for g in grids)
        for ax, module in zip(axes, modules):
            _clean(ax, 'y'); q = d[d.module == module]
            if set(cloud_shapes[module]) != set(q.group): raise ValueError('Cloud keys must cover exactly the observed groups')
            for i, group in enumerate(groups):
                z = q[q.group == group]; values = z.value.to_numpy()
                if len(values) < 1: raise ValueError('A selected module/group is missing; missing is not zero')
                _cloud(ax, values, i, cloud_shapes[module][group], palette[group])
                ax.boxplot([values], positions=[i], widths=.11, patch_artist=True, showfliers=False, boxprops=dict(fc='white', ec=palette[group], lw=1.2), medianprops=dict(c=palette[group], lw=1.5), whiskerprops=dict(c=palette[group]), capprops=dict(c=palette[group]))
                xx = i + .13 + (np.arange(len(values)) * .61803398875 % 1) * .19
                ax.scatter(xx, values, s=24, c=palette[group], ec='white', lw=.4, alpha=.8, zorder=3)
            ax.set_xticks(range(len(groups)), [_label(x, 14) for x in groups]); ax.set_ylabel(value_label); ax.set_title(module + ' · ' + str(len(q)) + ' units', loc='left', fontsize=12, fontweight='bold'); ax.set_xlim(-.6, len(groups) - .5)
            if value_limits is not None: ax.set_ylim(*value_limits)
            else:ax.set_ylim(grid_low-(grid_high-grid_low)*.03,grid_high+(grid_high-grid_low)*.03)
    elif mode == 'preservation_attributes':
        d = checked(data, ['module', 'attribute', 'probability', 'permutations'], ['probability', 'permutations']); _unique(d, ['module', 'attribute']); _prob(d, 'probability'); _integers(d, ['permutations'], 1)
        modules = _order(d.module, module_order); attrs = list(dict.fromkeys(d.attribute))
        if len(d) != len(modules) * len(attrs): raise ValueError('Complete selected attributes required; do not average probabilities or fill missing attributes')
        fig.set_size_inches(max(8, len(attrs) * 1.25 + 2.5), max(4, len(modules) * .6 + 2)); ax = fig.subplots()
        values = d.pivot(index='module', columns='attribute', values='probability').reindex(index=modules, columns=attrs)
        strength = -np.log10(np.maximum(values.to_numpy(), 1e-300)); cmap = LinearSegmentedColormap.from_list('preservation_q', ['#F1F6F4', '#6AA99F', '#275D78'])
        im = ax.imshow(strength, cmap=cmap, vmin=0, vmax=max(2, float(strength.max())), aspect='auto')
        for i in range(len(modules)):
            for j in range(len(attrs)):
                ax.text(j, i, f'{values.iloc[i,j]:.2g}', ha='center', va='center', fontsize=11, color='white' if strength[i,j] > .65 * max(2, strength.max()) else '#345A65')
        ax.set_xticks(range(len(attrs)), [_label(x, 14) for x in attrs]); ax.set_yticks(range(len(modules)), modules); ax.tick_params(length=0); ax.spines[:].set_visible(False)
        fig.colorbar(im, ax=ax, shrink=.7, label='−log10 supplied probability · definition in source')
    elif mode == 'topology':
        if 'record_type' not in data or not set(data.record_type) <= {'leaf', 'merge', 'matrix'}:
            raise ValueError('Supply frozen leaf/merge hierarchy and complete matrix records')
        leaves, segments, order = _tree(data, None)
        d = checked(data[data.record_type == 'matrix'], ['a', 'b', 'value'], ['value']); _unique(d, ['a', 'b'])
        if set(d.a) != set(order) or set(d.b) != set(order) or len(d) != len(order)**2:
            raise ValueError('Matrix must cover exactly every frozen tree leaf pair')
        matrix = d.pivot(index='a', columns='b', values='value').reindex(index=order, columns=order).to_numpy()
        if (matrix < 0).any() or (matrix > 1).any() or not np.allclose(matrix, matrix.T, atol=1e-8, rtol=0):
            raise ValueError('Supply an explicitly symmetric [0,1] topological-overlap matrix')
        modules = _order(leaves.module, module_order); palette = group_palette(theme, modules)
        n = len(order); fig.set_size_inches(8.5, 8.8); grid = fig.add_gridspec(3, 3, height_ratios=[1.8, .22, 7], width_ratios=[.22, 7, .3], hspace=.01, wspace=.02)
        tree = fig.add_subplot(grid[0,1]); tree.add_collection(LineCollection(segments, colors='#80959F', linewidths=.8)); tree.autoscale_view(); tree.set_xlim(0,n); tree.axis('off')
        colors=np.array([[plt.matplotlib.colors.to_rgba(palette[x]) for x in leaves.module]])
        top=fig.add_subplot(grid[1,1]);top.imshow(colors,aspect='auto');top.axis('off')
        left=fig.add_subplot(grid[2,0]);left.imshow(colors.transpose(1,0,2),aspect='auto');left.axis('off')
        ax=fig.add_subplot(grid[2,1]);cmap=LinearSegmentedColormap.from_list('annotated_TOM',['#F6F9F7','#D6E8DD','#71B4A4','#285C77'])
        im=ax.imshow(matrix,aspect='auto',vmin=0,vmax=1,cmap=cmap,interpolation='nearest')
        show=n<=35;step=1 if show else max(1,math.ceil(n/25));ticks=list(range(0,n,step))
        ax.set_xticks(ticks,[order[i] for i in ticks],rotation=90);ax.set_yticks([]);ax.tick_params(length=0,labelsize=9);ax.spines[:].set_visible(False)
        for i in ticks:ax.text(-.055,i,order[i],transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=9)
        bar=fig.add_subplot(grid[2,2]);fig.colorbar(im,cax=bar,label='Supplied TOM · complete selected scope')
        fig.legend(handles=[Line2D([],[],c=c,lw=5,label=m) for m,c in palette.items()],loc='outside lower center',ncols=min(6,len(modules)),frameon=False,fontsize=10)
        topology_axes=(tree,top,left,ax,bar)
    fig.suptitle(title, fontsize=15, fontweight='bold')
    fig.get_layout_engine().set(h_pad=.18, w_pad=.22, hspace=.14, wspace=.20)
    for ax in fig.axes:
        ax._explicit_guide_layout = True
        if len(ax.get_ylabel())>35:ax.set_ylabel(_label(ax.get_ylabel(),30))
        if len(ax.get_xlabel())>45:ax.set_xlabel(_label(ax.get_xlabel(),42))
    stamp(fig, data, 'coexpression_' + mode, mode=mode, title=title, context=context,
          definition=definition, module_order=module_order, columns=columns,
          value_label=value_label, value_limits=value_limits, label_genes=list(label_genes),
          edge_semantics=edge_semantics, directed=directed, cloud_shapes=cloud_shapes,
          analysis_performed=False)
    fig=apply_project_style(fig, theme)
    if attached_tracks or topology_axes:
        fig.canvas.draw();fig.set_layout_engine(None)
        for track,heat in attached_tracks:
            box=heat.get_position();track.set_position([box.x0,box.y1+.009,box.width,.020])
        if topology_axes:
            tree,top,left,ax,bar=topology_axes
            ax.set_position([.19,.16,.62,.55]);left.set_position([.168,.16,.014,.55]);top.set_position([.19,.718,.62,.014]);tree.set_position([.19,.741,.62,.15]);bar.set_position([.85,.16,.019,.55])
    return fig
