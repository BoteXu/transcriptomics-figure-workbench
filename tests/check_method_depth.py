"""Verify complete frozen method semantics, conservation and honest layout controls."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from figure_workbench.contracts import read_json,make_plan
    from figure_workbench.pipeline import project_appearance
    from render_frozen_table import load_table,render
    from figure_wgcna_views import plot_wgcna_view
    from figure_lineage_views import plot_lineage_view
    def get(root,k):
        p=SKILL/('assets/'+root+'-gallery')/k/'input/example.spec.json';s=read_json(p);return s,load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
    def bad(fn):
        try:fn()
        except ValueError:return
        finally:plt.close('all')
        raise AssertionError('Invalid scientific/drawing input accepted')
    s,d=get('wgcna','WGCNA_ModuleTrait');params=s['parameters'];theme=project_appearance(s);x=d.copy();x.loc[x.index[0],'n']=25;bad(lambda:plot_wgcna_view(x,theme,**params));bad(lambda:plot_wgcna_view(d,theme,**dict(params,module_order=params['module_order'][:-1])))
    s,d=get('wgcna','WGCNA_ModuleTree');x=d.copy();x.loc[x.record_type=='merge','left']='missing';bad(lambda:plot_wgcna_view(x,project_appearance(s),**s['parameters']))
    s,d=get('wgcna','WGCNA_TOM');x=d.copy();x.loc[x.index[1],'value']+=.01;bad(lambda:plot_wgcna_view(x,project_appearance(s),**s['parameters']))
    s,d=get('wgcna','hdWGCNA_ModuleActivity');x=d.copy();x.loc[x.index[0],'x']+=.1;bad(lambda:plot_wgcna_view(x,project_appearance(s),**s['parameters']))
    s,d=get('wgcna','hdWGCNA_MetacellQC');x=d.copy();x.loc[x.index[0],'n_shared']=1000;bad(lambda:plot_wgcna_view(x,project_appearance(s),**s['parameters']))
    s,d=get('wgcna','WGCNA_SoftPower');f,audit=render(s['renderer'],d,dict(s['parameters'],columns='auto'),project_appearance(s),layout={'columns':1});assert len(f.axes)==2 and f.axes[0].get_position().y0>f.axes[1].get_position().y0;plt.close(f)
    bad(lambda:plot_wgcna_view(d,project_appearance(s),**dict(s['parameters'],columns=3)))
    s,d=get('method-depth','ClusterFlow_2Column');x=d.copy();x.loc[x.record_type=='edge','n']+=1;bad(lambda:plot_lineage_view(x,project_appearance(s),**s['parameters']))
    s,d=get('method-depth','Trajectory_2Column');bad(lambda:plot_lineage_view(d,project_appearance(s),**dict(s['parameters'],root_id='unknown')))
    from figure_workbench.views import chapter_views,view_template
    import tempfile
    assert len(chapter_views())>=130 and len(chapter_views('bulk.wgcna'))>=12
    with tempfile.TemporaryDirectory() as tmp:
        for r in [next(r for r in chapter_views('bulk.programs') if r.get('panel_id')),next(r for r in chapter_views() if r['id']=='WGCNA_ModuleTrait')]:
            out=Path(tmp)/r['id'];view_template(r['id'],out);make_plan(read_json(out/'example.spec.json'),out)
    print(json.dumps(dict(status='METHOD_DEPTH_CONTRACTS_PASS',checks=['effective n','complete module order','valid frozen tree','symmetric TOM','exact shared activity coordinates','metacell donor nesting','custom one-column dual diagnostics','complete flow conservation','explicit root','portable independent view export'],scientific_acceptance=False)))
if __name__=='__main__':main()
