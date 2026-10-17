"""Package only exact individually reviewed per-analysis exports."""
import argparse,csv,hashlib,json,shutil
from pathlib import Path
from analysis_gallery_page import page
from build_analysis_library import LABELS
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def package(fixtures,rendered,review):
    from PIL import Image
    from pypdf import PdfWriter
    manifest=read(rendered/'manifest.json');proof=read(review);assert not manifest['failures']
    expected=read(fixtures/'manifest.json')['records'];assert {r['id'] for r in expected}=={r['id'] for r in manifest['records']}
    assert proof['state']=='SCREEN_REVIEWED';seen={r['id']:r for r in proof['records']};assert set(seen)=={r['id'] for r in expected}
    out=SKILL/'assets/companion-gallery';out.mkdir(parents=True,exist_ok=False);book=PdfWriter();records=[]
    for i,row in enumerate(manifest['records']):
        key=row['id'];s=read(fixtures/row['spec']);source=next(Path(p) for p in row['result']['files'] if p.endswith('.png'));r=seen[key]
        assert r['state']=='SCREEN_REVIEWED' and r['png_sha256']==sha(source) and r['notes']
        assert row['result']['print_readability']['state']=='MEASUREMENT_PASS'
        dest=out/key;dest.mkdir();inputs=dest/'input';inputs.mkdir();assets={};hashes={}
        for ext in ['png','svg','pdf','tsv']:
            p=dest/('example.'+ext);shutil.copyfile(source.with_suffix('.'+ext),p);assets[ext]=p.relative_to(out).as_posix();hashes[ext]=sha(p)
        shutil.copyfile(fixtures/row['spec'],inputs/'example.spec.json');shutil.copyfile((fixtures/row['spec']).parent/s['input']['path'],inputs/'example.tsv')
        assets['spec']=(inputs/'example.spec.json').relative_to(out).as_posix();hashes['spec']=sha(inputs/'example.spec.json')
        with Image.open(source) as im:im.thumbnail((1450,1500));im.convert('RGB').save(dest/'preview.jpg',quality=94)
        assets['preview']=(dest/'preview.jpg').relative_to(out).as_posix()
        with (inputs/'example.tsv').open(encoding='utf8',newline='') as f:channels=next(csv.reader(f,delimiter='\t'))
        record=dict(id=key,title=s['parameters']['title'],chapters=row['chapters'],stage=row['stage'],family=row['family'],variant=row['variant'] or key.endswith('_Evidence'),large_data=row.get('large_data',False),order=i,renderer=s['renderer'],parameters=s['parameters'],definition=s['parameters']['definition'],requirements=channels+['panel definitions','independent-unit/source context'],assets=assets,sha256=hashes,readability=row['result']['print_readability'],review=r,analysis_performed=False,scientific_acceptance=False)
        write(dest/'review.json',record);records.append(record);book.append(str(source.with_suffix('.pdf')))
    book.write(str(out/'All_Analysis_Companions.pdf'));book.close()
    write(out/'manifest.json',dict(version='0.10.0',records=records,analysis_performed=False,scientific_acceptance=False));write(out/'review-ledger.json',proof)
    chapters=[dict(id=c,label=LABELS[c]) for c in sorted({c for r in records for c in r['chapters']})]
    (out/'index.html').write_text(page(records,chapters,f'{len(chapters)} 个逐项扩展章节；{len(records)} 份实际单图、配套组图与数据量／自定义布局。全部为冻结合成示例。'),encoding='utf8')
    print(json.dumps(dict(state='REVIEWED_ANALYSIS_COMPANIONS_PACKAGED',chapters=len(chapters),figures=len(records))))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ['fixtures','rendered','review']:p.add_argument('--'+k,required=True,type=Path)
    a=p.parse_args();package(a.fixtures,a.rendered,a.review)
