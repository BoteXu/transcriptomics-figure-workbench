"""Original frozen-table QC/DE views informed by a user-supplied article.

No expression parsing, transforms, imputation, PCA, covariance, correlation,
clustering, differential tests, feature selection, interval estimation or FDR.
"""
import math
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Patch
from figure_core import checked
from figure_method_extensions import _new, _axis, _finish, _unique, _limits
from project_theme import group_palette

MODES = ('sample_boxstats', 'pca_scores', 'ma', 'deg_counts', 'pvalue_hist',
         'ranked_effects', 'radial_effects', 'deg_donut')


def _declarations(contract, fields):
    if not isinstance(contract, dict):
        raise ValueError('An explicit contract is required')
    for field in fields:
        if not isinstance(contract.get(field), str) or not contract[field].strip():
            raise ValueError('Declare ' + field)


def _numbers(data, fields):
    for field in fields:
        if pd.api.types.is_bool_dtype(data[field]):
            raise ValueError('Boolean values are not numeric observations')


def _exact_order(values, order):
    if not isinstance(order, list) or len(set(order)) != len(order) or set(order) != set(values):
        raise ValueError('Explicit display order must include every supplied identity exactly once')
    return order


def _effects(data, contract):
    d = checked(data, ['feature_id', 'effect', 'status'], ['effect'])
    _numbers(d, ['effect']); _unique(d, ['feature_id'])
    if set(d.status) - {'up', 'down', 'other', 'untested'}:
        raise ValueError('Use explicit up/down/other/untested status; unknown is not nonsignificant')
    if ((d.status == 'up') & (d.effect <= 0)).any() or ((d.status == 'down') & (d.effect >= 0)).any():
        raise ValueError('Status direction contradicts the supplied effect')
    _declarations(contract, ['effect_definition', 'status_definition', 'feature_selection'])
    return d


def _status_colors(theme):
    return {'up': theme['roles']['positive'], 'down': theme['roles']['negative'],
            'other': theme['roles']['neutral'], 'untested': '#FFFFFF'}


def _status_key(fig, colors, statuses):
    fig.legend(handles=[Patch(facecolor=colors[s], edgecolor='#59616B', label=s) for s in statuses],
               loc='upper left', bbox_to_anchor=(.78, .83), frameon=False)


def plot_frozen_qc_de(data, theme, *, mode, contract, order=None, marker_map=None, title=''):
    """Render eight bounded QC/DE modes from reviewed summaries; preserve exact input and project theme."""
    if mode not in MODES or not isinstance(data, pd.DataFrame) or not 1 <= len(data) <= 5000:
        raise ValueError('Choose a registered mode and 1-5000 reviewed summary rows')
    _declarations(contract, ['source_definition', 'independent_unit', 'denominator'])
    numeric = []
    if mode == 'sample_boxstats':
        numeric = ['q1', 'median', 'q3', 'whislo', 'whishi', 'n']
        d = checked(data, ['sample_id', 'project', *numeric], numeric); _numbers(d, numeric); _unique(d, ['sample_id'])
        order = _exact_order(d.sample_id, order)
        if ((d.whislo > d.q1) | (d.q1 > d['median']) | (d['median'] > d.q3) | (d.q3 > d.whishi)
                | (d.n <= 0) | (d.n % 1 != 0)).any():
            raise ValueError('Ordered box statistics and positive integer feature counts required')
        _declarations(contract, ['expression_scale', 'whisker_definition', 'outlier_display'])
        pal = group_palette(theme, list(pd.unique(d.project)))
        d = d.set_index('sample_id').loc[order]
        fig = _new(theme, (max(9, 3 + len(d) * .32), 5.5)); ax = _axis(fig, [.13, .30, .61, .54])
        stats = [dict(label=s, med=r['median'], q1=r.q1, q3=r.q3, whislo=r.whislo, whishi=r.whishi)
                 for s, r in d.iterrows()]
        artists = ax.bxp(stats, showfliers=False, patch_artist=True, widths=.55)
        for patch, (_, row) in zip(artists['boxes'], d.iterrows()):
            patch.set_facecolor(pal[row.project]); patch.set_alpha(.85)
        ax.tick_params(axis='x', rotation=60); ax.set_ylabel(contract['expression_scale'])
        fig.legend(handles=[Patch(color=pal[p], label=p) for p in pal], loc='upper left', bbox_to_anchor=(.77, .83), frameon=False)
    elif mode == 'pca_scores':
        if 'record_type' not in data or set(data.record_type) - {'sample', 'ellipse'}:
            raise ValueError('PCA uses sample and optional precomputed ellipse records')
        d = checked(data[data.record_type == 'sample'], ['sample_id', 'project', 'phenotype', 'x', 'y'], ['x', 'y'])
        _numbers(d, ['x', 'y']); _unique(d, ['sample_id'])
        _declarations(contract, ['axis_x', 'axis_y', 'pca_basis', 'feature_selection', 'ellipse_definition'])
        groups = list(pd.unique(d.phenotype)); projects = list(pd.unique(d.project))
        if not isinstance(marker_map, dict) or set(marker_map) != set(groups) or len(set(marker_map.values())) != len(marker_map):
            raise ValueError('Explicit distinct phenotype markers required; never cycle shapes')
        pal = group_palette(theme, projects)
        if len(set(pal.values())) != len(pal):
            raise ValueError('Projects need distinct stable colors')
        _limits(d.x, contract.get('x_limits', [])); _limits(d.y, contract.get('y_limits', []))
        fig = _new(theme, (9, 6.2)); ax = _axis(fig, [.13, .22, .59, .62])
        for (project, phenotype), subset in d.groupby(['project', 'phenotype'], sort=False):
            ax.scatter(subset.x, subset.y, c=pal[project], marker=marker_map[phenotype], s=42, ec='white', lw=.5)
        ellipses = data[data.record_type == 'ellipse']
        if len(ellipses):
            e = checked(ellipses, ['project', 'x', 'y', 'width', 'height', 'angle', 'coverage'], ['x', 'y', 'width', 'height', 'angle', 'coverage'])
            _numbers(e, ['x', 'y', 'width', 'height', 'angle', 'coverage']); _unique(e, ['project'])
            if set(e.project) - set(projects) or ((e.width <= 0) | (e.height <= 0) | (e.coverage <= 0) | (e.coverage >= 1)).any():
                raise ValueError('Valid precomputed ellipse geometry and declared coverage required')
            for r in e.itertuples():
                patch = Ellipse((r.x, r.y), r.width, r.height, angle=r.angle, fc=pal[r.project], ec=pal[r.project], alpha=.15)
                # The caller must include the entire supplied geometry, not clip an ellipse invisibly.
                vertices = patch.get_verts()
                _limits(vertices[:, 0], contract['x_limits']); _limits(vertices[:, 1], contract['y_limits'])
                ax.add_patch(patch)
        ax.set(xlabel=contract['axis_x'], ylabel=contract['axis_y'], xlim=contract['x_limits'], ylim=contract['y_limits'])
        project_key = ax.legend(handles=[Line2D([], [], marker='o', color=pal[p], ls='', label=p) for p in projects],
                                title='Project', loc='upper left', bbox_to_anchor=(1.06, 1), frameon=False)
        ax.add_artist(project_key)
        ax.legend(handles=[Line2D([], [], marker=marker_map[g], color=theme['roles']['border'], ls='', label=g) for g in groups],
                  title='Phenotype', loc='lower left', bbox_to_anchor=(1.06, 0), frameon=False)
    elif mode in {'ma', 'ranked_effects', 'radial_effects'}:
        d = _effects(data, contract); colors = _status_colors(theme)
        if mode == 'ma':
            d = checked(d, ['average', 'effect'], ['average', 'effect']); _declarations(contract, ['average_definition'])
            fig = _new(theme, (9, 5.5)); ax = _axis(fig, [.13, .23, .60, .60])
            for status in pd.unique(d.status):
                q = d[d.status == status]
                ax.scatter(q.average, q.effect, c=colors[status], ec=theme['roles']['border'] if status == 'untested' else 'none', s=18)
            ax.set(xlabel=contract['average_definition'], ylabel=contract['effect_definition']); ax.axhline(0, color=theme['roles']['border'], lw=.7)
        elif mode == 'ranked_effects':
            d = checked(d, ['rank'], ['rank']); _numbers(d, ['rank']); _unique(d, ['rank'])
            if ((d['rank'] <= 0) | (d['rank'] % 1 != 0)).any():
                raise ValueError('Use supplied unique positive integer ranks')
            _declarations(contract, ['rank_definition'])
            fig = _new(theme, (9, 5.5)); ax = _axis(fig, [.13, .23, .60, .60])
            for status in pd.unique(d.status):
                q = d[d.status == status]; ax.scatter(q['rank'], q.effect, c=colors[status], s=18, ec='none')
            ax.set(xlabel=contract['rank_definition'], ylabel=contract['effect_definition']); ax.axhline(0, color=theme['roles']['border'], lw=.7)
        else:
            order = _exact_order(d.feature_id, order); d = d.set_index('feature_id').loc[order]
            fig = _new(theme, (9, 7)); ax = fig.add_axes([.10, .20, .60, .62], projection='polar')
            angles = np.arange(len(d)) * 2 * math.pi / len(d)
            ax.bar(angles, d.effect.abs(), width=2 * math.pi / len(d) * .76, bottom=0,
                   color=[colors[x] for x in d.status], ec='white', lw=.5)
            ax.set_xticks(angles, order, fontsize=8); ax.set_theta_offset(math.pi / 2); ax.set_theta_direction(-1)
            ax.set_ylabel('Absolute ' + contract['effect_definition'], labelpad=30)
            if len(d) > 40:
                raise ValueError('Select an explicit reviewed <=40-feature radial view, retaining its full source index')
        _status_key(fig, colors, list(pd.unique(d.status)))
    elif mode in {'deg_counts', 'deg_donut'}:
        d = checked(data, ['status', 'count'], ['count']); _numbers(d, ['count']); _unique(d, ['status'])
        if set(d.status) != {'up', 'down', 'other', 'untested'} or ((d['count'] < 0) | (d['count'] % 1 != 0)).any():
            raise ValueError('Provide all four statuses, including untested, with nonnegative integer counts')
        _declarations(contract, ['status_definition', 'count_unit'])
        colors = _status_colors(theme); fig = _new(theme, (8, 5.5)); ax = _axis(fig, [.14, .22, .57, .61])
        if mode == 'deg_counts':
            ax.bar(d.status, d['count'], color=[colors[s] for s in d.status], ec=theme['roles']['border'], lw=.6)
            for i, r in enumerate(d.itertuples()):
                ax.annotate(str(int(r.count)), (i, r.count), xytext=(0, 5), textcoords='offset points', ha='center')
            ax.set_ylabel(contract['count_unit']); ax.margins(y=.17)
        else:
            total = int(d['count'].sum())
            if total:
                ax.pie(d['count'], colors=[colors[s] for s in d.status], startangle=90,
                       wedgeprops={'width': .28, 'edgecolor': theme['roles']['border'], 'linewidth': .5})
            else:
                ax.set(xlim=(-1, 1), ylim=(-1, 1)); ax.axis('off')
            selected = int(d.loc[d.status.isin(['up', 'down']), 'count'].sum())
            ax.text(0, .10, f'{selected} selected', ha='center', fontsize=13)
            ax.text(0, -.15, f'{total} supplied total', ha='center', fontsize=9)
            ax.set_aspect('equal')
        _status_key(fig, colors, list(d.status))
    else:
        d = checked(data, ['left', 'right', 'count'], ['left', 'right', 'count']); _numbers(d, ['left', 'right', 'count'])
        d = d.sort_values('left', kind='stable'); _unique(d, ['left'])
        if ((d.left < 0) | (d.right > 1) | (d.left >= d.right) | (d['count'] < 0) | (d['count'] % 1 != 0)).any():
            raise ValueError('Valid raw-P bins in [0,1] and integer counts required')
        if d.left.iloc[0] != 0 or d.right.iloc[-1] != 1 or not np.allclose(d.right.to_numpy()[:-1], d.left.to_numpy()[1:], rtol=0, atol=1e-12):
            raise ValueError('Histogram bins must cover [0,1] without gaps or overlap')
        _declarations(contract, ['pvalue_definition', 'bin_boundary_definition'])
        fig = _new(theme, (8, 5.5)); ax = _axis(fig, [.14, .22, .60, .61])
        ax.bar(d.left, d['count'], width=d.right - d.left, align='edge', color=theme['roles']['primary'], ec='white')
        ax.set(xlabel=contract['pvalue_definition'], ylabel='Supplied bin count', xlim=(0, 1))
    ax.set_title(title, loc='left')
    fig.text(.13, .06, 'Frozen results; ' + contract['independent_unit'] + ' | ' + contract['denominator'], fontsize=8, wrap=True)
    return _finish(fig, data, theme, 'frozen_qc_de', mode=mode, contract=contract,
                   order=order, marker_map=marker_map, title=title,
                   omitted_outliers='declared summary only' if mode == 'sample_boxstats' else 'none',
                   analysis='none; supplied coordinates, statistics, ranks, intervals and classifications only')
