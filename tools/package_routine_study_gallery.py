"""Portable, one-figure-at-a-time reader for an explicitly rendered study set."""
import argparse,hashlib,json,shutil
from pathlib import Path

TITLES={
 'BulkMain':'Bulk 研究总览','BulkQC':'Bulk 表达质控云雨图','BulkPCA':'PCA：样本、椭圆、边缘比例与解释方差',
 'BulkCorrelation':'Bulk 样本相关性','LibrarySizes':'Bulk 文库覆盖','StudyDesign':'条件、批次与设计矩阵',
 'BulkDE':'Bulk 火山图与完整堆积分布','BulkHeatmap':'Bulk 预先指定的表达程序','GeneEffects':'基因效应与区间','BulkMA':'Bulk MA 与完整边缘分布',
 'GeneExpression':'四个指定基因的逐供体云雨图','Pathways':'Bulk ORA 富集与基因支持','EnrichmentTracks':'Bulk GSEA：三条完整排序轨道',
 'bulk_GSEASummary':'Bulk GSEA 通路效应与基因支持','bulk_GeneSupport':'Bulk ORA 成员与基因效应',
 'CellQC':'单细胞三项质控云雨图','DonorCounts':'单细胞供体覆盖','CellBatches':'批次分面：保持完整坐标',
 'CellStudyDesign':'单细胞条件与批次设计','CellTypes':'单细胞身份图谱与 20 个 marker 证据','MarkerDot':'20 个 marker 的跨群均值与检出率','MarkerFeatures':'五个代表 marker：共同表达色阶',
 'ConditionAtlas':'按条件分开的细胞图谱：统一坐标范围','DonorComposition':'逐供体细胞比例','DonorTypeSupport':'各亚群的逐供体细胞数',
 'DonorDE':'Myeloid 供体级差异与堆积火山图','DonorEffects':'Myeloid 指定基因效应区间','DonorHeatmap':'Myeloid 指定表达程序','DonorMA':'Myeloid 供体级 MA 与边缘分布',
 'DonorPathways':'Myeloid ORA 富集与基因支持','DonorEnrichmentTracks':'Myeloid GSEA：三条完整轨道','single_cell_GSEASummary':'Myeloid GSEA 通路效应','single_cell_GeneSupport':'Myeloid ORA 成员与基因效应',
 'Subgroup_01':'T cells：定位、跨群特异性与四个 marker','Subgroup_02':'B cells：定位、跨群特异性与四个 marker','Subgroup_03':'Myeloid：定位、跨群特异性与四个 marker','Subgroup_04':'Stromal：定位、跨群特异性与四个 marker','Subgroup_05':'Endothelial：定位、跨群特异性与四个 marker',
 'bulk_GSEADetail_Reading':'Bulk GSEA：单通路阅读版','single_cell_GSEADetail_Reading':'Myeloid GSEA：单通路阅读版','Subgroup_01_Custom':'T cells：按要求改为两列 marker','Subgroup_03_Custom':'Myeloid：按要求改为三列整页布局','EnrichmentTracks_Custom':'GSEA：按要求横排三通路'}

PAGE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bulk 与单细胞 · 完整模拟结果绘图验收</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f4f5;color:#243e4b;font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}header{padding:22px 28px;background:#193f4b;color:white}header h1{font-size:24px;margin:0 0 6px}header p{margin:0;color:#c8dce1}.layout{display:grid;grid-template-columns:300px minmax(0,1fr);gap:20px;padding:20px}aside{height:calc(100vh - 170px);position:sticky;top:16px;overflow:auto;background:white;border-radius:12px;padding:12px}aside h3{margin:14px 8px 6px;font-size:14px;color:#69838c}button,a{touch-action:manipulation}button{font:inherit;cursor:pointer;border:1px solid #d4e1e5;border-radius:8px;background:white;color:#264650;padding:7px 13px}aside button{display:block;width:100%;text-align:left;margin:4px 0;font-size:13px}button.active{background:#e4f1ef;border-color:#65a39d;color:#166b6a}.top{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.top span{margin-right:auto;color:#56727c}article{background:white;border-radius:12px;padding:24px;min-width:0}h2{font-size:21px;margin:14px 0 4px}.sub{color:#6c828b;font-size:13px}#art{display:block;width:100%;height:auto;margin:18px 0;background:white}#viewport{overflow:auto}#art.native{width:auto;max-width:none}a{color:#157477;text-decoration:none;border-bottom:1px solid #a7cfca;margin-right:14px}.note{border-left:3px solid #75aaa3;background:#f0f7f6;padding:12px 15px;margin:12px 0}.links{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}details{margin:12px 0;color:#516f7a}footer{margin-top:20px;color:#72858b;font-size:12px}@media(max-width:900px){.layout{display:block;padding:10px}aside{height:190px;position:static;margin-bottom:10px}article{padding:15px}header{padding:18px}h2{font-size:18px}}@media print{aside,.top,.links{display:none}.layout{display:block}header{color:#193f4b;background:white}article{padding:0}#art{max-height:90vh;object-fit:contain}}</style>
<header><h1>Bulk 与单细胞：普通指令完整出图</h1><p>12 个模拟供体 · 900 个嵌套细胞 · 1,200 个虚构基因结果 · 五个身份 × 四个 marker。全部为模拟展示材料。</p></header>
<div class="layout"><aside id="menu"></aside><main><article><div class="top"><button id="prev">← 上一张</button><span id="counter"></span><button id="zoom">原像素 / 适应宽度</button><button id="next">下一张 →</button></div><h2 id="title"></h2><div id="subtitle" class="sub"></div><div id="viewport"><img id="art" alt=""></div><div id="notes" class="note"></div><div id="links" class="links"></div><details><summary>输入范围与默认参数</summary><pre id="parameters" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></details><footer>单细胞差异与通路部分指明 Myeloid 供体级对比；其余身份没有在这套模拟结果中做差异推断。PCA 的 95% 椭圆为给定的模拟离散范围，不是均值置信区间。图形自检不能证明分析方法或生物学结论成立。</footer></article></main></div>
<script>const rows=/*DATA*/;let index=0;const $=s=>document.querySelector(s);const menu=$('#menu');for(const section of ['bulk','single_cell','reading']){let h=document.createElement('h3');h.textContent={bulk:'Bulk：常规整套图',single_cell:'单细胞：常规整套图',reading:'单通路阅读与自定义布局'}[section];menu.append(h);rows.forEach((r,i)=>{if((r.stage==='reading'?'reading':r.assay)!==section)return;let b=document.createElement('button');b.textContent=String(i+1).padStart(2,'0')+' '+r.title;b.dataset.index=i;b.onclick=()=>show(i);menu.append(b)})}
function show(i){index=(i+rows.length)%rows.length;const r=rows[index];$('#title').textContent=r.title;$('#counter').textContent=(index+1)+' / '+rows.length;$('#subtitle').textContent=r.variant+' · '+r.width+' mm 阅读宽度 · '+r.review_state;const art=$('#art');art.src=r.assets.png;art.alt=r.title;art.classList.remove('native');$('#viewport').scrollLeft=0;$('#notes').textContent=r.note;$('#links').replaceChildren();for(const[k,v]of Object.entries(r.assets)){let a=document.createElement('a');a.href=v;a.textContent={svg:'打开矢量 SVG',pdf:'单张 PDF',png:'原始 PNG',tsv:'冻结绘图数据',spec:'绘图配置'}[k];a.target='_blank';$('#links').append(a)}$('#parameters').textContent=JSON.stringify(r.parameters,null,2);menu.querySelectorAll('button').forEach(b=>b.classList.toggle('active',Number(b.dataset.index)===index));location.hash=String(index+1)}$('#prev').onclick=()=>show(index-1);$('#next').onclick=()=>show(index+1);$('#zoom').onclick=()=>$('#art').classList.toggle('native');document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(index+1);if(e.key==='ArrowLeft')show(index-1)});show(Number(location.hash.slice(1)||1)-1);</script></html>'''


def package(source,out,review=None,fixtures=None,baseline=None):
    from pypdf import PdfWriter
    doc=json.loads((source/'manifest.json').read_text(encoding='utf8'));proof=json.loads(review.read_text(encoding='utf8')) if review else {'records':[]}
    by={r['id']:r for r in proof['records']};out.mkdir(parents=True,exist_ok=False);rows=[];writer=PdfWriter();page=0
    previous={r['id']:r for r in json.loads((baseline/'manifest.json').read_text(encoding='utf8'))['records']} if baseline else {}
    for row in doc['records']:
        k=row['id'];folder=out/'figures'/k;folder.mkdir(parents=True);assets={}
        files={Path(x).suffix:Path(x) for x in row['result']['files']}
        for ext in ['png','svg','pdf']:
            dest=folder/(k+'.'+ext);shutil.copyfile(files['.'+ext],dest);assets[ext]=dest.relative_to(out).as_posix()
        spec_path=Path(row['spec_path']);s=json.loads(spec_path.read_text(encoding='utf8'));table=spec_path.parent/s['input']['path']
        shutil.copyfile(table,folder/'input.tsv');s['input']['path']='input.tsv';(folder/'figure.spec.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        assets.update(tsv=(folder/'input.tsv').relative_to(out).as_posix(),spec=(folder/'figure.spec.json').relative_to(out).as_posix())
        sha=hashlib.sha256(files['.png'].read_bytes()).hexdigest();r=by.get(k)
        if r and r['png_sha256']!=sha:raise ValueError('Review invalidated by changed figure: '+k)
        title=TITLES.get(k,k);writer.append(str(files['.pdf']),import_outline=False);writer.add_outline_item(title,page);page+=1
        rows.append(dict(id=k,title=title,assay=row['assay'],stage=row['stage'],variant=row['variant'],assets=assets,width=s['export']['target_width_mm'],parameters=s['parameters'],png_sha256=sha,review_state=r['decision'] if r else '已生成，尚待逐张审阅',note=r['notes'] if r else '等待实际查看最终图像后记录，不以文件生成或自动检查代替美观性自检。'))
        if baseline:
            old=previous[k];old_table=baseline/old['assets']['tsv']
            if old_table.read_bytes()!=table.read_bytes():raise ValueError('Before/after comparison must preserve exact frozen input bytes: '+k)
            dest=out/'before'/(k+'.png');dest.parent.mkdir(exist_ok=True);shutil.copyfile(baseline/old['assets']['png'],dest)
            rows[-1].update(before_png=dest.relative_to(out).as_posix(),before_png_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),before_input_sha256=hashlib.sha256(old_table.read_bytes()).hexdigest(),input_sha256=hashlib.sha256(table.read_bytes()).hexdigest(),frozen_tsv_unchanged=True)
    writer.write(out/'Bulk_and_SingleCell_FigureBook.pdf');writer.close()
    page_html=PAGE.replace('/*DATA*/',json.dumps(rows,ensure_ascii=False).replace('<','\\u003c'))
    if baseline:
        page_html=page_html.replace('<button id="zoom">','<button id="compare">查看前版</button><button id="zoom">')
        page_html=page_html.replace('function show(i){','let before=false;function show(i){before=false;$(\'#compare\').textContent="查看前版";')
        page_html=page_html.replace("$('#prev').onclick", "$('#compare').onclick=()=>{before=!before;$('#art').src=before?rows[index].before_png:rows[index].assets.png;$('#compare').textContent=before?'返回本版':'查看前版';};$('#prev').onclick")
    (out/'index.html').write_text(page_html,encoding='utf8')
    (out/'manifest.json').write_text(json.dumps(dict(records=rows,ordinary_requests=doc['requests'],scientific_acceptance=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if fixtures:
        by_id={r['id']:r for r in rows}
        for assay in ['bulk','single_cell']:
            m=json.loads((fixtures/(assay+'.manifest.json')).read_text(encoding='utf8'))
            for result in m['results']:
                old=fixtures/result['spec'];key=json.loads(old.read_text(encoding='utf8'))['figure_id']
                if key not in by_id:raise ValueError('Manifest refers to an unrendered figure: '+key)
                result['spec']=by_id[key]['assets']['spec']
            (out/(assay+'.manifest.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        shutil.copyfile(fixtures/'coherence.json',out/'coherence.json')
    if review:shutil.copyfile(review,out/'visual-review.json')
    print(json.dumps(dict(state='PORTABLE_READER_READY',figures=len(rows),reviewed=len(by),pdf_pages=page)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--review',type=Path);p.add_argument('--fixtures',type=Path);p.add_argument('--baseline',type=Path);a=p.parse_args();package(a.source,a.output,a.review,a.fixtures,a.baseline)
