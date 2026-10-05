"""Synthetic behavioral tests, not research results. New output directory only."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from figure_publication import *
from figure_core import export_figure,file_sha256
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);fixture=out/'_input';fixture.mkdir()
cur=pd.DataFrame({'model':['A']*4+['B']*4,'x':[0,.2,.6,1,0,.3,.7,1],'y':[0,.5,.9,1,0,.6,.8,1]})
pr=cur.copy();pr['x']=[1,.6,.2,0]*2;pr['y']=[.5,.7,.9,1,.5,.6,.8,1]
mat=pd.DataFrame([{'feature':f,'sample':s,'value':float(i-j),'row_count':10+i*5,'feature_block':['one','one','two'][i]} for i,f in enumerate(['geneA','geneB','geneC']) for j,s in enumerate(['S1','S2','S3'])])
interval=pd.DataFrame({'label':['one','two'],'group':['A','B'],'estimate':[.4,-.1],'lower':[.1,-.3],'upper':[.8,.2]})
embedding=pd.DataFrame([{'cell_id':str(i),'x':float(i%7),'y':float(i//7),'feature':f,'value':float((i+k)%5)} for k,f in enumerate(['geneA','geneB','geneC']) for i in range(42)])
rain=pd.DataFrame({'sample_id':[str(i) for i in range(36)],'group':['A']*30+['B']*6,'value':np.r_[np.sin(np.linspace(0,4,30)),np.linspace(.1,.8,6)]})
inputs={'curve':cur,'PR':pr,'matrix':mat,'forest':interval,'features':embedding,'raincloud':rain}
for name,d in inputs.items():d.to_csv(fixture/(name+'.tsv'),sep='\t',index=False)
pal={'A':'#E98B2A','B':'#7562A5'};blocks={'one':'#2D9C95','two':'#4B88B5'}
meta={'source':'Explicitly synthetic software fixtures','palette':pal,'input_unit':'synthetic rows','experimental_unit':'none - synthetic fixture','contrast':'DEMO, not biological results','denominator':'defined synthetic table','model':'none; software rendering','limits':'supplied known ranges','filtering':'all fixture rows','uncertainty':'supplied synthetic intervals, not scientific CI','interpretation_limit':'SYNTHETIC DEMO; no scientific evidence','synthetic':True}
fns=[('ROC',cur,lambda:plot_publication_curve(cur,pal,curve_type='ROC',labels={'A':'A DEMO','B':'B DEMO'},title='SYNTHETIC DEMO ROC')),
 ('PR',pr,lambda:plot_publication_curve(pr,pal,curve_type='PR',labels={'A':'A DEMO','B':'B DEMO'},prevalence=.5,title='SYNTHETIC DEMO PR')),
 ('tile',mat,lambda:plot_aligned_matrix(mat,value_label='Synthetic values',limits=(-2,2),block_palette=blocks,title='SYNTHETIC DEMO tiles')),
 ('bubble',mat,lambda:plot_aligned_matrix(mat,value_label='Synthetic values',limits=(-2,2),geometry='bubble',block_palette=blocks,title='SYNTHETIC DEMO constant-area bubbles')),
 ('forest',interval,lambda:plot_publication_forest(interval,pal,x_label='Synthetic estimate',interval_label='Synthetic bounds',effect_scale='difference',title='SYNTHETIC DEMO intervals')),
 ('features',embedding,lambda:plot_feature_facets(embedding,value_label='Synthetic expression',limits=(0,4),title='SYNTHETIC DEMO stored coordinates')),
 ('raincloud',rain,lambda:plot_raincloud(rain,pal,y_label='Synthetic score',unit_label='synthetic observation',title='SYNTHETIC DEMO raincloud'))]
for name,d,fn in fns:
    fig=fn();export_figure(fig,d,out,name,meta);plt.close(fig)
    if name=='raincloud':assert fig._omics_spec['density_groups']==['A']
rejects=0
def rejects_call(fn):
    global rejects
    try:fn()
    except ValueError:rejects+=1;return
    raise AssertionError('Invalid fixture was accepted')
rejects_call(lambda:plot_aligned_matrix(mat.iloc[:-1],value_label='x',limits=(-2,2)))
rejects_call(lambda:plot_aligned_matrix(mat,value_label='x',limits=(-1,1),block_palette=blocks))
bad=mat.copy();bad.loc[0,'row_count']=3
rejects_call(lambda:plot_aligned_matrix(bad,value_label='x',limits=(-2,2),block_palette=blocks))
bad=embedding.copy();bad.loc[0,'x']=100
rejects_call(lambda:plot_feature_facets(bad,value_label='x',limits=(0,4)))
rejects_call(lambda:plot_feature_facets(embedding.iloc[:-1],value_label='x',limits=(0,4)))
bad_curve=cur.copy();bad_curve.loc[0,'x']=.5
rejects_call(lambda:plot_publication_curve(bad_curve,pal,curve_type='PR',labels={'A':'A','B':'B'},prevalence=.5))
rejects_call(lambda:plot_publication_curve(cur,pal,curve_type='ROC',labels={'A':'A'}))
bad=interval.copy();bad.loc[0,'lower']=.6
rejects_call(lambda:plot_publication_forest(bad,pal,x_label='x',interval_label='x',effect_scale='difference'))
rejects_call(lambda:plot_raincloud(pd.concat([rain,rain.iloc[:1]]),pal,y_label='x',unit_label='unit'))
rejects_call(lambda:plot_raincloud(rain,pal,y_label='x',unit_label=''))
assert rejects==10
for name,_,_ in fns:
    j=json.loads((out/name/(name+'.json')).read_text())
    for file,h in j['output_sha256'].items():assert file_sha256(out/name/file)==h
print(json.dumps({'exports':7,'reject_cases':rejects,'table_and_output_hashes':'PASS','output':str(out)}))
