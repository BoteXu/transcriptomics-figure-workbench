"""Package only reviewed public fixtures and exports; omit private runtime paths."""
import argparse,hashlib,html,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

PAGE='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'none'; form-action 'none'; base-uri 'none'"><title>转录组分析章节 · 真实绘图实例</title><style>
body{font:16px system-ui;background:#f1f5f5;color:#244352;margin:0}header{padding:32px max(4vw,24px);background:#fff;border-bottom:1px solid #d7e3e6}h1{font-size:30px;margin:0 0 12px}p{line-height:1.65}button,input,select,a{font:inherit}input,select,button{padding:10px;border:1px solid #afc8ce;border-radius:8px;background:white;color:#244352}nav{display:flex;gap:12px;flex-wrap:wrap}main{padding:24px;max-width:1500px;margin:auto}article{padding:24px;background:#fff;border-radius:12px;margin:0 0 24px}img{display:block;max-width:100%;height:auto;margin:16px auto;cursor:zoom-in}h2{margin:0 0 8px;font-size:22px}.tag{font-size:13px;color:#54717c}a{color:#186f80;margin-right:16px}details{margin-top:12px}button:disabled{opacity:.4}#count{padding:12px 0}dialog{width:94vw;height:92vh;padding:0;border:1px solid #abc;background:#eef4f4}dialog>div{position:sticky;top:0;padding:12px;background:#fff}dialog img{max-width:none;margin:0}dialog::backdrop{background:#123a4bcc}</style>
<header><h1>Bulk 与单细胞 · 分析章节图库</h1><p>58个分析章节，每章有实际绘图代码、可运行配置、准确示例表和PNG/SVG/PDF。按问题选择互补面板，支持多个对比、多个亚群。示例为虚构冻结结果，不代表分析后端或生物学结论通过验收。</p><nav><input id="q" placeholder="搜索分析、方法、输入要求" aria-label="搜索"><select id="assay" aria-label="数据类型"><option value="">全部数据类型</option><option value="bulk">Bulk</option><option value="single_cell">单细胞</option></select><button id="prev">上一页</button><button id="next">下一页</button></nav><div id="count"></div></header><main id="cards"></main><dialog id="zoom"><div><button id="close">关闭原像素查看</button></div><img id="large" alt="原像素图"></dialog><script>
const rows=/*ROWS*/;let page=0;const q=document.querySelector('#q'),assay=document.querySelector('#assay');
function el(t,text){const e=document.createElement(t);if(text)e.textContent=text;return e}
function update(){const filtered=rows.filter(x=>(!assay.value||x.assay===assay.value)&&JSON.stringify(x).toLowerCase().includes(q.value.toLowerCase()));page=Math.min(page,Math.max(0,Math.ceil(filtered.length/4)-1));const main=document.querySelector('#cards');main.replaceChildren();for(const r of filtered.slice(page*4,page*4+4)){const card=el('article');card.dataset.id=r.id;card.append(el('h2',r.title),el('div',r.id+' · '+r.assay+' · 屏幕自检 / 非科学验收'));const image=el('img');image.src=r.assets.preview;image.alt=r.title;image.loading='lazy';image.onclick=()=>{document.querySelector('#large').src=r.assets.png;document.querySelector('#zoom').showModal()};card.append(image);for(const key of ['png','svg','pdf','tsv','spec']){const a=el('a',key.toUpperCase());a.href=r.assets[key];a.target='_blank';a.rel='noopener';card.append(a)}const d=el('details');d.append(el('summary','输入、来源与使用范围'));d.append(el('p','需要的冻结结果：'+r.required_results.join('；')),el('p',r.specific_qc_and_limit));for(const url of r.sources){const a=el('a','作者来源');a.href=url;a.target='_blank';a.rel='noopener';d.append(a)}card.append(d);main.append(card)}document.querySelector('#count').textContent=filtered.length+'个章节 · 第'+(page+1)+'页 / '+Math.max(1,Math.ceil(filtered.length/4));document.querySelector('#prev').disabled=page===0;document.querySelector('#next').disabled=(page+1)*4>=filtered.length}
q.oninput=assay.onchange=()=>{page=0;update()};document.querySelector('#prev').onclick=()=>{page--;update()};document.querySelector('#next').onclick=()=>{page++;update()};document.querySelector('#close').onclick=()=>document.querySelector('#zoom').close();update();</script></html>'''

def build(fixtures,rendered,review,output):
    from PIL import Image
    proof=load(review);assert proof['state']=='SCREEN_REVIEWED';reviewed={r['id']:r for r in proof['records']};catalog=load(SKILL/'references/transcriptomic-chapters.json');lookup={x['id']:x for x in catalog['chapters']};records=[]
    output.mkdir(parents=True,exist_ok=False)
    for row in load(rendered/'manifest.json')['records']:
        k=row['id'];source=fixtures/k;spec=load(source/'example.spec.json');stem=next(Path(p) for p in row['result']['files'] if p.endswith('.png')).with_suffix('');assert sha(stem.with_suffix('.png'))==reviewed[k]['png_sha256']
        folder=output/k;folder.mkdir();inputs=folder/'input';inputs.mkdir();shutil.copyfile(source/'example.spec.json',inputs/'example.spec.json');shutil.copyfile(source/'example.tsv',inputs/'example.tsv');assets={};digests={}
        for ext in ['png','svg','pdf','tsv']:
            p=folder/('example.'+ext);shutil.copyfile(stem.with_suffix('.'+ext),p);assets[ext]=p.relative_to(output).as_posix();digests[ext]=sha(p)
        assets['spec']=(inputs/'example.spec.json').relative_to(output).as_posix();digests['spec']=sha(inputs/'example.spec.json')
        with Image.open(folder/'example.png') as im:im.thumbnail((1450,1350));im.convert('RGB').save(folder/'preview.jpg',quality=94)
        assets['preview']=(folder/'preview.jpg').relative_to(output).as_posix()
        record=dict(lookup[k],assets=assets,sha256=digests,visual_review=reviewed[k],readability=row['result']['print_readability'],scientific_acceptance=False)
        write(folder/'review.json',record);records.append(record)
    assert set(x['id'] for x in records)==set(lookup)
    write(output/'manifest.json',dict(version='0.9.1',records=records,chapters=58,analysis_performed=False,scientific_acceptance=False));write(output/'review-ledger.json',proof)
    (output/'index.html').write_text(PAGE.replace('/*ROWS*/',json.dumps(records,ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    destination=SKILL/'assets/chapter-gallery';shutil.copytree(output,destination,dirs_exist_ok=True)
    print(json.dumps(dict(status='CHAPTER_REVIEW_PACKAGED',chapters=len(records),private_runtime_metadata_included=False)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',required=True,type=Path);p.add_argument('--rendered',required=True,type=Path);p.add_argument('--review',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();build(a.fixtures,a.rendered,a.review,a.output)
