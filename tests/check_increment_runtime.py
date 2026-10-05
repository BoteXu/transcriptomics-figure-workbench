"""Bounded synthetic checks of preserved identities, drawing contracts and theme replacement.

Run explicitly in an existing plotting environment. No scientific model is fitted.
"""
from pathlib import Path
import sys,json,copy,tempfile,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from method_extension_fixture import fixture_cases,draw_case
from multiview_fixture import multiview_cases
from render_frozen_table import ADAPTERS,load_table,render
from project_theme import create_theme

def geometry(fig):
    out=[]
    for ax in fig.axes:
        out.append((ax.get_xscale(),ax.get_yscale(),tuple(ax.get_xlim()),tuple(ax.get_ylim())))
        for line in ax.lines:out.append(('line',np.asarray(line.get_xydata()).tolist()))
        for c in ax.collections:
            out.append(('offsets',np.asarray(c.get_offsets()).tolist()))
            if hasattr(c,'get_sizes'):out.append(('sizes',np.asarray(c.get_sizes()).tolist()))
            if hasattr(c,'get_segments'):out.append(('segments',[np.asarray(x).tolist() for x in c.get_segments()]))
            if getattr(c,'norm',None) is not None:out.append(('limits',c.norm.vmin,c.norm.vmax))
        for im in ax.images:out.append(('image',np.asarray(im.get_array()).tolist(),im.norm.vmin,im.norm.vmax))
        for p in ax.patches:out.append(('patch',p.get_path().vertices.tolist(),p.get_patch_transform().get_matrix().tolist()))
    return json.dumps(out,sort_keys=True,allow_nan=True)

def reject(case,theme,data=None,params=None):
    c=copy.copy(case);c['data']=case['data'].copy() if data is None else data;c['params']=dict(case['params']) if params is None else params
    try:fig=draw_case(c,theme)
    except (ValueError,KeyError):plt.close('all');return
    plt.close(fig);raise AssertionError('Invalid scientific contract accepted: '+case['title'])

def main():
    theme,a=fixture_cases();other,b=multiview_cases();assert theme==other;cases={**a,**b};assert len(cases)==52
    try:font_manager.findfont(font_manager.FontProperties(family=theme['font_family']),fallback_to_default=False)
    except ValueError:theme=create_theme(theme['project_id'],theme['palette_name'],theme['group_slots'],font_family='DejaVu Sans')
    # Same observations and the same members must agree across alternative geometries.
    d=a['E08']['data'];membership=set(zip(d.gene_id,d.term_id))
    m=a['E09']['data'];assert int(m.value.sum())==42==len(membership)
    assert membership==set(zip(m.loc[m.value==1,'feature'],m.loc[m.value==1,'sample']))
    x=a['E24']['data'].set_index('unit_id');y=a['E14']['data'].set_index('object_id')
    np.testing.assert_allclose((x.x+x.y)/2,y['mean']);np.testing.assert_allclose(x.y-x.x,y.difference)
    for id_ in ['E18','E26']:
        q=a[id_]['data'];q=q[q.record_type=='point'] if 'record_type' in q else q
        key=next(k for k in ['unit_id','object_id','cell_id'] if k in q);key0='cell_id'
        p=a['E25']['data'].set_index(key0)[['x','y']];q=q.drop_duplicates(key).set_index(key)[['x','y']].loc[p.index];np.testing.assert_allclose(p,q)
    overview=b['E28']['data'].set_index('variant_id');locus=b['E29']['data'];locus=locus[locus.record_type=='association'].set_index('variant_id')
    np.testing.assert_allclose(overview.loc[locus.index,['position','pvalue']],locus[['position','pvalue']])
    f=b['E30b']['data'];funnel=b['E30']['data'];funnel=funnel[funnel.record_type=='study'];np.testing.assert_allclose(f.estimate,funnel.estimate)
    pd.testing.assert_frame_equal(b['E33a']['data'],b['E33b']['data'])
    ends=a['E16']['data'];ends=ends[ends.record_type=='interval']
    risk=a['E15']['data'];risk=risk[risk.record_type=='risk']
    for row in risk.itertuples():assert row.at_risk==int(((ends.group==row.group)&(ends.end>row.time)).sum())
    diagnostic=b['M11a']['data']
    for i in 'bcd':pd.testing.assert_frame_equal(diagnostic,b['M11'+i]['data'])
    np.testing.assert_allclose(np.sort(diagnostic.standard_residual),diagnostic.ordered_residual)
    # Invalid values or contradictory semantics cannot be fixed silently for aesthetics.
    q=b['E27']['data'].copy();q.loc[0,'A']+=.1;reject(b['E27'],theme,q)
    q=b['E28']['data'].copy();q.loc[0,'pvalue']=0;reject(b['E28'],theme,q)
    q=b['M01']['data'].copy();q.loc[0,'status']='Both' if q.loc[0,'status']!='Both' else 'Neither';reject(b['M01'],theme,q)
    q=b['M04']['data'].iloc[1:].copy();reject(b['M04'],theme,q)
    q=b['M05']['data'].copy();q.loc[0,'x']=2;reject(b['M05'],theme,q)
    q=b['M06']['data'].copy();q.loc[0,'intensity']=-1;reject(b['M06'],theme,q)
    q=b['M11b']['data'].copy();q.loc[0,'ordered_residual']=9;reject(b['M11b'],theme,q)
    q=b['E32']['data'].copy();q.loc[0,'lower']=q.loc[0,'upper']+1;reject(b['E32'],theme,q)
    q=b['E31']['data'].copy();q.loc[q.node_id=='A1','x1']=1;reject(b['E31'],theme,q)
    params=dict(a['E01']['params']);params['column_order']=['wrong'];reject(a['E01'],theme,params=params)
    alternate=create_theme(theme['project_id'],'card_07',theme['group_slots'],font_family='DejaVu Serif')
    font_manager.findfont(font_manager.FontProperties(family=alternate['font_family']),fallback_to_default=False)
    with tempfile.TemporaryDirectory(prefix='figure-runtime-') as folder:
        for id_,c in cases.items():
            before=c['data'].copy(deep=True);fig=draw_case(c,theme);g=geometry(fig);plt.close(fig)
            fig=draw_case(c,alternate);assert geometry(fig)==g,id_+' color/font replacement changed data geometry';plt.close(fig)
            pd.testing.assert_frame_equal(before,c['data'])
            adapters=[key for key,(fn,_,_) in ADAPTERS.items() if fn is c['function']]
            assert len(adapters)==1,(id_,adapters)
            adapter=adapters[0];path=Path(folder)/(id_+'.tsv');c['data'].to_csv(path,sep='\t',index=False,lineterminator='\n')
            table=load_table(path,adapter,c['params']);fig,audit=render(adapter,table,c['params'],theme);assert not audit['issues'];plt.close(fig)
            print(id_+' theme geometry and fixed-table replay PASS',flush=True)
        idpath=Path(folder)/'ids.tsv';idpath.write_text('unit_id\tgroup\tx\ty\n001\tG1\t1\t2\nNA\tG7\t3\t4\n',encoding='utf8')
        table=load_table(idpath,'xy_points',{});assert table.unit_id.tolist()==['001','NA']
    try:render('arbitrary_exec',pd.DataFrame(),{},theme)
    except ValueError:pass
    else:raise AssertionError('Unregistered callable accepted')
    print(json.dumps(dict(status='INCREMENT_RUNTIME_PASS',synthetic_cases=52,theme_geometry_checks=52,fixed_adapter_replays=52,negative_contract_checks=10,identity_crosspanel_checks=8,identifier_roundtrip=True,scope='Small software fixtures; no research inference or universal backend validation'),indent=2))

if __name__=='__main__':main()
