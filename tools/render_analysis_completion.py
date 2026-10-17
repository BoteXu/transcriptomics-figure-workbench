"""Render selected synthetic method fixtures serially, preserving every failure."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,write_new,make_plan
from figure_workbench.pipeline import render_plan


def render(fixtures, output, selected=None):
    output.mkdir(parents=True,exist_ok=False);records=[];failures=[]
    for row in read_json(fixtures/'manifest.json')['records']:
        if selected and row['id'] not in selected:continue
        path=fixtures/row['spec']
        try:
            result=render_plan(make_plan(read_json(path),path.parent),output/row['id'])
            record=dict(**row,result=result);records.append(record)
            write_new(output/(row['id']+'.receipt.json'),record)
            print('RENDERED '+row['id'],flush=True)
        except Exception as exc:
            failure=dict(id=row['id'],error=type(exc).__name__+': '+str(exc));failures.append(failure)
            write_new(output/(row['id']+'.failure.json'),failure);print('FAILED '+row['id']+' '+failure['error'],flush=True)
    write_new(output/'manifest.json',dict(records=records,failures=failures,analysis_performed=False,visual_acceptance=False))
    print(json.dumps(dict(rendered=len(records),failed=len(failures))),flush=True)
    if failures:raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ids',nargs='+');a=p.parse_args();render(a.fixtures.resolve(),a.output.resolve(),a.ids)
