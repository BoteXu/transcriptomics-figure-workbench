"""Render hand-authored frozen display fixtures for dedicated GSEA/ORA entries."""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan, META_FIELDS
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest
from figure_workbench.methods import prepare_method_spec


def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def table(path,rows):
    columns=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns,delimiter='\t');writer.writeheader();writer.writerows(rows)


def build(output):
    from project_theme import create_theme
    output.mkdir(exist_ok=False);inputs=output/'inputs';inputs.mkdir()
    sets=['Response programme','Repair programme','Metabolic programme']
    theme=create_theme('synthetic-method-displays','C10',{sets[0]:1,sets[1]:0,sets[2]:3},font_family='DejaVu Sans',roles={'positive':'#CC6677','negative':'#4477AA','neutral':'#A9B1BA'})
    theme['continuous']['diverging']=['#4477AA','#F7F7F7','#CC6677']
    contract=dict(synthetic=True,source_definition='Hand-authored frozen software display fixture; no enrichment calculated',independent_unit='No biological independent units; software cells only',denominator='Complete selected display grid; demo ranked universe of twenty identities',value_definition='Supplied illustrative ES/NES/metric/membership cells',uncertainty_definition='No uncertainty estimated; adjusted probabilities are illustrative fixed inputs')
    provenance={k:'Explicit synthetic display fixture; not biological evidence' for k in META_FIELDS}
    provenance.update(synthetic=True,source=contract['source_definition'],contrast='Synthetic B versus A')
    positive=[.10,.20,.32,.44,.53,.61,.66,.70,.65,.60,.55,.50,.45,.40,.32,.26,.20,.13,.07,0]
    negative=[-.03,-.07,-.12,-.18,-.23,-.28,-.34,-.40,-.46,-.51,-.56,-.61,-.66,-.71,-.75,-.62,-.48,-.30,-.13,0]
    metric=[3,2.7,2.4,2.1,1.8,1.5,1.2,.9,.6,.3,-.1,-.4,-.7,-1,-1.3,-1.6,-1.9,-2.2,-2.5,-2.8]
    rows=[]
    for pathway,values,hits,lead,nes,padj in [(sets[0],positive,list(range(1,9)),list(range(1,9)),1.72,.007),(sets[1],negative,[8,12,15,16,17,18,19,20],[15,16,17,18,19,20],-1.61,.016)]:
        rows.extend(dict(kind='curve',pathway=pathway,rank=i+1,value=v) for i,v in enumerate(values))
        rows.extend(dict(kind='hit',pathway=pathway,rank=i,gene='Gene'+str(i),leading_edge=int(i in lead)) for i in hits)
        rows.append(dict(kind='summary',pathway=pathway,NES=nes,padj=padj,set_size=len(hits)))
    rows.extend(dict(kind='metric',rank=i+1,value=v) for i,v in enumerate(metric))
    shared=dict(contract=contract,curve_order=sets[:2],ranked_universe=20,metric_label='Rank metric (demo)',contrast='Synthetic B vs A',gene_set_version='Synthetic sets v1; no licensed gene-set content')
    cases=[]
    for key,index,mode,entry in [('GSEA01',0,'classic','enrichplot.gseaplot2'),('GSEA02',1,'classic','fgsea.plotEnrichment'),('GSEA03',None,'overlay','enrichplot.gseaplot2.overlay'),('GSEA04',None,'facets','enrichplot.gseaplot2.facets')]:
        selected=rows if index is None else [r for r in rows if r.get('pathway') in [None,sets[index]]]
        params=dict(shared,mode=mode,title='GSEA · '+('two-pathway comparison' if index is None else sets[index]))
        if index is not None:params['curve_order']=[sets[index]]
        cases.append((key,entry,selected,params))
    contrasts=['B vs A','C vs A','D vs A'];nes=[[1.72,1.2,-1.1],[-1.61,-.4,.8],[.8,None,1.9]]
    grid=[]
    for i,p in enumerate(sets):
        for j,c in enumerate(contrasts):
            value=nes[i][j];grid.append(dict(pathway=p,contrast=c,status='not_tested' if value is None else 'reported',NES=value,padj=None if value is None else [.007,.12,.032][j],set_size=None if value is None else [40,65,24][i]))
    cases.append(('GSEA05','fgsea.NES_matrix',grid,dict(contract=contract,pathway_order=sets,contrast_order=contrasts,nes_limits=[-2,2],size_max=80,title='GSEA · direction, support and missing tests')))
    genes=['Gene'+str(i) for i in range(1,9)];values=[1.4,.9,-.5,.8,-1.2,.6,-.8,1.1]
    member=[[1,1,1,1,0,0,0,0],[0,1,0,1,1,1,0,0],[0,0,1,0,1,0,1,1]]
    grid=[dict(pathway=p,gene=g,member=member[i][j],leading_edge=int(member[i][j] and j in [0,1,4,6]),value=values[j]) for i,p in enumerate(sets) for j,g in enumerate(genes)]
    cases.append(('GSEA06','fgsea.leading_edge',grid,dict(contract=contract,pathway_order=sets,gene_order=genes,value_limits=[-1.5,1.5],value_label='Gene effect (demo)',title='GSEA · leading-edge membership')))
    terms=['Extracellular organization','Stress response','RNA processing','Energy metabolism','Cell-cycle regulation','Membrane transport']
    ora=[dict(term=t,count=n,query_size=100,padj=p) for t,n,p in zip(terms,[30,24,21,18,15,12],[.0003,.001,.004,.012,.035,.08])]
    for key,entry in [('ORA01','clusterProfiler.dotplot'),('ORA02','clusterProfiler.lollipop')]:cases.append((key,entry,ora,dict(contract=contract,term_order=terms,background_definition='Synthetic background n=1000; no ORA calculated',ratio_max=.4,significance_max=4,title='ORA · selected term evidence')))
    records=[]
    for key,entry,rows,params in cases:
        file=inputs/(key+'.tsv');table(file,rows)
        template=dict(schema_version=1,figure_id=key,renderer='gsea_tracks',input=dict(path=file.name,sha256=digest(file)),parameters=params,theme=theme,provenance=provenance,appearance=dict(preset='paper'))
        spec=prepare_method_spec(entry,template,inputs,inputs/(key+'.spec.json'));write(inputs/(key+'.spec.json'),spec)
        render_plan(make_plan(spec,inputs),output)
        receipt=output/key/(key+'.json');meta=json.loads(receipt.read_text());meta['source_file']='inputs/'+file.name;write(receipt,meta)
        records.append(dict(id=key,entry=entry,png_sha256=digest(output/key/(key+'.png')),status='RENDERED_UNREVIEWED'))
    write(output/'manifest.json',dict(records=records,scientific_acceptance=False))
    cards=[]
    for r in records:
        k=r['id'];cards.append('<article id="'+k+'"><h2>'+k+' · '+r['entry']+'</h2><a href="'+k+'/'+k+'.svg"><img loading="lazy" src="'+k+'/'+k+'.png" alt="'+k+'"></a><p>'+ ' · '.join('<a href="'+k+'/'+k+'.'+e+'">'+e.upper()+'</a>' for e in ['svg','pdf','tsv','json'])+' · <a href="inputs/'+k+'.spec.json">FigureSpec</a></p></article>')
    page='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>GSEA / ORA 专项图</title><style>body{font:16px/1.6 Arial;color:#273540;background:#f3f5f7;max-width:1400px;margin:auto;padding:24px}article{background:white;margin:24px 0;padding:24px;border-radius:12px}img{display:block;max-width:100%;max-height:850px;margin:auto}a{color:#315a89}</style><h1>GSEA / ORA 专用绘图</h1><p>8个冻结合成示例。源表、配置、统计说明均保留；不执行上游富集。美观自检记录与科学验收分开。</p><p><a href="self-review.json">逐图检查记录（发布版）</a></p>'+''.join(cards)
    (output/'index.html').write_text(page,encoding='utf8')
    print(json.dumps(dict(status='EIGHT_DEDICATED_DISPLAYS_RENDERED',records=records)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
