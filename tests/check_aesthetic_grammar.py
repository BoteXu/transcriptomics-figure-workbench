"""Figure meaning and failure checks for the rebuilt and expanded display layer."""
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))


def main(examples):
    import matplotlib.pyplot as plt
    import numpy as np
    from figure_core import table_bytes
    from figure_editorial import audit_text_geometry
    from figure_expanded_grammar import _band_coordinates
    from figure_design import geometry_signature
    from figure_workbench.pipeline import project_appearance
    from figure_workbench.contracts import validate_spec
    from figure_workbench.review import inspect_bundle
    from render_frozen_table import load_table, render
    examples=Path(examples)
    specs={p.name.split('.')[0]:json.loads(p.read_text(encoding='utf8')) for p in (examples/'inputs').glob('*.spec.json')}
    assert set(specs)=={'A01','A02','A03','A04','A05','A06','B01','B02','B03','B04','B05','B06'}
    checks=[];inputs={}
    for id,spec in specs.items():
        validate_spec(spec)
        data=load_table(examples/'inputs'/spec['input']['path'],spec['renderer'],spec['parameters'])
        raw=table_bytes(data);inputs[id]=data
        fig,_=render(spec['renderer'],data,spec['parameters'],project_appearance(spec))
        try:
            assert table_bytes(data)==raw,'Renderer changed supplied input'
            assert not fig._omics_spec['text_geometry']['issues']
            assert not inspect_bundle(examples/id)['issues']
            if id=='B01':
                patches=fig.axes[0].patches
                expected=data['count'].to_numpy()/data['count'].sum()
                actual=[p.get_width()*p.get_height() for p in patches]
                # The renderer draws group-major/category-major in the supplied table order.
                assert np.allclose(actual,expected)
            elif id=='B02':
                assert len(fig.axes[0].patches)==60
                for category,count in zip(data.category,data['count']):
                    assert sum(p.get_gid()=='waffle:'+category for p in fig.axes[0].patches)==count
            elif id=='B03':
                assert len(fig.axes)==4 and fig._omics_spec['options']['linear_reference']
                for line,group in zip(fig.axes[0].lines[:3],data.series.drop_duplicates()):
                    sub=data[data.series==group];assert np.array_equal(line.get_ydata(),sub.value)
            elif id=='B04':
                assert len(fig.axes[0].lines)==data.series.nunique()
                for line,group in zip(fig.axes[0].lines,data.series.drop_duplicates()):
                    sub=data[data.series==group];assert np.array_equal(line.get_xdata(),sub.x) and np.array_equal(line.get_ydata(),sub.y)
            elif id=='B05':
                table=data.set_index(['category','group'])
                for patch in fig.axes[0].patches:
                    _,category,group=patch.get_gid().split(':')
                    assert abs(patch.get_width())==table.loc[(category,group),'value']
                lo,hi=fig.axes[0].get_xlim();assert lo==-hi
            elif id=='B06':
                assert sum(len(c.get_offsets()) for ax in fig.axes for c in ax.collections)==len(data)
                assert all(ax.get_yscale()=='log' for ax in fig.axes)
                assert fig.axes[0].get_ylim()==fig.axes[1].get_ylim()
            elif id=='A03':
                values=data.pivot(index='subject_id',columns='condition',values='value').loc[:,['Control','Treated']]
                assert sum(len(c.get_offsets()) for c in fig.axes[0].collections)==len(data)
                for i,collection in enumerate(fig.axes[0].collections):
                    assert np.array_equal(collection.get_offsets()[:,1],values.iloc[:,i])
                assert np.allclose(fig.axes[0].collections[1].get_offsets()[:,0]-fig.axes[0].collections[0].get_offsets()[:,0],1)
            elif id=='A05':assert all(t%1==0 for t in fig.axes[0].get_yticks())
            elif id=='A02':
                base=geometry_signature(fig);theme=project_appearance(spec);theme['font_family']='DejaVu Serif'
                replacement,_=render(spec['renderer'],data,spec['parameters'],theme)
                try:assert geometry_signature(replacement)==base
                finally:plt.close(replacement)
        finally:plt.close(fig)
    checks.append('12 actual bundles retain supplied values and pass final-size text bounds/collision checks')
    checks.append('Mosaic areas, 60 exact waffle units, mirrored magnitudes, ordered curves, rainfall marks and paired Y values verified')
    x,v=_band_coordinates(np.array([0.,3.]),np.array([-.5,2.5]),1,3)
    assert np.allclose(x,[0,.5,1.5,2.5,3]) and np.allclose(v,[-.5,0,1,2,2.5])
    checks.append('Horizon band crossings preserve straight-segment geometry; linear reference retained')
    failures=0
    def reject(id,change):
        nonlocal failures
        spec=copy.deepcopy(specs[id]);data=inputs[id].copy();change(data,spec)
        before=set(plt.get_fignums())
        try:
            validate_spec(spec);fig,_=render(spec['renderer'],data,spec['parameters'],project_appearance(spec))
        except (ValueError,KeyError):failures+=1
        else:plt.close(fig);raise AssertionError('Bad display input accepted: '+id)
        finally:
            for n in set(plt.get_fignums())-before:plt.close(n)
    for id,change in [
        ('B01',lambda d,s:d.drop(index=d.index[-1],inplace=True)),
        ('B01',lambda d,s:d.loc.__setitem__((0,'count'),-1)),
        ('B02',lambda d,s:d.__setitem__('count',[1.5,22.,10.])),
        ('B02',lambda d,s:d.loc.__setitem__((0,'count'),401)),
        ('B03',lambda d,s:d.loc.__setitem__((0,'value'),4)),
        ('B03',lambda d,s:d.loc.__setitem__((1,'x'),-1)),
        ('B04',lambda d,s:d.loc.__setitem__((1,'step'),0)),
        ('B05',lambda d,s:d.loc.__setitem__((0,'value'),-1)),
        ('B05',lambda d,s:d.drop(index=d.index[-1],inplace=True)),
        ('B06',lambda d,s:d.loc.__setitem__((0,'gap'),0)),
        ('B06',lambda d,s:d.loc.__setitem__((1,'position'),1)),
        ('A04',lambda d,s:d.loc.__setitem__((2,'y'),0)),
        ('A01',lambda d,s:s['provenance'].update(synthetic=False))]:reject(id,change)
    fig=plt.figure(figsize=(4,3));fig.text(.5,.5,'A label');fig.text(.5,.5,'Another label');fig.text(1.1,.2,'Outside')
    try:
        audit=audit_text_geometry(fig)
        assert {'text_collision','text_outside_canvas'}<=set(i['kind'] for i in audit['issues'])
    finally:plt.close(fig)
    checks.append(str(failures)+' semantic rejection cases and a real text collision/clipping fixture passed')
    print(json.dumps({'status':'AESTHETIC_GRAMMAR_SOFTWARE_CHECKS_PASS','checks':checks,
                      'perceptual_acceptance':False,'scientific_acceptance':False}))


if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else ROOT/'examples/aesthetic-v030')
