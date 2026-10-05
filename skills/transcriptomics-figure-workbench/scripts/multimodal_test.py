"""Deterministic synthetic renderer/invariant tests, never scientific results."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from figure_core import export_figure,file_sha256,plot_heatmap
from figure_publication import plot_aligned_matrix
from figure_multimodal import *

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
pal={'Cohort A':CATEGORY[0],'Cohort B':CATEGORY[1]}
cohort=pd.DataFrame([dict(feature=f,cohort=c,estimate=e,lower=e-.2,upper=e+.2)
    for f,es in [('Interferon program',(.65,.48)),('Cell death program',(.25,-.05)),('Cardiac function',(-.4,-.28))]
    for c,e in zip(pal,es)])
assoc=pd.DataFrame([dict(feature=f,modality=m,status='estimable',value=v,q=q,n=24)
    for f,vs in [('Program 1',(.7,.45,-.32)),('Program 2',(-.6,-.42,.53)),('Program 3',(.08,.03,-.18))]
    for m,v,q in zip(['RNA','Accessibility','Protein'],vs,[.01,.04,.3])])
assoc.loc[8,['status','value','q','n']]=['unavailable',np.nan,np.nan,np.nan]
cal=pd.DataFrame([dict(model=m,bin_left=i*.2,bin_right=(i+1)*.2,predicted=i*.2+.1,
    estimate=min(.95,max(.05,i*.2+.1+delta)),lower=max(0,i*.2+delta),upper=min(1,(i+1)*.2+delta),n=n)
    for m,delta in [('Cohort A',.02),('Cohort B',-.04)]
    for i,n in enumerate([25,32,46,28,15])])
tracks=pd.DataFrame([dict(track=t,start=10000+i*100,end=10000+(i+1)*100,value=v)
    for t,vs in [('RNA signal',[1,3,6,8,5,2,1,0,1]),('ATAC signal',[0,1,4,7,4,1,0,1,2])]
    for i,v in enumerate(vs) if i!=6])
dyn=pd.DataFrame([dict(series=s,time=i*10,estimate=v,lower=max(0,v-.04),upper=v+.04)
    for s,vs in [('Cohort A',[.1,.2,.25,.28,.3,.29,.31]),('Cohort B',[.1,.17,.24,.36,.4,.42,.44])]
    for i,v in enumerate(vs)])
conf=pd.DataFrame({'residue':list(range(1,41))+list(range(46,101)),
                   'plddt':[85+8*np.sin(i/7) for i in range(40)]+[48+30*np.sin(i/18)**2 for i in range(55)]})
mat=pd.DataFrame([dict(feature='Module '+str(i+1),sample=s,value=float((i+j)%9)/8)
    for i in range(8) for j,s in enumerate(['Animal 1','Animal 2','Animal 3','Sensitivity k15'])])
tables={'cohort':cohort,'association':assoc,'calibration':cal,'tracks':tracks,'dynamics':dyn,'confidence':conf,'old_heatmap':mat,'new_heatmap':mat}
meta={'source':'Explicit deterministic synthetic software fixture','palette':pal,
      'input_unit':'synthetic rows','experimental_unit':'none - synthetic fixture',
      'contrast':'DEMO, no biological inference','denominator':'synthetic table as supplied',
      'model':'none; frozen fixture values','limits':'declared in figure specification',
      'filtering':'all supplied fixture rows','uncertainty':'synthetic illustrative bounds, not scientific CI',
      'interpretation_limit':'SYNTHETIC DEMO; no scientific evidence','synthetic':True}

def new_matrix():
    fig=plot_aligned_matrix(mat,value_label='Synthetic magnitude',limits=(0,1),
                           signed=False,title='Same-table compact matrix')
    aliases={'Sensitivity k15':'k = 15'}
    labels=list(dict.fromkeys(mat['sample']))
    fig.axes[0].set_xticklabels([aliases.get(x,x) for x in labels],rotation=35,ha='right')
    fig._omics_spec['display_label_map']=aliases
    return fig

cases=[
 ('cohort',lambda:plot_cohort_intervals(cohort,pal,effect_scale='log_ratio',effect_label='Synthetic log2 effect',interval_label='Supplied synthetic bounds',title='Cross-cohort consistency')),
 ('association',lambda:plot_association_matrix(assoc,value_label='Synthetic Spearman rho',method_label='Synthetic matched-unit associations',title='Molecular-layer associations')),
 ('calibration',lambda:plot_calibration_counts(cal,pal,interval_label='Synthetic illustrative bounds',evaluation_label='Synthetic held-out units',title='Calibration with evaluation counts')),
 ('tracks',lambda:plot_interval_tracks(tracks,{'RNA signal':CATEGORY[0],'ATAC signal':CATEGORY[2]},assembly='DEMO assembly',chromosome='chrDemo',region=(10000,10900),value_label='Synthetic normalized signal',title='Aligned genomic signals')),
 ('dynamics',lambda:plot_frozen_dynamics(dyn,pal,time_label='Synthetic time (ns)',value_label='Synthetic RMSD (nm)',unit_label='Synthetic independent-start summaries',interval_label='Supplied illustrative bounds',title='Frozen computational trajectories')),
 ('confidence',lambda:plot_residue_confidence(conf,sequence_label='Synthetic chain A, artificial sequence',title='Sequence-resolved predicted confidence')),
 ('old_heatmap',lambda:plot_heatmap(mat,value_label='Synthetic magnitude',scale_type='sequential')),
 ('new_heatmap',new_matrix)
]
rejects=[]
def reject(name,fn):
    before=set(plt.get_fignums())
    try:fn()
    except (ValueError,TypeError):rejects.append(name)
    else:raise AssertionError('Invalid input accepted: '+name)
    finally:
        for n in set(plt.get_fignums())-before:plt.close(n)

with PdfPages(out/'synthetic_gallery.pdf') as pdf:
    for name,fn in cases:
        raw=tables[name].copy(deep=True);rc=plt.rcParams.copy()
        fig=fn();pd.testing.assert_frame_equal(raw,tables[name]);assert dict(plt.rcParams)==dict(rc)
        export_figure(fig,tables[name],out,name,meta);pdf.savefig(fig);plt.close(fig)
        receipt=json.loads((out/name/(name+'.json')).read_text())
        assert receipt['synthetic'] is True and receipt['status']=='RENDERED_UNREVIEWED'
        for f,h in receipt['output_sha256'].items():assert file_sha256(out/name/f)==h
        assert receipt['input_hash']==file_sha256(out/name/(name+'.tsv'))

co=lambda d,**kw:plot_cohort_intervals(d,pal,effect_scale=kw.get('scale','log_ratio'),effect_label='effect',interval_label='bounds')
bad=cohort.copy();bad.loc[0,'lower']=1
reject('reversed_bounds',lambda:co(bad))
reject('missing_cohort',lambda:co(cohort.iloc[:-1]))
reject('invalid_effect_scale',lambda:co(cohort,scale='AUC'))
reject('ratio_nonpositive',lambda:co(cohort,scale='ratio'))
reject('duplicate_cohort',lambda:co(pd.concat([cohort,cohort.iloc[:1]])))
ass=lambda d:plot_association_matrix(d,value_label='rho',method_label='matched units')
bad=assoc.copy();bad.loc[8,'value']=0
reject('missing_not_zero',lambda:ass(bad))
bad=assoc.copy();bad.loc[0,'q']=1.1
reject('q_outside_range',lambda:ass(bad))
bad=assoc.copy();bad.loc[0,'n']=2.5
reject('invalid_matched_n',lambda:ass(bad))
bad=assoc.copy();bad.loc[0,'value']=2
reject('invalid_correlation',lambda:ass(bad))
reject('missing_matrix_cell',lambda:ass(assoc.iloc[:-1]))
calfn=lambda d:plot_calibration_counts(d,pal,interval_label='bounds',evaluation_label='held-out')
bad=cal.copy();bad.loc[1,'bin_left']=.1
reject('overlap_bins',lambda:calfn(bad))
bad=cal.copy();bad.loc[0,'n']=0
reject('empty_calibration_bin',lambda:calfn(bad))
bad=cal.copy();bad.loc[0,'predicted']=.3
reject('mean_outside_bin',lambda:calfn(bad))
reject('unsorted_bins',lambda:calfn(cal.iloc[::-1]))
trk=lambda d,**kw:plot_interval_tracks(d,{'RNA signal':CATEGORY[0],'ATAC signal':CATEGORY[2]},assembly='demo',chromosome='demo',region=(10000,10900),value_label='signal',**kw)
bad=tracks.copy();bad.loc[1,'start']=10050
reject('overlap_intervals',lambda:trk(bad))
reject('wrong_coordinate_convention',lambda:trk(tracks,coordinate_system='one_based_closed'))
bad=tracks.copy();bad.loc[0,'start']=9999
reject('out_of_region',lambda:trk(bad))
dy=lambda d:plot_frozen_dynamics(d,pal,time_label='ns',value_label='nm',unit_label='repeats',interval_label='bounds')
reject('unsorted_time',lambda:dy(dyn.iloc[::-1]))
bad=conf.copy();bad.loc[0,'plddt']=101
reject('confidence_over100',lambda:plot_residue_confidence(bad,sequence_label='chain'))
reject('duplicate_residue',lambda:plot_residue_confidence(pd.concat([conf,conf.iloc[:1]]),sequence_label='chain'))
# Meaningful geometry invariants, not merely acceptance.
fig=plot_residue_confidence(conf,sequence_label='chain')
lines=fig.axes[0].lines;assert len(lines)==2
np.testing.assert_array_equal(np.concatenate([l.get_xdata() for l in lines]),conf.residue)
np.testing.assert_allclose(np.concatenate([l.get_ydata() for l in lines]),conf.plddt);plt.close(fig)
fig=co(cohort)
for line,c in zip([l for l in fig.axes[0].lines if l.get_marker() in ['o','s']],pal):
    np.testing.assert_allclose(np.asarray(line.get_xdata(),dtype=float),cohort[cohort.cohort==c].estimate.to_numpy(dtype=float))
plt.close(fig)
fig=trk(tracks);assert fig.axes[0].get_ylim()==fig.axes[1].get_ylim();assert len(fig.axes[0].collections)==8;plt.close(fig)
# Exact same values/order go to before and after renderers.
assert file_sha256(out/'old_heatmap/old_heatmap.tsv')==file_sha256(out/'new_heatmap/new_heatmap.tsv')
result={'exports':8,'new_adapter_families':6,'rejections':rejects,'input_immutability':'PASS',
        'global_theme_unchanged':'PASS','geometry_invariants':'PASS','bundle_hashes':'PASS',
        'before_after_same_input':'PASS','scientific_inference':'none','visual_review':'PENDING'}
(out/'test_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='rejections'}));print('negative cases',len(rejects))


