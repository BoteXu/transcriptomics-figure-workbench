"""Reflow every historical composition relationship, deduplicating aliases.

Three complete layouts per relationship; immutable source SVGs and TSVs remain
bound by hashes. These are full reading layouts, not paper-size approval.
"""
import argparse,collections,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.layout import make_layout,export_layout


def build(out,source_root=None):
    recipes=json.loads((ROOT/'examples/gallery/publication-v030/source-plan.json').read_text())['compositions']
    groups=collections.OrderedDict()
    for recipe in recipes:groups.setdefault(tuple(recipe['components']),[]).append(recipe)
    source_root=source_root or ROOT/'examples/forms-v080'
    for component in {c for components in groups for c in components}:
        for ext in ['svg','tsv']:
            if not (source_root/component/(component+'.'+ext)).is_file():raise ValueError('Missing current complete component '+component)
    out.mkdir(parents=True,exist_ok=False)
    records=[];relationships=[]
    for components,aliases in groups.items():
        base=aliases[0]['source_id'];relationships.append(dict(id=base,aliases=[a['id'] for a in aliases],components=list(components)))
        for mode in ['balanced','weighted','reading']:
            key=base+'_'+mode
            panels=[dict(id='Panel'+str(i+1),svg=str(source_root/c/(c+'.svg')),
                         table=str(source_root/c/(c+'.tsv'))) for i,c in enumerate(components)]
            req=dict(id=key,title=aliases[0]['title'],panels=panels,canvas_width_pt=1100,
                     gap_pt=24,padding_pt=24,label_order='reading')
            if mode=='balanced':req.update(columns='auto',preferred_panel_width_pt=450,packing='masonry',packing_order='input')
            elif mode=='weighted':req.update(columns=2,column_weights=[1.15,1],packing='masonry',packing_order='tall_first')
            else:req.update(columns=1,max_rows_per_page=2,canvas_width_pt=650)
            plan=make_layout(req,out);folder=out/key;export_layout(plan,folder)
            # Private audit plan paths are explicit; public packaging must
            # rewrite them against a selected portable source tree.
            (folder/'request.json').write_text(json.dumps(req,indent=2)+'\n',encoding='utf8')
            for page in plan['pages']:
                name=key+'-page-'+str(page['page']+1).zfill(2)
                records.append(dict(id=name,form=key,file=key+'/'+name+'.svg',
                    relationship=base,aliases=[a['id'] for a in aliases],components=list(components),
                    page_components=[components[int(p['id'][5:])-1] for p in page['panels']],
                    layout=mode,status='RENDERED_UNREVIEWED',visual_acceptance=False,target_size_assessed=False))
            (out/'manifest.json').write_text(json.dumps(dict(records=records,relationships=relationships,
                recipe_aliases=len(recipes),unique_relationships=len(groups),scope='Complete source-bound reading reflows; paper proof not implied',visual_acceptance=False),indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(relationships=len(groups),aliases=len(recipes),layouts=len(groups)*3,pages=len(records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--source-root',type=Path);a=p.parse_args();build(a.output,a.source_root)
