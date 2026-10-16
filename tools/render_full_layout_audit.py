"""Serial, bounded drawing checks of public frozen software fixtures."""
from pathlib import Path
import argparse, copy, hashlib, json, sys, traceback
from full_layout_cases import cases, ROOT, SKILL
sys.path.insert(0, str(SKILL/'scripts'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_cases(output, selected=None, level=None, example_ids=None,include_all=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
    from figure_core import table_bytes
    from figure_design import geometry_signature, audit_layout
    from render_frozen_table import render, load_table
    output.mkdir(parents=True, exist_ok=False)
    records=[]; inventory=[]
    for case in cases(example_ids,include_all):
        if case['route']!='native' or selected and case['form'] not in selected:
            continue
        key=case['form']; dest=output/key;dest.mkdir()
        try:
            data=pd.read_csv(ROOT/case['table'],sep='\t',dtype=str,keep_default_na=False).replace('',float('nan'))
            identity={'group','sample','sample_id','cell_id','unit_id','object_id','feature','feature_id','label','category','series','condition','record_type','kind','panel','layer','node_id','source','target','term','term_id','term_label','gene','gene_id','pathway','chromosome','chain','signal','variant_id','transcript_id','state','stage','surface_id','track','track_id','edge_id','family','segment','decision','spec_id','event','set_id'}
            for col in data.columns:
                if col not in identity and not col.endswith('_id') or (col in ['label','label_id'] and case['base_form']=='slice') or (col=='matrix_id' and case['adapter']=='figure_process_dashboard.plot_process_dashboard'):
                    try:data[col]=pd.to_numeric(data[col],errors='raise')
                    except (ValueError,TypeError):pass
            volume_receipt=None
            if level is not None:
                from frozen_volume_cases import volume
                case,data,volume_receipt=volume(case,data,level)
            from project_theme import create_theme
            palettes={}
            for name in ['palette','group_palette','stack_palette']:
                if isinstance(case['parameters'].get(name),dict):palettes.update(case['parameters'][name])
            groups=list(dict.fromkeys(str(v) for col in ['group','series','condition','stage'] if col in data for v in data[col].dropna()))
            if case['base_form']=='mosaic':groups+=case['parameters']['category_order']
            groups=list(dict.fromkeys(list(palettes)+groups))
            if groups:
                base=copy.deepcopy(case['theme'])
                if set(groups)-set(base['group_slots']):
                    if len(groups)>24:
                        if set(groups)-set(palettes):
                            # Non-colour fields are not category declarations.
                            groups=list(palettes)
                        if not groups:raise ValueError('An explicit complete named colour map is required')
                        base=create_theme('synthetic-full-layout-'+key,'package_editorial',{'Display':0},font_family='DejaVu Sans',roles={'positive':'#D8795B','negative':'#4477AA'})
                        base['category_colors']={g:palettes[g] for g in groups}
                    else:base=create_theme('synthetic-full-layout-'+key,'package_editorial' if len(groups)<=10 else 'atlas_cells',{g:i for i,g in enumerate(groups)},font_family='DejaVu Sans',roles={'positive':'#D8795B','negative':'#4477AA'})
                    base['continuous']['diverging']=['#4477AA','#F7F7F7','#D8795B']
                    base['continuous']['sequential']=['#E1E8EB','#396F91']
                case['theme']=base
            inventory.append(dict(form=key,example=case['example'],adapter=case['adapter'],rows=len(data),
                parameters=case['parameters'],columns={c:dict(dtype=str(data[c].dtype),unique=int(data[c].nunique()),examples=[str(v) for v in data[c].dropna().drop_duplicates().head(4)]) for c in data.columns}))
            source_hash=digest(ROOT/case['table']); before=table_bytes(data)
            layout=None if level is None else {'width_inches':[7.2,10,8.5][level]}
            if level is not None and case['form']=='feature-embedding':layout['columns']=[1,3,2][level]
            if level is not None and case['form']=='slice':case['parameters']['arrangement']=['vertical','horizontal','vertical'][level]
            fig,audit=render(case['adapter'],data,case['parameters'],case['theme'],layout=layout)
            assert table_bytes(data)==before
            width,height=fig.get_size_inches();dpi=min(130,(10_000_000/(width*height))**.5)
            with plt.rc_context({'svg.fonttype':'none','pdf.fonttype':42}):
                fig.savefig(dest/(key+'.svg'),format='svg',facecolor='white')
                if include_all or example_ids:fig.savefig(dest/(key+'.pdf'),format='pdf',facecolor='white')
            fig.savefig(dest/(key+'.png'),dpi=dpi,facecolor='white')
            (dest/(key+'.tsv')).write_bytes(before)
            (dest/'request.json').write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            record=dict(id=key,form=key,example=case['example'],rows=len(data),source_input_sha256=source_hash,
                input_sha256=hashlib.sha256(before).hexdigest(),adapter=case['adapter'],size_inches=[width,height],
                quantitative_geometry_sha256=geometry_signature(fig),automated_layout=audit_layout(fig),
                volume=volume_receipt,requested_layout=layout,
                files={p.name:digest(p) for p in dest.iterdir()},status='RENDERED_UNREVIEWED',visual_acceptance=False,scientific_acceptance=False)
            plt.close(fig)
            print(key+' RENDERED',flush=True)
        except Exception as exc:
            record=dict(id=key,form=key,status='FAILED',error=type(exc).__name__+': '+str(exc))
            (dest/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
            plt.close('all');print(key+' FAILED '+str(exc)[:180],flush=True)
        records.append(record)
        (output/'manifest.json').write_text(json.dumps(dict(records=records,visual_acceptance=False),indent=2)+'\n',encoding='utf-8')
        (output/'input-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(rendered=sum(r['status']=='RENDERED_UNREVIEWED' for r in records),failed=sum(r['status']=='FAILED' for r in records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--forms',nargs='*');p.add_argument('--examples',nargs='*');p.add_argument('--all-examples',action='store_true');p.add_argument('--volumes',action='store_true');a=p.parse_args()
    if a.volumes and (a.examples or a.all_examples):raise ValueError('Volume audit uses consolidated base forms; source example replay is separate')
    if a.volumes:
        a.output.mkdir(parents=True,exist_ok=False)
        for level,name in enumerate(['small','medium','large']):render_cases(a.output/name,a.forms,level)
    else:render_cases(a.output,a.forms,example_ids=a.examples,include_all=a.all_examples)
