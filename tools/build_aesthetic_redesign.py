"""Actual redesigned prototypes from existing frozen public synthetic fixtures."""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import META_FIELDS,make_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest


def build(output):
    from project_theme import create_theme
    output=Path(output);output.mkdir(parents=True,exist_ok=False);inputs=output/'inputs';inputs.mkdir()
    slots={'Control':1,'Treated':0,'Before':1,'After':0,'Model A':1,'Model B':0,'Model C':3,
           'G1':1,'G2':0,'G3':3,'G4':5,'G5':6,'Coding':1,'Regulatory':0,'Intergenic':3}
    theme=create_theme('synthetic-aesthetic-rebuild','C10',slots,font_family='DejaVu Sans',
                       roles={'positive':'#CC6677','negative':'#332288','neutral':'#A9B1BA'})
    theme['continuous']['diverging']=['#332288','#F8F8F7','#CC6677']
    cases=[('A01','volcano','P08',{'title':'Differential expression','alpha':.05,'effect_cutoff':1}),
           ('A02','forest','E21',{'title':'Estimated effects','x_label':'Effect size','effect_scale':'difference'}),
           ('A03','paired','P03',{'title':'Within-unit change','order':['Control','Treated'],'y_label':'Measurement (demo units)'}),
           ('A04','roc','P25a',{'title':'Classification performance','order':['Model A','Model B','Model C']}),
           ('A05','rank','N09',{'title':'Rank trajectories','order':['Stage 1','Stage 2','Stage 3','Stage 4']}),
           ('A06','matrix','E47',{'title':'Regulator activity','limits':[-1,1],'scale_type':'signed','y_label':'Activity score'})]
    cases=[(id,'editorial',source,{'kind':kind,'options':options},kind) for id,kind,source,options in cases]
    cases += [
        ('B01','mosaic_counts','mosaic',{'category_order':['Coding','Regulatory','Intergenic']},'mosaic'),
        ('B02','waffle_counts','waffle',{'unit_label':'event','columns':10},'waffle'),
        ('B03','horizon_series','horizon',{'band_width':1,'bands':3,'x_label':'Time (demo days)','y_label':'Signed score'},'horizon'),
        ('B04','connected_scatter','connected',{'x_label':'Measurement X (demo units)','y_label':'Measurement Y (demo units)'},'connected'),
        ('B05','mirrored_bars','mirror',{'unit_label':'Supplied count','left_group':'Before','right_group':'After'},'mirror'),
        ('B06','genomic_rainfall','rainfall',{'assembly':'SYNTHETIC COORDINATES; no biological assembly',
          'gap_definition':'Hand-authored positive gaps; prior first event omitted in each chromosome'},'rainfall')]
    records=[]
    for figure_id,renderer,source_id,parameters,kind in cases:
        legacy=figure_id.startswith('A')
        source=ROOT/'examples/gallery/figures'/source_id/(source_id+'.tsv') if legacy else ROOT/'examples/aesthetic-fixtures'/(source_id+'.tsv')
        table=inputs/(source_id+'.tsv');shutil.copyfile(source,table)
        context=json.loads((ROOT/'examples/gallery/metadata'/((source_id if legacy else 'E21')+'.json')).read_text(encoding='utf8'))
        meta={k:context[k] for k in META_FIELDS}
        if not legacy:
            meta.update(source='Original hand-authored frozen synthetic display fixture '+source_id,
                        input_unit='Explicit supplied table cells/coordinates',
                        interpretation_limit='Synthetic display fixture only; no biological inference or upstream analysis',
                        uncertainty='No uncertainty estimated; none encoded in this mode')
        contract={'synthetic':True,'source_definition':meta['source'],
                  'independent_unit':'Synthetic software display units only','denominator':'All rows in the bound fixture',
                  'value_definition':'Existing frozen values; no scientific analysis rerun',
                  'uncertainty_definition':'Supplied illustrative bounds where present; no interval calculated'}
        parameters=dict(parameters,contract=contract)
        spec={'schema_version':1,'figure_id':figure_id,'renderer':renderer,
              'input':{'path':table.name,'sha256':digest(table)},'theme':theme,'provenance':meta,
              'parameters':parameters,'appearance':{'preset':'paper'}}
        (inputs/(figure_id+'.spec.json')).write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
        render_plan(make_plan(spec,inputs),output)
        path=output/figure_id/(figure_id+'.json');receipt=json.loads(path.read_text(encoding='utf8'))
        receipt['source_file']='inputs/'+table.name
        path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        records.append({'id':figure_id,'kind':kind,'renderer':renderer,'source_id':source_id,'source_sha256':digest(source),
                        'png_sha256':digest(output/figure_id/(figure_id+'.png')),'status':'RENDERED_UNREVIEWED'})
    (output/'manifest.json').write_text(json.dumps({'status':'AESTHETIC_CANDIDATE','records':records,'scientific_acceptance':False},indent=2)+'\n',encoding='utf8')
    names={'volcano':'火山图','forest':'森林图','paired':'配对变化','roc':'ROC 阶梯曲线','rank':'排名轨迹','matrix':'调控活性矩阵',
           'mosaic':'面积马赛克','waffle':'精确计数方格','horizon':'地平线 + 线性参照','connected':'时间连线散点','mirror':'双向条形','rainfall':'基因组降雨'}
    cards=[]
    for record in records:
        id=record['id']; name=names[record['kind']]; links=' · '.join('<a href="'+id+'/'+id+'.'+ext+'">'+ext.upper()+'</a>' for ext in ['svg','pdf','tsv','json'])
        cards.append('<article id="'+id+'" data-search="'+id+' '+name+' '+record['kind']+'"><h2>'+id+' · '+name+'</h2><a href="'+id+'/'+id+'.svg"><img loading="lazy" src="'+id+'/'+id+'.png" alt="'+name+'"></a><p>'+links+' · <a href="inputs/'+id+'.spec.json">重绘配置</a></p><p class="scope">'+('重新设计既有图型' if id.startswith('A') else '新增绘图入口')+'；合成示例，不代表科研验收</p><label>逐图意见<textarea data-id="'+id+'" placeholder="标签、比例、配色或需要改的细节"></textarea></label></article>')
    page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>绘图重构审美审查</title>
<style>body{font:15px system-ui,sans-serif;color:#273540;background:#f5f7fa;margin:0}header{max-width:1320px;margin:auto;padding:28px 24px 20px}h1{font-size:28px;font-weight:600;margin:0 0 10px}h2{font-size:17px;font-weight:500}p{line-height:1.6}input{padding:10px;width:min(420px,80%);border:1px solid #bac6d1;border-radius:6px}button{padding:10px;margin:6px;border:1px solid #bac6d1;border-radius:6px;background:white}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;max-width:1320px;margin:auto;padding:0 24px 40px}article{background:white;padding:18px;border-radius:12px;border:1px solid #dfe6ed;min-width:0}article img{width:100%;height:330px;object-fit:contain}a{color:#285d86}textarea{display:block;width:95%;height:60px;margin-top:7px;border:1px solid #ccd5de;padding:8px;border-radius:6px;font:inherit}.scope{color:#637381;font-size:12px}[hidden]{display:none}@media(max-width:740px){main{grid-template-columns:1fr}article img{height:auto}}</style>
<header><h1>绘图重构 · 逐图审美检查</h1><p>6 种重绘 + 6 种补充入口。输入数值完整保留；每张图可打开 SVG/PDF、下载数据与重绘配置。美观自检与科研有效性分开。</p><input id="search" placeholder="按编号、图型或英文名筛选"><button id="export">导出逐图意见</button><p id="storage">意见仅保存在当前浏览器，不联网。离线文件模式下保存能力由浏览器决定，可随时导出。</p></header><main>'''+''.join(cards)+'''</main><script>
const key='figure-aesthetic-rebuild-v030-notes';let notes={};try{notes=JSON.parse(localStorage.getItem(key)||'{}')}catch{};
for(const el of document.querySelectorAll('textarea')){el.value=notes[el.dataset.id]||'';el.addEventListener('input',()=>{notes[el.dataset.id]=el.value;try{localStorage.setItem(key,JSON.stringify(notes))}catch{document.querySelector('#storage').textContent='当前浏览器无法持久保存，请导出意见。'}})}
document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();for(const el of document.querySelectorAll('article'))el.hidden=!el.dataset.search.toLowerCase().includes(q)});
document.querySelector('#export').addEventListener('click',()=>{const link=document.createElement('a');const url=URL.createObjectURL(new Blob([JSON.stringify({scope:'visual opinions only',notes},null,2)],{type:'application/json;charset=utf-8'}));link.href=url;link.download='aesthetic-review-notes.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
</script></html>'''
    (output/'index.html').write_text(page,encoding='utf8')
    print(json.dumps({'status':'TWELVE_FROZEN_CANDIDATES_RENDERED','records':records}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();build(args.output)
