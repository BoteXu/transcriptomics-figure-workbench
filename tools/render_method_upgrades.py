"""Serial actual rendering; preserve failures and never overwrite old exports."""
import argparse,json,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(S/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan


def run(base,output,selected=None):
    base=base.resolve();output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    rows=json.loads((base/'manifest.json').read_text(encoding='utf8'))['records'];records=[]
    for row in rows:
        if selected and row['id'] not in selected:continue
        source=base/row['spec'];spec=json.loads(source.read_text(encoding='utf8'))
        try:
            receipt=render_plan(make_plan(spec,source.parent),output)
            records.append(dict(id=row['id'],state=receipt['status'],files=receipt['files'],print_readability=receipt['print_readability']))
            print(row['id']+' RENDERED',flush=True)
        except Exception as exc:
            records.append(dict(id=row['id'],state='FAILED',error=str(exc),traceback=traceback.format_exc()))
            print(row['id']+' FAILED '+str(exc),flush=True)
        (output/'render-receipt.json').write_text(json.dumps(dict(records=records),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(total=len(records),failed=sum(r['state']=='FAILED' for r in records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--ids',nargs='*');a=p.parse_args();run(a.fixtures,a.output,a.ids)
