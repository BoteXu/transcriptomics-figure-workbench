"""Named package/method display entries; no package installation or native object execution."""
import copy
import csv
import json
import os
from pathlib import Path
from .registry import REFERENCES, resolve, digest
from .contracts import local_path, validate_spec


def catalog_methods(search=''):
    rows=json.loads((REFERENCES/'method-entries.json').read_text(encoding='utf8'))['entries']
    for row in rows:
        resolve(row['renderer'])
    return [r for r in rows if search.casefold() in json.dumps(r,ensure_ascii=False).casefold()]


def method_entry(name):
    rows=[r for r in catalog_methods() if r['id']==name]
    if len(rows)!=1:raise ValueError('Select an exact registered method entry')
    return rows[0]


def prepare_method_spec(name, template, base, output):
    row=method_entry(name)
    spec=copy.deepcopy(template)
    styled=spec.get('renderer')=='package_style'
    spec['renderer']='package_style' if styled else row['renderer']
    params=copy.deepcopy(row.get('defaults',{}))
    supplied=copy.deepcopy(spec['parameters'])
    if styled:
        if set(supplied)-{'view','contract','options'}:raise ValueError('Package style accepts view, contract and options only')
        if supplied.get('view',row['publication_view'])!=row['publication_view']:raise ValueError('Selected method fixes its publication view')
        params.update(supplied.get('options',{}))
    else:params.update(supplied)
    for key,value in row.get('fixed_parameters',{}).items():
        if key in params and params[key]!=value:raise ValueError('Selected entry fixes '+key)
        params[key]=value
    if styled:params.pop('kind',None)
    spec['parameters']={'view':row['publication_view'],'contract':supplied['contract'],'options':params} if styled else params
    path=local_path(spec['input']['path'],base)
    if path.stat().st_size>spec['input'].get('max_bytes',5*1024**2):raise ValueError('Selected result table exceeds bound')
    with path.open(encoding='utf-8-sig',newline='') as stream:
        columns=next(csv.reader(stream,delimiter='\t'),[])
    # Fixed schema profiles do not guess native column names, units or axes.
    if set(row['required_columns'])-set(columns):raise ValueError('Export canonical columns: '+', '.join(row['required_columns']))
    current=digest(path)
    if spec['input'].get('sha256',current)!=current:raise ValueError('Selected result table changed')
    spec['input']['sha256']=current
    spec['input']['path']=Path(os.path.relpath(path,Path(output).resolve().parent)).as_posix()
    validate_spec(spec)
    return spec
