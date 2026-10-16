"""Exercise ordinary requests against the selected fictional study manifests."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.study import study_plan,render_study
from figure_workbench.contracts import read_json,write_new


def main(base):
    base=base.resolve()
    records=[];requests=[]
    for assay in ['bulk','single_cell']:
        manifest=read_json(base/(assay+'.manifest.json'))
        for i,request in enumerate(['画质控图','展示差异和通路','做一套文章组图']):
            plan=study_plan(manifest,request,base);write_new(base/(assay+'-request-'+str(i+1)+'.plan.json'),plan)
            if plan['state']!='FIGURE_SET_PLANNED':raise ValueError('Ordinary request unexpectedly held')
            requests.append(dict(assay=assay,request=request,sections=plan['sections'],figures=len(plan['panels']),missing_results=plan['missing_results']))
        receipt=render_study(plan,base/(assay+'-render'))
        for panel in receipt['panels']:
            files=panel['result']['files'];svg=next(Path(p) for p in files if p.endswith('.svg'));key=svg.stem
            records.append(dict(id=key,form=panel['role'],file=svg.relative_to(base).as_posix(),assay=assay,role=panel['role'],
                status='RENDERED_UNREVIEWED',readability=panel['result']['print_readability'],visual_acceptance=False))
        write_new(base/(assay+'-ordinary-requests.json'),dict(requests=[r for r in requests if r['assay']==assay]))
    write_new(base/'manifest.json',dict(records=records,ordinary_requests=requests,visual_acceptance=False,analysis_performed=False))
    print(json.dumps(dict(figures=len(records),ordinary_requests=len(requests),visual_acceptance=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);a=p.parse_args();main(a.fixtures)
