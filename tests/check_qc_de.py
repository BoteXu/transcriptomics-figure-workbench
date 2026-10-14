"""Frozen synthetic renderer acceptance; run in isolated CI when local memory admission is denied."""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/transcriptomics-figure-workbench/scripts'))
import matplotlib.pyplot as plt
import pandas as pd
from figure_core import export_figure
from figure_qc_de import plot_frozen_qc_de, MODES
from project_theme import create_theme


def cases():
    common = dict(source_definition='SYNTHETIC DEMO frozen summaries', independent_unit='synthetic donor', denominator='complete synthetic fixture',
                  feature_selection='predeclared fixture; no selection calculated', effect_definition='supplied log2 expression contrast',
                  status_definition='frozen upstream classifications', average_definition='supplied mean log2 expression', rank_definition='supplied effect rank',
                  count_unit='features', pvalue_definition='raw P from synthetic fixture', bin_boundary_definition='left inclusive; last right inclusive',
                  expression_scale='supplied log2 expression', whisker_definition='supplied precomputed whiskers', outlier_display='not available in supplied box summary')
    effects = pd.DataFrame(dict(feature_id=['g1', 'g2', 'g3', 'g4'], effect=[-1.2, -.1, .4, 1.1],
                                status=['down', 'untested', 'other', 'up'], average=[3., 4., 6., 5.], rank=[1, 2, 3, 4]))
    counts = pd.DataFrame(dict(status=['down', 'up', 'other', 'untested'], count=[2, 3, 20, 4]))
    box = pd.DataFrame(dict(sample_id=['s1', 's2', 's3', 's4'], project=['p1', 'p1', 'p2', 'p2'],
                            q1=[1., 1.1, 1.2, 1.3], median=[2., 2.1, 2.2, 2.3], q3=[3., 3.1, 3.2, 3.3],
                            whislo=[.5, .6, .7, .8], whishi=[3.5, 3.6, 3.7, 3.8], n=[100, 100, 100, 100]))
    pca = pd.DataFrame([dict(record_type='sample', sample_id='s' + str(i), project='p1' if i < 2 else 'p2',
                             phenotype='A' if i % 2 == 0 else 'B', x=x, y=y)
                        for i, (x, y) in enumerate([(-2., -1.), (-1., 1.), (1., -1.), (2., 1.)])]
                       + [dict(record_type='ellipse', project='p1', x=-1.5, y=0., width=2., height=3., angle=0., coverage=.95)])
    result = {}
    for mode in MODES:
        if mode == 'sample_boxstats': table = box
        elif mode == 'pca_scores': table = pca
        elif mode in {'deg_counts', 'deg_donut'}: table = counts
        elif mode == 'pvalue_hist': table = pd.DataFrame(dict(left=[0., .25, .5, .75], right=[.25, .5, .75, 1.], count=[4, 2, 3, 5]))
        else: table = effects
        contract = dict(common)
        contract.update(axis_x='PC1 (supplied 35%)', axis_y='PC2 (supplied 20%)', pca_basis='same frozen reference basis',
                        ellipse_definition='supplied Gaussian data-dispersion region, not mean CI', x_limits=[-4., 4.], y_limits=[-3., 3.])
        result[mode] = dict(data=table, mode=mode, contract=contract,
                            order=list(box.sample_id) if mode == 'sample_boxstats' else list(effects.feature_id) if mode == 'radial_effects' else None,
                            marker_map={'A': 'o', 'B': 's'} if mode == 'pca_scores' else None,
                            title='SYNTHETIC DEMO — ' + mode)
    return result


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    theme = create_theme('synthetic-qc-de', 'card_06', {'p1': 0, 'p2': 1}, font_family='DejaVu Sans')
    records = []; negative = 0
    for mode, case in cases().items():
        source = case['data'].copy(deep=True)
        fig = plot_frozen_qc_de(theme=theme, **case)
        fig.canvas.draw(); pd.testing.assert_frame_equal(source, case['data'])
        ax = fig.axes[0]
        if mode == 'ma':
            offsets = [tuple(x) for collection in ax.collections for x in collection.get_offsets()]
            assert sorted(offsets) == sorted(zip(source.average, source.effect))
        if mode == 'ranked_effects':
            offsets = [tuple(x) for collection in ax.collections for x in collection.get_offsets()]
            assert sorted(offsets) == sorted(zip(source['rank'], source.effect))
        if mode == 'radial_effects':
            assert [p.get_height() for p in ax.patches] == list(abs(source.effect))
        if mode in {'deg_counts', 'pvalue_hist'}:
            assert [p.get_height() for p in ax.patches] == list(source['count'])
        meta = {k: 'synthetic fixture' for k in ['source', 'input_unit', 'experimental_unit', 'contrast', 'denominator', 'model', 'limits', 'filtering', 'uncertainty', 'interpretation_limit']}
        meta.update(palette=theme['palette_name'], synthetic=True)
        files = export_figure(fig, source, output, 'QDE_' + mode, meta)
        record = {'id': mode, 'files': [p.relative_to(output).as_posix() for p in files],
                  'png': 'QDE_' + mode + '/QDE_' + mode + '.png', 'source_unchanged': True,
                  'geometry_checked': True, 'status': 'RENDERED_UNREVIEWED',
                  'source_sha256': hashlib.sha256((ROOT / 'skills/transcriptomics-figure-workbench/scripts/figure_qc_de.py').read_bytes()).hexdigest()}
        records.append(record); plt.close(fig)
    def reject(mode, mutate):
        nonlocal negative
        case = copy.deepcopy(cases()[mode]); mutate(case)
        try:
            fig = plot_frozen_qc_de(theme=theme, **case)
        except (ValueError, TypeError):
            negative += 1
        else:
            plt.close(fig); raise AssertionError('Invalid data accepted: ' + mode)
        finally:
            plt.close('all')
    reject('sample_boxstats', lambda c: c['data'].__setitem__('n', 0))
    reject('sample_boxstats', lambda c: c.update(order=['s1']))
    reject('ma', lambda c: c['data'].__setitem__('effect', float('nan')))
    reject('ma', lambda c: c['data'].__setitem__('effect', True))
    reject('ma', lambda c: c['data'].__setitem__('status', 'up'))
    reject('ma', lambda c: c['contract'].__setitem__('effect_definition', ''))
    reject('ranked_effects', lambda c: c['data'].__setitem__('rank', 1))
    reject('pca_scores', lambda c: c.update(marker_map={'A': 'o', 'B': 'o'}))
    reject('pca_scores', lambda c: c['contract'].__setitem__('x_limits', [-1., 1.]))
    reject('pvalue_hist', lambda c: c['data'].__setitem__('count', .5))
    reject('pvalue_hist', lambda c: c['data'].__setitem__('right', [.2, .5, .75, 1.]))
    reject('deg_counts', lambda c: c.update(data=c['data'].iloc[:3]))
    # A zero-total donut must not fabricate a unit wedge.
    case = cases()['deg_donut']; case['data']['count'] = 0
    fig = plot_frozen_qc_de(theme=theme, **case)
    assert not fig.axes[0].patches; plt.close(fig)
    receipt = {'scope': 'synthetic frozen-table software validation only', 'modes': records,
               'rejection_cases': negative, 'zero_total_no_wedge': True, 'scientific_analysis_executed': False}
    (output / 'validation.json').write_text(json.dumps(receipt, indent=2), encoding='utf8')
    html = '<!doctype html><meta charset="utf-8"><title>Frozen QC / DE modes</title><h1>SYNTHETIC DEMO — QC / DE</h1><p>Frozen summaries only; no analysis executed. Visual review is recorded separately.</p>'
    for row in records:
        html += '<h2>' + row['id'] + '</h2><a href="' + row['png'] + '"><img width="720" src="' + row['png'] + '"></a>'
    (output / 'index.html').write_text(html, encoding='utf8')
    print(json.dumps({'modes': len(records), 'rejection_cases': negative, 'passed': True}))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
