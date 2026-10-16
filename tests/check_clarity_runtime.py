"""Frozen-channel and rejection checks for clarity views; no aesthetic acceptance."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection,LineCollection
import numpy as np
import pandas as pd
from render_frozen_table import load_table,render

def refused(call):
    try:call()
    except (ValueError,TypeError,KeyError):return
    finally:plt.close('all')
    raise AssertionError('Invalid frozen display accepted')

def main():
    base=ROOT/'examples/clarity-v070/inputs';records=json.loads((base.parent/'manifest.json').read_text())['records'];invalid=0
    for row in records:
        key=row['id'];spec=json.loads((base/(key+'.spec.json')).read_text());p=spec['parameters'];o=p['options'];view=p['view'];d=load_table(base/(key+'.tsv'),'clarity',p);before=d.copy(deep=True)
        fig,_=render('clarity',d,p,spec['theme']);pd.testing.assert_frame_equal(d,before)
        if view=='profiles':
            for name,line in zip(o['group_order'],fig.axes[0].lines):
                q=d[d.group==name];np.testing.assert_array_equal(line.get_xdata(),q.x);np.testing.assert_array_equal(line.get_ydata(),q.y)
            assert sum(len(c.get_offsets()) for c in fig.axes[0].collections if isinstance(c,PathCollection))==len(d)
        elif view=='contribution':
            points=[c for c in fig.axes[0].collections if isinstance(c,PathCollection)];assert sum(len(c.get_offsets()) for c in points)==len(d)
            for name,c in zip(o['feature_order'],points):
                q=d[d.feature==name];np.testing.assert_array_equal(c.get_offsets()[:,0],q.contribution);np.testing.assert_array_equal(c.get_array(),q.feature_value)
        elif view=='effects':
            points=[c for a in fig.axes[:2] for c in a.collections if isinstance(c,PathCollection)];assert sum(len(c.get_offsets()) for c in points)==len(d)
            for panel,ax in zip(o['panel_order'],fig.axes[:2]):
                segments=[c.get_segments()[0] for c in ax.collections if isinstance(c,LineCollection)]
                z=d[(d.record_type=='summary')&(d.panel==panel)].set_index('row').loc[o['row_order']]
                np.testing.assert_allclose([[s[0,0],s[1,0]] for s in segments],z[['lower','upper']])
        elif view=='membership':
            assert len(fig.axes[0].patches)==len(o['member_order'])*len(o['term_order'])
            from matplotlib.colors import to_hex
            assert sum(to_hex(r.get_facecolor())=='#218c8d' for r in fig.axes[0].patches)==sum(d.record_type=='link')
        elif view=='shares':assert len(fig.axes[0].patches)==len(d)
        elif view=='pixels':
            for i,ax in enumerate(fig.axes[:3] if o['mode']=='slices' else fig.axes[:2]):
                q=d[d.view==o['view_order'][i]] if o['mode']=='slices' else d
                field='intensity' if o['mode']=='slices' else ('fixed' if i==0 else 'registered');expected=q.pivot(index='v',columns='u',values=field).to_numpy()
                np.testing.assert_array_equal(ax.images[0].get_array(),expected)
            if o['mode']=='registration':np.testing.assert_array_equal(fig.axes[3].images[0].get_array(),d.pivot(index='v',columns='u',values='registered').to_numpy()-d.pivot(index='v',columns='u',values='fixed').to_numpy())
        elif view=='estimation':
            assert sum(len(c.get_offsets()) for c in fig.axes[0].collections)==sum(d.record_type=='observation')
            z=d[d.record_type=='density'];np.testing.assert_array_equal(fig.axes[1].lines[0].get_ydata(),z.x)
        elif view in ['decision','precision_recall']:
            for name,line in zip(o['series_order'],fig.axes[0].lines):
                q=d[d.series==name];np.testing.assert_array_equal(line.get_xdata(),q.x);np.testing.assert_array_equal(line.get_ydata(),q.value)
        elif view=='rank_stability':assert sum(len(c.get_offsets()) for ax in fig.axes for c in ax.collections if isinstance(c,PathCollection))==sum(d.status=='reported')
        plt.close(fig)
        bad=d.copy()
        if view=='profiles':bad.loc[0,'x']=999999
        elif view=='contribution':bad.loc[0,'feature_value']=99
        elif view=='effects':bad.loc[bad.record_type=='summary','lower']=999
        elif view=='shares':bad=pd.concat([bad,bad.iloc[:1]],ignore_index=True)
        elif view=='membership':bad.loc[bad.record_type=='link','term_id']='absent'
        elif view=='pixels':bad=pd.concat([bad,bad.iloc[:1]],ignore_index=True)
        elif view=='estimation':bad.loc[bad.record_type=='summary','lower']=999
        elif view in ['decision','precision_recall']:bad.loc[0,'x']=2
        elif view=='rank_stability':bad.loc[bad.status=='unassessed','rank']=8
        refused(lambda:render('clarity',bad,p,spec['theme']));invalid+=1
        q=copy.deepcopy(p);q['options']['unknown']=True;refused(lambda:render('clarity',d,q,spec['theme']));invalid+=1
    print(json.dumps(dict(status='CLARITY_CHANNEL_PASS',examples=len(records),views=10,invalid_cases=invalid,scientific_acceptance=False,visual_acceptance=False)))

if __name__=='__main__':main()
