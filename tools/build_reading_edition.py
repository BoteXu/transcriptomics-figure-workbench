"""Bound and export selected frozen PDF pages into serial reading volumes."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.reading import make_reading_plan,export_reading
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--index',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=export_reading(make_reading_plan(a.index,ROOT),a.output)
    print(json.dumps(dict(figures=result['figures'],volumes=len(result['volumes']),pages=sum(r['pages'] for r in result['volumes']),status=result['state'])))
