"""Frozen display tests: actual data amount, user layout and stale-review behavior."""
from pathlib import Path
import sys,json,copy,math,hashlib
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench/scripts';sys.path.insert(0,str(S))
from figure_workbench.responsive import grid_shape,validate_layout

def main(output):
    from project_theme import create_theme
    import pandas as pd
    import matplotlib.pyplot as plt
    from render_frozen_table import render
    from figure_core import table_bytes
    from figure_design import geometry_signature,audit_layout
    out=Path(output);out.mkdir(parents=True,exist_ok=False);rows=[]
    names=['Pathway '+str(i+1) for i in range(9)];groups=['Control','Treated']
    theme=create_theme('synthetic-responsive-layout','C10',{k:i for i,k in enumerate(names)},font_family='DejaVu Sans')
    theme['group_slots'].update({'Control':0,'Treated':1})
    theme['continuous']['diverging']=['#4477AA','#F7F7F7','#D8795B'];theme['continuous']['sequential']=['#EDF3F3','#218C8D'];theme['roles'].update(positive='#D8795B',negative='#4477AA')
    contract=dict(synthetic=True,source_definition='Hand-authored frozen display fixtures',independent_unit='Software fixtures; no biological units',denominator='All selected fixture identities',value_definition='Fixed supplied values',uncertainty_definition='Fixed illustrative intervals; no inference')
    def save(k,data,adapter,params,layout=None):
        before=table_bytes(data);fig,audit=render(adapter,data,params,theme,layout=layout)
        assert table_bytes(data)==before
        if fig.get_figwidth()*fig.get_figheight()*150**2>18_000_000:plt.close(fig);raise ValueError('Bounded fixture raster budget exceeded')
        svg=out/(k+'.svg');png=out/(k+'.png');fig.savefig(svg,format='svg',facecolor='white');fig.savefig(png,dpi=150,facecolor='white')
        from matplotlib.text import Text
        texts=[t.get_text() for t in fig.findobj(Text) if t.get_visible()]
        result=dict(id=k,renderer=adapter,layout=layout,input_rows=len(data),input_sha256=hashlib.sha256(before).hexdigest(),geometry_sha256=geometry_signature(fig),axes=len(fig.axes),size_inches=list(fig.get_size_inches()),automated_layout=audit_layout(fig),text=texts,output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [svg,png]},screen_review='PENDING',target_size_assessed=False,scientific_acceptance=False)
        (out/(k+'.tsv')).write_bytes(before);(out/(k+'.request.json')).write_text(json.dumps(dict(renderer=adapter,parameters=params,layout=layout),indent=2)+'\n')
        rows.append(result);plt.close(fig);return result
    for n,m in [(3,4),(17,11),(31,7)]:
        data=pd.DataFrame([dict(feature='Feature '+str(i+1),sample='Condition '+str(j+1),value=((i*7+j*3)%21-10)/10) for i in range(n) for j in range(m)])
        r=save('Matrix_'+str(n)+'x'+str(m),data,'heatmap',dict(value_label='Frozen signed score',scale_type='signed',row_label_wrap=18,column_label_wrap=14),dict(width_inches=max(7,3+m*.48),height_inches=max(3,1.5+n*.30)))
        assert all(f'Feature {i+1}' in r['text'] for i in range(n))
    for n,cols in [(1,'auto'),(5,2),(7,4)]:
        data=pd.DataFrame([dict(cell_id='Point'+str(i),feature='Feature '+str(f+1),x=i%8,y=i//8,value=(i+f)%5) for f in range(n) for i in range(32)])
        r=save('Features_'+str(n)+'_cols_'+str(cols),data,'feature_facets',dict(value_label='Supplied value',limits=[0,4],title='Complete feature facets'),dict(columns=cols,panel_width_inches=3.1))
        assert all('Feature '+str(i+1) in r['text'] for i in range(n))
    long=pd.DataFrame([dict(feature='Complete feature identity with long label '+str(i+1),sample='Long condition identity '+str(j+1),value=((i+j)%9-4)/4) for i in range(12) for j in range(6)])
    save('Matrix_long_labels',long,'heatmap',dict(value_label='Frozen score',row_label_wrap=20,column_label_wrap=14),dict(width_inches=10,height_inches=10))
    gs=[];universe=20
    for n in names:
        gs += [dict(kind='curve',pathway=n,rank=i+1,value=[.1,.2,.3,.4,.5,.6,.7,.8,.7,.6,.5,.4,.3,.25,.2,.15,.1,.07,.03,0][i]) for i in range(universe)]
        gs += [dict(kind='hit',pathway=n,rank=i,gene='Gene'+str(i),leading_edge=1) for i in range(1,9)]
        gs.append(dict(kind='summary',pathway=n,NES=1.92,padj=.008,set_size=8))
    gs += [dict(kind='metric',rank=i+1,value=3-i*.3) for i in range(universe)]
    allg=pd.DataFrame(gs)
    for n,cols in [(2,1),(5,2),(9,3)]:
        d=allg[allg.pathway.isna()|allg.pathway.isin(names[:n])].copy()
        p=dict(contract=contract,curve_order=names[:n],ranked_universe=20,metric_label='Rank metric',contrast='Synthetic B versus A',gene_set_version='Synthetic sets v1',mode='facets',title='Complete GSEA tracks')
        r=save('GSEA_'+str(n)+'_cols_'+str(cols),d,'figure_gsea.plot_gsea_tracks',p,dict(columns=cols,panel_width_inches=4.2,panel_height_inches=3.8))
        assert r['axes']==3*n and all(any(name in t for t in r['text']) for name in names[:n])
    for n,cols in [(2,1),(7,3),(13,5)]:
        d=pd.DataFrame([dict(sample=g+str(i),group=g,celltype='Type '+str(j+1),count=i+j+1) for g in groups for i in range(4) for j in range(n)])
        r=save('Composition_'+str(n)+'_cols_'+str(cols),d,'figure_styles.plot_composition_panels',dict(unit_label='synthetic sample',y_max=None,palette={'Control':'#218C8D','Treated':'#D8795B'}),dict(columns=cols))
        assert all('Type '+str(i+1) in r['text'] for i in range(n))
    data=pd.DataFrame([dict(label='Feature '+str(i+1),group='Control',estimate=.2+i*.01,lower=.1+i*.01,upper=.3+i*.01) for i in range(41)])
    save('Forest_41',data,'figure_editorial.plot_editorial',dict(kind='forest',contract=contract,options={'effect_scale':'difference','x_label':'Supplied effect','title':'Complete interval rows'}))
    (out/'manifest.json').write_text(json.dumps(dict(records=rows,scientific_analysis=False,visual_acceptance=False),indent=2)+'\n')
    assert grid_shape(19,5)==(4,5)
    assert grid_shape(19,'auto',2)==(2,10)
    from figure_workbench.responsive import canvas_budget
    try:canvas_budget(100,100)
    except ValueError:pass
    else:raise AssertionError('Unbounded canvas accepted')
    assert not plt.get_fignums()
    tiny=pd.DataFrame([dict(feature='F1',sample='C1',value=.1),dict(feature='F2',sample='C1',value=.2)])
    try:render('heatmap',tiny,{'value_label':'Supplied value'},theme,layout={'columns':2})
    except ValueError as e:assert 'axis_groups' in str(e)
    else:raise AssertionError('Unsupported columns silently ignored')
    assert not plt.get_fignums()
    for req in [dict(columns=0),dict(width_inches=-2),dict(rows=1.5)]:
        try:validate_layout(req)
        except ValueError:pass
        else:raise AssertionError('Invalid layout accepted')
    print(json.dumps(dict(status='RESPONSIVE_LAYOUT_RUNTIME_PASS',exports=len(rows),input_values_preserved=True,screen_review='REQUIRED')))

if __name__=='__main__':main(sys.argv[1])
