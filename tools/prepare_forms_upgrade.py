"""Bind every current example to a same-form presentation revision, without inference."""
import argparse, copy, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output):
    old = json.loads((ROOT / 'examples/review-v070/review-index.json').read_text(encoding='utf8'))
    source = json.loads((ROOT / 'examples/gallery/publication-v030/source-plan.json').read_text(encoding='utf8'))
    contexts = {r['id']: r['context'] for r in source['items']}
    groups = {
        'R04': [['axes_1', 'axes_2'], ['axes_3'], ['axes_4', 'axes_5', 'axes_6', 'axes_7']],
        'R11': [[f'axes_{i}', f'axes_{i+1}'] for i in [1, 3, 5, 7, 9]] + [['axes_11', 'axes_12']],
        'R24': [['axes_1'], ['axes_2'], ['axes_3'], ['axes_4'], ['axes_5'], ['axes_6']],
        'R16': [['axes_1'], ['axes_2', 'axes_3']],
    }
    items, compositions = [], []
    titles={'P01':'Sample expression','P08':'Differential expression','P09':'Labelled differential expression',
            'P10':'Differential expression with marginals','P11a':'Over-representation analysis','P11b':'Gene-set enrichment summary',
            'P12a':'Signed expression matrix','P12b':'Magnitude matrix','P13':'Expression and fraction','P14':'Effect and evidence',
            'P19a':'Difference estimates','P19b':'Ratio estimates','P20a':'Grouped difference estimates','P20b':'Grouped ratio estimates',
            'P21a':'Cohort difference estimates','P21b':'Cohort ratio estimates','P25a':'ROC curves','P25b':'Precision-recall curves',
            'P25c':'Calibration curves','P26a':'ROC step curves','P26b':'Precision-recall step curves','R18':'Principal-component scores',
            'R19':'Principal-component scores and rugs','R08':'Joint observations and marginals','R12':'Joint observations and supplied summaries',
            'R13':'Joint observations and supplied trends','R25':'Typed interaction networks'}
    for record in old['records']:
        r = copy.deepcopy(record)
        meta = json.loads((ROOT / r['assets']['meta']).read_text(encoding='utf8'))
        if r.get('components'):
            compositions.append(dict(id=r['id'], components=r['components'], source=r['assets'],
                                     source_sha256=r['sha256'], orientation=meta.get('arrangement', 'default'),
                                     relationship=meta.get('relationship', 'Independent complete panels')))
            continue
        ctx = copy.deepcopy(contexts.get(r['id'], {}))
        if r['id'] in titles:ctx['title_en']=titles[r['id']]
        kind = ctx.get('kind', meta.get('figure_spec', {}).get('parameters', {}).get('kind', 'frozen_display'))
        role = ctx.get('role', 'figure')
        profile = ('reference' if role == 'palette' else 'structure' if r['id'] in ['S01','S02','S03'] else
                   'enrichment' if any(s in str(kind).lower() for s in ['enrich', 'gsea']) or r['id'].startswith('GSEA') else
                   'matrix' if any(s in str(kind).lower() for s in ['matrix', 'heatmap', 'dotplot']) else
                   'network' if any(s in str(kind).lower() for s in ['network', 'chord', 'flow', 'alluvial']) else
                   'distribution' if any(s in str(kind).lower() for s in ['violin', 'box', 'density', 'raincloud']) else
                   'curve' if any(s in str(kind).lower() for s in ['curve', 'roc', 'pr_', 'profile', 'ribbon']) else
                   'effects' if any(s in str(kind).lower() for s in ['forest', 'effect', 'volcano', 'dumbbell']) else 'journal')
        table = meta.get('input_table')
        local_table = (ROOT / r['assets']['meta']).with_suffix('.tsv')
        if local_table.exists():
            table = local_table.relative_to(ROOT).as_posix()
        elif not table and r['id'] in contexts:
            table = next(a.get('tsv') for a in source['items'] if a['id'] == r['id'])
        item = dict(id=r['id'], source=r['assets'], source_sha256=r['sha256'],
                    context=ctx, kind=kind, profile=profile, table=table,
                    input_sha256=sha(ROOT / table) if table else None,
                    layout_groups=groups.get(r['id']), layout_columns=2 if r['id'] in ['R11','R16'] else 1,
                    notes=[], preserve_all_categories=True)
        items.append(item)
    assert len(items)==332 and len(compositions)==126
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(schema_version=1, version='0.8.0', scope='All 458 existing exports; same forms and frozen inputs',
                                     source_index='examples/review-v070/review-index.json', source_index_sha256=sha(ROOT/'examples/review-v070/review-index.json'),
                                     items=items, compositions=compositions, scientific_acceptance=False), indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(standalone=len(items),compositions=len(compositions),output=str(output))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output', type=Path, required=True);prepare(p.parse_args().output)
