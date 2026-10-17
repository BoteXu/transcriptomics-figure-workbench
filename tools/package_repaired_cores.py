"""Publish reviewed fictional core revisions into their existing gallery slots.

Only explicit manifest folders inside the skill are replaced. Previous bytes are
preserved in the caller-selected private snapshot, with no runtime receipts in
the public gallery. Rebuilds the affected indexes and collected PDF afterwards.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from analysis_gallery_page import page
from package_chapter_review import PAGE
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(fixtures,rendered,review,snapshot):
    from PIL import Image
    from pypdf import PdfWriter
    manifest=read(rendered/'manifest.json');proof=read(review)
    assert not manifest.get('failures') and proof['state']=='SCREEN_REVIEWED'
    seen={r['id']:r for r in proof['records']};expected={r['id'] for r in read(fixtures/'manifest.json')['records']}
    assert set(seen)==expected=={r['id'] for r in manifest['records']}
    checked=[]
    for row in manifest['records']:
        k=row['id'];r=seen[k];s=read(fixtures/row['spec']);source=next(Path(p) for p in row['result']['files'] if p.endswith('.png'))
        assert r['state']=='SCREEN_REVIEWED' and r['notes'] and sha(source)==r['png_sha256'] and row['result']['print_readability']['state']=='MEASUREMENT_PASS'
        dest=(SKILL/row['public_folder']).resolve();assert SKILL.resolve() in dest.parents and dest.is_dir()
        assert s['provenance']['synthetic'] is True
        checked.append((row,r,s,source,dest))
    snapshot.mkdir(parents=True,exist_ok=False);changed={}
    for row,r,s,source,dest in checked:
        old=read(dest/'review.json');gallery=dest.parent;relative=dest.relative_to(SKILL)
        shutil.copytree(dest,snapshot/relative)
        for ext in ['png','svg','pdf','tsv']:shutil.copyfile(source.with_suffix('.'+ext),dest/('example.'+ext))
        shutil.copyfile(fixtures/row['spec'],dest/'input/example.spec.json')
        shutil.copyfile((fixtures/row['spec']).parent/s['input']['path'],dest/'input/example.tsv')
        with Image.open(source) as im:im.thumbnail((1450,1500));im.convert('RGB').save(dest/'preview.jpg',quality=94)
        old['title']=s['parameters'].get('title',old['title']);old['readability']=row['result']['print_readability']
        old['sha256']={k:sha(gallery/v) for k,v in old['assets'].items() if k!='preview'}
        if 'parameters' in old:old['parameters']=s['parameters']
        if 'definition' in old:old['definition']=s['parameters'].get('definition',s['parameters'].get('scope_note',old['definition']))
        # A panel view ID and its parent gallery ID are distinct identities.
        # The gallery ledger stays keyed by the gallery ID, retaining the view.
        old['review' if 'review' in old else 'visual_review']=dict(r,id=old['id'],core_view_id=r['id'])
        history=list(old.get('display_revision_history',[]))
        if old.get('display_revision') and old['display_revision'] not in history:history.append(old['display_revision'])
        old['display_revision_history']=history;old['display_revision']='0.10.0';old['scientific_acceptance']=False
        write(dest/'review.json',old);changed.setdefault(gallery,{})[old['id']]=old
    for gallery,updates in changed.items():
        current=read(gallery/'manifest.json');current['records']=[updates.get(r['id'],r) for r in current['records']];current['display_revision']='0.10.0';write(gallery/'manifest.json',current)
        reviews=[]
        for row in current['records']:reviews.append(row.get('review',row.get('visual_review')))
        write(gallery/'review-ledger.json',dict(state='SCREEN_REVIEWED',records=reviews,scientific_acceptance=False))
        if gallery.name=='analysis-gallery':
            chapters=[dict(id=c,label=c) for c in sorted({c for r in current['records'] for c in r['chapters']})]
            text=page(current['records'],chapters,'Original network and program companions, with individually reviewed core display revisions.')
            book=PdfWriter()
            for row in current['records']:book.append(str(gallery/row['assets']['pdf']))
            book.write(str(gallery/'Analysis_Companions_FigureBook.pdf'));book.close()
        else:
            text=PAGE.replace('/*ROWS*/',json.dumps(current['records'],ensure_ascii=False).replace('<','\\u003c'))
            if gallery.name!='chapter-gallery':text=text.replace('x.assay===assay.value','(x.assay===assay.value||x.assays.includes(assay.value))').replace('58个分析章节，每章有实际绘图代码、可运行配置、准确示例表和PNG/SVG/PDF。',str(len(current['records']))+'个专用配套示例，有准确输入和实际导出。')
        (gallery/'index.html').write_text(text,encoding='utf8')
    print(json.dumps(dict(state='EXACT_REVIEWED_CORE_REVISIONS_PACKAGED',figures=len(checked),galleries=len(changed),runtime_receipts_public=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['fixtures','rendered','review','snapshot']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();package(a.fixtures,a.rendered,a.review,a.snapshot)
