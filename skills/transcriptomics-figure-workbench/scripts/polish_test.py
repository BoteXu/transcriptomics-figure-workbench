"""Synthetic-only invariants for additive polish renderers; no research computation."""
from pathlib import Path
import json,sys
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from figure_polish import *
from figure_core import export_figure
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
m=pd.DataFrame([dict(feature=f,sample=s,value=v) for f,vs in [('a',[-1,0]),('b',[.2,1])] for s,v in zip(['x','y'],vs)])
t=pd.DataFrame(dict(cluster=['C1','C2'],denominator=[3,2],single_complete_nonnegative_pair=[2,0],missing_multiple_invalid_or_negative_dates=[1,2],no_linked_therapy=[0,0]))
c=pd.DataFrame([dict(cluster=k,comedication=drug,denominator=n,any_role=any_,suspect_role=sus,status=status) for k,n,drug,any_,sus,status in [('C1',3,'D1',0,0,'recorded_field_count'),('C1',3,'D2',np.nan,np.nan,'index_drug_not_comedication'),('C2',2,'D1',2,1,'recorded_field_count'),('C2',2,'D2',np.nan,np.nan,'unavailable')]])
e=recorded_evidence_table(t,c)
a=pd.DataFrame(dict(display_cluster=['C1','C2'],reports=[3,2],any_therapy_rows=[2,0],nonempty_literature_reference=[0,0]))
meta=dict(source='Explicit synthetic software fixture',palette='as stamped',input_unit='synthetic counts/values',experimental_unit='none; software fixture',contrast='DEMO',denominator='fixture rows',model='none',limits='declared',filtering='all',uncertainty='none; synthetic',interpretation_limit='SYNTHETIC DEMO; no scientific inference',synthetic=True)
checks=[]
def reject(name,fn):
 try:fn()
 except (ValueError,TypeError,KeyError):checks.append(name);return
 raise AssertionError('Accepted '+name)
def matrix(data=m,**kw):return plot_polished_matrix(data,value_label='SYNTHETIC value',limits=(-1,1),signed=True,**kw)
rc=plt.rcParams.copy()
for layout in ['matrix','blocks','transpose']:
 original=m.copy(deep=True);fig=matrix(layout=layout,column_blocks={'x':'A','y':'B'},title='SYNTHETIC matrix')
 images=[ax.collections[0].get_array() for ax in fig.axes if ax is not fig.axes[-1]]
 expected=m.pivot(index='feature',columns='sample',values='value').reindex(index=['a','b'],columns=['x','y']).to_numpy()
 actual=np.concatenate(images,axis=1)
 np.testing.assert_array_equal(actual,expected.T if layout=='transpose' else expected)
 assert sum(text.get_text()=='−' for ax in fig.axes for text in ax.texts)==1
 pd.testing.assert_frame_equal(m,original)
 export_figure(fig,m,out,'synthetic_matrix_'+layout,meta);plt.close(fig)
 checks.append('matrix '+layout+' exact values/order/negative marks/input immutability')
for layout in ['aligned','split','table']:
 original=e.copy(deep=True);fig=plot_recorded_evidence(e,layout=layout,row_aliases={'C1':'C1 drug\nMYO','C2':'C2 drug\nCMP'},title='SYNTHETIC recorded evidence')
 texts=[x.get_text() for ax in fig.axes for x in ax.texts]
 assert '0 / 0' in texts and 'N/A' in texts and '?' in texts and '1 / 2' in texts
 assert all('n=' in x.get_text() for x in fig.axes[0].get_yticklabels())
 pd.testing.assert_frame_equal(e,original)
 export_figure(fig,e,out,'synthetic_evidence_'+layout,meta);plt.close(fig);checks.append('evidence '+layout+' zero/missing/denominator/immutability')
fig=plot_availability_counts(a,title='SYNTHETIC availability');assert sum(x.get_text()=='0' for x in fig.axes[0].texts)==2
export_figure(fig,a,out,'synthetic_availability',meta);plt.close(fig);checks.append('literature zeroes retained')
assert all(plt.rcParams[k]==v for k,v in rc.items());checks.append('rcParams restored')
reject('incomplete matrix',lambda:matrix(m.iloc[:-1]))
reject('duplicate matrix',lambda:matrix(pd.concat([m,m.iloc[:1]])))
reject('nonfinite matrix',lambda:matrix(m.assign(value=np.inf)))
reject('clipped values',lambda:plot_polished_matrix(m,value_label='value',limits=(-.5,.5),signed=True))
reject('missing value semantics',lambda:plot_polished_matrix(m,value_label='',limits=(-1,1),signed=True))
reject('signed scale without zero',lambda:plot_polished_matrix(m,value_label='value',limits=(-1,1),signed='yes'))
reject('nonboolean sign marks',lambda:matrix(sign_marks='yes'))
reject('alias collision',lambda:matrix(row_aliases={'a':'same','b':'same'}))
reject('empty alias',lambda:matrix(row_aliases={'a':''}))
reject('incomplete blocks',lambda:matrix(column_blocks={'x':'only'}))
reject('noncontiguous blocks',lambda:contiguous_blocks(['a','b','c'],{'a':'A','b':'B','c':'A'}))
reject('tiny geometry',lambda:matrix(width_mm=50))
reject('unknown layout',lambda:matrix(layout='bad'))
reject('reserved union column',lambda:recorded_evidence_table(t.assign(table_kind='bad'),c))
reject('missing drug grid',lambda:plot_recorded_evidence(e.iloc[:-1]))
def altered(column,value,where=0):
 d=e.copy();
 if isinstance(value,float) and column in d.select_dtypes(include='number'):d[column]=d[column].astype(float)
 d.loc[where,column]=value;return d
reject('negative count',lambda:plot_recorded_evidence(altered('single_complete_nonnegative_pair',-1)))
reject('fractional count',lambda:plot_recorded_evidence(altered('single_complete_nonnegative_pair',1.5)))
reject('category sum mismatch',lambda:plot_recorded_evidence(altered('single_complete_nonnegative_pair',1)))
reject('mismatched denominator',lambda:plot_recorded_evidence(altered('denominator',4,2)))
reject('suspect above any',lambda:plot_recorded_evidence(altered('suspect_role',1,2)))
reject('N/A coerced zero',lambda:plot_recorded_evidence(altered('any_role',0,3)))
reject('unknown status',lambda:plot_recorded_evidence(altered('status','invented',2)))
reject('availability above denominator',lambda:plot_availability_counts(a.assign(any_therapy_rows=[4,0])))
reject('negative literature count',lambda:plot_availability_counts(a.assign(nonempty_literature_reference=[-1,0])))
(out/'checks.json').write_text(json.dumps({'passed':checks,'count':len(checks),'synthetic':True},indent=2),encoding='utf-8')
print('PASS',len(checks),'checks; seven explicitly synthetic export bundles')
