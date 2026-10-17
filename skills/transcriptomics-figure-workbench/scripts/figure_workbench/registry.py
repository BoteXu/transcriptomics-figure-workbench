"""Source-derived discovery. Importing this module never imports plotting stacks."""
import ast
import hashlib
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
REFERENCES = SKILL / 'references'


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def source_identity():
    result = {p.relative_to(SCRIPTS).as_posix(): digest(p) for p in sorted(SCRIPTS.rglob('*.py'))
              if '__pycache__' not in p.parts}
    for name in ['renderer-registry.json','renderer-adapters.json','reference-palettes.json','method-entries.json']:
        result['references/'+name] = digest(REFERENCES/name)
    if (REFERENCES/'transcriptomic-chapters.json').is_file():result['references/transcriptomic-chapters.json']=digest(REFERENCES/'transcriptomic-chapters.json')
    if (REFERENCES/'analysis-views.json').is_file():result['references/analysis-views.json']=digest(REFERENCES/'analysis-views.json')
    if (REFERENCES/'analysis-suites.json').is_file():result['references/analysis-suites.json']=digest(REFERENCES/'analysis-suites.json')
    return result


def literal(node):
    try:
        return json.loads(json.dumps(ast.literal_eval(node)))
    except (ValueError, TypeError):
        return {'source_expression': ast.unparse(node)}


def parameters(node):
    result = []
    args = [*node.args.posonlyargs, *node.args.args]
    defaults = [None] * (len(args) - len(node.args.defaults)) + list(node.args.defaults)
    for arg, default in zip(args + node.args.kwonlyargs, defaults + node.args.kw_defaults):
        if arg.arg in {'data', 'theme'}:
            continue
        row = {'name': arg.arg, 'required': default is None,
               'annotation': ast.unparse(arg.annotation) if arg.annotation else None}
        if default is not None:
            row['default'] = literal(default)
        result.append(row)
    return result


def build_registry():
    aliases = json.loads((REFERENCES / 'renderer-adapters.json').read_text(encoding='utf8'))['adapters']
    labels = json.loads((REFERENCES / 'renderer-labels.json').read_text(encoding='utf8'))
    records = []
    for path in sorted(SCRIPTS.glob('figure*.py')):
        tree = ast.parse(path.read_text(encoding='utf8'))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith('plot_'):
                continue
            names = [a.arg for a in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]]
            key = path.stem + '.' + node.name
            routes = [name for name, row in aliases.items() if row['renderer'] == key]
            numeric = {c for name in routes for c in aliases[name]['numeric_columns']}
            for call in ast.walk(node):
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='checked' and len(call.args)>2:
                    known=literal(call.args[2])
                    if isinstance(known,(list,tuple)) and all(isinstance(c,str) for c in known):numeric.update(known)
            records.append({'id': key, 'module': path.stem, 'function': node.name,
                'display_name': labels[node.name],
                'summary': (ast.get_docstring(node) or '').split('\n')[0], 'parameters': parameters(node),
                'frozen_table_entry': 'data' in names, 'theme_mode': 'argument' if 'theme' in names else 'wrapper',
                'aliases': routes, 'source_sha256': digest(path),
                'validation': 'implemented_source; runtime and visual receipts are separate',
                'numeric_columns': sorted(numeric)})
    indexed = {r['id']: r for r in records}
    for name, row in aliases.items():
        if row['renderer'] not in indexed or not indexed[row['renderer']]['frozen_table_entry']:
            raise ValueError('Adapter has no table renderer: ' + name)
        if indexed[row['renderer']]['theme_mode'] != row['theme_mode']:
            raise ValueError('Adapter theme signature mismatch: ' + name)
    return {'schema_version': 1, 'version': (SKILL / 'VERSION').read_text().strip(),
            'counts': {'python_functions': len(records), 'fixed_aliases': len(aliases),
                       'table_entries': sum(r['frozen_table_entry'] for r in records)},
            'renderers': records, 'aliases': aliases}


def read_registry():
    return json.loads((REFERENCES / 'renderer-registry.json').read_text(encoding='utf8'))


def resolve(name, registry=None):
    registry = read_registry() if registry is None else registry
    key = registry['aliases'].get(name, {}).get('renderer', name)
    row = next((r for r in registry['renderers'] if r['id'] == key), None)
    if row is None:
        raise ValueError('Choose a fixed renderer from catalog')
    return row


def load_callable(name):
    import importlib
    row = resolve(name)
    path = SCRIPTS / (row['module'] + '.py')
    if digest(path) != row['source_sha256']:
        raise ValueError('Renderer changed; regenerate and review the registry')
    return getattr(importlib.import_module(row['module']), row['function'])
