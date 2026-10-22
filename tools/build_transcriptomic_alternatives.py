"""Prepare exact published frozen inputs; optional rendering runs in CI only."""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
ASSETS=SKILL/'assets'
sys.path.insert(0,str(SKILL/'scripts'))


def cases():
    result=[]
    def add(name,source,parameters,renderer=None):result.append((name,source,parameters,renderer))
    routine=lambda name:ASSETS/'routine-gallery/figures'/name/'figure.spec.json'
    for view in ['evidence','facets']:
        add('PCA_'+view,routine('BulkPCA'),{'presentation':view,'title':'Sample structure and supporting evidence'})
    add('PCA_one_column',routine('BulkPCA'),{'presentation':'facets','ncols':1,'panel_width':5.0,'panel_height':3.8,'title':'Sample identity at matched limits'})
    for view in ['evidence','landscape']:
        add('Volcano_'+view,routine('BulkDE'),{'presentation':view,'title':'Differential expression with complete context'})
    for view in ['cards','aligned']:
        add('GSEA_'+view,routine('EnrichmentTracks'),{'mode':view,'ncols':2 if view=='cards' else 'auto','panel_height':4.7},'figure_gsea.plot_gsea_tracks')
    add('GSEA_single',routine('EnrichmentTracks'),{'mode':'cards','ncols':1,'panel_height':4.7,'curve_order':['Interferon response']},'figure_gsea.plot_gsea_tracks')
    add('GSEA_one_column',routine('EnrichmentTracks'),{'mode':'cards','ncols':1,'panel_height':4.7},'figure_gsea.plot_gsea_tracks')
    for view in ['raincloud_horizontal','raincloud_vertical']:
        add('Expression_'+view,routine('GeneExpression'),{'presentation':view,'title':'Donor expression distributions'})
    add('Expression_single',routine('GeneExpression'),{'presentation':'raincloud_horizontal','columns':1,'title':'A complete donor distribution'})
    add('Expression_one_column',routine('GeneExpression'),{'presentation':'raincloud_horizontal','columns':1,'title':'Donor expression reading page'})
    for i in range(1,6):
        source=ASSETS/'subgroup-gallery'/f'Subgroup_{i:02d}'/'input/example.spec.json'
        for composition in ['strips','paired_cards']:
            add(f'Subgroup_{i:02d}_{composition}',source,{'composition':composition})
    add('Markers_eight_three_columns',ASSETS/'subgroup-gallery/Layout_08Markers_3Columns/input/example.spec.json',{'composition':'paired_cards','ncols':3})
    add('Markers_two_one_column',ASSETS/'subgroup-gallery/Layout_02Markers_1Columns/input/example.spec.json',{'composition':'paired_cards','ncols':1})
    return result


def build(output,render=False):
    out=Path(output)
    if out.exists():raise FileExistsError('Use a fresh output directory')
    out.mkdir(parents=True);records=[]
    for name,source,updates,renderer in cases():
        spec=json.loads(source.read_text('utf8'));original=copy.deepcopy(spec);table=source.parent/spec['input']['path'];raw=table.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==spec['input']['sha256']
        if renderer=='figure_gsea.plot_gsea_tracks':
            spec['parameters']={'contract':spec['parameters']['contract'],**spec['parameters']['options']}
            spec['parameters'].pop('line_encoding',None)
        spec['parameters'].update(updates)
        if renderer:spec['renderer']=renderer
        if name.startswith('Subgroup_') or name.startswith('Markers_'):
            spec['parameters']['title']=spec['parameters']['focus_group']+' | multi-marker evidence'
        folder=out/name;folder.mkdir();spec['figure_id']=name
        if name=='Expression_single':
            import csv,io
            p=spec['parameters']['panels'][:1];spec['parameters']['panels']=p
            rows=list(csv.DictReader(io.StringIO(raw.decode('utf8')),delimiter='\t'));rows=[r for r in rows if r['panel_id']==p[0]['id']]
            buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);raw=buf.getvalue().encode('utf8')
            spec['provenance']['filtering']='Complete explicitly selected first expression panel; all its donors and groups retained'
        if name=='GSEA_single':
            import csv,io
            rows=list(csv.DictReader(io.StringIO(raw.decode('utf8')),delimiter='\t'));rows=[r for r in rows if r['kind']=='metric' or r['pathway']=='Interferon response']
            buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);raw=buf.getvalue().encode('utf8')
            spec['provenance']['filtering']='Complete explicitly selected Interferon response and full shared ranked metric; no curve/hit thinning'
        spec.pop('layout',None)
        spec['input']['path']='input.tsv';spec['input']['sha256']=hashlib.sha256(raw).hexdigest()
        spec['provenance']['source']+='; alternative composition reuses the frozen results without scientific analysis'
        # Reading pages retain their physical type size. Journal-column acceptance
        # requires separate reflow and review at the requested final width.
        spec['export']={'raster_dpi':300,'minimum_text_pt':7.5,'readability_policy':'warn'}
        (folder/'input.tsv').write_bytes(raw)
        (folder/'figure.spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        record={'id':name,'source_spec':source.relative_to(ROOT).as_posix(),'original_input_sha256':original['input']['sha256'],'input_sha256':spec['input']['sha256'],'renderer':spec['renderer'],'parameters':updates,'rendered':False,'screen_review':'UNREVIEWED','scientific_acceptance':False}
        if render:
            from figure_workbench.contracts import make_plan
            from figure_workbench.pipeline import render_plan
            result=render_plan(make_plan(spec,folder),folder/'export');record['rendered']=True;record['rows']=result['rows']
            # Publish only portable bundles, never runtime paths from local plans.
            for path in (folder/'export').glob('.*'):raise ValueError('Unexpected hidden runtime member '+path.name)
        records.append(record)
        (out/'manifest.json').write_text(json.dumps({'schema_version':1,'analysis_performed':False,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(name,record['rendered'],flush=True)
    cards=[]
    for r in records:
        name=r['id'];base=name+'/export/'+name+'/'+name
        cards.append('<section id="'+name+'"><h2>'+html.escape(name.replace('_',' '))+'</h2><img loading="lazy" src="'+base+'.png" alt="'+html.escape(name)+'"><p>'+''.join('<a href="'+base+'.'+e+'">'+e.upper()+'</a> ' for e in ['svg','pdf','tsv'])+'<a href="'+name+'/figure.spec.json">Exact call</a></p></section>')
    page='<!doctype html><meta charset="utf-8"><title>Five transcriptomic figure families</title><style>body{font:16px system-ui;max-width:1200px;margin:36px auto;padding:20px;color:#263e4b}section{border-top:1px solid #dce5e8;padding:20px 0}img{max-width:100%;height:auto}a{margin-right:12px;color:#24747d}</style><h1>Alternative compositions from frozen results</h1><p>Fictional display fixtures. All classic methods remain available. Complete data, counts and exact calls accompany each export. Rendering is not visual or scientific acceptance.</p>'+''.join(cards)
    (out/'index.html').write_text(page,encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--render',action='store_true');args=parser.parse_args();build(args.output,args.render)
