"""Render all explicitly selected public chapter fixtures, serially."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,make_plan,write_new
from figure_workbench.pipeline import render_plan

def render(base,output):
    output.mkdir(parents=True,exist_ok=False);records=[]
    for row in read_json(base/'manifest.json')['records']:
        p=base/row['spec'];spec=read_json(p);plan=make_plan(spec,p.parent)
        result=render_plan(plan,output/row['id']);records.append(dict(**row,result=result))
        write_new(output/(row['id']+'.receipt.json'),dict(state='RENDERED_UNREVIEWED',record=records[-1]));print('CHAPTER_RENDERED '+row['id'],flush=True)
    write_new(output/'manifest.json',dict(records=records,analysis_performed=False,visual_acceptance=False));print('ALL_CHAPTERS_RENDERED '+str(len(records)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();render(a.fixtures.resolve(),a.output.resolve())
