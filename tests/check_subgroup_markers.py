"""Scientific identity and full-background retention gates for marker pages."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path[:0]=[str(ROOT/'tools'),str(SKILL/'scripts')]
def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from figure_annotation_views import plot_annotation_evidence
    from figure_workbench.pipeline import project_appearance
    from figure_workbench.quality import print_readability
    from render_frozen_table import load_table,render
    base=SKILL/'assets/subgroup-gallery'
    def bad(d,p,t):
        try:plot_annotation_evidence(d,t,**p)
        except ValueError:return
        finally:plt.close('all')
        raise AssertionError('Misassigned or incomplete marker evidence accepted')
    for row in json.loads((base/'manifest.json').read_text(encoding='utf8'))['records']:
        p=base/row['assets']['spec'];s=json.loads(p.read_text(encoding='utf8'));t=project_appearance(s)
        d=load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
        f,a=render(s['renderer'],d,s['parameters'],t)
        assert print_readability(f,s['export'])['state']=='MEASUREMENT_PASS'
        assert len(f.axes)==len(s['parameters']['marker_order'])+3
        maps=f.axes[2:-1];assert all(len(ax.collections[0].get_offsets())==900 for ax in maps)
        assert len({tuple(ax.get_xlim()) for ax in maps})==len({tuple(ax.get_ylim()) for ax in maps})==1
        assert all(tuple(ax.collections[0].get_clim())==tuple(s['parameters']['expression_limits']) for ax in maps)
        f.canvas.draw();renderer=f.canvas.get_renderer()
        headers=[t.get_window_extent(renderer) for t in f.texts[:2]]
        headings=[t.get_window_extent(renderer) for ax in f.axes for t in ax.texts if getattr(t,'_panel_heading',False)]
        assert all(not a.overlaps(b) for a in headers for b in headings),'Header collides with panel headings'
        assert not f.legends[0].get_window_extent(renderer).overlaps(f.axes[-1].get_tightbbox(renderer)),'Detection key collides with expression key'
        plt.close(f)
        x=d.copy();x.loc[x.record_type=='marker_dot','feature_group']='Wrong identity';bad(x,s['parameters'],t)
        x=d.drop(d[d.record_type=='feature_map'].index[0]);bad(x,s['parameters'],t)
        x=d.copy();x.loc[x[x.record_type=='feature_map'].index[0],'x']+=.01;bad(x,s['parameters'],t)
        x=d.copy();x.loc[x[x.record_type=='marker_dot'].index[0],'fraction']=1.01;bad(x,s['parameters'],t)
        if row['id']=='Subgroup_01':
            f=plot_annotation_evidence(d,t,**dict(s['parameters'],ncols='auto',nrows=1))
            assert f._omics_spec['layout']=={'rows':1,'columns':6},'Explicit row request was ignored'
            plt.close(f)
    print(json.dumps(dict(status='SUBGROUP_MARKER_GATES_PASS',figures=8,
        checks=['correct identity assignment','all background cells','unchanged coordinates','shared explicit colour limits','complete comparison identities','detection fraction bounds','2/4/8 markers and 1/2/3 columns'],scientific_acceptance=False)))
if __name__=='__main__':main()
