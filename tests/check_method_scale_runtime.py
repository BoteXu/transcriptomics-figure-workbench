"""Real drawing regressions exposed by varied synthetic scopes; no inference."""
import copy
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';G=S/'assets/method-scale-gallery'
sys.path.insert(0,str(S/'scripts'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from render_frozen_table import load_table,render
from figure_design import geometry_signature
from figure_layout import optimize_guide_layout

def draw(method,variant):
    p=G/('Scale_'+method+'_'+variant)/'example.spec.json';spec=json.loads(p.read_text('utf8'));d=load_table(p.parent/spec['input']['path'],spec['renderer'],spec['parameters'],spec['input']['numeric_columns']);before=d.copy(deep=True)
    fig,audit=render(spec['renderer'],d,spec['parameters'],spec['theme'],layout=spec.get('layout'))
    import pandas as pd
    pd.testing.assert_frame_equal(d,before)
    assert not audit['issues'];return fig,d,spec

def main():
    checked=0
    for variant in ['Small','Large']:
        f,d,s=draw('H10_split_metric_matrix',variant)
        assert len(f.axes[0].patches)==d.row_id.nunique()*(1+2*d.column_id.nunique())
        assert len(set(s['parameters']['row_slots'].values()))<=d.row_id.nunique();plt.close(f);checked+=1
    f,d,s=draw('H21_aligned_views','Custom')
    links=[a for a in f.artists if (a.get_gid() or '').startswith('object-link:')]
    assert len(links)==d.object_id.nunique()*(d.view.nunique()-1)
    assert f._omics_spec['columns']==1 and f._omics_spec['rows']==3
    assert all(a.axesA is not a.axesB for a in links);plt.close(f);checked+=1
    f,d,s=draw('H18_association_matrix','Large')
    values=d[d.status=='estimable'];displayed=[t.get_text() for a in f.axes for t in a.texts]
    assert sum(t.startswith('n=') for t in displayed)==len(values);plt.close(f);checked+=1
    for variant in ['Small','Medium','Large']:
        f,d,s=draw('H23_locus_tracks',variant)
        assert s['parameters']['ld_reference'] in set(d.loc[d.record_type=='association','variant_id']);plt.close(f);checked+=1
        f,d,s=draw('H27_running_enrichment',variant)
        assert int((d.record_type=='hit').sum())==80 and int((d.record_type=='metric').sum())==300
        assert sum(len(c.get_segments()) for c in f.axes[1].collections)==80;plt.close(f);checked+=1
    f,d,s=draw('H36_multiclass_contributions','Small')
    assert f._responsive_facets['panels']==d['class'].nunique()+1
    signature=geometry_signature(f);optimize_guide_layout(f);assert signature==geometry_signature(f);plt.close(f);checked+=1
    f,d,s=draw('H29_process_dashboard','Custom')
    assert f._responsive_facets['columns']==2 and len(f.axes)>=12
    body=next(a for a in f.axes if a.get_title(loc='left').startswith('A  Supplied process geometry'))
    assert sum(p.get_zorder()==4 for p in body.patches)==int(((d.record_type=='node')&(d.group=='Paper')).sum())
    assert all(t.get_zorder()==5 for t in body.texts)
    assert f._omics_spec['analysis'].startswith('none');plt.close(f);checked+=1
    f,d,s=draw('H39_activity_dashboard','Large')
    assert len(f.axes[0].get_yticklabels())==150 and f.get_figwidth()*f.get_figheight()*300**2<=40e6
    density=[a for a in f.axes if a.get_title(loc='left').startswith('Module ')]
    assert len(density)==5 and len({a.get_ylim() for a in density})==1
    assert all(len(a.get_yticks())==2 and a.get_yticks()[0]==0 for a in density)
    assert density[0].get_ylabel()=='Supplied density';plt.close(f);checked+=1
    f,d,s=draw('H28_contour_field','Medium')
    labels=[t for t in f.axes[0].texts if t.get_text().replace('-','',1).replace('.','',1).isdigit()]
    assert labels and all(not t.get_clip_on() for t in labels);plt.close(f);checked+=1
    heights=[]
    for variant in ['Small','Large']:
        f,d,s=draw('H41_facet_bubble_matrix',variant);heights.append(f.get_figheight());plt.close(f);checked+=1
    assert heights[0]<heights[1]
    f,d,s=draw('H37_embedding_atlas','Large')
    ring=next(a for a in f.axes if a.get_title(loc='left').startswith('A  Embedding'))
    numbers=[t for t in ring.texts if t.get_text().isdigit()]
    assert len(numbers)==70
    radii={round(np.hypot(*t.get_position()),2) for t in numbers}
    assert radii=={.87,.96};plt.close(f);checked+=1
    assert not plt.get_fignums()
    print(json.dumps(dict(state='SCALE_EXPOSED_DRAWING_REGRESSIONS_PASS',cases=checked,scientific_inference=False)))

if __name__=='__main__':main()
