"""Bounded real-measurement and declared synthetic-curve drawing fixtures."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from full_layout_cases import ROOT,SKILL
sys.path.insert(0,str(SKILL/'scripts'))


def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out,public_data):
    import numpy as np,pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from render_frozen_table import render
    from project_theme import create_theme
    from figure_core import table_bytes
    from figure_design import geometry_signature,audit_layout
    out.mkdir(parents=True,exist_ok=False);rows=[]
    def save(key,data,adapter,params,theme,layout,context):
        folder=out/key;folder.mkdir();raw=table_bytes(data)
        names=list(data['model' if 'model' in data else 'group'].drop_duplicates())
        params['palette']={g:theme['palette_colors'][theme['group_slots'][g]] for g in names}
        fig,_=render(adapter,data,params,theme,layout=layout)
        assert raw==table_bytes(data)
        for fmt in ['svg','png','pdf']:fig.savefig(folder/(key+'.'+fmt),dpi=130,facecolor='white')
        (folder/(key+'.tsv')).write_bytes(raw)
        spec=dict(form=key,example=key,route='native',adapter=adapter,parameters=params,theme=theme)
        write(folder/'request.json',spec)
        rows.append(dict(id=key,form=key,rows=len(data),context=context,requested_layout=layout,
            size_inches=list(fig.get_size_inches()),quantitative_geometry_sha256=geometry_signature(fig),
            automated_layout=audit_layout(fig),files={p.name:sha(p) for p in folder.iterdir()},
            status='RENDERED_UNREVIEWED',visual_acceptance=False,scientific_acceptance=False))
        plt.close(fig);write(out/'manifest.json',dict(records=rows));print(key,flush=True)
    receipt=json.loads((public_data/'receipt.json').read_text())
    for record in receipt['files']:
        source=public_data/Path(record['path']).name
        if sha(source)!=record['sha256']:raise ValueError('Pinned public data changed')
    sources=out/'public-source';sources.mkdir()
    for file in ['penguins.csv','LICENSE.md','receipt.json']:shutil.copyfile(public_data/file,sources/file)
    raw=pd.read_csv(public_data/'penguins.csv');raw['source_row_id']=np.arange(1,len(raw)+1)
    complete=raw.dropna(subset=['bill_length_mm','bill_depth_mm'])
    groups=list(complete.species.unique());theme=create_theme('public-penguin-layout','package_editorial',{g:i for i,g in enumerate(groups)},font_family='DejaVu Sans')
    for level,n in [('small',6),('medium',24),('large',None)]:
        selected=complete if n is None else complete.groupby('species',sort=False).head(n)
        data=pd.DataFrame(dict(unit_id=['Source row '+str(i) for i in selected.source_row_id],group=selected.species,x=selected.bill_length_mm,y=selected.bill_depth_mm))
        context=dict(kind='REAL_PUBLIC_MEASUREMENTS',license='CC0-1.0',source=receipt,source_rows=len(raw),complete_rows=len(complete),missing_measurement_rows=len(raw)-len(complete),
            selection='All complete records' if n is None else 'First '+str(n)+' complete source rows per species; declared layout fixture, not a representative analysis',
            limits='Source rows identify display records; this simplified table does not independently establish longitudinal individual identity. No tests, fit or biological conclusion.')
        save('Penguins_'+level,data,'xy_points',dict(x_label='Bill length (mm)',y_label='Bill depth (mm)',unit_label='Public penguin measurement record'),theme,
            {'width_inches':dict(small=5.8,medium=7,large=8)[level]},context)
    x=np.linspace(0,1,21)
    for kind in ['ROC','PR','calibration']:
        for count,cols in [(1,'auto'),(5,2),(9,4)]:
            names=['Model '+str(i+1) for i in range(count)]
            theme=create_theme('synthetic-curve-facets','package_editorial',{n:i for i,n in enumerate(names)},font_family='DejaVu Sans')
            parts=[]
            for i,name in enumerate(names):
                y=x**(.4+i*.04) if kind=='ROC' else 1-(.4+i*.025)*x if kind=='PR' else np.clip(x+.08*np.sin(np.pi*x+i*.1),0,1)
                parts.append(pd.DataFrame(dict(model=name,x=x,y=y)))
            data=pd.concat(parts,ignore_index=True)
            save('Curves_'+kind+'_'+str(count),data,'figure_core.plot_curve',dict(kind=kind,ncols=cols),theme,None,
                dict(kind='DECLARED_SYNTHETIC_CURVE',models=count,points_per_curve=21,preparation='Illustrative equations frozen before drawing; not empirical model evaluation',scientific_validity=False))
    print(json.dumps(dict(cases=len(rows),scientific_acceptance=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--public-data',type=Path,required=True);a=p.parse_args();main(a.output,a.public_data)
