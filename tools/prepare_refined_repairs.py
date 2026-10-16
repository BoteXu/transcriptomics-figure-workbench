"""Prepare explicitly scoped display repairs; archived source bytes stay intact."""
from pathlib import Path
import argparse,copy,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))

CATEGORY_IDS=['T06','T07','T08','T09','T10','T12','T13','T14','T15','T17','T18','T19','T25','T26','T27','T28','T29','T31','T32','T35','T36','T37','T38','T39','T40','T43','N09','M01']
CATEGORY_MAP=dict(zip(['#506aaa','#728dc1','#91bbdf','#b6dbf1','#f6d3d9','#e79fbf','#e17692'],['#4b70a6','#218c8d','#b47b43','#8d70aa','#c96068','#698553','#b25d8c']))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def prepare(output):
    output=output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    plan=json.loads((ROOT/'examples/gallery/publication-v030/source-plan.json').read_text(encoding='utf8'))
    selected=CATEGORY_IDS+['P10','R08','R21','R05'];items=[]
    for key in selected:
        row=copy.deepcopy(next(x for x in plan['items'] if x['id']==key));patch=row.setdefault('patch',{})
        if key in CATEGORY_IDS:patch['color_map']=CATEGORY_MAP
        if key=='M01':patch['color_map']={'#b6dbf1':'#a8adb3','#506aaa':'#4b70a6','#f6d3d9':'#d8795b','#e17692':'#218c8d'}
        if key=='P10':patch['color_map']={'#9ac65b':'#4b70a6','#e58b7d':'#d8795b'}
        if key=='R21':patch['color_map']={'#7ccd14':'#4b70a6','#ff6a3d':'#d8795b'}
        if key=='R08':patch['color_map']={'#aedfcb':'#218c8d','#ffd0af':'#d8795b','#c9d4eb':'#7569a5'}
        if key=='P10':
            # The old scatter is embedded as a raster layer. Recolour the actual
            # artists before export; a hex-only SVG patch cannot recolour it.
            import pandas as pd
            import matplotlib.pyplot as plt
            from matplotlib.colors import to_hex
            from figure_styles import plot_volcano_marginal
            from figure_core import export_figure
            original=json.loads((ROOT/row['meta']).read_text(encoding='utf8'));spec=original['figure_spec']
            table=pd.read_csv(ROOT/row['tsv'],sep='\t')
            fig=plot_volcano_marginal(table,labels=spec['labels'],alpha=spec['alpha'],fc=spec['fc'],x_bins=spec['x_histogram_bins'],y_bins=spec['y_histogram_bins'])
            for collection in fig.axes[1].collections:
                rgba=collection.get_facecolors()
                for i,color in enumerate(rgba):
                    mapped=patch['color_map'].get(to_hex(color,keep_alpha=False))
                    if mapped:
                        from matplotlib.colors import to_rgba
                        rgba[i]=to_rgba(mapped,color[3])
                collection.set_facecolors(rgba)
            metadata={k:v for k,v in original.items() if k not in ['figure_spec','output_sha256']}
            metadata['palette']='Declared blue/coral directions; exact coordinates and histogram bins retained'
            export_figure(fig,table,output,key,metadata);plt.close(fig)
            source=output/key/(key+'.svg');meta=output/key/(key+'.json')
            row.update(svg=source.relative_to(ROOT).as_posix(),meta=meta.relative_to(ROOT).as_posix(),source_sha256=sha(source),source_metadata_sha256=sha(meta))
        if key=='R05':
            # Reuse the original renderer's semantic palette hook so the ellipses
            # AND embedded colourbar image share the same centred mapping.
            # Replacing isolated SVG hex values would leave the guide incorrect.
            import pandas as pd
            import matplotlib.pyplot as plt
            from figure_reference import plot_ellipse_correlation
            from figure_reference_palettes import palette_scope
            from figure_core import export_figure
            original=json.loads((ROOT/row['meta']).read_text(encoding='utf8'))
            table=pd.read_csv(ROOT/row['tsv'],sep='\t')
            with palette_scope({'continuous':{'diverging':['#327d9f','#f7f7f4','#d8795b']},'project_id':'synthetic-r05-refined'}):
                fig=plot_ellipse_correlation(table,labels=original['figure_spec']['labels'])
            metadata={k:v for k,v in original.items() if k not in ['figure_spec','output_sha256']}
            metadata['palette']='Declared blue-neutral-coral centred at zero'
            export_figure(fig,table,output,'R05',metadata);plt.close(fig)
            source=output/'R05/R05.svg';meta=output/'R05/R05.json'
            row.update(svg=source.relative_to(ROOT).as_posix(),meta=meta.relative_to(ROOT).as_posix(),source_sha256=sha(source),source_metadata_sha256=sha(meta))
            row['context']['title_en']='Signed correlations with a neutral zero'
        items.append(row)
    result=dict(schema_version=1,items=items,category_ids=CATEGORY_IDS,scientific_acceptance=False,
        policy='Exact identity-to-colour substitution for declared categorical figures only; continuous ramps and reference colour cards excluded')
    write(output/'source-plan.json',result)
    print(json.dumps(dict(items=len(items),category_items=len(CATEGORY_IDS))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);prepare(p.parse_args().output)
