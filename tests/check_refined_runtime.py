"""Verify frozen view channels and malformed inputs, not aesthetic acceptance."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from render_frozen_table import load_table,render

def refused(call):
    try:call()
    except (ValueError,TypeError,KeyError):return
    finally:plt.close('all')
    raise AssertionError('Malformed channel accepted')

def main():
    base=ROOT/'examples/refined-v060/inputs';invalid=0
    for n in range(1,6):
        key=f'REF{n:02d}';spec=json.loads((base/(key+'.spec.json')).read_text())
        d=load_table(base/(key+'.tsv'),spec['renderer'],spec['parameters']);before=d.copy(deep=True)
        fig,_=render(spec['renderer'],d,spec['parameters'],spec['theme']);pd.testing.assert_frame_equal(d,before)
        if key=='REF01':
            q=d[d.kind=='curve'];expected=np.stack([np.column_stack([q['rank'],q.value])[:-1],np.column_stack([q['rank'],q.value])[1:]],axis=1)
            layers=[c for c in fig.axes[0].collections if isinstance(c,LineCollection) and len(c.get_segments())==len(expected)]
            assert len(layers)==2
            for layer in layers:np.testing.assert_allclose(layer.get_segments(),expected)
            np.testing.assert_allclose(layers[1].get_array(),d.loc[d.kind=='metric','value'].to_numpy()[:-1])
        if key=='REF03':
            for name,line in zip(spec['parameters']['options']['series_order'],fig.axes[0].lines):
                q=d[d.series==name];np.testing.assert_allclose(line.get_xdata(),q.x);np.testing.assert_allclose(line.get_ydata(),q.estimate)
        plt.close(fig)
        bad=d.copy()
        if key in ['REF01','REF02']:bad.loc[bad.kind=='hit','rank']=999999
        elif key=='REF03':bad.loc[0,'lower']=999999
        elif key=='REF04':bad.loc[0,'delta']=999999
        else:bad.loc[0,'r']=99
        refused(lambda:render(spec['renderer'],bad,spec['parameters'],spec['theme']));invalid+=1
        p=copy.deepcopy(spec['parameters']);p['options']['unknown']=True
        refused(lambda:render(spec['renderer'],d,p,spec['theme']));invalid+=1
    print(json.dumps(dict(status='REFINED_CHANNEL_PASS',views=5,invalid_cases=invalid,exact_ES_layers=True,scientific_acceptance=False,visual_acceptance=False)))
if __name__=='__main__':main()
