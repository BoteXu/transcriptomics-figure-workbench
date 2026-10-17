"""Rejection, conservation, exact-source and portable multi-view acceptance."""
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from figure_workbench.contracts import read_json,make_plan
    from figure_workbench.pipeline import project_appearance
    from figure_workbench.analysis_suites import analysis_library,analysis_suite,named_analysis_chapters
    from render_frozen_table import load_table,render
    from figure_coexpression_evidence import plot_coexpression_evidence,MODES
    gallery=SKILL/'assets/analysis-gallery';m=read_json(gallery/'manifest.json');assert len(m['records'])==43
    modes=set();by={r['id']:r for r in m['records']}
    for row in m['records']:
        assert row['analysis_performed'] is False and row['scientific_acceptance'] is False
        for key,digest in row['sha256'].items():assert hashlib.sha256((gallery/row['assets'][key]).read_bytes()).hexdigest()==digest
        assert row['review']['state']=='SCREEN_REVIEWED' and row['review']['png_sha256']==row['sha256']['png']
        assert row['readability']['state']=='MEASUREMENT_PASS'
        p=gallery/row['assets']['spec'];s=read_json(p);make_plan(s,p.parent)
        if s['renderer'].startswith('figure_coexpression_evidence.'):modes.add(s['parameters']['mode'])
    assert modes==set(MODES)
    def get(key):
        p=gallery/by[key]['assets']['spec'];s=read_json(p)
        return s,load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
    def bad(s,d,params=None):
        try:plot_coexpression_evidence(d,project_appearance(s),**(params or s['parameters']))
        except ValueError:return
        finally:plt.close('all')
        raise AssertionError('Invalid scientific display accepted')
    s,d=get('Hubs_CoexpressionNeighborhoods');x=d.copy();x.loc[x.record_type=='edge','target']='UNKNOWN';bad(s,x)
    bad(s,d,dict(s['parameters'],edge_semantics=None));bad(s,d,dict(s['parameters'],label_genes=['UNKNOWN']))
    s,d=get('Modules_CrossCohortOverlap');bad(s,d.iloc[:-1]);x=d.copy();x.loc[x.index[0],'count']=-1;bad(s,x)
    s,d=get('Eigengenes_DonorContrasts');x=d.copy();x.loc[x.index[0],'n']=25;bad(s,x);x=d.copy();x.loc[x.index[0],'lower']=9;bad(s,x);bad(s,d.iloc[:-1])
    s,d=get('Eigengenes_DonorRainclouds');p=copy.deepcopy(s['parameters']);p['cloud_shapes']['M1']['Control']['n']=900;bad(s,d,p)
    p=copy.deepcopy(s['parameters']);p['cloud_shapes']['M1']['Control']={};bad(s,d,p)
    s,d=get('TOM_AlignedHierarchy');x=d.copy();at=x.index[(x.record_type=='matrix')&(x.a!=x.b)][0];x.loc[at,'value']+=.02;bad(s,x)
    s,d=get('Modules_FunctionAndGeneSupport');x=d.copy();x.loc[x.index[0],'overlap']=99999;bad(s,x)
    x=d.copy();x.loc[x.index[0],'overlap']=0
    f=plot_coexpression_evidence(x,project_appearance(s),**s['parameters']);assert f.axes[0].collections[0].get_sizes()[0]==0;plt.close(f)
    s,d=get('Modules_ExpressionAndEigengenes');bad(s,d[d.unit!='D01'].iloc[:-1])
    s,d=get('Modules_SensitivityAndStability');bad(s,d.iloc[:-1])
    s,d=get('Preservation_Attributes');bad(s,d.iloc[:-1])
    s,d=get('Modules_BranchDynamics');original=d.copy(deep=True)
    f,audit=render(s['renderer'],d,s['parameters'],project_appearance(s),layout={'columns':2});assert not audit['issues']
    assert len({tuple(a.get_ylim()) for a in f.axes})==1 and d.equals(original);plt.close(f)
    s,d=get('TOM_AlignedHierarchy');f,audit=render(s['renderer'],d,s['parameters'],project_appearance(s));heat=f.axes[-2] if len(f.axes)==5 else f.axes[3]
    # Actual axes share one matrix coordinate lane; no faraway annotation strips.
    assert abs(f.axes[1].get_position().x0-f.axes[3].get_position().x0)<.001
    assert 0<f.axes[3].get_position().x0-f.axes[2].get_position().x1<.02;plt.close(f)
    suites=analysis_library();assert len(suites)==58 and len(analysis_library('WGCNA'))==2
    assert named_analysis_chapters('single_cell','整套 hdWGCNA 图')==['single_cell.hdwgcna']
    assert named_analysis_chapters('bulk','完整的 WGCNA 和 GSVA 图')==['bulk.wgcna','bulk.gsva']
    assert not named_analysis_chapters('bulk','完整的 GSEA 和常规图')
    from figure_workbench.study import study_plan
    scope=dict(schema_version=1,assay='bulk',title='Synthetic route check',contrast='A versus B',independent_unit='donor',denominator='explicit synthetic scope',frozen_results=True,upstream_qc='reviewed',results=[])
    routed=study_plan(scope,'完整的 WGCNA 和 GSVA 图',ROOT)
    assert routed['state']=='ANALYSIS_SUITE_ROUTE_REQUIRED' and not routed['panels'] and routed['analysis_suites']==['bulk.wgcna','bulk.gsva']
    from figure_workbench.registry import source_identity
    assert 'references/analysis-suites.json' in source_identity()
    w=next(r for r in suites if r['id']=='bulk.wgcna');assert len(w['primary_views'])>=20
    assert 'WGCNA_EigengeneProfiles' not in w['primary_views'] and 'Eigengenes_DonorRainclouds' in w['primary_views']
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)/'suite';receipt=analysis_suite('bulk.wgcna',out);manifest=read_json(out/'manifest.json')
        assert receipt['figures']==len(w['primary_views'])==len(manifest['records'])
        for row in manifest['records']:
            p=out/row['spec'];make_plan(read_json(p),p.parent)
    print(json.dumps(dict(state='ANALYSIS_COMPLETION_PASS',actual_reviewed_pages=43,modes=len(MODES),chapters=58,rejection_and_semantic_checks=True,analysis_performed=False)))

if __name__=='__main__':main()
