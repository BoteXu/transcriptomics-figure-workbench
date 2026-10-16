"""Package an explicitly hash-reviewed set; never infer visual approval from a render."""
import argparse,copy,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def selected(work):
    result=[]
    def add(root,section,level=None):
        for row in load(root/'manifest.json')['records']:
            stem=(root/row['file']).with_suffix('') if row.get('file') else root/row['id']/row['id']
            result.append(dict(key=section+'/'+(level+'/' if level else '')+row['id'],section=section,level=level,row=row,stem=stem,root=root))
    add(work/'all-source-final-v4','source')
    for level in ['small','medium','large']:
        start=len(result);add(work/'candidate-volumes-v3'/level,'volume',level)
        for replacement in ['last-volume-repairs-v1','gating-volume-final-v1']:
            for row in load(work/replacement/level/'manifest.json')['records']:
                hit=next(r for r in result[start:] if r['row']['id']==row['id'])
                hit.update(row=row,root=work/replacement/level,stem=work/replacement/level/row['id']/row['id'])
    add(work/'composition-final-v3','composition')
    add(work/'fixed-reference-final-v2','reference')
    add(work/'study-final-v10','study')
    add(work/'study-layout-final-v4','study-layout')
    add(work/'special-final-v3','special')
    return result

def build(work,review,out):
    chosen=selected(work);approval=load(review)
    bound={r['key']:r for r in approval['records']}
    assert len(chosen)==len(bound)==803 and {r['key'] for r in chosen}==set(bound),'Incomplete explicit review scope'
    assert approval['status']=='SCREEN_REVIEW_COMPLETE'
    for r in chosen:assert sha(r['stem'].with_suffix('.png'))==bound[r['key']]['png_sha256'],'Changed image needs review: '+r['key']
    out.mkdir(parents=True,exist_ok=False);records=[]
    for item in chosen:
        key=item['key'];row=item['row'];stem=item['stem'];folder=out/key;folder.mkdir(parents=True)
        assets={};digests={}
        for ext in ['png','svg','pdf','tsv']:
            p=stem.with_suffix('.'+ext)
            if p.is_file():
                dest=folder/(row['id']+'.'+ext);shutil.copyfile(p,dest);assets[ext]=dest.relative_to(out).as_posix();digests[ext]=sha(dest)
        # Private runtime receipts/plans are deliberately not exported. These
        # selected fields bind public files and the actual limited review.
        meta={k:copy.deepcopy(row[k]) for k in ['form','adapter','rows','source_input_sha256','input_sha256','quantitative_geometry_sha256','volume','requested_layout','size_inches','readability','context','assay','role','layout','relationship','aliases','components','page_components','source_example','limitation'] if k in row}
        meta.update(id=row['id'],section=item['section'],level=item['level'],assets=assets,sha256=digests,visual_review=bound[key],scientific_acceptance=False)
        if item['section'] in ['source','volume']:
            req=load(stem.parent/'request.json');write(folder/'request.json',req)
            meta['form']=req.get('base_form',meta.get('form',row['id']))
            meta['title']=req.get('title',row['id'])
        if item['section']=='composition':
            req=load(stem.parent/'request.json')
            for panel,c in zip(req['panels'],row['components']):
                for field,ext in [('svg','svg'),('table','tsv')]:panel[field]='../../../source/'+c+'/'+c+'.'+ext
            write(folder/'request.json',req)
        if item['section'] in ['study','study-layout']:
            src=item['root']/('inputs/'+row['id'] if item['section']=='study-layout' else row['id'])
            inputs=folder/'input';inputs.mkdir()
            for p in src.iterdir():
                if p.suffix=='.tsv' or p.name.endswith('.spec.json'):shutil.copyfile(p,inputs/p.name)
            assets['spec']=(inputs/(row['id']+'.spec.json')).relative_to(out).as_posix()
        write(folder/'review.json',meta)
        with Image.open(stem.with_suffix('.png')) as im:
            im.thumbnail((1000,850));im.convert('RGB').save(folder/'preview.jpg',quality=90)
        records.append(dict(key=key,id=row['id'],title=meta.get('title',row['id']),section=item['section'],level=item['level'],form=meta.get('form',row['id']),assay=row.get('assay'),assets=assets,sha256=digests,preview=key+'/preview.jpg',review=key+'/review.json',visual_review=bound[key]))
    study=work/'study-final-v10'
    for assay in ['bulk','single_cell']:
        m=load(study/(assay+'.manifest.json'))
        for role in m['results']:
            name=role['spec'].split('/')[0];role['spec']='../study/'+name+'/input/'+name+'.spec.json'
        write(out/'study-manifests'/(assay+'.json'),m)
    ordinary=load(study/'manifest.json')['ordinary_requests']
    write(out/'ordinary-requests.json',ordinary)
    write(out/'manifest.json',dict(version='0.9.0',records=records,counts={s:sum(r['section']==s for r in records) for s in sorted({r['section'] for r in records})},scientific_acceptance=False,review_scope=approval['scope']))
    write(out/'review-ledger.json',approval)
    (out/'index.html').write_text(PAGE.replace('/*MANIFEST*/',json.dumps(records,ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    # The installed skill has two complete, runnable study examples and compact
    # current base-form previews; the complete atlas is a separate download.
    installed=SKILL/'assets/study-gallery';installed.mkdir(parents=True,exist_ok=True)
    for key in ['BulkMain','SingleCellMain']:
        shutil.copyfile(out/'study'/key/'preview.jpg',installed/(key+'.jpg'))
    for section in ['study','study-layout','study-manifests']:
        shutil.copytree(out/section,installed/section,dirs_exist_ok=True)
    write(installed/'manifest.json',dict(records=[r for r in records if r['section'] in ['study','study-layout']],scientific_acceptance=False))
    write(installed/'ordinary-requests.json',ordinary)
    (installed/'index.html').write_text(PAGE.replace('/*MANIFEST*/',json.dumps([r for r in records if r['section'] in ['study','study-layout']],ensure_ascii=False).replace('<','\\u003c')),encoding='utf8')
    catalog=load(SKILL/'references/form-catalog.json')
    by_id={r['id']:r for r in records if r['section']=='source'}
    ref={r['id'].split('_')[0]:r for r in records if r['section']=='reference' and '_wide-' in r['id']}
    comp={alias:next(r for r in records if r['section']=='composition' and r['id']==q['id']) for q in load(work/'composition-final-v3/manifest.json')['records'] if q['layout']=='reading' and q['id'].endswith('-page-01') for alias in q['aliases']}
    for form in catalog['forms']:
        for entry in form['extensions']:
            current=by_id.get(entry['id']) or ref.get(entry['id']) or comp.get(entry['id'])
            if current:entry['current_example']='examples/validated-v090/'+current['assets']['png'];entry['current_bundle']='examples/validated-v090/'+current['key']+'/'
        current=by_id.get(form['default']) or ref.get(form['default'])
        if current:shutil.copyfile(out/current['preview'],SKILL/'assets/forms-gallery'/(form['default']+'.jpg'))
    catalog['current_review_version']='0.9.0';catalog['current_gallery']='examples/validated-v090/index.html';write(SKILL/'references/form-catalog.json',catalog)
    # Reject private absolute paths even in nested metadata before publication.
    private=re.compile(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/(?:Users|home)/[^/]+/')
    for p in out.rglob('*'):
        if p.suffix in ['.json','.svg','.html','.tsv']:assert not private.search(p.read_text(encoding='utf8')),p.name
    print(json.dumps(dict(status='EXPLICIT_REVIEWED_PUBLIC_SET_PACKAGED',pages=len(records),bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()))))

PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figure Workbench · v0.9 review library</title><style>
body{margin:0;background:#f4f7f8;color:#20343f;font:16px system-ui,sans-serif}header,main{max-width:1440px;margin:auto;padding:24px}h1{font-size:30px;margin:0 0 12px}p{max-width:100ch;line-height:1.6}nav{display:flex;gap:10px;flex-wrap:wrap}button,input,select{font:inherit;padding:10px;border:1px solid #bdcbd1;border-radius:6px;background:white;color:inherit}button{cursor:pointer}#cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}article{background:white;padding:18px;border:1px solid #dce4e8;border-radius:8px}article img{width:100%;height:350px;object-fit:contain;cursor:zoom-in}a{color:#256978;margin-right:14px}small{display:block;line-height:1.6;color:#526875}.bar{display:flex;justify-content:space-between;margin:22px 0}dialog{width:92vw;max-width:1600px;max-height:92vh;border:1px solid #607e8d;border-radius:8px}dialog img{width:100%;height:auto}dialog button{position:sticky;top:0;float:right}output{display:block;margin:18px 0}</style>
<header><h1>科研绘图 · 完整图组与布局复查</h1><p>从普通任务到互补主图与完整配套图。先看 bulk 或单细胞整套，再按图型和数据量选择扩展。全部示例为冻结绘图测试；屏幕自检与字号测量不代表科学有效性或校准印刷打样。</p><nav><button data-pick="study">整套示例</button><button data-pick="study-layout">自定义主图</button><button data-pick="source">旧图重绘</button><button data-pick="volume">不同数据量</button><button data-pick="composition">组图与分页</button><button data-pick="reference">固定参考</button><button data-pick="special">公开测量 / 多曲线</button></nav></header>
<main><nav><input id="search" aria-label="检索" placeholder="图编号、图型或关键词"><select id="assay" aria-label="分析类型"><option value="">全部分析类型</option><option>bulk</option><option>single_cell</option></select><select id="volume" aria-label="数据量"><option value="">全部数据量</option><option>small</option><option>medium</option><option>large</option></select><button id="clear">清除筛选</button></nav><output id="status"></output><div id="cards"></div><div class="bar"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></div><p><a href="manifest.json">准确文件与审阅范围</a><a href="ordinary-requests.json">六条常规指令的实际选图</a></p></main><dialog id="zoom"><button id="close">关闭</button><img alt="完整图放大"></dialog>
<script>let rows=/*MANIFEST*/,section='study',page=0;const $=s=>document.querySelector(s);function draw(){let q=$('#search').value.toLowerCase(),assay=$('#assay').value,volume=$('#volume').value;let list=rows.filter(r=>(!section||r.section===section)&&(!assay||r.assay===assay)&&(!volume||r.level===volume)&&JSON.stringify([r.id,r.form,r.section,r.assay,r.level]).toLowerCase().includes(q));page=Math.max(0,Math.min(page,Math.max(0,Math.ceil(list.length/12)-1)));$('#status').textContent=list.length+' 份完整图像；每页最多 12 份，按需加载。';$('#page').textContent=(page+1)+' / '+Math.max(1,Math.ceil(list.length/12));$('#cards').replaceChildren();for(let r of list.slice(page*12,page*12+12)){let a=document.createElement('article'),h=document.createElement('h2'),im=document.createElement('img'),note=document.createElement('small'),links=document.createElement('p');a.id=r.id;h.textContent=r.id;im.src=r.preview;im.loading='lazy';im.alt=r.form+' · '+r.id;im.onclick=()=>{$('#zoom img').src=r.assets.png;$('#zoom').showModal()};note.textContent=r.form+' · '+(r.assay||r.level||r.section)+' · '+r.visual_review.status;for(let [kind,path] of Object.entries({...r.assets,review:r.review})){let link=document.createElement('a');link.href=path;link.textContent=kind.toUpperCase();links.append(link)}a.append(h,im,note,links);$('#cards').append(a)}}document.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{section=b.dataset.pick;page=0;draw()});['search','assay','volume'].forEach(id=>$('#'+id).oninput=()=>{page=0;draw()});$('#clear').onclick=()=>{section='';['search','assay','volume'].forEach(id=>$('#'+id).value='');page=0;draw()};$('#prev').onclick=()=>{page--;draw()};$('#next').onclick=()=>{page++;draw()};$('#close').onclick=()=>$('#zoom').close();draw();</script></html>'''

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.workspace,a.review,a.output)
