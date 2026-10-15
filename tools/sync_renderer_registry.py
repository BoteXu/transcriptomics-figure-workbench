"""Regenerate registry and parameter reference from actual shipped functions."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/transcriptomics-figure-workbench/scripts'
sys.path.insert(0, str(SCRIPTS))
from figure_workbench.registry import build_registry, REFERENCES


def outputs():
    registry = build_registry()
    lines = ['# Executable renderer directory', '',
        'Generated from shipped Python source. Function, alias, family and example counts are separate.', '',
        'Discovery does not import plotting dependencies. Source availability is not runtime or scientific acceptance.', '',
        '| Callable | Fixed aliases | Table entry | Required parameters |', '|---|---|---|---|']
    for row in registry['renderers']:
        needed = ', '.join(p['name'] for p in row['parameters'] if p['required']) or 'none'
        lines.append('| ' + ' | '.join([row['id'], ', '.join(row['aliases']) or 'canonical ID',
                                      'yes' if row['frozen_table_entry'] else 'legacy callable only', needed]) + ' |')
    for row in registry['renderers']:
        lines += ['', '## ' + row['id'], '', row['summary'] or 'See the fixed implementation and its input contract.', '',
                  '| Parameter | Required | Default |', '|---|---|---|']
        for p in row['parameters']:
            default = json.dumps(p.get('default'), ensure_ascii=False).replace('|', '\\|') if not p['required'] else '—'
            lines.append('| ' + p['name'] + ' | ' + str(p['required']).lower() + ' | ' + default + ' |')
    return {REFERENCES / 'renderer-registry.json': json.dumps(registry, ensure_ascii=False, indent=2) + '\n',
            REFERENCES / 'renderer-directory.md': '\n'.join(lines) + '\n'}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf8') != content:
                raise ValueError('Generated renderer reference is stale: ' + path.name)
        else:
            path.write_text(content, encoding='utf8')
    print(json.dumps({'status': 'REGISTRY_CHECKED' if args.check else 'REGISTRY_GENERATED'}))


if __name__ == '__main__': main()
