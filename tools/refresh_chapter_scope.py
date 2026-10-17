"""Reuse only byte-identical frozen specs/inputs; render every changed chapter."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import make_plan,read_json,write_new
from figure_workbench.pipeline import render_plan
def run(old_inputs,old_exports,new_inputs,out):
    out.mkdir(parents=True,exist_ok=False)
    old={r['id']:r for r in read_json(old_exports/'manifest.json')['records']}
    rows=[];changed=[];retained=[]
    for row in read_json(new_inputs/'manifest.json')['records']:
        key=row['id'];previous=old[key]
        op=old_inputs/previous['spec'];np=new_inputs/row['spec']
        os=read_json(op);ns=read_json(np)
        same=op.read_bytes()==np.read_bytes() and (op.parent/os['input']['path']).read_bytes()==(np.parent/ns['input']['path']).read_bytes()
        if same:
            result=previous['result'];retained.append(key)
        else:
            result=render_plan(make_plan(ns,np.parent),out/key);changed.append(key)
        rows.append(dict(**row,result=result,export_origin='retained exact original spec and input bytes' if same else 'new render'))
    write_new(out/'manifest.json',dict(records=rows,rerendered=changed,retained_identical=retained,
        analysis_performed=False,visual_acceptance=False))
    print(json.dumps(dict(rerendered=changed,retained_identical=len(retained))))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for x in ['old-inputs','old-exports','new-inputs','output']:p.add_argument('--'+x,required=True,type=Path)
    a=p.parse_args();run(a.old_inputs,a.old_exports,a.new_inputs,a.output)
