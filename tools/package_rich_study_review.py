"""Publish exact reviewed richer defaults, with portable inputs and prior views."""
import argparse,hashlib,json,shutil,sys
from pathlib import Path
from PIL import Image
from build_v090_public_review import PAGE,write
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(source,proof,out):
    approved=load(proof);assert approved['state']=='SCREEN_REVIEWED';by={r['id']:r for r in approved['records']};manifest=load(source/'manifest.json');assert len(by)==len(manifest['records'])==25
    out.mkdir(parents=True,exist_ok=False);records=[]
    for row in manifest['records']:
        k=row['id'];stem=(source/row['file']).with_suffix('');assert sha(stem.with_suffix('.png'))==by[k]['png_sha256'],k
        folder=out/'study'/k;folder.mkdir(parents=True);assets={};digests={}
        for ext in ['png','svg','pdf','tsv']:
            target=folder/(k+'.'+ext);shutil.copyfile(stem.with_suffix('.'+ext),target);assets[ext]=target.relative_to(out).as_posix();digests[ext]=sha(target)
        inputs=folder/'input';inputs.mkdir()
        for p in (source/k).iterdir():
            if p.suffix=='.tsv' or p.name.endswith('.spec.json'):shutil.copyfile(p,inputs/p.name)
        assets['spec']=(inputs/(k+'.spec.json')).relative_to(out).as_posix()
        old=ROOT/'examples/rejected-v091'/k/(k+'.png')
        if not old.is_file():old=ROOT/'examples/validated-v090/study'/k/(k+'.png')
        shutil.copyfile(old,folder/'previous.png');assets['previous']=(folder/'previous.png').relative_to(out).as_posix();digests['previous']=sha(folder/'previous.png')
        spec=load(inputs/(k+'.spec.json'))
        meta=dict(id=k,assay=row['assay'],role=row['role'],source='Fictional frozen study; no scientific analysis',renderer=spec['renderer'],parameters=spec['parameters'],readability=row['readability'],assets=assets,sha256=digests,visual_review=by[k],scientific_acceptance=False)
        write(folder/'review.json',meta)
        with Image.open(folder/(k+'.png')) as im:im.thumbnail((1100,1000));im.convert('RGB').save(folder/'preview.jpg',quality=93)
        records.append(dict(key='study/'+k,id=k,section='study',form=row['role'],assay=row['assay'],level=None,assets=assets,sha256=digests,preview='study/'+k+'/preview.jpg',review='study/'+k+'/review.json',visual_review=by[k]))
    for assay in ['bulk','single_cell']:
        m=load(source/(assay+'.manifest.json'))
        for r in m['results']:
            k=r['spec'].split('/')[0];r['spec']='../study/'+k+'/input/'+k+'.spec.json'
        write(out/'study-manifests'/(assay+'.json'),m)
    write(out/'ordinary-requests.json',manifest['ordinary_requests']);write(out/'manifest.json',dict(version='0.9.1',records=records,counts={'study':25},review_scope=approved['scope'],scientific_acceptance=False));write(out/'review-ledger.json',approved)
    page=PAGE.replace('/*MANIFEST*/',json.dumps(records,ensure_ascii=False).replace('<','\\u003c')).replace('科研绘图 · 完整图组与布局复查','科研绘图 · 更丰富的默认画法').replace('从普通任务到互补主图与完整配套图。','PCA 椭圆与分布、火山堆积分布、单细胞亚群与 marker 整合图。')
    (out/'index.html').write_text(page,encoding='utf8')
    dest=SKILL/'assets/study-gallery';dest.mkdir(exist_ok=True)
    for name in ['study','study-manifests']:shutil.copytree(out/name,dest/name,dirs_exist_ok=True)
    for name in ['index.html','manifest.json','ordinary-requests.json','review-ledger.json']:shutil.copyfile(out/name,dest/name)
    for k in ['BulkMain','SingleCellMain']:shutil.copyfile(out/'study'/k/'preview.jpg',dest/(k+'.jpg'))
    catalog=load(SKILL/'references/form-catalog.json');catalog['preferred_study_gallery']='examples/rich-v091/index.html';catalog['presentation_policy']='Prefer compatible multi-channel extensions; require a reason for a basic fallback';write(SKILL/'references/form-catalog.json',catalog)
    write(SKILL/'references/review-supersession-v091.json',dict(superseded_scope=['v0.9.0 minimal ordinary study defaults','v0.9.1 crowded candidate study dashboards'],reason='User rejected both simplistic defaults and crowded integrated dashboards. Annotation/marker evidence now has one scope per page and per-identity multi-marker companions.',old_screen_records='Preserved as actual historical screen inspection; withdrawn as aesthetic publication approval',rejected_examples='examples/rejected-v091',replacement='examples/rich-v091/index.html',marker_companions='examples/subgroup-v091/index.html',journal_acceptance_claim=False,scientific_acceptance=False))
    print(json.dumps(dict(status='RICH_REVIEW_SET_PACKAGED',figures=len(records),previous_views_retained=True)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.fixtures,a.review,a.output)
