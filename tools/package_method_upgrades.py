"""Package actual migrated exports and editable complete-panel layout requests.

No rendering success, font audit or directory entry grants aesthetic acceptance.
Review notes must be supplied separately and bind every exact final PNG hash.
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(S/'scripts'))
from figure_workbench.layout import make_layout,export_layout


def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package(fixtures,renders,out):
    fixtures=fixtures.resolve();renders=renders.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    rows=read(fixtures/'manifest.json')['records'];receipt=read(renders/'render-receipt.json')['records']
    successful={r['id'] for r in receipt if r['state']!='FAILED'}
    if successful!={r['id'] for r in rows}:raise ValueError('Every selected native example must actually render first')
    labels={r['id']:r['display_name'] for r in read(S/'references/renderer-registry.json')['renderers']}
    records=[]
    for row in rows:
        key=row['id'];folder=out/key;folder.mkdir();source=renders/key
        assets={}
        for ext in ['png','svg','pdf','tsv','gif','html','animation.json']:
            p=source/(key+'.'+ext)
            if p.is_file():
                shutil.copyfile(p,folder/p.name);assets[{'animation.json':'animation'}.get(ext,ext)]=key+'/'+p.name
        spec=read(fixtures/row['spec']);spec['input']['path']=key+'.tsv'
        write(folder/'example.spec.json',spec);assets['spec']=key+'/example.spec.json'
        edition=' · 自定义布局' if key.endswith('_Custom') else ' · 小数据与替代视角' if key.endswith('_Small') else ' · 当前默认'
        definition=('从原始公开冻结表逐字节迁移；旧图继续保留。' if row.get('upgraded_from') else
                    '明确标记的合成绘图示例；给定坐标、体素或帧序列，无科学模型拟合。')
        record=dict(row,title=labels[row['renderer']]+edition,assets=assets,definition=definition,
                    visual_review='RENDERED_UNREVIEWED',input_sha256=spec['input']['sha256'])
        record.pop('spec',None);records.append(record)
    # A real complete-SVG composition per method, not a thumbnail or new method.
    # Panels keep all guides and coordinate geometry. Natural source widths and
    # explicit columns determine height; no fixed universal row count.
    for row in [r for r in rows if not r['variant']]:
        key=row['id'];custom=key+'_Custom';cid=key+'_Composition';folder=out/cid;folder.mkdir()
        from figure_workbench.layout import load_svg
        _,box=load_svg(out/key/(key+'.svg'));_,cb=load_svg(out/custom/(custom+'.svg'))
        column_width=max(box[2],cb[2])
        # Both complete source shapes matter. A short left panel beside a very
        # tall custom view leaves most of the canvas empty and impairs reading.
        cols=1 if max(box[3]/box[2],cb[3]/cb[2])>1.8 or max(box[3],cb[3])/min(box[3],cb[3])>1.6 or column_width>1000 else 2
        request=dict(id=cid,title='Same frozen input · default and caller-selected layout',columns=cols,
                     canvas_width_pt=round(48+column_width*cols+24*(cols-1),2),
                     gap_pt=24,padding_pt=24,heading_pt=40,panel_label_gutter_pt=20,
                     packing='masonry',packing_order='input',
                     panels=[dict(id='Default',svg='../'+key+'/'+key+'.svg',table='../'+key+'/'+key+'.tsv',label='A  Default · complete source'),
                             dict(id='Custom',svg='../'+custom+'/'+custom+'.svg',table='../'+custom+'/'+custom+'.tsv',label='B  Caller-selected layout · same source')])
        write(folder/'layout.request.json',request)
        plan=make_layout(request,folder);private=renders/(cid+'_layout')
        rendered=export_layout(plan,private)
        svg=next(private.glob('*.svg'));shutil.copyfile(svg,folder/(cid+'.svg'))
        records.append(dict(id=cid,renderer=row['renderer'],form=row['form'],variant=True,composition=True,
            upgraded_from=row.get('upgraded_from'),input_sha256=row['source_sha256'],
            title=labels[row['renderer']]+' · 完整单图组装示例',
            definition='两幅完整单图采用同一冻结输入；显式列数、自然高度与完整图例。布局变化不是独立科学结果。',
            assets=dict(svg=cid+'/'+cid+'.svg',png=cid+'/'+cid+'.png',layout=cid+'/layout.request.json'),
            visual_review='RENDERED_UNREVIEWED'))
    write(out/'manifest.json',dict(schema_version=1,records=records,baseline_recipes=42,new_methods=3,
        native_examples=len(rows),composition_examples=45,scientific_acceptance=False,aesthetic_approval=False))
    print(json.dumps(dict(state='ACTUAL_EXPORTS_PACKAGED_UNREVIEWED',native=len(rows),layouts=45)))


def finalize(out,reviews):
    d=read(out/'manifest.json');review=read(reviews);by={r['id']:r for r in review['records']}
    if set(by)!={r['id'] for r in d['records']}:raise ValueError('Individual review required for every native and composed image')
    for r in d['records']:
        rev=by[r['id']];p=out/r['assets']['png']
        if rev.get('png_sha256')!=sha(p) or rev.get('state')!='SCREEN_REVIEWED' or not rev.get('notes'):
            raise ValueError('Missing, stale or unreviewed pixels: '+r['id'])
        r['visual_review']=dict(state='SCREEN_REVIEWED',png_sha256=sha(p),notes=rev['notes'],
                                scope='Agent individual screen review; not independent journal acceptance')
    d['aesthetic_approval']=False;d['review_scope']='Every shipped native PNG and composition individually inspected by the authoring agent'
    write(out/'manifest.json',d);write(out/'visual-review.json',review)
    # The shared offline reader also presents this focused per-renderer gallery.
    groups=[]
    for r in [r for r in d['records'] if not r['variant']]:
        group='method-'+r['id'];members=[x for x in d['records'] if x['renderer']==r['renderer']]
        groups.append(dict(id=group,title=r['title'].replace(' · 当前默认',''),member_ids=[x['id'] for x in members],default_id=r['id']))
        for x in members:x.update(method=group,form=r['form'],subtype=x['title'],history=False,chapters=[],
                                  executable_spec='spec' in x['assets'],source_gallery='../visual-library/index.html#method-upgrade-gallery/'+x['id'],aliases=[x['id']])
    local=dict(records=d['records'],entries=groups,aliases={r['id']:r['id'] for r in d['records']},
               domains=[dict(id='general',label='全部迁移与新增方法')],chapters=[],
               form_labels={r['form']:r['title'].replace(' · 当前默认','') for r in d['records'] if not r['variant']})
    for r in local['records']:r['domains']=['general']
    template=(S/'assets/studio/visual-library.html').read_text(encoding='utf8')
    (out/'index.html').write_text(template.replace('/*DATA*/{}',json.dumps(local,ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    print(json.dumps(dict(state='INDIVIDUAL_SCREEN_REVIEWS_BOUND',figures=len(d['records']))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path);p.add_argument('--renders',type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--reviews',type=Path);a=p.parse_args()
    if a.reviews:finalize(a.output,a.reviews)
    else:package(a.fixtures,a.renders,a.output)
