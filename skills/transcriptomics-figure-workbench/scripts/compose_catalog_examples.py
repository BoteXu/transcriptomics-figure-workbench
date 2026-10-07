"""Rebuild saved gallery compositions from separately exported, verified panels.

Reads only the shipped recipe registry and gallery bundles. It does not fit a
model, invent alignment, change component data, or overwrite an existing output.
"""
from pathlib import Path
import argparse
import hashlib
import json

from compose_panels import compose_bundles,arrangement_layout

REGISTRY = Path(__file__).resolve().parents[1]/'references'/'combination-recipes.json'


def safe_file(root, relative):
    path = (root/relative).resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError('Missing or out-of-gallery source file: '+relative)
    return path


def rebuild(gallery, output, ids,arrangement=None):
    gallery = Path(gallery).resolve()
    output = Path(output)
    recipes = {r['id']: r for r in json.loads(REGISTRY.read_text(encoding='utf8'))['recipes']}
    if not ids or len(set(ids)) != len(ids) or set(ids)-set(recipes):
        raise ValueError('Supply unique registered composition IDs')
    if output.exists():
        raise FileExistsError('Fresh composition output directory required')
    prepared = []
    for id_ in ids:
        recipe = recipes[id_]
        panels = []
        for bundle in recipe['bundles']:
            prefix = safe_file(gallery, bundle['prefix']+'.pdf').with_suffix('')
            meta = safe_file(gallery, bundle['metadata'])
            table = safe_file(gallery, bundle['prefix']+'.tsv')
            if hashlib.sha256(table.read_bytes()).hexdigest() != bundle['table_sha256']:
                raise ValueError('Source component table differs from saved recipe')
            panels.append({'prefix':str(prefix),'metadata':str(meta)})
        prepared.append((recipe,panels))
    output.mkdir(parents=True)
    results = []
    for recipe,panels in prepared:
        layout=arrangement_layout(recipe['layout'],arrangement) if arrangement else recipe['layout']
        receipt = compose_bundles(panels,layout,output/recipe['id'])
        results.append({'id':recipe['id'],'relationship':recipe['relation'],
                        'components':[b['name'] for b in recipe['bundles']],
                        'status':receipt['status'],'files':receipt['files']})
    (output/'composition-manifest.json').write_text(
        json.dumps({'status':'COMPOSED_UNREVIEWED','synthetic':True,'records':results},
                   ensure_ascii=False,indent=2),encoding='utf8')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gallery',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--arrangement',choices=['horizontal','vertical'])
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--ids',nargs='+')
    select.add_argument('--all',action='store_true')
    args = parser.parse_args()
    ids = [r['id'] for r in json.loads(REGISTRY.read_text(encoding='utf8'))['recipes']] if args.all else args.ids
    results = rebuild(args.gallery,args.output,ids,args.arrangement)
    print(json.dumps({'status':'COMPOSED_UNREVIEWED','compositions':len(results),
                      'source_tables_verified':True,'scientific_inference':False},indent=2))


if __name__ == '__main__':
    main()
