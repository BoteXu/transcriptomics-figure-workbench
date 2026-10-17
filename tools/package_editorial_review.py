# -*- coding: utf-8 -*-
"""Publish exact screened exports; retain old versioned snapshots and private logs."""
import argparse, copy, hashlib, json, shutil
from pathlib import Path
from PIL import Image
from package_chapter_review import PAGE
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'

def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def preview(source,target):
    with Image.open(source) as im:
        im.thumbnail((1450,1350));im.convert('RGB').save(target,quality=94)

def inline_rows(path,rows):
    text=path.read_text(encoding='utf8')
    marker='const rows=' if 'const rows=' in text else 'let rows='
    start=text.index(marker)+len(marker)
    old,n=json.JSONDecoder().raw_decode(text[start:])
    assert {r['id'] for r in old}=={r['id'] for r in rows}
    text=text[:start]+json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')+text[start+n:]
    text=text.replace('r.visual_review.status','(r.visual_review.decision||r.visual_review.status)')
    path.write_text(text,encoding='utf8')

def build(fixtures,rendered,review,out):
    proof=load(review);assert proof['state']=='SCREEN_REVIEWED'
    accepted={r['id']:r for r in proof['records']}
    source=load(rendered/'manifest.json')['records']
    assert {r['id'] for r in source}==set(accepted)
    out.mkdir(parents=True,exist_ok=False);rows=[];changes={}
    for row in source:
        k=row['id'];stem=next(Path(p).with_suffix('') for p in row['result']['files'] if p.endswith('.png'))
        assert sha(stem.with_suffix('.png'))==accepted[k]['png_sha256']
        spec=load(fixtures/row['spec']);folder=out/k;folder.mkdir();(folder/'input').mkdir()
        assets={};hashes={}
        for ext in ['png','svg','pdf','tsv']:
            target=folder/('example.'+ext);shutil.copyfile(stem.with_suffix('.'+ext),target)
            assets[ext]=target.relative_to(out).as_posix();hashes[ext]=sha(target)
        for filename in ['example.spec.json','example.tsv']:
            shutil.copyfile((fixtures/row['spec']).parent/filename,folder/'input'/filename)
        assets['spec']=(folder/'input/example.spec.json').relative_to(out).as_posix()
        hashes['spec']=sha(folder/'input/example.spec.json')
        preview(folder/'example.png',folder/'preview.jpg');assets['preview']=(folder/'preview.jpg').relative_to(out).as_posix()
        record=dict(id=k,title=spec['parameters'].get('title',k),assay=row['assay'],assets=assets,sha256=hashes,
            visual_review=accepted[k],readability=row['result']['print_readability'],scientific_acceptance=False,
            required_results=sorted(spec['parameters']),sources=['https://www.nature.com/articles/s41590-025-02267-8/figures/1','https://www.nature.com/articles/s41587-026-03068-6/figures/3'],
            specific_qc_and_limit='Fictional frozen display inputs; no inference or biological acceptance. Long vertical variants are reading editions, not default manuscript layouts.',
            input_unchanged=row.get('frozen_input_unchanged',False))
        if row.get('origin_spec'):
            origin=SKILL/row['origin_spec'];oldspec=load(origin)
            assert sha(origin.parent/oldspec['input']['path'])==spec['input']['sha256']
            # Find the unique exact current-gallery record by its spec path.
            gallery=SKILL/Path(row['origin_spec']).parts[0]/Path(row['origin_spec']).parts[1]
            old=load(gallery/'manifest.json');matches=[r for r in old['records'] if (gallery/r['assets']['spec']).resolve()==origin.resolve()];assert len(matches)==1
            previous=matches[0];pathmap=previous.get('assets',previous)
            before=gallery/pathmap['png'];oldhash=sha(before)
            shutil.copyfile(before,folder/'before.png');record['before_png']=k+'/before.png';record['before_sha256']=oldhash
            current_check=dict(accepted[k],id=previous['id'],source_figure_id=k)
            changes.setdefault(gallery,{})[previous['id']]=(row,current_check,stem,oldhash)
        write(folder/'review.json',record);rows.append(record)
    write(out/'manifest.json',dict(version='0.9.2',records=rows,analysis_performed=False,scientific_acceptance=False))
    write(out/'review-ledger.json',proof)
    page=PAGE.replace('58个分析章节，每章有实际绘图代码、可运行配置、准确示例表和PNG/SVG/PDF。','27个经过实际屏幕复看的编辑修订与布局检验示例。23个已有示例保留相同输入，4个明确虚构的 marker 数量变体检查布局。').replace('Bulk 与单细胞 · 分析章节图库','注释证据与富集故事 · 布局修订').replace('/*ROWS*/',json.dumps(rows,ensure_ascii=False).replace('<','\\u003c'))
    page=page.replace("const d=el('details');","if(r.before_png){const a=el('a','修订前 PNG');a.href=r.before_png;a.target='_blank';a.rel='noopener';card.append(a)}const d=el('details');")
    (out/'index.html').write_text(page,encoding='utf8')
    for gallery,updates in changes.items():
        doc=load(gallery/'manifest.json')
        for r in doc['records']:
            if r['id'] not in updates:continue
            row,check,stem,oldhash=updates[r['id']];pathmap=r.get('assets',r)
            for ext in ['png','svg','pdf','tsv']:
                target=gallery/pathmap[ext];shutil.copyfile(stem.with_suffix('.'+ext),target)
                r.setdefault('sha256',{})[ext]=sha(target)
            preview(gallery/pathmap['png'],gallery/(pathmap.get('preview') or r['preview']))
            r['visual_review']=copy.deepcopy(check);r['readability']=row['result']['print_readability']
            r['display_revision']='0.9.2';r['previous_png_sha256']=oldhash
            rp=gallery/r['review'] if 'review' in r else (gallery/pathmap['png']).parent/'review.json'
            write(rp,r)
            if gallery.name=='study-gallery' and r['id']=='SingleCellMain':
                preview(gallery/pathmap['png'],gallery/'SingleCellMain.jpg')
        doc['display_revision']='0.9.2';write(gallery/'manifest.json',doc)
        ledger=load(gallery/'review-ledger.json')
        ledger['records']=[copy.deepcopy(updates[r['id']][1]) if r['id'] in updates else r for r in ledger['records']]
        ledger['display_revision']='0.9.2';write(gallery/'review-ledger.json',ledger)
        inline_rows(gallery/'index.html',doc['records'])
    shutil.copytree(out,SKILL/'assets/editorial-gallery',dirs_exist_ok=False)
    print(json.dumps(dict(status='EDITORIAL_REVIEW_PACKAGED',figures=len(rows),existing_updated=sum(map(len,changes.values())),private_runtime_metadata_included=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['fixtures','rendered','review','output']:p.add_argument('--'+key,required=True,type=Path)
    a=p.parse_args();build(a.fixtures,a.rendered,a.review,a.output)
