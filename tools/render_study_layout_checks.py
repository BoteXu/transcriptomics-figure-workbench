"""Reflow the same complete frozen study channels under explicit layout requests."""
import argparse,copy,json,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan


def main(fixtures,out):
    out.mkdir(parents=True,exist_ok=False);records=[]
    for source in ['BulkMain','SingleCellMain']:
        original=json.loads((fixtures/source/(source+'.spec.json')).read_text(encoding='utf8'))
        for mode,cols,panels,width in [('column',1,None,178),('wide',3,None,330),('focused',2,['embedding','de','matrix'] if source=='BulkMain' else ['embedding','marker_dot','de'],210),('detail',1,['matrix'] if source=='BulkMain' else ['composition'],178)]:
            key=source+'_'+mode;folder=out/'inputs'/key;folder.mkdir(parents=True)
            spec=copy.deepcopy(original);spec['figure_id']=key
            spec['parameters'].update(ncols=cols)
            if panels:
                spec['parameters']['panels']=panels
                spec['parameters']['panel_titles']={k:v for k,v in spec['parameters'].get('panel_titles',{}).items() if k in panels}
            spec['export'].update(target_width_mm=width,raster_dpi=300)
            raw=fixtures/source/(source+'.tsv');shutil.copyfile(raw,folder/(key+'.tsv'));spec['input']['path']=key+'.tsv'
            (folder/(key+'.spec.json')).write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
            result=render_plan(make_plan(spec,folder),out/'figures')
            records.append(dict(id=key,form='study_overview',file='figures/'+key+'/'+key+'.svg',source=source,layout=mode,
                                target_width_mm=width,readability=result['print_readability'],status='RENDERED_UNREVIEWED',visual_acceptance=False))
            (out/'manifest.json').write_text(json.dumps(dict(records=records,visual_acceptance=False),indent=2)+'\n')
            print(key,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.fixtures,a.output)
