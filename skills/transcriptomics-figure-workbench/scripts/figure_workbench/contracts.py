"""Strict portable figure specifications and bounded, dependency-free preflight."""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
from .registry import digest, resolve, source_identity, REFERENCES

META_FIELDS = {'source','input_unit','experimental_unit','contrast','denominator','model',
               'limits','filtering','uncertainty','interpretation_limit','synthetic'}
PRESETS = {
    'paper': {'label_pt':10, 'tick_pt':9, 'title_pt':11, 'note_pt':8},
    'compact': {'label_pt':9, 'tick_pt':8, 'title_pt':10, 'note_pt':7},
    'presentation': {'label_pt':15, 'tick_pt':13, 'title_pt':17, 'note_pt':11},
    'large_print': {'label_pt':13, 'tick_pt':12, 'title_pt':15, 'note_pt':10}}


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')


def hash_value(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 2*1024*1024:
        raise ValueError('JSON exceeds the bounded configuration limit')
    return json.loads(path.read_text(encoding='utf-8-sig'),parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def write_new(path,value):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as output:
        output.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def local_path(value,base):
    if not isinstance(value,str) or not value.strip() or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://',value):
        raise ValueError('Select one local file; URLs are not data inputs')
    path = Path(value)
    path = path if path.is_absolute() else Path(base)/path
    if path.is_symlink() or not path.is_file():
        raise ValueError('Selected file is missing or linked')
    return path.resolve()


def validate_spec(spec):
    fields = {'schema_version','figure_id','renderer','input','theme','parameters','provenance','appearance','export'}
    if not isinstance(spec,dict) or set(spec)-fields or not (fields-{'appearance','export'})<=set(spec):
        raise ValueError('FigureSpec has missing or unknown fields')
    if spec['schema_version']!=1 or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}',spec['figure_id']):
        raise ValueError('Unsupported schema or unsafe stable figure ID')
    row = resolve(spec['renderer'])
    if not row['frozen_table_entry']:
        raise ValueError('This legacy callable needs its specialist input route')
    if not isinstance(spec['parameters'],dict):
        raise ValueError('Drawing parameters must be a JSON object')
    accepted={p['name'] for p in row['parameters']}
    required={p['name'] for p in row['parameters'] if p['required']}
    if set(spec['parameters'])-accepted or required-set(spec['parameters']):
        raise ValueError('Unknown or missing drawing parameters; use describe')
    inp=spec['input']
    if not isinstance(inp,dict) or set(inp)-{'path','sha256','numeric_columns','max_rows','max_bytes'} or 'path' not in inp:
        raise ValueError('Select one bounded TSV input')
    if inp.get('sha256') is not None and not re.fullmatch('[0-9a-f]{64}',inp['sha256']):
        raise ValueError('Expected SHA256 must be lowercase hex')
    if not isinstance(inp.get('numeric_columns',[]),list) or any(not isinstance(c,str) or not c for c in inp.get('numeric_columns',[])):
        raise ValueError('Numeric columns must be explicit field names')
    for name,default,maximum in [('max_rows',20000,100000),('max_bytes',5*1024**2,20*1024**2)]:
        value=inp.get(name,default)
        if type(value) is not int or not 1<=value<=maximum:
            raise ValueError('Input bound outside supported range')
    meta=spec['provenance']
    if not isinstance(meta,dict) or set(meta)!=META_FIELDS or type(meta.get('synthetic')) is not bool:
        raise ValueError('Complete explicit provenance is required')
    if any(not isinstance(meta[k],str) or not meta[k].strip() for k in META_FIELDS-{'synthetic'}):
        raise ValueError('Provenance text cannot be empty')
    if row['module'] in {'figure_editorial','figure_expanded_grammar'}:
        contract=spec['parameters'].get('contract')
        if not isinstance(contract,dict) or type(contract.get('synthetic')) is not bool or contract['synthetic']!=meta['synthetic']:
            raise ValueError('Frozen-input contract and export provenance must agree about synthetic data')
    if not isinstance(spec['theme'],dict):
        raise ValueError('Embed the selected project theme in FigureSpec')
    theme=spec['theme']
    theme_fields={'schema_version','project_id','palette_name','palette_colors','group_slots','roles',
                  'continuous','font_family','design','line_width','point_edge_width','preview_only'}
    if not theme_fields<=set(theme) or theme['schema_version']!=1:
        raise ValueError('Incomplete project theme')
    cards=read_json(REFERENCES/'reference-palettes.json')['palettes']
    card=cards.get(theme['palette_name'],{})
    if card.get('semantic')!='categorical' or card.get('colors')!=theme['palette_colors']:
        raise ValueError('Theme must preserve an existing declared categorical card')
    if not isinstance(theme['group_slots'],dict) or any(type(v) is not int or not 0<=v<len(theme['palette_colors']) for v in theme['group_slots'].values()):
        raise ValueError('Invalid category identities or color capacity')
    if not isinstance(theme['font_family'],str) or not theme['font_family'].strip():
        raise ValueError('Font family required')
    for key in ['label_pt','tick_pt','title_pt','note_pt']:
        value=theme['design'].get(key)
        if type(value) not in {int,float} or not math.isfinite(value) or not 0<value<=40:
            raise ValueError('Theme text hierarchy must be explicit and bounded')
    app=spec.get('appearance',{})
    if not isinstance(app,dict) or set(app)-{'preset','font_family','label_pt','tick_pt','title_pt','note_pt','line_width'}:
        raise ValueError('Appearance edits contain unknown or quantitative fields')
    if app.get('preset','paper') not in PRESETS:
        raise ValueError('Choose a documented typography preset')
    for key in set(app)-{'preset','font_family'}:
        v=app[key]
        if type(v) not in {int,float} or not math.isfinite(v) or not .1<=v<=40:
            raise ValueError('Bounded positive appearance values required')
    if 'font_family' in app and (not isinstance(app['font_family'],str) or not app['font_family'].strip()):
        raise ValueError('Font family must be explicit')
    export=spec.get('export',{})
    if (not isinstance(export,dict) or set(export)-{'raster_dpi','tiff'}
            or type(export.get('raster_dpi',300)) is not int or export.get('raster_dpi',300) not in {300,600}
            or type(export.get('tiff',False)) is not bool):
        raise ValueError('Export supports explicit 300/600 DPI and optional TIFF')
    canonical(spec)
    return row


def make_plan(spec,base):
    row=validate_spec(spec)
    path=local_path(spec['input']['path'],base)
    if path.stat().st_size>spec['input'].get('max_bytes',5*1024**2):
        raise ValueError('Selected table exceeds the declared byte budget')
    before=digest(path)
    if spec['input'].get('sha256',before)!=before:
        raise ValueError('Selected table does not match expected SHA256')
    rows=0
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.reader(stream,delimiter='\t');header=next(reader,[])
        if not header or len(header)>250 or any(not c for c in header) or len(header)!=len(set(header)):
            raise ValueError('TSV needs unique nonempty column names')
        for record in reader:
            if len(record)!=len(header):raise ValueError('Ragged TSV row')
            rows+=1
            if rows>spec['input'].get('max_rows',20000):raise ValueError('Selected table exceeds the declared row budget')
    if not rows or digest(path)!=before:
        raise ValueError('Input is empty or changed during preflight')
    return {'schema_version':1,'spec':spec,'spec_sha256':hash_value(spec),'input_path':str(path),
            'input_sha256':before,'rows':rows,'columns':header,'renderer':row['id'],
            'source_identity':source_identity(),'state':'PREFLIGHT_ONLY',
            'inference_performed':False,'visual_acceptance':False}


def check_plan(plan):
    if not isinstance(plan,dict) or plan.get('schema_version')!=1:
        raise ValueError('Unsupported plan')
    validate_spec(plan['spec'])
    # Rebind the selected resolved file, independent of the original spec directory.
    rebound=json.loads(json.dumps(plan['spec']))
    rebound['input']['path']=plan['input_path']
    fresh=make_plan(rebound,Path(plan['input_path']).parent)
    fresh['spec']=plan['spec'];fresh['spec_sha256']=hash_value(plan['spec'])
    if fresh!=plan:
        raise ValueError('Plan inputs, source, parameters or provenance changed; prepare a new plan')
    return plan
