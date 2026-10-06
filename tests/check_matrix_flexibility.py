"""Small positive/negative checks for flexible matrix inputs.

These checks exercise rendering contracts only; they do not calculate an
association, cluster rows, or infer missing values.
"""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'transcriptomics-figure-workbench' / 'scripts'))
from figure_core import plot_heatmap, plot_dot
from figure_general import plot_confusion_counts
from figure_publication import plot_aligned_matrix
from figure_polish import plot_polished_matrix
from figure_multimodal import plot_association_matrix
from figure_reference import plot_activity_dashboard


def close(fig):
    spec = fig._omics_spec
    plt.close(fig)
    return spec


def main():
    wide = pd.DataFrame({
        'row_id': ['r3', 'r1', 'r2'],
        'annotation': ['B', 'A', 'A'],
        'sample-02': [0.2, 0.4, 0.1],
        'sample-01': [0.5, 0.2, 0.3],
        'sample-03': [0.1, 0.8, 0.6],
    })
    spec = close(plot_heatmap(
        wide, 'supplied value', row_field='row_id',
        value_columns=['sample-02', 'sample-01', 'sample-03'],
        row_order=['r1', 'r2', 'r3'],
        column_order=['sample-03', 'sample-01', 'sample-02'],
        row_aliases={'r1': 'Row one', 'r2': 'Row two', 'r3': 'Row three'},
        column_aliases={'sample-01': 'S1', 'sample-02': 'S2', 'sample-03': 'S3'},
    ))
    assert spec['row_order'] == ['r1', 'r2', 'r3']
    assert spec['column_order'] == ['sample-03', 'sample-01', 'sample-02']
    assert spec['missing'] == 'error'
    long_labels = wide.rename(columns={'row_id': 'feature', 'sample-01': 'sample 1', 'sample-02': 'sample 2', 'sample-03': 'sample 3'})
    long_labels['feature'] = [
        'cell population with a long marker-defined identity A',
        'cell population with a long marker-defined identity B',
        'cell population with a long marker-defined identity C',
    ]
    label_spec = close(plot_heatmap(long_labels, 'value', row_field='feature', value_columns=['sample 1', 'sample 2', 'sample 3'], row_label_wrap=18))
    assert label_spec['row_label_wrap'] == 18

    long = pd.DataFrame([
        (row, col, value, block, count)
        for row, block, count in [('r1', 'A', 3), ('r2', 'A', 5), ('r3', 'B', 8), ('r4', 'B', 13)]
        for col, value in [('c1', 0.2), ('c2', -0.1), ('c3', 0.8)]
    ], columns=['gene', 'assay', 'score', 'block', 'n'])
    common = dict(row_field='gene', column_field='assay', value_field='score',
                  row_order=['r4', 'r3', 'r2', 'r1'], column_order=['c3', 'c2', 'c1'],
                  row_aliases={f'r{i}': f'R{i}' for i in range(1, 5)},
                  column_aliases={'c1': 'C1', 'c2': 'C2', 'c3': 'C3'})
    spec = close(plot_aligned_matrix(
        long, value_label='score', limits=(-1, 1), signed=True,
        row_block_field='block', row_count_field='n', block_palette={'A': '#aaccff', 'B': '#ffccaa'}, **common
    ))
    assert spec['row_order'] == ['r4', 'r3', 'r2', 'r1']
    close(plot_polished_matrix(long, value_label='score', limits=(-1, 1), signed=True,
                               row_blocks={'r4': 'B', 'r3': 'B', 'r2': 'A', 'r1': 'A'},
                               row_label_wrap=8, **common))

    dot = pd.DataFrame([
        (row, col, frac, val) for row in ['r1', 'r2', 'r3']
        for col, frac, val in [('bulk-1', .2, .4), ('bulk-2', .7, -.2)]
    ], columns=['gene_id', 'condition_id', 'detected_fraction', 'scaled_value'])
    spec = close(plot_dot(
        dot, 'scaled score', value_semantics='scaled', denominator_label='fraction of cells',
        row_field='gene_id', column_field='condition_id', fraction_field='detected_fraction', value_field='scaled_value',
        row_order=['r3', 'r2', 'r1'], column_aliases={'bulk-1': 'Bulk 1', 'bulk-2': 'Bulk 2'}, row_label_wrap=4,
    ))
    assert spec['row_order'] == ['r3', 'r2', 'r1']

    confusion = pd.DataFrame([
        (actual, predicted, count) for actual in ['low', 'mid', 'high'] for predicted, count in [('low', 8), ('mid', 3), ('high', 1)]
    ], columns=['actual', 'predicted', 'count'])
    spec = close(plot_confusion_counts(
        confusion, unit_label='samples', label_order=['high', 'mid', 'low'],
        label_aliases={'low': 'Low class', 'mid': 'Middle class', 'high': 'High class'}, label_wrap=5,
    ))
    assert spec['label_order'] == ['high', 'mid', 'low']

    assoc = pd.DataFrame([
        (row, col, 'estimable', .2, .03, 10)
        for row in ['a', 'b', 'c', 'd', 'e'] for col in ['x', 'y', 'z']
    ], columns=['term', 'view', 'status', 'value', 'q', 'n'])
    spec = close(plot_association_matrix(
        assoc, value_label='r', method_label='Spearman', row_field='term', column_field='view',
        row_order=['e', 'd', 'c', 'b', 'a'], column_aliases={'x': 'X', 'y': 'Y', 'z': 'Z'}
    ))
    assert spec['row_order'] == ['e', 'd', 'c', 'b', 'a']

    activity = pd.DataFrame([
        (row, col, float(i + j) / 10)
        for i, row in enumerate(['row A with a long label', 'row B with a long label'])
        for j, col in enumerate(['column 01', 'column 02', 'column 03', 'column 04', 'column 05', 'column 06', 'column 07', 'column 08', 'column 09'])
    ], columns=['row', 'column', 'value'])
    activity_rows = pd.DataFrame({'row': ['row A with a long label', 'row B with a long label'], 'group': ['A', 'B']})
    activity_top = pd.DataFrame({'column': [f'column {i:02d}' for i in range(1, 10)], 'bar': range(9), 'line': range(9)})
    activity_density = pd.DataFrame([
        (g, x, .2 + .01 * x) for g in ['A', 'B'] for x in range(5)
    ], columns=['group', 'coordinate', 'value'])
    activity = pd.concat([
        activity.assign(record_type='matrix'),
        activity_rows.assign(record_type='row'),
        activity_top.assign(record_type='top'),
        activity_density.assign(record_type='density'),
    ], ignore_index=True, sort=False)
    spec = close(plot_activity_dashboard(
        activity,
        {'A': '#336699', 'B': '#CC6677'}, row_order=list(activity_rows.row), column_order=list(activity_top.column),
        value_label='value', bar_label='bar', line_label='line', row_label_wrap=10, column_label_wrap=8,
    ))
    assert spec['column_order'] == list(activity_top.column)

    incomplete = long[~((long.gene == 'r2') & (long.assay == 'c2'))].copy()
    try:
        plot_heatmap(incomplete, 'value', row_field='gene', column_field='assay', value_field='score')
    except ValueError:
        pass
    else:
        raise AssertionError('Incomplete matrix accepted without an explicit missing policy')
    spec = close(plot_heatmap(incomplete, 'value', row_field='gene', column_field='assay', value_field='score', missing='mask'))
    assert spec['missing'] == 'mask'
    print('MATRIX_FLEXIBILITY_PASS')


if __name__ == '__main__':
    main()
