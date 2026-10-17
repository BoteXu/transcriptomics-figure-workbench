"""Regress actual guide, quantity and semantic failures found during review.

These checks do not judge aesthetics, scientific validity or paper acceptance.
"""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'));sys.path.insert(0,str(ROOT/'tools'))


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from figure_core import plot_dot,plot_curve,table_bytes
    from project_theme import create_theme,apply_project_style,render_with_theme
    theme=create_theme('source-regression','package_editorial',{'A':0,'B':1},font_family='DejaVu Sans')
    # Complete long identity names and a wide requested canvas once made the
    # colour and size guides overlap. Their actual final display boxes matter.
    from figure_workbench.responsive import apply_native_layout
    d=pd.DataFrame({'feature':['A / long display identity','B / long display identity'],'group':['Only','Only'],'fraction':[0.,1.],'value':[-1.,1.]})
    frozen=table_bytes(d);f=plot_dot(d,'Supplied effect',value_semantics='signed_effect',denominator_label='all supplied objects')
    apply_project_style(f,theme);apply_native_layout(f,{'width_inches':10})
    f.canvas.draw();renderer=f.canvas.get_renderer();key=f.axes[-1].get_tightbbox(renderer)
    assert all(not key.overlaps(l.get_window_extent(renderer)) for l in f.legends),'dot guides overlap'
    np.testing.assert_allclose(f.axes[0].collections[0].get_sizes(),[0,260]);assert table_bytes(d)==frozen
    plt.close(f)
    try:plot_dot(d,'Effect',value_semantics='signed_effect',denominator_label='objects',row_counts={'A':5},count_label='n')
    except ValueError:pass
    else:raise AssertionError('Incomplete support counts silently accepted')
    # Supplied PR bounds must use the same declared stair convention; no
    # fabricated interval or changed curve vertex is acceptable.
    curves=pd.DataFrame({'model':['A']*3,'x':[0,.5,1.],'y':[1.,.7,.4],'lower':[.94,.64,.34],'upper':[1.,.76,.46]})
    try:plot_curve(curves,kind='PR')
    except ValueError:pass
    else:raise AssertionError('Unlabelled uncertainty silently accepted')
    f=plot_curve(curves,kind='PR',palette={'A':'#35618F'},prevalence=.2,interval_label='Illustrative bounds',interpolation='steps-post')
    assert f.axes[0].lines[0].get_drawstyle()=='steps-post';np.testing.assert_equal(f.axes[0].lines[0].get_ydata(),curves.y)
    assert len(f.axes[0].collections)==1;plt.close(f)
    # Applying the project theme twice must retain the curve/guide hierarchy.
    from figure_core import stamp
    f,ax=plt.subplots();a,=ax.plot([0,1],[0,1],lw=.5);b,=ax.plot([0,1],[1,0],lw=2)
    stamp(f,curves,'source_runtime');apply_project_style(f,theme);first=[a.get_linewidth(),b.get_linewidth()]
    apply_project_style(f,theme);np.testing.assert_allclose(first,[a.get_linewidth(),b.get_linewidth()]);assert b.get_linewidth()==4*a.get_linewidth();plt.close(f)
    # Unreported edges are masked, never encoded as measured zero associations.
    from figure_reference import plot_signed_network
    network=pd.DataFrame([dict(record_type='node',node=k,order=i,a=None,b=None,r=None) for i,k in enumerate(['a','b','c'])]+[dict(record_type='edge',node=None,order=None,a='a',b='b',r=.6)])
    f=plot_signed_network(network,view='matrix');arr=f.axes[0].images[0].get_array()
    assert np.ma.getmaskarray(arr).sum()==7;assert np.count_nonzero(~np.ma.getmaskarray(arr))==2;plt.close(f)
    from figure_network_extensions import plot_weighted_chord
    chord=pd.DataFrame({'source':['A'],'target':['B'],'weight':[10.]})
    f=plot_weighted_chord(chord,theme,weight_label='Supplied count',order=['A','B'])
    ribbon=f.axes[0].patches[-1].get_path().vertices
    assert len(ribbon)>100 and np.ptp(ribbon[:,0])>1.8,'two-sector ribbon collapsed instead of following its allocated arcs'
    plt.close(f)
    # Registered palette panels must use named project categories rather than
    # old hard-coded, almost indistinguishable blue profiles.
    from figure_palette_applications import plot_palette_panel
    d=pd.DataFrame([dict(panel='p',record_type='radar',group=g,category=k,value=v) for g,v in [('A',.3),('B',.6)] for k in ['x','y','z']])
    spec=dict(id='p',type='radar',title='Profiles',radial_limits=[0,1])
    f=render_with_theme(plot_palette_panel,d,dict(palette_name='package_editorial',panel_spec=spec),theme)
    assert f.axes[0].lines[0].get_color()!=f.axes[0].lines[1].get_color();assert f.axes[0].lines[0].get_linestyle()!=f.axes[0].lines[1].get_linestyle();plt.close(f)
    # The portable specs must replay through the same public entry point, not
    # just be valid JSON next to an unrelated picture.
    from render_frozen_table import load_table,render
    from figure_design import geometry_signature
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        p=Path(temporary)/'round-trip.tsv';p.write_text('cell_id\tx\ty\tfeature\tvalue\n001\t1.2345678901234567\t0.0\tF\t1.0\n')
        parsed=load_table(p,'figure_publication.plot_feature_facets',{},['x','y','value'])
        assert parsed.cell_id.iloc[0]=='001' and parsed.x.iloc[0]==float('1.2345678901234567')
    base=ROOT/'examples/source-v093/single';rows={r['id']:r for r in json.loads((base/'manifest.json').read_text())['records']}
    replayed=[]
    for key in ['dot-matrix__identity-support','roc__supplied-bounds','precision-recall__supplied-bounds','network','chord','radar','object-schematic','reference-aligned-tracks','feature-embedding','pathway-quantity-overlay']:
        folder=base/key;spec=json.loads((folder/'example.spec.json').read_text())
        d=load_table(folder/spec['input']['path'],spec['renderer'],spec['parameters'],spec['input']['numeric_columns'])
        before=table_bytes(d);f,_=render(spec['renderer'],d,spec['parameters'],spec['theme'],layout=spec.get('layout'))
        f.canvas.draw() # export geometry includes deferred colourbar/axis paths
        assert table_bytes(d)==before
        assert geometry_signature(f)==rows[key]['quantitative_geometry_sha256'],'Portable replay changed geometry: '+key
        if key in ['feature-embedding','object-schematic']:
            ratio=f._responsive_canvas_aspect;apply_native_layout(f,{'width_inches':9.6})
            assert abs(f.get_figwidth()/f.get_figheight()-ratio)<1e-10,'Width-only request stretched fixed-aspect content'
        plt.close(f);replayed.append(key)
    print(json.dumps(dict(status='SOURCE_RUNTIME_PASS',checks=['long-label dot guides','true zero area','complete support map','named PR bounds','step semantics','idempotent guide hierarchy','masked unreported edges','circular sector ribbon','named radar identities','portable exact-geometry replay','fixed-aspect width response'],portable_replays=replayed,aesthetic_acceptance=False)))


if __name__=='__main__':main()
