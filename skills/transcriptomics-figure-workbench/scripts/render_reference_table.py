"""Render reviewed input and explicit JSON settings; never generate research data."""
from pathlib import Path
import argparse,json,hashlib,importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_core import export_figure,file_sha256

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('figure_id'); parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--style',required=True,type=Path); parser.add_argument('--meta',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path); parser.add_argument('--design',type=Path)
    args=parser.parse_args(); registry=json.loads((Path(__file__).parent.parent/'references/reference-patterns.json').read_text(encoding='utf8'))
    patterns={r['id']:r for r in registry['patterns']}
    if args.figure_id in patterns:
        r=patterns[args.figure_id]; module=importlib.import_module(r['module']); fn=getattr(module,r['function']); numeric=r['numeric_columns']
    elif args.figure_id in [f'C{i:02d}' for i in range(1,8)]:
        from figure_palette_applications import plot_palette_plate
        fn=plot_palette_plate; numeric=['x','y','x0','y0','x1','y1','coordinate','value','lower','upper','area','color_value','radius','width','height','angle','order','q1','median','q3','low','high']
    else: raise ValueError('Unknown reference ID')
    # Preserve identifier strings, including leading zeroes and literal NA.
    data=pd.read_csv(args.input,sep='\t',dtype=str,keep_default_na=False).replace('',np.nan)
    for c in set(numeric)&set(data.columns): data[c]=pd.to_numeric(data[c],errors='raise')
    settings=json.loads(args.style.read_text(encoding='utf8')); meta=json.loads(args.meta.read_text(encoding='utf8'))
    fig=fn(data,**settings)
    if args.design:
        from figure_design import apply_design
        fig=apply_design(fig,json.loads(args.design.read_text(encoding='utf8')))
    paths=export_figure(fig,data,args.output,args.figure_id,meta,source_file=args.input,expected_source_sha256=file_sha256(args.input))
    plt.close(fig)
    print(json.dumps({'figure_id':args.figure_id,'files':[str(p) for p in paths]},ensure_ascii=True))

if __name__=='__main__': main()
