"""Serial drawing of explicitly selected publication-revision FigureSpecs."""
import argparse,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan


def render(base,out,ids=None,reuse=None):
    m=json.loads((base/'prepared.manifest.json').read_text(encoding='utf8'));out.mkdir(parents=True,exist_ok=False);records=[]
    selected=m['records'] if ids is None else [r for r in m['records'] if r['id'] in ids]
    if ids is not None and {r['id'] for r in selected}!=set(ids):raise ValueError('Unknown selected figure identity')
    for r in selected:
        p=base/r['spec_path'];s=json.loads(p.read_text(encoding='utf8'));row=dict(r);row['spec_path']=str(p.resolve());row['parameters']=s['parameters'];plan=make_plan(s,p.parent)
        old=reuse/r['id']/r['id'] if reuse else None
        receipt=old/(r['id']+'.json') if old else None
        if receipt and receipt.exists():
            proof=json.loads(receipt.read_text(encoding='utf8'));w=proof['workbench']
            if w['spec_sha256']!=plan['spec_sha256'] or w['input_sha256']!=plan['input_sha256']:raise ValueError('Completed spec/input binding differs; use a fresh selected render')
            for name,sha in proof['output_sha256'].items():
                if Path(name).name!=name or hashlib.sha256((old/name).read_bytes()).hexdigest()!=sha:raise ValueError('Completed artifact integrity changed')
            if w['print_readability']['state']!='MEASUREMENT_PASS':raise ValueError('Unaccepted physical text size')
            row['result']=dict(status='RENDERED_UNREVIEWED',renderer=w['renderer'],files=[str(f.resolve()) for f in old.iterdir() if f.is_file()],print_readability=w['print_readability'],inference_performed=False,visual_review_required=True)
        else:row['result']=render_plan(plan,out/r['id'])
        records.append(row)
        (out/'partial-manifest.json').write_text(json.dumps(dict(records=records,requests=m['requests'],visual_acceptance=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print('DRAWN '+r['id'],flush=True)
    (out/'manifest.json').write_text(json.dumps(dict(records=records,requests=m['requests'],all_frozen_tables_unchanged=True,analysis_performed=False,visual_acceptance=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ids',nargs='+');p.add_argument('--reuse-completed',type=Path);a=p.parse_args();render(a.fixtures,a.output,a.ids,a.reuse_completed)
