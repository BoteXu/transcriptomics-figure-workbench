"""Rerender only explicitly selected audit figures; preserve prior exports."""
import argparse,json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,make_plan,write_new
from figure_workbench.pipeline import render_plan


def revise(source,fixtures,output,ids):
    doc=read_json(source/'manifest.json');known={r['id'] for r in doc['records']}
    if len(ids)!=len(set(ids)) or set(ids)-known:raise ValueError('Select unique existing figure identities')
    output.mkdir(parents=True,exist_ok=False)
    for row in doc['records']:
        if row['id'] not in ids:continue
        k=row['id'];base_key=k.removesuffix('_Reading');p=fixtures/base_key/(base_key+'.spec.json');s=read_json(p)
        if s['figure_id']!=base_key:raise ValueError('Figure identity changed')
        if k!=base_key:
            table=p.parent/s['input']['path'];s=copy.deepcopy(s);s['figure_id']=k;s['input']['path']='input.tsv'
            folder=output/'inputs'/k;folder.mkdir(parents=True);(folder/'input.tsv').write_bytes(table.read_bytes());p=folder/'figure.spec.json';write_new(p,s)
        row['result']=render_plan(make_plan(s,p.parent),output/k);row['spec_path']=str(p);row['parameters']=s['parameters']
        print('REVISED '+k,flush=True)
    doc['visual_acceptance']=False;doc['revision']=dict(selected=ids,previous_manifest=str(source/'manifest.json'),prior_exports_preserved=True)
    write_new(output/'manifest.json',doc)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ids',nargs='+',required=True);a=p.parse_args();revise(a.source,a.fixtures,a.output,a.ids)
