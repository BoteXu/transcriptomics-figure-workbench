"""Discover/export one explicitly selected within-analysis view, offline."""
from pathlib import Path
from .contracts import read_json,write_new,local_path
SKILL=Path(__file__).resolve().parents[2]

def chapter_views(chapter='',search=''):
    doc=read_json(SKILL/'references/analysis-views.json')
    return [r for r in doc['views'] if (not chapter or chapter in r['chapters']) and search.casefold() in str(r).casefold()]

def view_template(entry,output):
    row=next((r for r in chapter_views() if r['id']==entry),None)
    if row is None:raise ValueError('Choose an explicit shipped analysis view')
    source=SKILL/row['spec'];s=read_json(source);table=local_path(s['input']['path'],source.parent)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    if row.get('panel_id'):
        # This exports the exact selected records; it never discovers or subsets
        # private results. No scientific selection or table imputation occurs.
        import csv,hashlib,io
        with table.open(encoding='utf8',newline='') as f:
            reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;rows=[r for r in reader if r['panel_id']==row['panel_id']]
        if not rows:raise ValueError('Stale selected panel binding')
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows);raw=stream.getvalue().encode('utf8')
        s['parameters']['panels']=[p for p in s['parameters']['panels'] if p['id']==row['panel_id']];s['parameters'].update(title=row['title'],columns=1,rows=None);s['input']['sha256']=hashlib.sha256(raw).hexdigest()
    else:raw=table.read_bytes()
    (output/'example.tsv').write_bytes(raw);s['input']['path']='example.tsv';s['figure_id']=row['id'].replace('.','_');write_new(output/'example.spec.json',s);write_new(output/'view.json',row)
    return dict(state='EXPLICIT_VIEW_TEMPLATE_EXPORTED',view=entry,analysis_performed=False,visual_acceptance=False)
