"""Reviewable alternate arrangements; archived sources remain byte-for-byte intact."""
from pathlib import Path
import sys,json,shutil,html,argparse,inspect
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';G=ROOT/'examples/gallery'
sys.path.insert(0,str(S/'scripts'))
from compose_panels import compose_bundles,arrangement_layout
from figure_core import export_figure,file_sha256
from biomni_view_fixture import biomni_view_cases


def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main(output,resume=False,current_tag='current'):
    if not current_tag or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in current_tag):raise ValueError('Use a simple current-preview directory name')
    if output.exists() and not resume:raise FileExistsError('Fresh output required')
    output.mkdir(parents=True,exist_ok=True);catalog=json.loads((G/'catalog.json').read_text(encoding='utf8'));by={i['id']:i for i in catalog['preserved_examples']}
    registry=json.loads((S/'references/combination-recipes.json').read_text(encoding='utf8'));theme=json.loads((G/'project_theme.json').read_text(encoding='utf8'));records=[]
    for recipe in registry['recipes']:
        sources=[dict(prefix=str(G/b['prefix']),metadata=str(G/b['metadata'])) for b in recipe['bundles']]
        id_=recipe['id'];alternatives=[]
        for orientation in ('horizontal','vertical'):
            layout=arrangement_layout(recipe['layout'],orientation)
            # Preserve each guide and label, embed original vectors and exact tables.
            cached=output/orientation/id_/(id_+'.json')
            if resume and cached.exists():
                receipt=json.loads(cached.read_text(encoding='utf8'))
                for b,r in zip(recipe['bundles'],receipt['panels']):
                    if b['table_sha256']!=r['source_table_sha256'] or file_sha256(G/(b['prefix']+'.pdf'))!=r['source_pdf_sha256']:raise ValueError('Cached source bundle changed')
                for file,sha in receipt['files'].items():
                    if file_sha256(cached.parent/file)!=sha:raise ValueError('Cached layout file changed')
            else:receipt=compose_bundles(sources,layout,output/orientation/id_,preview_dpi=120)
            prefix=f'layout_review/{orientation}/{id_}/{id_}'
            alternatives.append(dict(orientation=orientation,png=prefix+'.png',pdf=prefix+'.pdf',svg=prefix+'.svg',meta=prefix+'.json',png_sha256=receipt['files'][id_+'.png']))
        by[id_]['layout_alternatives']=alternatives;records.append(dict(id=id_,title=recipe['title'],alternatives=alternatives));print(id_+' both arrangements saved',flush=True)
    for id_,c in biomni_view_cases().items():
        if id_ not in ('E41','E42'):continue
        alternatives=[]
        for orientation in ('horizontal','vertical'):
            if resume and (output/orientation/id_/(id_+'.json')).exists():
                prefix=f'layout_review/{orientation}/{id_}/{id_}'
                alternatives.append(dict(orientation=orientation,png=prefix+'.png',pdf=prefix+'.pdf',svg=prefix+'.svg',meta=prefix+'.json',png_sha256=file_sha256(output/orientation/id_/(id_+'.png'))));continue
            fig=c['function'](c['data'],theme,**dict(c['params'],arrangement=orientation))
            meta=dict(source='Original procedural software fixture',palette=theme['palette_name'],input_unit=c['data_required'],experimental_unit='Synthetic display records',contrast='Frozen display',denominator='All records',model='No upstream model executed',limits='Explicit',filtering='None',uncertainty='None',interpretation_limit=c['limitations'],synthetic=True,example_id=id_)
            export_figure(fig,c['data'],output/orientation,id_,meta);plt.close(fig)
            prefix=f'layout_review/{orientation}/{id_}/{id_}'
            alternatives.append(dict(orientation=orientation,png=prefix+'.png',pdf=prefix+'.pdf',svg=prefix+'.svg',meta=prefix+'.json',png_sha256=file_sha256(output/orientation/id_/(id_+'.png'))))
        by[id_]['layout_alternatives']=alternatives;records.append(dict(id=id_,title=c['title'],alternatives=alternatives))
    # Fresh previews for materially repaired historical renderers, without replacing
    # archived pixels or the hashes used by saved browser review notes.
    from reference_fixture import reference_fixtures
    from project_theme import render_with_theme
    from figure_reference import plot_activity_dashboard,plot_training_dashboard,plot_effect_distribution_forest
    from figure_process_dashboard import plot_process_dashboard
    from figure_polish import plot_availability_counts
    from process_fixture import process_fixture
    import pandas as pd
    from figure_network_extensions import plot_alluvial
    for id_,fn in [('R15',plot_activity_dashboard),('R14',plot_training_dashboard),('R16',plot_effect_distribution_forest),('R24',plot_process_dashboard),('P32',plot_availability_counts),('N05',plot_alluvial)]:
        if resume and (output/current_tag/id_/(id_+'.json')).exists():
            prefix=f'layout_review/{current_tag}/{id_}/{id_}'
            by[id_]['current_preview']=dict(png=prefix+'.png',pdf=prefix+'.pdf',svg=prefix+'.svg',tsv=prefix+'.tsv',meta=prefix+'.json',png_sha256=file_sha256(output/current_tag/id_/(id_+'.png')))
            continue
        if id_.startswith('R'):
            import copy
            c=process_fixture() if id_=='R24' else reference_fixtures()[id_];data=c['data'];selected_theme=copy.deepcopy(theme)
            if id_=='R14':selected_theme['group_slots'].update({'Train':0,'Validation':6})
            if id_=='R15':selected_theme['group_slots'].update({'Module 1':0,'Module 2':1,'Module 3':2,'Module 4':4,'Module 5':6})
            if id_=='R24':selected_theme['group_slots'].update(dict(Module=2,Object=0,Accent=6,Backdrop=3,Highlight=6,Paper=3,Stage1=6,Stage2=5,Stage3=0,Stage4=3))
            fig=render_with_theme(fn,data,c['params'],selected_theme)
        elif id_=='P32':
            old=json.loads((G/by[id_]['meta']).read_text(encoding='utf8'));data=pd.read_csv(G/by[id_]['tsv'],sep='\t')
            accepted=set(inspect.signature(fn).parameters)-{'data'};params={k:v for k,v in old['figure_spec'].items() if k in accepted}
            fig=render_with_theme(fn,data,params,theme)
        else:
            old=json.loads((G/by[id_]['meta']).read_text(encoding='utf8'));spec=old['figure_spec']
            data=pd.read_csv(G/by[id_]['tsv'],sep='\t',dtype=str);data['weight']=pd.to_numeric(data['weight'])
            accepted=set(inspect.signature(fn).parameters)-{'data','theme'};params={k:v for k,v in spec.items() if k in accepted};fig=fn(data,theme,**params)
        meta=dict(source='Original deterministic software fixture; current renderer',palette=theme['palette_name'],input_unit=by[id_]['data_required'],experimental_unit='Synthetic display records',contrast='Frozen display',denominator='All records',model='No upstream analysis',limits='Explicit',filtering='None',uncertainty='Supplied only',interpretation_limit=by[id_]['limitations'],synthetic=True,example_id=id_)
        export_figure(fig,data,output/current_tag,id_,meta);plt.close(fig)
        prefix=f'layout_review/{current_tag}/{id_}/{id_}';by[id_]['current_preview']=dict(png=prefix+'.png',pdf=prefix+'.pdf',svg=prefix+'.svg',tsv=prefix+'.tsv',meta=prefix+'.json',png_sha256=file_sha256(output/current_tag/id_/(id_+'.png')))
    page=['<!doctype html><meta charset="utf-8"><title>排版对照</title><style>body{font:16px Arial;margin:32px;color:#25364a}article{margin:35px 0}img{max-width:100%;max-height:500px;border:1px solid #dae2ea}section{display:grid;grid-template-columns:1fr 1fr;gap:30px}a{color:#345e94}</style><h1>完整 panel 横纵排版对照</h1><p>每个布局保留所有 panel、图例、输入表与矢量内容。跨 panel 共轴必须另行声明共同坐标；相同外框不等于共轴。</p>']
    for row in records:
        page.append('<article id="'+row['id']+'"><h2>'+row['id']+' '+html.escape(row['title'])+'</h2><section>')
        for alt in row['alternatives']:
            rel=alt['png'].removeprefix('layout_review/');pdf=alt['pdf'].removeprefix('layout_review/')
            page.append('<div><h3>'+('横向' if alt['orientation']=='horizontal' else '纵向')+'</h3><a href="'+pdf+'"><img loading="lazy" src="'+rel+'"></a><p><a href="'+pdf+'">打开完整矢量PDF</a></p></div>')
        page.append('</section></article>')
    (output/'index.html').write_text('\n'.join(page),encoding='utf8');write(output/'manifest.json',dict(status='ALTERNATE_LAYOUTS_EXPORTED',source_compositions=len(registry['recipes']),composite_arrangements=2*len(registry['recipes']),extra_image_arrangements=4,records=records))
    shutil.copytree(output,G/'layout_review',dirs_exist_ok=resume);write(G/'catalog.json',catalog)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--resume',action='store_true');p.add_argument('--current-tag',default='current');a=p.parse_args();main(a.output,a.resume,a.current_tag)
