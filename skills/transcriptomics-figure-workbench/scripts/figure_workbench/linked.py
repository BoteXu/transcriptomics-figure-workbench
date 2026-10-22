"""Offline coordinated views of explicit frozen columns; no embedding or statistics."""
import csv
import html
import json
import math
from pathlib import Path
import re
from .contracts import local_path, read_json, write_new
from .registry import digest, REFERENCES


def build_linked(request, base, output):
    required = {'schema_version','title','subtitle','input','id_column','group_column','views','colors','context','layout'}
    if not isinstance(request, dict) or set(request)!=required or type(request['schema_version']) is not int or request['schema_version']!=1:
        raise ValueError('Use the documented linked-view request fields')
    for field in ['title','subtitle','id_column','group_column']:
        if not isinstance(request[field],str) or not request[field].strip() or len(request[field])>500:
            raise ValueError('Explicit bounded titles and column names are required')
    inp = request['input']
    if not isinstance(inp,dict) or set(inp)!={'path','sha256'}: raise ValueError('Select one exact frozen input')
    path = local_path(inp['path'],base)
    if path.stat().st_size>5*1024**2 or digest(path)!=inp['sha256']: raise ValueError('Input bytes or bounded size mismatch')
    context = request['context']
    if (not isinstance(context,dict) or set(context)!={'independent_unit','scope','missingness','synthetic'}
            or type(context['synthetic']) is not bool
            or any(not isinstance(context[k],str) or not context[k].strip() or len(context[k])>2000 for k in ['independent_unit','scope','missingness'])):
        raise ValueError('Document independent unit, complete scope, missingness and synthetic status')
    views = request['views']; view_fields = {'id','title','x','y','x_label','y_label'}
    extras = {'kind','x_lower','x_upper','interval_label'}
    if (not isinstance(views,list) or not 2<=len(views)<=6
            or any(not isinstance(v,dict) or not view_fields<=set(v) or set(v)-view_fields-extras
                   or any(not isinstance(x,str) or not x.strip() or len(x)>200 for x in v.values()) for v in views)
            or len({v['id'] for v in views})!=len(views)):
        raise ValueError('Supply two to six explicitly named coordinate or feature views')
    for view in views:
        kind=view.get('kind','scatter')
        if kind not in {'scatter','labels','interval'}:raise ValueError('View kind must be scatter, labels or interval')
        interval_fields={'x_lower','x_upper','interval_label'}
        if (kind=='interval' and not interval_fields<=set(view)) or (kind!='interval' and interval_fields&set(view)):
            raise ValueError('Only interval views require supplied bounds and their exact meaning')
    colors = request['colors']
    if (not isinstance(colors,dict) or not 1<=len(colors)<=20
            or any(not isinstance(k,str) or not k.strip() or len(k)>200 or not isinstance(v,str) or not re.fullmatch(r'#[0-9A-Fa-f]{6}',v) for k,v in colors.items())):
        raise ValueError('Use an explicit, stable named color map for up to 20 groups')
    layout = request['layout']
    if (not isinstance(layout,dict) or set(layout)-{'columns','width_px','panel_height'}
            or not (layout.get('columns','auto')=='auto' or type(layout.get('columns')) is int and layout['columns'] in [1,2,3])
            or type(layout.get('width_px',1440)) is not int or not 700<=layout.get('width_px',1440)<=2200
            or type(layout.get('panel_height',320)) is not int or not 240<=layout.get('panel_height',320)<=560):
        raise ValueError('Use auto or 1/2/3 columns, bounded width and panel height')
    numeric = sorted({v[k] for v in views for k in ['x','y','x_lower','x_upper'] if k in v})
    rows = []; ids = set(); unavailable = {v['id']:0 for v in views}
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader = csv.DictReader(stream,delimiter='\t'); header = reader.fieldnames or []
        if len(header)!=len(set(header)) or not {request['id_column'],request['group_column'],*numeric}<=set(header):
            raise ValueError('Unique shared IDs, group and numeric columns are required')
        for row in reader:
            if len(rows)>=5000 or None in row or any(v is None for v in row.values()): raise ValueError('Ragged or overlong linked display table')
            rid = row[request['id_column']]; group = row[request['group_column']]
            if not rid.strip() or len(rid)>200 or rid in ids or group not in colors:
                raise ValueError('Object identities must be unique, complete and covered by the color map')
            ids.add(rid); values = {}
            for key in numeric:
                raw = row[key].strip()
                if raw in {'','NA','NaN'}: values[key]=None
                else:
                    try: value = float(raw)
                    except ValueError: raise ValueError('Display coordinates must be numeric or explicitly missing')
                    if not math.isfinite(value): raise ValueError('Infinite display values are not supported')
                    values[key]=value
            for view in views:
                keys=[view[k] for k in ['x','y','x_lower','x_upper'] if k in view]
                if any(values[k] is None for k in keys): unavailable[view['id']]+=1
                elif view.get('kind')=='interval' and not values[view['x_lower']]<=values[view['x']]<=values[view['x_upper']]:
                    raise ValueError('Supplied interval bounds must contain the estimate')
            rows.append({'id':rid,'group':group,'values':values})
    if not rows or digest(path)!=inp['sha256']: raise ValueError('Empty or changing frozen display table')
    for view in views:
        if unavailable[view['id']]==len(rows): raise ValueError('Every view requires at least one supplied coordinate pair')
        if view.get('kind')=='labels' and len(rows)-unavailable[view['id']]>30:
            raise ValueError('Full object labels require at most 30 supplied pairs; use scatter and selection for larger data')
    payload = {'title':request['title'],'subtitle':request['subtitle'],'rows':rows,'views':views,'colors':colors,
               'context':context,'layout':layout,'numeric':numeric,'unavailable':unavailable,'input_sha256':inp['sha256']}
    template = (REFERENCES/'linked-views-template.html').read_text('utf8')
    encoded = json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    document = template.replace('<!--TITLE-->',html.escape(request['title'])).replace('/*PAYLOAD*/',encoded)
    destination = Path(output)
    if destination.exists(): raise ValueError('Use a fresh linked-view output directory')
    destination.mkdir(parents=True,exist_ok=False)
    (destination/'index.html').write_bytes(document.encode('utf8'))
    (destination/'input.tsv').write_bytes(path.read_bytes())
    if digest(destination/'input.tsv')!=inp['sha256']: raise ValueError('Input changed while exporting; preserve partial output and retry under a new ID')
    portable = json.loads(json.dumps(request)); portable['input']['path']='input.tsv'
    write_new(destination/'request.json',portable)
    receipt = {'schema_version':1,'state':'OFFLINE_LINKED_VIEWS_EXPORTED','rows':len(rows),'views':len(views),
               'input_sha256':inp['sha256'],'html_sha256':digest(destination/'index.html'),
               'unavailable_pairs':unavailable,'analysis_performed':False,'visual_acceptance':False,
               'scientific_validity_established':False,'external_requests_required':False}
    write_new(destination/'manifest.json',receipt)
    return receipt
