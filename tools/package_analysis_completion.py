"""Package only actually reviewed exports; no private plans or runtime logs."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from analysis_gallery_page import page
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')


def package(fixtures,rendered,review):
    from PIL import Image
    from pypdf import PdfWriter
    proof=read(review);assert proof['state']=='SCREEN_REVIEWED'
    seen={r['id']:r for r in proof['records']};manifest=read(rendered/'manifest.json');assert not manifest['failures']
    out=SKILL/'assets/analysis-gallery';out.mkdir(parents=True,exist_ok=False);records=[];book=PdfWriter()
    for order,row in enumerate(manifest['records']):
        key=row['id'];s=read(fixtures/row['spec']);source=next(Path(p) for p in row['result']['files'] if p.endswith('.png'))
        assert seen[key]['png_sha256']==sha(source) and seen[key]['state']=='SCREEN_REVIEWED'
        folder=out/key;folder.mkdir();inputs=folder/'input';inputs.mkdir();assets={};hashes={}
        for ext in ['png','svg','pdf','tsv']:
            dest=folder/('example.'+ext);shutil.copyfile(source.with_suffix('.'+ext),dest);assets[ext]=dest.relative_to(out).as_posix();hashes[ext]=sha(dest)
        shutil.copyfile(fixtures/row['spec'],inputs/'example.spec.json');shutil.copyfile((fixtures/row['spec']).parent/s['input']['path'],inputs/'example.tsv')
        assets['spec']=(inputs/'example.spec.json').relative_to(out).as_posix();hashes['spec']=sha(inputs/'example.spec.json')
        with Image.open(source) as image:image.thumbnail((1450,1250));image.convert('RGB').save(folder/'preview.jpg',quality=94)
        assets['preview']=(folder/'preview.jpg').relative_to(out).as_posix()
        for ext in ['png','svg','pdf','tsv']:assert hashes[ext]==sha(out/assets[ext])
        entry=dict(id=key,title=s['parameters']['title'],chapters=row['chapters'],stage=row['stage'],family=row['family'],variant=row['variant'],order=order,
                   renderer=s['renderer'],parameters=s['parameters'],definition=s['parameters'].get('definition',s['parameters']['context']['selection']),
                   requirements=sorted(s['parameters']),assets=assets,sha256=hashes,readability=row['result']['print_readability'],review=seen[key],
                   analysis_performed=False,scientific_acceptance=False)
        write(folder/'review.json',entry);records.append(entry);book.append(str(source.with_suffix('.pdf')))
    assert set(seen)==set(r['id'] for r in records)
    book.write(str(out/'Analysis_Companions_FigureBook.pdf'));book.close()
    write(out/'manifest.json',dict(version='0.9.7',records=records,analysis_performed=False,scientific_acceptance=False));write(out/'review-ledger.json',proof)
    chapters=[dict(id=k,label=k) for k in sorted({c for r in records for c in r['chapters']})]
    (out/'index.html').write_text(page(records,chapters,f'{len(records)} 个本轮专用视图与数据量／布局实例；每页有可复用代码、冻结输入及 PNG／SVG／PDF。'),encoding='utf8')
    print(json.dumps(dict(state='EXACT_REVIEWED_EXPORTS_PACKAGED',figures=len(records))))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['fixtures','rendered','review']:p.add_argument('--'+key,required=True,type=Path)
    a=p.parse_args();package(a.fixtures,a.rendered,a.review)
