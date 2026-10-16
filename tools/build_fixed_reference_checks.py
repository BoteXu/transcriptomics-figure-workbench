"""Exercise complete, immutable reference content at two reading widths.

These are layout checks, not callable analysis backends or new data volumes.
"""
import argparse,json,sys
from pathlib import Path
from full_layout_cases import ROOT,SKILL,cases
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.layout import make_layout,export_layout


def build(out):
    out.mkdir(parents=True,exist_ok=False);records=[]
    for case in cases(include_all=True):
        if case['route']!='fixed_reference':continue
        key=case['example'];source=ROOT/'examples/forms-v080'/key
        for mode,width in [('wide',1000),('compact',620)]:
            name=key+'_'+mode
            panel=dict(id='Panel1',svg=str(source/(key+'.svg')))
            if (source/(key+'.tsv')).is_file():panel['table']=str(source/(key+'.tsv'))
            req=dict(id=name,panels=[panel],
                     columns=1,canvas_width_pt=width,padding_pt=24,gap_pt=24)
            plan=make_layout(req,out);folder=out/name;export_layout(plan,folder)
            for page in plan['pages']:
                stem=name+'-page-'+str(page['page']+1).zfill(2)
                records.append(dict(id=stem,form=case['base_form'],file=name+'/'+stem+'.svg',source_example=key,
                    layout=mode,route='fixed_reference',status='RENDERED_UNREVIEWED',visual_acceptance=False,
                    limitation='Source content unchanged; width and complete framing checked only; no runtime or volume validation'))
    (out/'manifest.json').write_text(json.dumps(dict(records=records,visual_acceptance=False),indent=2)+'\n')
    print(json.dumps(dict(references=len(records)//2,pages=len(records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
