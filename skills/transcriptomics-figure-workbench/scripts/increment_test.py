"""Synthetic execution and appearance-invariance checks. Use a fresh output folder."""
from pathlib import Path
import json, sys, hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_core import export_figure, table_bytes, plot_samples, stamp
from figure_general import (plot_xy_points,plot_grouped_estimates,plot_binned_distribution,
                            plot_confusion_counts,plot_density_ridges)
from figure_design import DesignSpec,apply_design,audit_layout,geometry_signature,resolve_font,named_layout

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False);(out/'inputs').mkdir()
palette={'Group A':'#35618F','Group B':'#C45A2D','Group C':'#67A9A2'}
rng=np.random.default_rng(20261005)
tables={
 'P33':pd.DataFrame([dict(unit_id=f'U{i:02}',group=list(palette)[i%3],x=float(i/5),y=float(i/8+rng.normal(0,.6))) for i in range(48)]),
 'P34':pd.DataFrame([dict(category=c,group=g,estimate=v,lower=v-.35,upper=v+.35) for j,c in enumerate(['Panel A','Panel B','Panel C','Panel D']) for i,g in enumerate(palette) for v in [1.2+j*.3+i*.4]]),
 'P35':pd.DataFrame([dict(group=g,left=i,right=i+1,count=int(n)) for g,counts in zip(palette,[[2,6,12,22,31,18,9,3],[1,3,8,15,26,24,16,7],[5,11,20,26,21,13,5,1]]) for i,n in enumerate(counts)]),
 'P36':pd.DataFrame([dict(actual=a,predicted=b,count=[[38,4,2],[6,32,3],[1,5,29]][i][j]) for i,a in enumerate(['Class A','Class B','Class C']) for j,b in enumerate(['Class A','Class B','Class C'])]),
 'P37':pd.DataFrame([dict(group=g,x=float(x),density=float(np.exp(-.5*((x-i*.6)/.8)**2)/(.8*np.sqrt(2*np.pi)))) for i,g in enumerate(palette) for x in np.linspace(-3,4,81)])}
calls={
 'P33':lambda d:plot_xy_points(d,palette,'Supplied X','Supplied Y',unit_label='Demo independent unit'),
 'P34':lambda d:plot_grouped_estimates(d,palette,'Supplied estimate',interval_label='Supplied illustrative interval'),
 'P35':lambda d:plot_binned_distribution(d,palette,'Frozen bin boundaries',denominator_label='Demo units per group'),
 'P36':lambda d:plot_confusion_counts(d,unit_label='Demo held-out units'),
 'P37':lambda d:plot_density_ridges(d,palette,'Supplied score',density_label='Precomputed demo density')}
meta=dict(source='Deterministic synthetic fixture 20261005',palette=palette,input_unit='Supplied fixture rows',
 experimental_unit='No biological units; software fixture',contrast='Illustrative groups',denominator='All supplied fixture rows',
 model='No fitted analysis model',limits='Explicit renderer semantics',filtering='No row selection',
 uncertainty='Illustrative supplied bounds; not research confidence intervals',interpretation_limit='Synthetic demonstration only',synthetic=True)
records=[]
for ident,d in tables.items():
 original=d.copy(deep=True);(out/'inputs'/f'{ident}.tsv').write_bytes(table_bytes(d));fig=calls[ident](d)
 design=DesignSpec(width_mm=180,height_mm=115,font_family='DejaVu Sans',spine_mode='minimal',grid='none',
   axis_bounds={'0':[.12,.18,.54,.68]},legend_zone=[.69,.32,.30,.45]) if ident!='P36' and ident!='P37' else DesignSpec(width_mm=180,height_mm=115)
 before=geometry_signature(fig) if False else None
 apply_design(fig,design);design.write(out/'inputs'/f'{ident}_design.json')
 export_figure(fig,d,out/'python',ident,meta)
 pd.testing.assert_frame_equal(original,d)
 receipt=json.loads((out/'python'/ident/f'{ident}.json').read_text(encoding='utf-8'))
 for file,digest in receipt['output_sha256'].items(): assert hashlib.sha256((out/'python'/ident/file).read_bytes()).hexdigest()==digest
 records.append({'id':ident,'renderer':receipt['figure_spec']['kind'],'input_hash':receipt['input_hash'],'layout_audit':audit_layout(fig)})
 plt.close(fig)

def rejects(fn):
 try: fn()
 except (ValueError,TypeError,FileExistsError): return
 raise AssertionError('Invalid input accepted')
rejects(lambda:plot_xy_points(pd.concat([tables['P33'],tables['P33'].iloc[:1]]),palette,'X','Y',unit_label='unit'))
rejects(lambda:plot_grouped_estimates(tables['P34'].iloc[:-1],palette,'estimate',interval_label='interval'))
bad=tables['P34'].copy();bad.loc[0,'lower']=100
rejects(lambda:plot_grouped_estimates(bad,palette,'estimate',interval_label='interval'))
bad=tables['P35'].astype({'left':float}).copy();bad.loc[1,'left']=.5
rejects(lambda:plot_binned_distribution(bad,palette,'X',denominator_label='units'))
bad=tables['P35'].copy();bad.loc[0,'count']=-1
rejects(lambda:plot_binned_distribution(bad,palette,'X',denominator_label='units'))
rejects(lambda:plot_confusion_counts(tables['P36'].iloc[:-1],unit_label='units'))
bad=tables['P36'].astype({'count':float}).copy();bad.loc[0,'count']=.5
rejects(lambda:plot_confusion_counts(bad,unit_label='units'))
bad=tables['P37'].copy();bad.loc[1,'x']=bad.loc[0,'x']
rejects(lambda:plot_density_ridges(bad,palette,'X',density_label='density'))
rejects(lambda:DesignSpec(width_mm=-1).validate())
rejects(lambda:DesignSpec(axis_bounds={'0':[0,0,2,1]}).validate())
rejects(lambda:DesignSpec(statistical_threshold=.01))
rejects(lambda:design.write(out/'inputs'/'P37_design.json'))

# Check old renderer compatibility, input identity, and actionable bbox detection.
d=pd.DataFrame({'sample_id':['A','B','C','D'],'group':['Group A']*2+['Group B']*2,'value':[1.,2.,3.,4.]})
fig=plot_samples(d,palette,'Frozen value');fig.canvas.draw();signature=geometry_signature(fig);hashed=fig._omics_input_sha256
apply_design(fig,DesignSpec(width_mm=160,height_mm=110,x_tick_rotation=30,grid='y'))
assert geometry_signature(fig)==signature and fig._omics_input_sha256==hashed
fig.text(.5,.94,'Heading one');fig.text(.5,.94,'Heading two')
fig.text(-.1,.3,'Outside');audit=audit_layout(fig)
assert any(i['kind']=='heading_overlap' for i in audit['issues'])
assert any(i['kind']=='text_outside_canvas' for i in audit['issues'])
plt.close(fig)
fig=plt.figure();axes=named_layout(fig,{'main':[.1,.18,.65,.65],'legend':[.8,.2,.18,.6]});assert set(axes)=={'main','legend'};plt.close(fig)
font=resolve_font('DejaVu Sans','Demo ABC 123')
report={'status':'SYNTHETIC_PASS','python_bundles':len(records),'invalid_input_checks':12,
 'appearance_invariance':'Exact table stamp, artist data arrays/geometry/scales; no palette or data-statistic mutation',
 'records':records,'limits':'Software validation; synthetic fixtures; visual approval separate','resolved_demo_font':font}
(out/'python_test_receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'bundles':len(records),'layout_warnings':sum(len(r['layout_audit']['issues']) for r in records)}))
