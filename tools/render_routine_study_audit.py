"""Render an explicit synthetic fixture through ordinary Chinese requests."""
import argparse,copy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,write_new,make_plan,hash_value
from figure_workbench.study import study_plan,render_study
from figure_workbench.pipeline import render_plan


def render(base,out,resume=False):
    out.mkdir(parents=True,exist_ok=resume);records=[];requests=[]
    for assay in ['bulk','single_cell']:
        m=read_json(base/(assay+'.manifest.json'))
        request='帮我把这套 '+('bulk' if assay=='bulk' else '单细胞')+' 结果画成整套图'
        for phrase in ['画质控图','展示差异和通路']+(['展示各个亚群的 marker'] if assay=='single_cell' else [])+[request]:
            p=study_plan(m,phrase,base)
            if p['state']!='FIGURE_SET_PLANNED':raise ValueError(p['blocking_reasons'])
            requests.append(dict(assay=assay,request=phrase,selected=[x.get('id',x['role']) for x in p['panels']],missing=p['missing_results']))
        saved=out/(assay+'.plan.json')
        if saved.exists():
            if not resume or read_json(saved)!=p:raise ValueError('Resume requires the same exact saved plan')
            r=read_json(out/assay/'figure-set-receipt.json')
            if r['state']!='RENDERED_REVIEW_REQUIRED' or r['plan_sha256']!=hash_value(p):raise ValueError('No complete matching figure-set receipt')
            for item in r['panels']:
                receipt=read_json(next(Path(x) for x in item['result']['files'] if x.endswith('.json')))
                folder=Path(item['result']['files'][0]).parent
                for filename,expected in receipt['output_sha256'].items():
                    if hashlib.sha256((folder/filename).read_bytes()).hexdigest()!=expected:raise ValueError('Changed saved export')
            print('REUSE_VERIFIED_DRAWINGS '+assay+' '+str(len(r['panels'])),flush=True)
        else:
            write_new(saved,p);r=render_study(p,out/assay)
        for row,panel in zip(r['panels'],p['panels']):
            s=panel['plan']['spec'];records.append(dict(id=s['figure_id'],assay=assay,stage=row['stage'],role=row['role'],result=row['result'],spec_path=str(base/next(x['spec'] for x in m['results'] if x.get('id',x['role'])==row['id'])),parameters=s['parameters'],variant='ordinary default'))
        progress=out/(assay+'.progress.json')
        if not progress.exists():write_new(progress,dict(records=records,requests=requests))
    # Explicit layout requests are companions to, rather than silent changes
    # in, the ordinary default. Each becomes a fresh source-bound export.
    choices=[('bulk_GSEADetail','bulk',{},240),('single_cell_GSEADetail','single_cell',{},240),
        ('Subgroup_01','single_cell',dict(ncols=2,composition='evidence',title='T cells · requested two-column marker block'),240),
        ('Subgroup_03','single_cell',dict(ncols=3,composition='grid',title='Myeloid · requested three-column panel grid'),297),
        ('EnrichmentTracks','bulk',dict(ncols=3,nrows=1,panel_width=4.2,panel_height=4,title='GSEA · requested horizontal pathway comparison'),297)]
    for index,(key,assay,change,width) in enumerate(choices):
        source=base/key/(key+'.spec.json');s=read_json(source);s['figure_id']=key+'_Reading' if not change else key+'_Custom'
        params=s['parameters'].get('options',s['parameters']);params.update(change);s['export']['target_width_mm']=width
        dest=out/'custom-inputs'/s['figure_id'];dest.mkdir(parents=True)
        table=source.parent/s['input']['path'];(dest/table.name).write_bytes(table.read_bytes());write_new(dest/'example.spec.json',s)
        result=render_plan(make_plan(s,dest),out/'companions'/s['figure_id'])
        records.append(dict(id=s['figure_id'],assay=assay,stage='reading',role='custom_layout' if change else 'gsea_detail',result=result,spec_path=str(dest/'example.spec.json'),parameters=s['parameters'],variant='explicit requested layout' if change else 'single-pathway reading companion'))
        write_new(out/(s['figure_id']+'.receipt.json'),records[-1]);print('COMPANION '+s['figure_id'],flush=True)
    write_new(out/'manifest.json',dict(records=records,requests=requests,analysis_performed=False,scientific_acceptance=False,visual_acceptance=False))
    print(json.dumps(dict(state='RENDERED_REVIEW_REQUIRED',figures=len(records))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--resume-verified-drawings',action='store_true');a=p.parse_args();render(a.fixtures.resolve(),a.output.resolve(),a.resume_verified_drawings)
