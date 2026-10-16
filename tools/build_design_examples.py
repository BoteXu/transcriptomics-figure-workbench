"""Render attractive alternatives from existing frozen synthetic display tables."""
from pathlib import Path
import argparse, copy, csv, json, sys
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest
from project_theme import create_theme


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream,delimiter='\t'))


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def build(output):
    output.mkdir(exist_ok=False,parents=True);inputs=output/'inputs';inputs.mkdir()
    template=json.loads((ROOT/'examples/package-v040/inputs/PKG12.spec.json').read_text(encoding='utf8'))
    cases=[]
    source=ROOT/'examples/package-v040/PKG09/PKG09.tsv';q=read(source);names=list(dict.fromkeys(r['group'] for r in q))
    density=[dict(record_type='density',label=r['group'],x=r['x'],density=r['density']) for r in q]
    # Independent illustrative display constants, not inferred from a density.
    for n,e in zip(names,[-.5,.5,-1.,1.,-1.5]):density.append(dict(record_type='summary',label=n,estimate=e,lower=e-.85,upper=e+.85,inner_lower=e-.30,inner_upper=e+.30))
    cases.append(('VIS01','publication_plus','halfeye',density,dict(order=list(reversed(names)),reference=0,x_label='Supplied gene-level statistic',interval_definition='Illustrative outer/inner display bounds; probabilities unspecified',title='Distribution profiles and supplied summaries',subtitle='Frozen gene-level display profiles / illustrative points and bounds'),source))
    source=ROOT/'examples/package-v040/PKG12/PKG12.tsv';q=read(source);rows=list(dict.fromkeys(r['feature'] for r in q));cols=list(dict.fromkeys(r['sample'] for r in q))
    matrix=[dict(row=r['feature'],column=r['sample'],value=r['value'],row_group='Response' if rows.index(r['feature'])<4 else 'Maintenance',column_group='Condition '+r['sample'][0]) for r in q]
    cases.append(('VIS02','publication_plus','split_matrix',matrix,dict(row_order=rows,column_order=cols,limits=[-1,1],value_label='GSVA score (demo)',title='Pathway activity in a shared coordinate grid',subtitle='Supplied pathway scores / predefined row and condition groups'),source))
    source=ROOT/'examples/gallery/figures/R02/R02.tsv';q=read(source);names=list(dict.fromkeys(r['series'] for r in q))
    cases.append(('VIS03','publication_plus','profile',q,dict(category_order=list(dict.fromkeys(r['category'] for r in q)),series_order=names,area_max=9000,area_label='Secondary value\n(point area)',value_limits=[0,5500],value_label='Primary value',title='Compare profiles on aligned linear scales',subtitle='Same frozen table as R02 / original category order and units'),source))
    source=ROOT/'examples/gallery/figures/P34/P34.tsv';q=read(source)
    forest=[dict(label=r['category']+' · '+r['group'],group=r['group'],estimate=r['estimate'],lower=r['lower'],upper=r['upper']) for r in q]
    cases.append(('VIS04','package_style','forest',forest,dict(effect_scale='difference',interval_label='Same supplied estimates and intervals as P34',x_label='Supplied estimate',title='Compare estimates without filled bars'),source))
    source=ROOT/'examples/gallery/figures/T19/T19.tsv';q=read(source)
    points=[dict(cell_id=r['unit_id'],group=r['group'],x=r['x'],y=r['y']) for r in q]
    cases.append(('VIS05','package_style','embedding',points,dict(point_size=5,label_positions={'G1':[-5,7],'G2':[0,7],'G3':[5,2.5],'G4':[-5,-7],'G5':[0,-8.5],'G6':[5,-7.5]},axis_prefix='Dim',title='Distinct identities in stored coordinates',subtitle='Same frozen coordinates as T19 / six distinguishable category colours'),source))
    records=[]
    for key,renderer,view,rows,options,source in cases:
        columns=list(dict.fromkeys(k for r in rows for k in r));p=inputs/(key+'.tsv')
        with p.open('w',encoding='utf8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns,delimiter='\t');writer.writeheader();writer.writerows(rows)
        groups=list(dict.fromkeys(str(r[k]) for r in rows for k in ['label' if view=='halfeye' else 'group','row_group','column_group','series'] if k in r))
        if view=='forest':groups=list(dict.fromkeys(r['group'] for r in rows))
        spec=copy.deepcopy(template);spec.update(figure_id=key,renderer=renderer,input=dict(path=p.name,sha256=digest(p)))
        spec['parameters'].update(view=view,options=options)
        spec['theme']=create_theme('synthetic-design-'+key,'package_editorial',{g:i for i,g in enumerate(groups)},font_family='DejaVu Sans')
        spec['theme']['continuous'].update(diverging=['#327D9F','#F7F7F4','#D8795B'],sequential=['#E2EFEB','#6DB3A7','#1C6C70'])
        spec['provenance'].update(source='Frozen public synthetic display source: '+source.relative_to(ROOT).as_posix(),contrast='Synthetic display only; no biological inference')
        spec['export']=dict(target_width_mm=178,minimum_text_pt=6.5,readability_policy='block')
        write(inputs/(key+'.spec.json'),spec)
        render_plan(make_plan(spec,inputs),output)
        receipt=output/key/(key+'.json');meta=json.loads(receipt.read_text(encoding='utf8'));meta['source_file']='inputs/'+p.name;write(receipt,meta)
        records.append(dict(id=key,renderer=renderer,view=view,source=source.relative_to(ROOT).as_posix(),source_sha256=digest(source),input_sha256=digest(p),png_sha256=digest(output/key/(key+'.png')),status='RENDERED_UNREVIEWED'))
        write(output/'manifest.json',dict(records=records,scientific_acceptance=False));print(key+' rendered',flush=True)
    cards=[]
    for row in records:
        k=row['id'];cards.append('<article id="'+k+'"><h2>'+k+' · '+row['view']+'</h2><img src="'+k+'/'+k+'.png" alt="Synthetic '+row['view']+'"><p>'+ ' · '.join('<a href="'+k+'/'+k+'.'+e+'">'+e.upper()+'</a>' for e in ['svg','pdf','tsv','json'])+' · <a href="inputs/'+k+'.spec.json">FigureSpec</a></p></article>')
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Publication alternatives</title><style>body{font:16px/1.6 system-ui;background:#edf1f3;color:#243449;max-width:1080px;padding:24px;margin:auto}article{background:white;padding:30px;margin:24px 0;border-radius:12px}img{max-width:100%;max-height:1100px;display:block;margin:auto}a{color:#218C8D}</style><h1>Attractive publication alternatives</h1><p>Five actual frozen-result examples. Original source tables are synthetic; no native package, density estimation, model or clustering was run. <a href="self-review.json">Exact visual review</a>.</p>'+''.join(cards),encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);build(parser.parse_args().output)
