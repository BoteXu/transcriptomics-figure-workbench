"""Resolve frozen public display examples to current allowlisted drawing calls."""
from pathlib import Path
import ast
import copy
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/transcriptomics-figure-workbench'
sys.path.insert(0, str(SKILL / 'scripts'))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def origin(path):
    seen = set()
    while True:
        if path in seen:
            raise ValueError('Cyclic source metadata')
        seen.add(path)
        data = read(path)
        if data.get('figure_spec') or data.get('scene'):
            return data, path
        source = data.get('source', {})
        nxt = data.get('source_metadata') or (source.get('meta') if isinstance(source, dict) else None)
        if not nxt:
            return data, path
        path = ROOT / nxt


def kind_index():
    result = {}
    for path in (SKILL / 'scripts').glob('figure_*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for fn in tree.body:
            if not isinstance(fn, ast.FunctionDef) or not fn.name.startswith('plot_'):
                continue
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.id if isinstance(node.func, ast.Name) else ''
                if name == 'stamp' and len(node.args) > 2 and isinstance(node.args[2], ast.Constant):
                    result.setdefault(node.args[2].value, []).append(path.stem + '.' + fn.name)
                if name == '_finish':
                    for arg in node.args[2:4]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            kind = ('reference_' if path.stem == 'figure_reference' else '') + arg.value
                            result.setdefault(kind, []).append(path.stem + '.' + fn.name)
    return result


def cases(example_ids=None,include_all=False):
    registry = read(SKILL / 'references/renderer-registry.json')
    functions = {r['id']: r for r in registry['renderers']}
    aliases = registry['aliases']
    kinds = kind_index()
    forms = read(SKILL / 'references/form-catalog.json')['forms']
    source_plan = read(ROOT / 'examples/gallery/publication-v030/source-plan.json')
    original = {r['id']: r for r in source_plan['items']}
    result = [];selected=[];found=set()
    for form in forms:
        if form['id'] == 'composition':
            continue
        keys=[e['id'] for e in form['extensions'] if include_all or example_ids and e['id'] in example_ids] if include_all or example_ids else [form['default']]
        for key in keys:
            item=copy.deepcopy(form);item['default']=key;selected.append(item);found.add(key)
    if example_ids and set(example_ids)-found:raise ValueError('Unknown selected source examples: '+','.join(sorted(set(example_ids)-found)))
    for form in selected:
        key = form['default']
        ext = next(e for e in form['extensions'] if e['id'] == key)
        meta, path = origin(ROOT / ext['source_record'])
        spec = meta.get('figure_spec', {})
        wb = meta.get('workbench', {}).get('spec')
        row = dict(form=key if include_all or example_ids else form['id'],base_form=form['id'], example=key, title=form['title'], source_meta=path.relative_to(ROOT).as_posix())
        if not spec:
            row.update(route='fixed_reference', reason='Reference palette or structure scene; layout varies, source content fixed')
            result.append(row)
            continue
        if wb:
            adapter = wb['renderer']
            params = copy.deepcopy(wb['parameters'])
            theme = copy.deepcopy(wb['theme'])
        else:
            candidates = sorted(set(kinds.get(spec['kind'], [])))
            if spec['kind'] in aliases:
                candidates = [aliases[spec['kind']]['renderer']]
            if spec['kind'] == 'frozen_qc_de':
                candidates = [aliases['qc_de']['renderer']]
            dynamic = {'registered_spatial_categorical':'spatial_overlay','registered_spatial_continuous':'spatial_overlay', 'distribution_qq':'distribution',
                       'distribution_ecdf':'distribution', 'model_diagnostic_residual':'model_diagnostic',
                       'model_diagnostic_qq':'model_diagnostic','model_diagnostic_scale_location':'model_diagnostic','model_diagnostic_influence':'model_diagnostic',
                       'mass_spectrum_mirror':'mass_spectrum', 'hex_density':'figure_network_extensions.plot_hex_density','contour_field':'figure_network_extensions.plot_contour_field'}
            if spec['kind']=='forest' and 'palette' not in spec:candidates=['figure_core.plot_forest']
            if spec['kind'] in dynamic:
                key_binding = dynamic[spec['kind']]
                candidates = [aliases[key_binding]['renderer'] if key_binding in aliases else key_binding]
            if len(candidates) != 1:
                row.update(route='UNRESOLVED', kind=spec['kind'], candidates=candidates)
                result.append(row)
                continue
            adapter = candidates[0]
            accepted = {p['name']: p for p in functions[adapter]['parameters']}
            params = {k: copy.deepcopy(v) for k, v in spec.items() if k in accepted}
            theme = copy.deepcopy(spec.get('project_theme') or read(ROOT / 'examples/gallery/project_theme.json'))
            if 'palette_name' in accepted:
                palette = spec.get('palette', {})
                refs = palette.get('references', []) if isinstance(palette, dict) else [palette]
                if refs:
                    params['palette_name'] = 'card_' + refs[0][1:] if refs[0].startswith('C') else refs[0]
            for source_name, target_name in [('cmap','cmap_name'), ('summary','summary_label'), ('x_label','contribution_label')]:
                if target_name in accepted and source_name in spec:
                    params.setdefault(target_name, spec[source_name])
            if spec['kind'] == 'weighted_chord':
                params['order'] = spec['sector_order']
            if spec['kind'] == 'score_comparison':
                params['condition_labels'] = spec['conditions']
            if spec['kind'] == 'hex_density':
                params.update(x_label='Supplied X', y_label='Supplied Y')
            if spec['kind']=='contour_field':params.update(x_label='Supplied X',y_label='Supplied Y')
            if spec['kind']=='publication_grouped_forest':params.setdefault('x_label','Supplied '+spec['effect_scale'])
            if spec['kind']=='reference_pca':params['group_order']=list(spec['palette'])
            if spec['kind']=='reference_effect_distribution_forest':
                if not spec.get('p_semantics','').startswith('raw supplied p'):raise ValueError('Unknown stored probability semantics')
                params['p_type']='raw'
            if spec['kind'] == 'curve':
                params['kind'] = spec['curve_kind']
            if 'font_family' in accepted:
                params['font_family'] = 'DejaVu Sans'
        binding = functions[adapter] if adapter in functions else functions[aliases[adapter]['renderer']]
        missing = [p['name'] for p in binding['parameters'] if p['required'] and p['name'] not in params]
        if missing:
            row.update(route='UNRESOLVED', adapter=adapter, missing=missing, parameters=params)
            result.append(row)
            continue
        if form['id']=='feature-embedding':
            # Retire the old fixed two-point mark for sparse displays. The
            # renderer sizes marks from the actual retained cell count.
            params.pop('point_size',None)
            theme['continuous']['sequential']=['#DFE7EA','#326B8D']
        table = original.get(key, {}).get('tsv')
        if not table:
            candidate = path.with_suffix('.tsv')
            if candidate.exists():
                table = candidate.relative_to(ROOT).as_posix()
        if not table and wb:
            table = (path.parent / wb['input']['path']).relative_to(ROOT).as_posix()
        if not table or not (ROOT / table).is_file():
            raise ValueError('Missing frozen table for ' + key)
        theme['font_family'] = 'DejaVu Sans'
        row.update(route='native', adapter=adapter, parameters=params, theme=theme, table=table)
        result.append(row)
    return result


if __name__ == '__main__':
    rows = cases()
    print(json.dumps(dict(count=len(rows), native=sum(r['route']=='native' for r in rows), unresolved=[r for r in rows if r['route']=='UNRESOLVED'], references=[r['form'] for r in rows if r['route']=='fixed_reference']), ensure_ascii=True, indent=2))
