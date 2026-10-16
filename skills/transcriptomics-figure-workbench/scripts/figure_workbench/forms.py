"""Read the consolidated same-form catalog without importing plotting packages."""
import json
from pathlib import Path


def catalog_forms(search=''):
    data=json.loads((Path(__file__).resolve().parents[2]/'references/form-catalog.json').read_text(encoding='utf8'))
    q=search.casefold()
    return dict(counts=data['counts'],forms=[g for g in data['forms'] if q in json.dumps(g,ensure_ascii=False).casefold()],scientific_acceptance=False)


def form_entry(key):
    data=json.loads((Path(__file__).resolve().parents[2]/'references/form-catalog.json').read_text(encoding='utf8'))
    resolved=data['aliases'].get(key,key)
    matches=[g for g in data['forms'] if g['id']==resolved]
    if not matches:raise ValueError('Unknown form or retained example ID')
    return dict(**matches[0],requested=key,alias_resolved=key!=resolved,analysis_performed=False)
