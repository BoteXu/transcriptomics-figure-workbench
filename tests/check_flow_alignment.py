"""Numerical and rendered-centre checks; no analysis is inferred."""
from pathlib import Path
import sys,json,tempfile,copy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from alluvial_geometry import layout_paths
from figure_network_extensions import plot_alluvial,plot_weighted_chord
from project_theme import create_theme
from figure_layout import apply_page_layout
from figure_design import geometry_signature
from indexed_alignment import audit_index_alignment
from figure_core import plot_dot,plot_heatmap
from figure_reference import plot_activity_dashboard
from figure_palette_applications import plot_palette_panel
from compose_panels import arrangement_layout,_validate_layout,align_data_rects


def rejects(fn):
    try:fn()
    except (ValueError,TypeError):return
    raise AssertionError('Invalid drawing contract accepted')


def main():
    stages=['s'+str(i) for i in range(7)]
    data=pd.DataFrame([dict(path_id=p,weight=w,**{s:g if j%2==0 else h for j,s in enumerate(stages)})
                       for p,w,g,h in [('001',3,'A','C'),('002',5,'B','C'),('NA',2,'A','D'),('zero',0,'B','D')]])
    orders={s:['A','B'] if j%2==0 else ['C','D'] for j,s in enumerate(stages)}
    ledger=layout_paths(data,stages,stage_orders=orders)
    assert ledger==layout_paths(data.sample(frac=1,random_state=14),stages,stage_orders=orders)
    assert ledger['total']==10 and ledger['zero_paths']==['zero']
    for j,s in enumerate(stages):
        assert sum(n['weight'] for n in ledger['nodes'] if n['stage']==s)==10
    for r in ledger['segments']:
        for key in ['source_interval','target_interval']:
            np.testing.assert_allclose(np.diff(r[key]),r['weight'])
    for n in ledger['nodes']:
        np.testing.assert_allclose(n['hi']-n['lo'],n['weight'],rtol=1e-12,atol=1e-13)
    theme=create_theme('flow-check','card_06',{'A':0,'B':1,'C':4,'D':6})
    for direction in ['horizontal','vertical']:
        fig=plot_alluvial(data,theme,stage_columns=stages,weight_label='Count',stage_orders=orders,orientation=direction)
        flows=[p for p in fig.axes[0].patches if (p.get_gid() or '').startswith('flow:')]
        assert len(flows)==3*6
        lookup={(r['path_id'],r['stage_index']):r for r in ledger['segments']}
        for patch in flows:
            _,id_,stage=patch.get_gid().split(':');r=lookup[(id_,int(stage))];v=patch.get_path().vertices
            dim=1 if direction=='horizontal' else 0
            np.testing.assert_allclose([v[7,dim]-v[0,dim],v[4,dim]-v[3,dim]],[r['weight']]*2)
        signature=geometry_signature(fig);apply_page_layout(fig,'portrait' if direction=='horizontal' else 'landscape')
        assert signature==geometry_signature(fig);plt.close(fig)
    negatives=[lambda:layout_paths(data,stages+[stages[0]]),lambda:layout_paths(data.assign(weight=-1),stages),
               lambda:layout_paths(data.assign(weight=0),stages),lambda:layout_paths(pd.concat([data,data.iloc[:1]]),stages),
               lambda:layout_paths(data.assign(s0=''),stages),lambda:layout_paths(data,stages,stage_orders={}),
               lambda:layout_paths(data,stages,path_order=['001']),lambda:layout_paths(data,stages,gap_fraction=-1),
               lambda:plot_alluvial(data,theme,stage_columns=stages,weight_label='Count',orientation='diagonal'),
               lambda:plot_weighted_chord(pd.DataFrame(dict(source=['A','B'],target=['B','A'],weight=[1.,2.])),theme,weight_label='count',order=['A','B'])]
    for fn in negatives:rejects(fn)
    # Independent oracle: size, colour and coordinates must come from the same cell,
    # including shuffled long-table rows and explicit reversed axis orders.
    dot=pd.DataFrame([dict(feature=f,group=c,fraction=(i*2+j+1)/10,value=i*3+j+.5)
                      for i,f in enumerate(['r1','r2','r3']) for j,c in enumerate(['c1','c2'])]).sample(frac=1,random_state=4)
    fig=plot_dot(dot,'Score',value_semantics='mean_all',denominator_label='All cells',row_order=['r3','r1','r2'],column_order=['c2','c1'])
    collection=fig.axes[0].collections[0];xy=np.asarray(collection.get_offsets());sizes=collection.get_sizes();colors=collection.get_array()
    for r in dot.itertuples():
        idx=np.flatnonzero((xy[:,0]==['c2','c1'].index(r.group))&(xy[:,1]==['r3','r1','r2'].index(r.feature))).item()
        np.testing.assert_allclose(sizes[idx],150*r.fraction);np.testing.assert_allclose(colors[idx],r.value)
    plt.close(fig)
    wide=pd.DataFrame({'id':['r3','r1','r2'],'c2':[3.,1.,2.],'c1':[6.,4.,5.]})
    fig=plot_heatmap(wide,'Value',row_field='id',value_columns=['c2','c1'],row_order=['r1','r2','r3'],column_order=['c1','c2'],
        row_annotations={'Module':{'r1':'A','r2':'B','r3':'A'}},column_annotations={'Group':{'c1':'D','c2':'C'}},
        annotation_palettes={'Module':{'A':'#7CB1D0','B':'#EC9CAB'},'Group':{'C':'#F4B08F','D':'#A4C9DC'}})
    assert not audit_index_alignment(fig)['issues']
    np.testing.assert_allclose(fig.axes[0].images[0].get_array(),[[4,1],[5,2],[6,3]])
    apply_page_layout(fig,'portrait');assert not audit_index_alignment(fig)['issues'];plt.close(fig)
    # Top bars, their line scale and row annotation all follow the matrix centres.
    d=pd.DataFrame([dict(record_type='matrix',row=r,column=c,value=i+j+.1) for i,r in enumerate(['r1','r2','r3']) for j,c in enumerate(['c1','c2','c3'])]
        +[dict(record_type='row',row=r,group=g) for r,g in [('r3','A'),('r1','B'),('r2','A')]]
        +[dict(record_type='top',column=c,bar=v,line=v/10) for c,v in [('c3',7),('c1',2),('c2',4)]]
        +[dict(record_type='density',group=g,coordinate=x,value=1-x/2) for g in ['A','B'] for x in [0.,1.]])
    fig=plot_activity_dashboard(d,{'A':'#7CB1D0','B':'#EC9CAB'},row_order=['r2','r3','r1'],column_order=['c3','c1','c2'],value_label='Value',bar_label='Count',line_label='Rate')
    assert len(fig._index_bindings)==3 and not audit_index_alignment(fig)['issues']
    apply_page_layout(fig,'portrait');assert not audit_index_alignment(fig)['issues'];plt.close(fig)
    for arrangement in ['horizontal','vertical']:
        layout=arrangement_layout(dict(id='Demo',panels=[dict(id='A',label='A'),dict(id='B',label='B')]),arrangement)
        _validate_layout([{},{}],layout)
        a,b=[p['rect_pt'] for p in layout['panels']]
        assert (a[1]==b[1]) if arrangement=='horizontal' else (a[0]==b[0])
    rejects(lambda:_validate_layout([{},{}],dict(id='Demo',size_pt=[300,200],panels=[dict(id='A',label='A',rect_pt=[0,0,50,60]),dict(id='B',rect_pt=[60,0,120,60])])))
    # Independent PDF coordinate oracle: different margins may not be treated
    # as aligned merely because complete panel cells start at the same edge.
    import fitz,copy
    prepared=[]
    for i,bounds in enumerate([[.1,.2,.6,.6],[.3,.1,.5,.7]]):
        source=fitz.open();source.new_page(width=400,height=300)
        prepared.append(dict(cell=dict(id=str(i),rect_pt=[10,20+i*350,510,320+i*350]),source=source,clip=fitz.Rect(0,0,400,300),meta=dict(width_inches=400/72,height_inches=300/72,layout_geometry=[dict(bounds=bounds,xlim=[0,10],ylim=[0,1],xscale='linear',yscale='linear')]),fitted=None))
    group=dict(dimension='x',coordinate_definition='Same supplied physical position and units',panels=[dict(id=str(i),axis=0) for i in range(2)])
    receipt=align_data_rects(prepared,[group])[0];interval=[]
    for p in prepared:
        b=p['meta']['layout_geometry'][0]['bounds'];f=p['fitted'];scale=f.width/400
        interval.append([f.x0+b[0]*400*scale,f.x0+(b[0]+b[2])*400*scale])
    np.testing.assert_allclose(interval,[receipt['target_span_pt']]*2)
    bad=copy.deepcopy(group);bad['panels'][0]['keys']=['A','B'];bad['panels'][1]['keys']=['B','A']
    rejects(lambda:align_data_rects(prepared,[bad]))
    for p in prepared:p['source'].close()
    print(json.dumps(dict(status='FLOW_INDEX_LAYOUT_PASS',flow_directions=2,stages=7,negative_checks=len(negatives)+2,
        dot_channel_identity=True,indexed_tracks=5,composite_arrangements=2,shared_pdf_axis_oracle=True,scope='Numerical and rendered-coordinate checks on synthetic fixtures')))

if __name__=='__main__':main()
