"""Package real scale variants and complete SVG layouts; require individual review.

Only synthetic public tables/specs and exports are selected. Private runtime
paths, logs, execution receipts and source profiles are never included.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.layout import make_layout,export_layout,load_svg

def read(p):return json.loads(Path(p).read_text('utf8'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package(fixtures,renders,out):
    fixtures=fixtures.resolve();renders=renders.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    rows=read(fixtures/'manifest.json')['records'];receipt=read(renders/'render-receipt.json')['records']
    if {r['id'] for r in rows}!={r['id'] for r in receipt if r['state']!='FAILED'}:raise ValueError('Every scale variant must actually render')
    labels={r['id']:r['display_name'] for r in read(SKILL/'references/renderer-registry.json')['renderers']}
    records=[];methods={}
    for row in rows:
        key=row['id'];methods.setdefault(row['method_id'],[]).append(row);folder=out/key;folder.mkdir();assets={}
        for extension in ['png','svg','pdf','tsv','gif','html','animation.json']:
            source=renders/key/(key+'.'+extension)
            if source.is_file():
                shutil.copyfile(source,folder/source.name);assets['animation' if extension=='animation.json' else extension]=key+'/'+source.name
        spec=read(fixtures/row['spec']);spec['input']['path']=key+'.tsv';write(folder/'example.spec.json',spec);assets['spec']=key+'/example.spec.json'
        record=dict(row,assets=assets,title=labels[row['renderer']]+' · '+{'Small':'小数据','Medium':'中数据','Large':'大数据','Custom':'自定义布局'}[row['variant']],variant=row['variant']!='Medium',scale_variant=row['variant'],visual_review='RENDERED_UNREVIEWED',definition='明确标记的合成绘图测试；'+row['volume']['preparation'])
        record.pop('spec',None);records.append(record)
    for method,members in methods.items():
        large=next(r for r in members if r['variant']=='Large');custom=next(r for r in members if r['variant']=='Custom')
        if large['input_sha256']!=custom['input_sha256']:raise ValueError('Custom layout must use identical complete input')
        key='Scale_'+method+'_Composition';folder=out/key;folder.mkdir();panels=[]
        boxes=[]
        for name,r in [('A  Large · complete selected source',large),('B  Caller layout · same source',custom)]:
            native=r['id'];_,box=load_svg(out/native/(native+'.svg'));boxes.append(box)
            panels.append(dict(id=native,label=name,svg='../'+native+'/'+native+'.svg',table='../'+native+'/'+native+'.tsv'))
        cols=1 if max(b[3]/b[2] for b in boxes)>1.9 or max(b[3] for b in boxes)/min(b[3] for b in boxes)>1.6 else 2
        width=max(b[2] for b in boxes)
        request=dict(id=key,title=labels[large['renderer']]+' · same input, different complete layout',columns=cols,canvas_width_pt=round(48+cols*width+(cols-1)*24,2),gap_pt=24,padding_pt=24,heading_pt=40,panel_label_gutter_pt=20,packing='masonry',packing_order='input',panels=panels)
        write(folder/'layout.request.json',request);plan=make_layout(request,folder);private=renders/(key+'_layout');export_layout(plan,private)
        shutil.copyfile(next(private.glob('*.svg')),folder/(key+'.svg'))
        records.append(dict(id=key,renderer=large['renderer'],form=large['form'],method_id=method,variant=True,composition=True,scale_variant='Composition',input_sha256=large['input_sha256'],title=labels[large['renderer']]+' · 完整单图组装',definition='同一大数据冻结输入；所有坐标、图例与数值通道随完整 SVG 保留。布局变化不是新科学结果。',assets=dict(svg=key+'/'+key+'.svg',png=key+'/'+key+'.png',layout=key+'/layout.request.json'),visual_review='RENDERED_UNREVIEWED'))
    write(out/'manifest.json',dict(schema_version=1,records=records,methods=45,native_examples=180,composition_examples=45,scientific_acceptance=False,aesthetic_approval=False))
    print(json.dumps(dict(state='ACTUAL_SCALE_EXPORTS_PACKAGED_UNREVIEWED',native=len(rows),compositions=len(methods))))


def finalize(out,reviews):
    doc=read(out/'manifest.json');review=read(reviews);by={r['id']:r for r in review['records']}
    if set(by)!={r['id'] for r in doc['records']}:raise ValueError('All 225 actual PNGs require individual review')
    for row in doc['records']:
        r=by[row['id']];digest=sha(out/row['assets']['png'])
        if r.get('state')!='SCREEN_REVIEWED' or r.get('png_sha256')!=digest or not r.get('notes'):raise ValueError('Missing or stale exact-pixel review: '+row['id'])
        row['visual_review']=dict(state=r['state'],png_sha256=digest,notes=r['notes'],scope='Authoring-agent individual actual image inspection; not independent aesthetic or scientific acceptance')
        row.update(method='method-'+row['method_id'],subtype=row['title'],history=False,chapters=[],domains=['general'],executable_spec='spec' in row['assets'],source_gallery='../visual-library/index.html#method-scale-gallery/'+row['id'],aliases=[row['id']])
    entries=[]
    for row in [r for r in doc['records'] if r['scale_variant']=='Medium']:
        entries.append(dict(id=row['method'],title=row['title'].rsplit(' · ',1)[0],member_ids=[r['id'] for r in doc['records'] if r['method_id']==row['method_id']],default_id=row['id']))
    doc['review_scope']='180 singles and 45 complete SVG compositions individually inspected; long pages additionally inspected in native crops'
    write(out/'manifest.json',doc);write(out/'visual-review.json',review)
    local=dict(records=doc['records'],entries=entries,aliases={r['id']:r['id'] for r in doc['records']},domains=[dict(id='general',label='45 种方法 · 数据量与布局实测')],chapters=[],form_labels={r['form']:r['title'].rsplit(' · ',1)[0] for r in doc['records'] if r['scale_variant']=='Medium'})
    template=(SKILL/'assets/studio/visual-library.html').read_text('utf8');(out/'index.html').write_text(template.replace('/*DATA*/{}',json.dumps(local,ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    print(json.dumps(dict(state='ALL_SCALE_REVIEWS_BOUND',images=len(by))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path);p.add_argument('--renders',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--reviews',type=Path);a=p.parse_args()
    if a.reviews:finalize(a.output,a.reviews)
    else:package(a.fixtures,a.renders,a.output)
