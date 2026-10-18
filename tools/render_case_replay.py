"""Render a fresh coherent fixture via the ordinary-request study planner."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,write_new,make_plan
from figure_workbench.study import study_plan,render_study
from figure_workbench.pipeline import render_plan

def render(base,out):
    out.mkdir(parents=True,exist_ok=False);records=[];requests=[]
    presentation=read_json(base/'prepared.manifest.json')
    for assay in ['bulk','single_cell']:
        manifest=read_json(base/(assay+'.manifest.json'))
        phrases=['画质控图','展示差异和通路']+(['展示各个亚群的 marker'] if assay=='single_cell' else [])+['把这套结果画成整套图']
        for phrase in phrases:
            plan=study_plan(manifest,phrase,base)
            if plan['state']!='FIGURE_SET_PLANNED':raise ValueError(plan['blocking_reasons'])
            requests.append(dict(assay=assay,request=phrase,selected=[p.get('id',p['role']) for p in plan['panels']],missing=plan['missing_results']))
        write_new(out/(assay+'.plan.json'),plan)
        receipt=render_study(plan,out/assay)
        for row,p in zip(receipt['panels'],plan['panels']):
            spec=p['plan']['spec'];source=next(x['spec'] for x in manifest['results'] if x.get('id',x['role'])==row['id'])
            records.append(dict(id=spec['figure_id'],assay=assay,stage=row['stage'],role=row['role'],result=row['result'],spec_path=str((base/source).resolve()),parameters=spec['parameters'],variant='ordinary default'))
        write_new(out/(assay+'.progress.json'),dict(records=records,requests=requests))
    for row in presentation['records']:
        if not row['variant']:continue
        source=base/row['spec_path'];spec=read_json(source)
        result=render_plan(make_plan(spec,source.parent),out/'extensions'/row['id'])
        records.append(dict(id=row['id'],assay=row['assay'],stage='reading',role='explicit_layout',result=result,spec_path=str(source.resolve()),parameters=spec['parameters'],variant='explicit reading / layout extension'))
        write_new(out/(row['id']+'.receipt.json'),records[-1]);print('EXTENSION_DRAWN '+row['id'],flush=True)
    write_new(out/'manifest.json',dict(records=records,requests=requests,analysis_performed=False,visual_acceptance=False,scientific_acceptance=False))
    print(json.dumps(dict(state='FRESH_STUDY_DRAWN_REVIEW_REQUIRED',figures=len(records))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();render(a.fixtures.resolve(),a.output.resolve())
