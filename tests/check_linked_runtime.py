"""Bounded synthetic contracts, shared IDs and replay of linked displays."""
from pathlib import Path
import sys,json,copy,tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from linked_evidence_fixture import linked_cases
from render_frozen_table import render,load_table,ADAPTERS
from project_theme import create_theme
from check_increment_runtime import geometry

def reject(c,data=None,params=None):
    try:fig,_=render(c['adapter'],c['data'] if data is None else data,c['params'] if params is None else params,THEME)
    except (ValueError,KeyError):plt.close('all');return
    plt.close(fig);raise AssertionError('Invalid linked-display contract accepted')

THEME=create_theme('linked-test','card_06',{f'G{i+1}':i for i in range(7)},font_family='DejaVu Sans')
def main():
    cases=linked_cases();assert len(cases)==14
    d=cases['E34']['data'];m=d[d.record_type=='member'];t=d[d.record_type=='term'];e=d[d.record_type=='link']
    assert set(m.member_id)==set(cases['c37_sets']['data'].object_id)
    counts=e.groupby('term_id').member_id.nunique();np.testing.assert_allclose(t['count'],counts.loc[t.term_id]);np.testing.assert_allclose(t.ratio,t['count']/20)
    bars=cases['c37_terms']['data'].groupby('object_id').value.sum();np.testing.assert_allclose(-np.log10(t.padj),bars.loc[t.term_id])
    full=cases['c37_network']['data'];local=cases['c37_local']['data'];selected=set(local[local.record_type=='node'].node_id)
    expected=full[((full.record_type=='node')&full.node_id.isin(selected))|((full.record_type=='edge')&full.source.isin(selected)&full.target.isin(selected))]
    pd.testing.assert_frame_equal(expected,local)
    pd.testing.assert_frame_equal(cases['E36']['data'],cases['E37']['data'])
    leaves=cases['E36']['data'];leaves=leaves[leaves.record_type=='leaf'];scores=cases['c38_scores']['data']
    assert leaves.node_id.tolist()==scores.unit_id.tolist();assert leaves.group.tolist()==scores.group.tolist()
    matrix=cases['c40_matrix']['data'];assert set(leaves.node_id)==set(matrix.feature)==set(matrix['sample'])==set(cases['c39_stack']['data'].object_id)
    assert set(leaves.group)==set(cases['E35']['data'].row_id)==set(cases['c40_network']['data'].query("record_type=='node'").node_id)
    bad=d.copy();bad.loc[bad.record_type=='term','count']+=1;reject(cases['E34'],bad)
    reject(cases['E34'],pd.concat([d,e.iloc[:1]],ignore_index=True))
    bad=d.copy();bad.loc[bad.record_type=='link','member_id']='unknown';reject(cases['E34'],bad)
    bad=d.copy();bad.loc[bad.record_type=='term','padj']=0;reject(cases['E34'],bad)
    reject(cases['E35'],cases['E35']['data'].iloc[1:])
    bad=cases['E35']['data'].copy();bad.loc[0,'pvalue']=2;reject(cases['E35'],bad)
    params=copy.deepcopy(cases['E36']['params']);params['leaf_order'][1],params['leaf_order'][8]=params['leaf_order'][8],params['leaf_order'][1];reject(cases['E36'],params=params)
    bad=cases['E37']['data'].copy();bad.loc[0,'area_value']=1.1;reject(cases['E37'],bad)
    bad=cases['c39_stack']['data'].copy();bad.loc[0,'value']=-1;reject(cases['c39_stack'],bad)
    reject(cases['c38_fit'],cases['c38_fit']['data'].iloc[::-1])
    alternate=create_theme('linked-test','card_07',THEME['group_slots'],font_family='DejaVu Serif')
    with tempfile.TemporaryDirectory(prefix='linked-fixtures-') as folder:
        for id_,c in cases.items():
            before=c['data'].copy(deep=True);fig,audit=render(c['adapter'],c['data'],c['params'],THEME);assert not audit['issues'];g=geometry(fig);plt.close(fig)
            fig,_=render(c['adapter'],c['data'],c['params'],alternate);assert geometry(fig)==g,id_;plt.close(fig)
            pd.testing.assert_frame_equal(before,c['data'])
            p=Path(folder)/(id_+'.tsv');c['data'].to_csv(p,sep='\t',index=False)
            table=load_table(p,c['adapter'],c['params']);fig,audit=render(c['adapter'],table,c['params'],THEME);assert not audit['issues'];plt.close(fig)
            print(id_+' linked contracts/theme/replay PASS',flush=True)
    print(json.dumps(dict(status='LINKED_RUNTIME_PASS',fixtures=14,negative_contracts=10,crosspanel_checks=8,theme_geometry_checks=14,fixed_replays=14,scientific_analysis=False)))
if __name__=='__main__':main()
