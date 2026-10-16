"""Concrete layout regressions found by the full-gallery visual audit."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np,pandas as pd
    from figure_core import plot_curve,plot_qc,table_bytes
    from figure_workbench.responsive import canvas_budget
    from figure_layout import optimize_guide_layout
    from figure_design import geometry_signature
    from project_theme import create_theme,group_palette,validate_theme
    checks=[]
    assert canvas_budget(np.float64(7.2),np.float64(4))==(7.2,4.)
    names=['Model '+str(i) for i in range(9)];theme=create_theme('layout-regression','package_editorial',{v:i for i,v in enumerate(names)},font_family='DejaVu Sans')
    palette={v:theme['palette_colors'][i] for i,v in enumerate(names)}
    extended=copy.deepcopy(theme);extended['category_colors']={'Identity '+str(i):'#'+format(i*1237+256,'06x') for i in range(70)}
    chosen=['Identity 61','Identity 2'];assert group_palette(extended,chosen)=={k:extended['category_colors'][k] for k in chosen}
    try:group_palette(extended,['Unregistered'])
    except ValueError:pass
    else:raise AssertionError('Unknown category silently cycled')
    bad=copy.deepcopy(extended);bad['category_colors']['Identity 1']='url(remote)'
    try:validate_theme(bad)
    except ValueError:pass
    else:raise AssertionError('Unsafe explicit colour accepted')
    checks.append('Large named colour maps preserve exact identities without cycling and reject unknown identities or non-Hex values')
    data=pd.DataFrame([dict(model=n,x=x,y=x**(.5+i*.03)) for i,n in enumerate(names) for x in np.linspace(0,1,11)])
    before=table_bytes(data);fig=plot_curve(data,palette=palette,ncols=4)
    assert table_bytes(data)==before and len(fig.axes)==9
    for a,n in zip(fig.axes,names):
        q=data[data.model==n];assert any(np.array_equal(line.get_xdata(),q.x) and np.array_equal(line.get_ydata(),q.y) for line in a.lines)
    last=fig.axes[-1].get_position();firstrow=fig.axes[:4];centre=(firstrow[0].get_position().x0+firstrow[-1].get_position().x1)/2
    assert abs((last.x0+last.x1)/2-centre)<.005;plt.close(fig)
    try:plot_curve(data,palette=palette,mode='overlay')
    except ValueError:pass
    else:raise AssertionError('Crowded overlay accepted')
    checks.append('Nine-model facets retain exact curves and centre the incomplete final row; explicit crowded overlay is rejected')
    qc=pd.DataFrame([dict(cell_id='Cell'+str(c),sample='Sample'+str(c%2),metric=m,value=float(c+1+j)) for j,m in enumerate(['genes','umis','mito']) for c in range(12)])
    labels={'genes':'Detected genes','umis':'UMIs','mito':'Mitochondrial fraction (%)'}
    before=table_bytes(qc);fig=plot_qc(qc,y_label='QC',metric_field='metric',metric_labels=labels,ncols=2)
    assert len(fig.axes)==3 and table_bytes(qc)==before;plt.close(fig)
    for invalid,ls in [(pd.concat([qc,qc.iloc[:1]]),labels),(qc,{'genes':'Genes'})]:
        try:plot_qc(invalid,y_label='QC',metric_field='metric',metric_labels=ls)
        except ValueError:pass
        else:raise AssertionError('Ambiguous QC observations or units accepted')
    checks.append('Multi-metric QC preserves all observations and rejects duplicate identities or missing metric units')
    d=pd.DataFrame(dict(model=['M']*3,x=[0,.5,1],y=[0,.7,1]));fig=plot_curve(d,palette={'M':'#326B8D'})
    fig.canvas.draw();a=fig.axes[0];bb=a.xaxis.label.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    note=fig.text((bb.x0+bb.x1)/2,(bb.y0+bb.y1)/2,'A complete source caption',ha='center',fontsize=10)
    before=geometry_signature(fig);optimize_guide_layout(fig);assert before==geometry_signature(fig)
    fig.canvas.draw();r=fig.canvas.get_renderer();assert not note.get_window_extent(r).overlaps(a.xaxis.label.get_window_extent(r))
    size=fig.get_size_inches().copy();optimize_guide_layout(fig);np.testing.assert_allclose(fig.get_size_inches(),size,atol=.02);plt.close(fig)
    checks.append('Measured caption lane resolves a real x-label collision, preserves quantities and is idempotent')
    from figure_publication import plot_aligned_matrix
    from indexed_alignment import audit_index_alignment
    matrix=pd.DataFrame([dict(feature='F'+str(i),sample='S'+str(j),value=(i-j)/4,feature_block='A' if i<2 else 'B',row_count=i+2) for i in range(4) for j in range(4)])
    fig=plot_aligned_matrix(matrix,value_label='Frozen score',limits=[-1,1],block_palette={'A':'#228B8D','B':'#AA8899'})
    before=geometry_signature(fig);optimize_guide_layout(fig);assert geometry_signature(fig)==before
    assert not audit_index_alignment(fig)['issues']
    main=fig._index_bindings[0]['main'];side=fig._index_bindings[-1]['track'];fig.canvas.draw()
    assert (side.get_position().x0-main.get_position().x1)*fig.get_figwidth()>=.27
    assert {t.get_text() for l in fig.legends for t in l.get_texts()}=={'A','B'};plt.close(fig)
    checks.append('Right count tracks keep a physical gap after reflow, exact row alignment, and a complete categorical strip key')
    import tempfile
    sys.path.insert(0,str(ROOT/'tools'))
    from build_transcriptomic_study_examples import prepare
    from figure_study_overview import plot_transcriptomic_overview
    from figure_workbench.pipeline import project_appearance
    with tempfile.TemporaryDirectory() as temporary:
        fixture=Path(temporary)/'fixture';prepare(fixture)
        spec=json.loads((fixture/'SingleCellMain/SingleCellMain.spec.json').read_text(encoding='utf8'))
        data=pd.read_csv(fixture/'SingleCellMain/SingleCellMain.tsv',sep='\t')
        fig=plot_transcriptomic_overview(data,project_appearance(spec),**dict(spec['parameters'],ncols=1))
        optimize_guide_layout(fig);fig.canvas.draw();renderer=fig.canvas.get_renderer()
        headings=[t for t in fig.texts if getattr(t,'_panel_heading',False)]
        assert len(headings)==4
        for heading in headings:
            box=heading.get_window_extent(renderer)
            for ax in fig.axes:
                tight=ax.get_tightbbox(renderer,bbox_extra_artists=[])
                assert tight is None or not box.overlaps(tight),'Panel heading collided with a complete axis guide'
        plt.close(fig)
    checks.append('Four-row single-cell main figure retains all headings above their panels without composition-label collisions')
    assert not plt.get_fignums()
    print(json.dumps(dict(status='LAYOUT_DEPTH_REGRESSIONS_PASS',checks=checks,visual_acceptance=False)))


if __name__=='__main__':main()
