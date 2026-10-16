"""Reflow actual frozen single figures with variable counts, weights and pagination."""
from pathlib import Path
import sys,json,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.layout import make_layout,export_layout

def main():
    root=ROOT/'examples/responsive-v081';dest=root/'compositions';dest.mkdir(exist_ok=False)
    keys=['Matrix_3x4','Matrix_17x11','Features_7_cols_4','Composition_7_cols_3','GSEA_2_cols_1']
    def p(k,i,**extra):return dict(id='Panel'+str(i),svg='../'+k+'.svg',**extra)
    reqs=[dict(id='Solo',columns=1,canvas_width_pt=600,panels=[p(keys[0],1)]),
          dict(id='AutoFour',columns='auto',packing='masonry',packing_order='tall_first',label_order='reading',preferred_panel_width_pt=450,canvas_width_pt=1100,panels=[p(k,i+1) for i,k in enumerate(keys[:4])]),
          dict(id='Asymmetric',columns=3,column_weights=[1,1,1],canvas_width_pt=1100,panels=[p('Matrix_long_labels',1,row=0,column=0,row_span=2,column_span=2),p('Features_1_cols_auto',2,row=0,column=2),p('Composition_2_cols_1',3,row=1,column=2)]),
          dict(id='PagedEleven',columns=2,max_rows_per_page=2,canvas_width_pt=1100,panels=[p(keys[i%3],i+1) for i in range(11)])]
    records=[]
    for req in reqs:
        req['title']='Complete frozen panels / '+req['id'];plan=make_layout(req,dest)
        for page in plan['pages']:
            for panel in page['panels']:panel['source_svg']=os.path.relpath(panel['source_svg'],dest).replace(os.sep,'/')
        (dest/(req['id']+'.request.json')).write_text(json.dumps(req,indent=2)+'\n');(dest/(req['id']+'.plan.json')).write_text(json.dumps(plan,indent=2)+'\n')
        out=dest/req['id'];receipt=export_layout(plan,out,dest)
        for page in receipt['layout']['pages']:
            for panel in page['panels']:panel['source_svg']=os.path.relpath(panel['source_svg'],out).replace(os.sep,'/')
        (out/'layout-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        for page in plan['pages']:records.append(dict(id=req['id'],file=req['id']+'/'+req['id']+'-page-'+str(page['page']+1).zfill(2)+'.svg',panels=[p['id'] for p in page['panels']],screen_review='PENDING'))
    (dest/'manifest.json').write_text(json.dumps(dict(records=records,scientific_analysis=False,visual_acceptance=False),indent=2)+'\n');print(json.dumps(dict(configurations=4,pages=len(records),panel_uses=19)))
if __name__=='__main__':main()
