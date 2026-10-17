# -*- coding: utf-8 -*-
"""Package actual, hash-bound reviewed dedicated method displays, privately gated."""
import argparse,hashlib,json,shutil
from pathlib import Path
from package_chapter_review import PAGE
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def build(fixtures,rendered,review,out,kind):
    from PIL import Image
    proof=load(review);assert proof['state']=='SCREEN_REVIEWED';by={r['id']:r for r in proof['records']};out.mkdir(parents=True,exist_ok=False);rows=[]
    sources=['https://edo98811.github.io/WGCNA_official_documentation/','https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html'] if kind=='wgcna' else ['https://lazappi.github.io/clustree/articles/clustree.html','https://cole-trapnell-lab.github.io/monocle3/docs/trajectories/','https://github.com/guigolab/ggsashimi']
    for row in load(rendered/'manifest.json')['records']:
        k=row['id'];stem=next(Path(p).with_suffix('') for p in row['result']['files'] if p.endswith('.png'));assert sha(stem.with_suffix('.png'))==by[k]['png_sha256'];s=load(fixtures/row['spec']);folder=out/k;folder.mkdir();inputs=folder/'input';inputs.mkdir();assets={};hashes={}
        for ext in ['png','svg','pdf','tsv']:
            p=folder/('example.'+ext);shutil.copyfile(stem.with_suffix('.'+ext),p);assets[ext]=p.relative_to(out).as_posix();hashes[ext]=sha(p)
        shutil.copyfile(fixtures/row['spec'],inputs/'example.spec.json');shutil.copyfile(fixtures/row['spec'].split('/')[0]/s['input']['path'],inputs/'example.tsv')
        assets['spec']=(inputs/'example.spec.json').relative_to(out).as_posix();hashes['spec']=sha(inputs/'example.spec.json')
        with Image.open(folder/'example.png') as im:im.thumbnail((1450,1350));im.convert('RGB').save(folder/'preview.jpg',quality=94)
        assets['preview']=(folder/'preview.jpg').relative_to(out).as_posix()
        assays=sorted({x.split('.')[0] for x in row.get('chapters',[row.get('assay','bulk')+'.display'])})
        r=dict(id=k,title=s['parameters'].get('title',k),assay='single_cell' if k.startswith(('hdWGCNA','Cluster','Trajectory')) else assays[0],assays=assays,assets=assets,sha256=hashes,readability=row['result']['print_readability'],visual_review=by[k],scientific_acceptance=False,required_results=sorted(s['parameters']),specific_qc_and_limit='Fictional supplied display inputs; actual source, assay, method and independent-unit QC required. No backend executed.',sources=sources);write(folder/'review.json',r);rows.append(r)
    assert set(by)==set(r['id'] for r in rows)
    write(out/'manifest.json',dict(version='0.9.1',records=rows,analysis_performed=False,scientific_acceptance=False));write(out/'review-ledger.json',proof)
    page=PAGE.replace('58个分析章节，每章有实际绘图代码、可运行配置、准确示例表和PNG/SVG/PDF。',str(len(rows))+'个专用配套视图，均有实际代码、可运行输入与PNG/SVG/PDF。').replace('Bulk 与单细胞 · 分析章节图库','WGCNA 与 hdWGCNA · 诊断和证据' if kind=='wgcna' else '分析内部 · 专用配套视图').replace('/*ROWS*/',json.dumps(rows,ensure_ascii=False).replace('<','\\u003c'))
    if kind=='subgroup':page=page.replace('分析内部 · 专用配套视图','逐个亚群 · 多 marker 证据页')
    if kind=='chapter-layouts':page=page.replace('分析内部 · 专用配套视图','大数据量 · 自定义纵向阅读布局')
    page=page.replace('x.assay===assay.value','(x.assay===assay.value||x.assays.includes(assay.value))')
    (out/'index.html').write_text(page,encoding='utf8');shutil.copytree(out,SKILL/('assets/'+kind+'-gallery'),dirs_exist_ok=True);print(json.dumps(dict(state='DEDICATED_REVIEW_PACKAGED',kind=kind,figures=len(rows))))
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for x in ['fixtures','rendered','review','output']:p.add_argument('--'+x,required=True,type=Path)
    p.add_argument('--kind',required=True,choices=['wgcna','method-depth','subgroup','chapter-layouts']);a=p.parse_args();build(a.fixtures,a.rendered,a.review,a.output,a.kind)
