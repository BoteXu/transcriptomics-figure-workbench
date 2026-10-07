"""Enumerate every saved Python grammar and exercise existing synthetic fixtures.

Reports runtime, immutable input, geometry and page orientation separately from
advisory visual warnings. Does not label a software pass as aesthetic approval.
"""
from pathlib import Path
import sys,ast,importlib,inspect,functools,json,tempfile,hashlib,argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd,numpy as np
ROOT=Path(__file__).resolve().parents[1];SCRIPTS=ROOT/'skills/transcriptomics-figure-workbench/scripts'
sys.path.insert(0,str(SCRIPTS))
from figure_design import geometry_signature,audit_layout
from figure_layout import apply_page_layout,optimize_guide_layout
from indexed_alignment import audit_index_alignment
from figure_core import table_bytes


def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);records={};inventory={};failures=[]
    for file in sorted(SCRIPTS.glob('figure_*.py')):
        module=importlib.import_module(file.stem)
        for node in ast.parse(file.read_text(encoding='utf8')).body:
            if isinstance(node,ast.FunctionDef) and node.name.startswith('plot_'):
                name=file.stem+'.'+node.name;fn=getattr(module,node.name)
                inventory[name]=dict(module=file.stem,function=node.name,line=node.lineno,signature=str(inspect.signature(fn)),
                    source_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
                def instrument(function,name):
                    @functools.wraps(function)
                    def wrapped(*args,**kw):
                        original=args[0].copy(deep=True) if args and isinstance(args[0],pd.DataFrame) else None
                        fig=function(*args,**kw)
                        if name in records:return fig
                        records[name]=dict(runtime='PASS',page_layouts={},visual_review='NOT_MANUALLY_APPROVED')
                        r=records[name]
                        try:
                            fig=optimize_guide_layout(fig)
                            if original is not None:
                                pd.testing.assert_frame_equal(original,args[0]);r['input_immutable']=True
                                assert fig._omics_input_sha256==hashlib.sha256(table_bytes(original)).hexdigest()
                            r['kind']=fig._omics_spec['kind'];r['quantitative_geometry_sha256']=geometry_signature(fig)
                            r['index_alignment']=audit_index_alignment(fig)
                            assert not r['index_alignment']['issues']
                            r['advisory_layout']=audit_layout(fig)
                            fig.savefig(output/(name+'.png'),dpi=90,facecolor='white')
                            r['preview']=name+'.png'
                            for orientation in ['horizontal','vertical']:
                                other=optimize_guide_layout(function(*args,**kw));other.canvas.draw();signature=geometry_signature(other)
                                apply_page_layout(other,'landscape' if orientation=='horizontal' else 'portrait')
                                assert signature==geometry_signature(other)
                                assert not audit_index_alignment(other)['issues']
                                r['page_layouts'][orientation]='PASS';plt.close(other)
                            print(name+' runtime + both page layouts PASS',flush=True)
                        except Exception as e:
                            r['runtime']='FAIL';r['error']=type(e).__name__+': '+str(e);failures.append(name);raise
                        return fig
                    return wrapped
                setattr(module,node.name,instrument(fn,name))
    def close(fig):plt.close(fig)
    with tempfile.TemporaryDirectory(prefix='plot-audit-') as tmp:
        temp=Path(tmp)
        # Read only the setup/positive drawing portions of existing fixtures.
        def prefix(filename,stop,main_function=False):
            tree=ast.parse((SCRIPTS/filename).read_text(encoding='utf8'));namespace={'__name__':'fixture_setup','__file__':str(SCRIPTS/filename)}
            if main_function:
                body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main').body
                setup=[]
                for node in body:
                    setup.append(node)
                    if stop(node):break
                imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
                exec(compile(ast.Module(body=imports,type_ignores=[]),filename,'exec'),namespace)
                namespace['out']=temp/filename;namespace['export_figure']=lambda *a,**k:None
                exec(compile(ast.Module(body=setup,type_ignores=[]),filename,'exec'),namespace)
            else:
                setup=[]
                for node in tree.body:
                    setup.append(node)
                    if stop(node):break
                old=sys.argv;sys.argv=[filename,str(temp/filename)]
                try:exec(compile(ast.Module(body=setup,type_ignores=[]),filename,'exec'),namespace)
                finally:sys.argv=old
            return namespace
        assigned=lambda name:lambda n:isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)
        z=prefix('style_test.py',assigned('jobs'),True)
        for _,_,fn in z['jobs']:close(fn())
        z=prefix('publication_test.py',assigned('fns'))
        for _,_,fn in z['fns']:close(fn())
        z=prefix('increment_test.py',assigned('calls'))
        for key,fn in z['calls'].items():close(fn(z['tables'][key]))
        z=prefix('multimodal_test.py',assigned('cases'))
        for _,fn in z['cases']:close(fn())
        z=prefix('polish_test.py',assigned('rc'))
        close(z['matrix']());close(z['plot_recorded_evidence'](z['e']));close(z['plot_availability_counts'](z['a']))
        # Smoke fixture setup draws all core and original extension functions.
        tree=ast.parse((SCRIPTS/'smoke_test.py').read_text(encoding='utf8'));namespace={'out':temp/'smoke','__name__':'fixture_setup'}
        imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        exec(compile(ast.Module(body=imports,type_ignores=[]),'smoke','exec'),namespace);namespace['export_figure']=lambda *a,**k:None
        body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main').body;setup=[]
        for n in body:
            if isinstance(n,ast.FunctionDef) and n.name=='fails':break
            setup.append(n)
        exec(compile(ast.Module(body=setup,type_ignores=[]),'smoke','exec'),namespace)
        from reference_fixture import reference_fixtures
        import figure_reference,figure_process_dashboard
        for c in reference_fixtures().values():
            module=figure_reference if hasattr(figure_reference,c['function']) else figure_process_dashboard
            close(getattr(module,c['function'])(c['data'],**c['params']))
        from method_extension_fixture import fixture_cases,draw_case
        from multiview_fixture import multiview_cases
        from linked_evidence_fixture import linked_cases
        theme,cases=fixture_cases();_,more=multiview_cases()
        for c in {**cases,**more}.values():close(draw_case(c,theme))
        for c in linked_cases().values():
            from render_frozen_table import render
            close(render(c['adapter'],c['data'],c['params'],theme)[0])
        from biomni_view_fixture import biomni_view_cases
        for c in biomni_view_cases().values():close(c['function'](c['data'],theme,**c['params']))
        from analysis_result_fixture import analysis_result_cases
        for c in analysis_result_cases().values():
            from render_frozen_table import render
            close(render(c['adapter'],c['data'],c['params'],theme)[0])
        # Independent saved network tables and standalone palette applications.
        gallery=ROOT/'examples/gallery';catalog=json.loads((gallery/'catalog.json').read_text(encoding='utf8'))
        original_theme=json.loads((gallery/'project_theme.json').read_text(encoding='utf8'))
        import figure_network_extensions as network
        map_names={'typed_network':'plot_typed_network','weighted_chord':'plot_weighted_chord','alluvial':'plot_alluvial','upset':'plot_upset',
                   'multistate_matrix':'plot_multistate_matrix','running_enrichment':'plot_running_enrichment','rank_bump':'plot_rank_bump','hex_density':'plot_hex_density','contour_field':'plot_contour_field'}
        numeric={'x','y','area','weight','sign','rank','score','value','left','right','height'}
        for item in catalog['preserved_examples']:
            if not item['id'].startswith('N') or not item.get('tsv'):continue
            meta=json.loads((gallery/item['meta']).read_text(encoding='utf8'));spec=meta['figure_spec'];kind=spec['kind']
            if kind not in map_names:continue
            fn=getattr(network,map_names[kind]);accepted=set(inspect.signature(fn).parameters)-{'data','theme'}
            params={k:v for k,v in spec.items() if k in accepted}
            if kind=='weighted_chord':params['order']=spec['sector_order']
            if kind in ('hex_density','contour_field'):
                params.setdefault('x_label','Supplied X');params.setdefault('y_label','Supplied Y')
            data=pd.read_csv(gallery/item['tsv'],sep='\t',dtype=str,keep_default_na=False).replace('',np.nan)
            for col in (numeric|set(params.get('set_columns',[])))&set(data):data[col]=pd.to_numeric(data[col])
            close(fn(data,original_theme,**params))
        from project_theme import render_panel
        for item in catalog['preserved_examples']:
            if item['id']!='T24':continue
            style=json.loads((gallery/item['style']).read_text(encoding='utf8'));data=pd.read_csv(gallery/item['tsv'],sep='\t')
            close(render_panel(data,style['panel_spec'],original_theme))
    result=dict(status='DRAWING_RUNTIME_AND_LAYOUT_AUDIT',functions=len(inventory),executed=len(records),
                failures=failures,uncovered=sorted(set(inventory)-set(records)),
                scope='Synthetic runtime/input/page geometry checks; advisory warnings and visual acceptance remain separate',
                records=[dict(inventory[name],**records.get(name,dict(runtime='UNEXERCISED'))) for name in sorted(inventory)])
    (output/'plot-logic-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
    assert not failures and not result['uncovered']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.output)
