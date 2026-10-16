"""Build two reproducible layouts from the existing frozen gallery components."""
from pathlib import Path
import json,os,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.layout import make_layout,export_layout

def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    base=ROOT/'examples/layout-v080';base.mkdir(exist_ok=False)
    def panel(k,**kw):return dict(id=k,svg='../forms-v080/'+k+'/'+k+'.svg',**kw)
    requests=[dict(id='Asymmetric',title='Flexible complete panels',canvas_width_pt=1100,columns=3,column_weights=[1.4,1,1],gap_pt=20,
        panels=[panel('PKG13',row=0,column=0,row_span=2,column_span=2,label='A  Differential effects'),panel('REF01',row=0,column=2,label='B  Enrichment'),panel('PKG14',row=1,column=2,label='C  Supplied intervals')]),
        dict(id='Paged',title='Automatic rows and pagination',canvas_width_pt=738,columns='auto',preferred_panel_width_pt=300,max_rows_per_page=2,gap_pt=20,
        panels=[panel(k) for k in ['P09','REF01','PKG14','PKG16','P17b','REF03','REF04']])]
    rows=[]
    for req in requests:
        write(base/(req['id']+'.request.json'),req);plan=make_layout(req,base)
        for page in plan['pages']:
            for p in page['panels']:p['source_svg']=os.path.relpath(p['source_svg'],base).replace(os.sep,'/')
        write(base/(req['id']+'.plan.json'),plan)
        target=base/req['id'];receipt=export_layout(plan,target,base)
        for page in receipt['layout']['pages']:
            for p in page['panels']:p['source_svg']=os.path.relpath(p['source_svg'],target).replace(os.sep,'/')
        write(target/'layout-receipt.json',receipt)
        for page in plan['pages']:rows.append(dict(id=req['id'],file=req['id']+'/'+f"{req['id']}-page-{page['page']+1:02d}.svg",panels=[p['id'] for p in page['panels']]))
    write(base/'manifest.json',dict(records=rows,scientific_analysis=False,visual_acceptance=False,source='existing frozen gallery; no added chart type'))
    html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Flexible existing-panel layouts</title><style>body{font:16px system-ui;margin:35px;color:#283740;background:#f2f5f5}article{background:white;padding:20px;margin:20px 0}img{width:100%;max-width:1200px}p{line-height:1.7}a{color:#177c7e}</style><h1>Flexible complete-panel layouts</h1><p>Two layout demonstrations using existing synthetic frozen components: unequal columns and spans; automatic rows with pagination. No new chart type or inference. Screen examples do not establish manuscript-size acceptance.</p>'
    for r in rows:html+='<article><h2>'+r['file']+'</h2><img src="'+r['file']+'" alt="'+r['id']+'"><p>'+', '.join(r['panels'])+'</p><a href="'+r['id']+'.request.json">Layout request</a> · <a href="'+r['file']+'">Complete SVG</a></article>'
    (base/'index.html').write_text(html,encoding='utf8');print(json.dumps(dict(layouts=2,pages=len(rows),panels=10)))
if __name__=='__main__':main()
