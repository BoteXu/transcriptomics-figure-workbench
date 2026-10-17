"""Bounded serial drawing checks before expensive final vector/raster exports."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.contracts import read_json,make_plan
from figure_workbench.pipeline import project_appearance
from figure_workbench.quality import print_readability
from render_frozen_table import load_table,render
def main(base,out):
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False);results=[]
    for row in read_json(base/'manifest.json')['records']:
        try:
            p=base/row['spec'];s=read_json(p);make_plan(s,p.parent);d=load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns']);fig,audit=render(s['renderer'],d,s['parameters'],project_appearance(s));q=print_readability(fig,s['export']);fig.savefig(out/(row['id']+'.png'),dpi=110)
            result=dict(id=row['id'],state=q['state'],smallest_pt=q['smallest_pt'],below=q['below_threshold'])
        except Exception as e:result=dict(id=row['id'],state='ERROR',error=str(e))
        finally:plt.close('all')
        results.append(result);print(json.dumps(result),flush=True)
    (out/'preflight.json').write_text(json.dumps(results,indent=2)+'\n');assert all(x['state']=='MEASUREMENT_PASS' for x in results),'Resolve exact listed drawing/size issues'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.fixtures,a.output)
