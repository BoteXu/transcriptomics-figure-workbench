# -*- coding: utf-8 -*-
"""Index actual callable views/companions, not hypothetical analysis features."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def build(chapters,wgcna,depth,subgroup=None):
    views=[]
    for r in load(chapters/'manifest.json')['records']:
        s=load(chapters/r['spec']);ps=s['parameters'];members=ps.get('panels',[])
        for p in members or [dict(id='complete',title=ps.get('title',r['id']),kind=ps.get('mode','complete'))]:
            key=r['id']+'.'+p['id'];views.append(dict(id=key,chapters=[r['id']],title=p['title'],form=p['kind'],renderer=s['renderer'],panel_id=p['id'] if members else None,spec='assets/chapter-gallery/'+r['id']+'/input/example.spec.json',input_channels=sorted(p.keys()),meaning=p,example='assets/chapter-gallery/index.html',review_scope='Complete panel actually drawn in its chapter; a newly exported single/layout view needs its own review'))
    for root,asset in [(wgcna,'wgcna'),(depth,'method-depth')]+([(subgroup,'subgroup')] if subgroup else []):
        for r in load(root/'manifest.json')['records']:
            s=load(root/r['spec']);chap=r.get('chapters',['single_cell.hdwgcna'] if r['id'].startswith('hdWGCNA') else ['bulk.wgcna','single_cell.hdwgcna'])
            views.append(dict(id=r['id'],chapters=chap,title=s['parameters'].get('title',r['id']),form=s['parameters'].get('mode','dedicated'),renderer=s['renderer'],panel_id=None,spec='assets/'+asset+'-gallery/'+r['id']+'/input/example.spec.json',input_channels=sorted(s['parameters']),meaning=s['parameters'],example='assets/'+asset+'-gallery/index.html',review_scope='Dedicated actual export; review bound to exact gallery image'))
    assert len({r['id'] for r in views})==len(views)
    (SKILL/'references/analysis-views.json').write_text(json.dumps(dict(schema_version=1,version='0.9.1',views=views,analysis_performed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    lines=['# 分析内部的画法与实际入口','','每项绑定真实绘图器、输入和实例。章节内的单个面板可用 `view-template` 单独导出；改变布局后需要重新审图。此表只记已实现的画法，不表示执行过对应分析。','','|分析|具体画法|入口|形式|','|---|---|---|---|']
    for r in views:lines.append('|'+','.join(r['chapters'])+'|'+r['title']+'|`'+r['id']+'`|'+r['form']+'|')
    lines+=['','## 使用顺序','','先用 `choose` 明确研究问题、数据语义、独立单位和实际数据量，再用 `chapter-views` 查看具体画法。`view-template` 导出一个可运行示例，`book-plan` 的 `view` 可区分同一章节、同一对比下的基础图、诊断图和阅读页。通用面板代码复用不代表方法、检验族或单位可以混用。','','## 来源与实现边界','','本轮对照作者材料检查了 [DESeq2](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html)、[clustree](https://lazappi.github.io/clustree/articles/clustree.html)、[Monocle3](https://cole-trapnell-lab.github.io/monocle3/docs/trajectories/)、[CellChat](https://github.com/sqjin/CellChat/blob/master/tutorial/CellChat-vignette.Rmd)、[ggsashimi](https://github.com/guigolab/ggsashimi) 和 [hdWGCNA](https://smorabit.github.io/hdWGCNA/articles/network_visualizations.html)。采用信息组织和科学语义，绘图为本项目实现；没有复制或运行第三方分析脚本，也未运行上述分析后端。']
    (SKILL/'references/analysis-depth-v091.md').write_text('\n'.join(lines)+'\n',encoding='utf8');print(json.dumps(dict(actual_views=len(views),chapters=58)))
    if (SKILL/'assets/analysis-gallery/manifest.json').is_file():
        from build_analysis_library import build as refresh_current
        refresh_current()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--chapters',required=True,type=Path);p.add_argument('--wgcna',required=True,type=Path);p.add_argument('--depth',required=True,type=Path);p.add_argument('--subgroup',type=Path);a=p.parse_args();build(a.chapters,a.wgcna,a.depth,a.subgroup)
