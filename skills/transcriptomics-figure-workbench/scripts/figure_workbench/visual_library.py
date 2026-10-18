"""Offline lookup and explicit export across the complete drawing library."""
import json
from pathlib import Path
from .contracts import local_path, read_json, write_new
from .registry import digest

SKILL = Path(__file__).resolve().parents[2]
BASE = SKILL / 'assets/visual-library'


def library():
    path = BASE / 'manifest.json'
    if path.stat().st_size > 12 * 1024**2:
        raise ValueError('Shipped drawing index exceeds the bounded catalog limit')
    return json.loads(path.read_text(encoding='utf8'))


def find(search=''):
    doc = library(); q = search.casefold(); found = []
    by_id = {r['id']:r for r in doc['records']}
    for entry in doc['entries']:
        matches = [by_id[k] for k in entry['member_ids'] if q in json.dumps([entry['title'],by_id[k]],ensure_ascii=False).casefold()]
        if matches:
            found.append(dict(id=entry['id'],title=entry['title'],forms=entry['forms'],
                examples=[dict(id=r['id'],title=r['title'],history=r['history'],executable_spec=r['executable_spec']) for r in matches]))
    return dict(counts=doc['counts'],families=found,analysis_performed=False)


def export(entry, output):
    doc = library(); key = doc['aliases'].get(entry,entry)
    row = next((r for r in doc['records'] if r['id']==key),None)
    if row is None: raise ValueError('Choose an explicit shipped drawing example')
    if not row['executable_spec']:
        raise ValueError('This is a historical or fixed reference, without a current executable FigureSpec')
    source = local_path(row['assets']['spec'],BASE)
    if SKILL not in source.parents: raise ValueError('Drawing source escapes the installed skill')
    spec = read_json(source); table = local_path(spec['input']['path'],source.parent)
    if SKILL not in table.parents or digest(table)!=spec['input']['sha256']:
        raise ValueError('Shipped frozen input binding changed')
    output = Path(output); output.mkdir(parents=True,exist_ok=False)
    (output/'example.tsv').write_bytes(table.read_bytes()); spec['input']['path']='example.tsv'
    write_new(output/'example.spec.json',spec)
    write_new(output/'source.json',dict(id=key,method=row['method'],source_spec=row['assets']['spec'],input_sha256=spec['input']['sha256']))
    return dict(state='EXPLICIT_VISUAL_TEMPLATE_EXPORTED',entry=key,analysis_performed=False,visual_acceptance=False)
