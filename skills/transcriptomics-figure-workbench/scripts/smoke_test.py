"""Renderer fixtures only. Run into a NEW directory, never a scientific output folder."""
import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_core import *
from figure_extensions import *

def main(out):
    if out.exists(): raise FileExistsError('New output directory required')
    rng=np.random.default_rng(1409); palette={'Control':'#35618F','Treated':'#C45A2D'}
    meta=dict(source='Synthetic fixture seed 1409',input_unit='synthetic test units',experimental_unit='synthetic only',contrast='DEMO',denominator='see plotted table',model='none; renderer test',limits='no truncation',filtering='none',uncertainty='synthetic bounds',interpretation_limit='No scientific interpretation',synthetic=True)
    meta['palette']='Control=#35618F;Treated=#C45A2D;other scales as figure_core.py'
    def save(fig,d,name):
        export_figure(fig,d,out,name,meta); plt.close(fig)
    d=pd.DataFrame({'cell_id':[f'c{i}' for i in range(80)],'x':rng.normal(size=80),'y':rng.normal(size=80),'group':['Control']*40+['Treated']*40})
    save(plot_embedding(d,palette),d,'embedding')
    q=pd.DataFrame({'cell_id':d.cell_id,'sample':d.group,'value':abs(d.x)*1000})
    save(plot_qc(q,'DEMO counts'),q,'qc')
    s=pd.DataFrame({'sample_id':[f's{i}' for i in range(10)],'group':['Control']*5+['Treated']*5,'value':rng.normal(size=10)})
    save(plot_samples(s,palette,'DEMO expression'),s,'samples')
    f=pd.DataFrame({'label':['A','B','C'],'estimate':[.3,-.2,.8],'lower':[-.1,-.6,.2],'upper':[.7,.2,1.4]})
    save(plot_forest(f,'DEMO effect','Synthetic bounds',effect_scale='difference'),f,'forest')
    v=pd.DataFrame({'gene':[f'g{i}' for i in range(80)],'log2FC':rng.normal(size=80)*2,'padj':10**rng.uniform(-5,0,80)})
    save(plot_volcano(v),v,'volcano')
    z=pd.DataFrame([(f'gene{i}',g) for i in range(5) for g in palette],columns=['feature','group']); z['fraction']=rng.uniform(size=10); z['value']=rng.uniform(0,3,10)
    save(plot_dot(z,'DEMO mean',value_semantics='mean_all',denominator_label='All eligible demo cells'),z,'dot')
    h=pd.DataFrame([(f'gene{i}',f'sample{j}') for i in range(8) for j in range(6)],columns=['feature','sample']); h['value']=rng.normal(size=len(h))
    save(plot_heatmap(h,'DEMO signed values'),h,'heatmap')
    c=pd.DataFrame([(f'sample{i}',g) for i in range(4) for g in palette],columns=['sample','celltype']); c['count']=rng.integers(10,90,len(c))
    save(plot_composition(c,palette),c,'composition')
    for kind in ['ROC','PR','calibration']:
        x=np.linspace(0,1,20); curve=pd.DataFrame({'model':'DEMO','x':x,'y':1-.5*x if kind=='PR' else x})
        save(plot_curve(curve,kind),curve,kind.lower())
    ratio=f.copy(); ratio[['estimate','lower','upper']]=np.exp(ratio[['estimate','lower','upper']])
    save(plot_forest(ratio,'DEMO hazard ratio','Synthetic bounds',effect_scale='ratio'),ratio,'forest_ratio')
    unsigned=h.copy(); unsigned['value']=abs(unsigned.value)
    save(plot_heatmap(unsigned,'DEMO nonnegative values',scale_type='sequential'),unsigned,'heatmap_sequential')
    paired=pd.DataFrame({'subject_id':np.repeat(['s1','s2','s3'],2),'condition':['Control','Treated']*3,'value':[1,2,2,1.5,1.2,2.4]})
    save(plot_paired(paired,palette,['Control','Treated'],'DEMO value'),paired,'paired')
    effects=pd.DataFrame([(g,c) for g in ['T cells','B cells','Myeloid'] for c in ['Contrast 1','Contrast 2']],columns=['feature','contrast'])
    effects['estimate']=[-.8,.3,.6,-.4,.1,.7]; effects['lower']=effects.estimate-.3; effects['upper']=effects.estimate+.3; effects['padj']=[.001,.1,.04,.2,1,.000001]
    save(plot_effect_matrix(effects,'DEMO log odds ratio',effect_scale='log_ratio'),effects,'effect_matrix')
    annotated=h.copy(); annotated['sample_group']=annotated['sample'].map(lambda x:'Control' if int(x[-1])<3 else 'Treated'); annotated['feature_block']=annotated.feature.map(lambda x:'Program A' if int(x[-1])<4 else 'Program B')
    save(plot_annotated_heatmap(annotated,'DEMO signed values',palette,{'Program A':'#8172B2','Program B':'#55A868'},scale_type='signed'),annotated,'annotated_heatmap')
    scores=pd.DataFrame({'feature':['T cells','B cells','Myeloid'],'score_a':[.6,.72,.8],'score_b':[.8,.65,.85]}); scores['delta']=scores.score_b-scores.score_a; scores['lower_delta']=scores.delta-.04; scores['upper_delta']=scores.delta+.04
    save(plot_score_comparison(scores,'DEMO AUC',['Condition A','Condition B']),scores,'score_comparison')
    def fails(fn):
        try: fn()
        except (ValueError,FileExistsError): return
        raise AssertionError('Negative test unexpectedly passed')
    bad=f.copy(); bad.loc[0,'lower']=1; fails(lambda:plot_forest(bad,'effect','bounds',effect_scale='difference'))
    bad=z.copy(); bad.loc[0,'fraction']=2; fails(lambda:plot_dot(bad,'value',value_semantics='mean_all',denominator_label='cells'))
    bad=d.copy(); bad.loc[1,'cell_id']=bad.loc[0,'cell_id']; fails(lambda:plot_embedding(bad,palette))
    bad=v.copy(); bad.loc[0,'padj']=0; fails(lambda:plot_volcano(bad))
    fails(lambda:plot_embedding(d,{'Control':'blue'}))
    fails(lambda:plot_heatmap(h.iloc[:-1],'value'))
    fails(lambda:export_figure(plot_forest(f,'effect','bounds',effect_scale='difference'),f,out,'forest',meta))
    fails(lambda:export_figure(plot_forest(f,'effect','bounds',effect_scale='difference'),f,out,'../escape',meta))
    fails(lambda:plot_samples(pd.concat([s,s.iloc[:1]]),palette,'value'))
    plt.close('all')
    files=[p for p in out.rglob('*') if p.is_file()]; assert len(files)==102 and all(p.stat().st_size>0 for p in files)
    for p in out.glob('*/*.json'):
        r=json.loads(p.read_text(encoding='utf-8')); assert r['synthetic'] and r['status']=='RENDERED_UNREVIEWED'
        for name,sha in r['output_sha256'].items(): assert hashlib.sha256((p.parent/name).read_bytes()).hexdigest()==sha
        assert r['input_hash']==r['output_sha256'][p.stem+'.tsv']
    print('PASS: 17 synthetic figures x 6 files; 9 negative tests; verified output hashes; no biological analysis')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: python smoke_test.py NEW_OUTPUT_DIRECTORY')
    main(Path(sys.argv[1]))
