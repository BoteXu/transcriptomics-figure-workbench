"""Frozen encodings, invalid channels, size HOLD and review-scope acceptance."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from render_frozen_table import load_table,render
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.review import record_visual,verify_visual,VISUAL_CHECKS
from figure_workbench.registry import digest

def refused(call,contains=None):
    try:call()
    except (ValueError,TypeError,KeyError) as e:
        if contains:assert contains in str(e)
    else:raise AssertionError('Invalid input accepted')
    finally:plt.close('all')

def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);base=ROOT/'examples/design-v050/inputs'
    manifest=json.loads((base.parent/'manifest.json').read_text())['records'];invalid=0
    for row in manifest:
        key=row['id'];spec=json.loads((base/(key+'.spec.json')).read_text());data=load_table(base/(key+'.tsv'),spec['renderer'],spec['parameters'])
        original=data.copy(deep=True);fig,audit=render(spec['renderer'],data,spec['parameters'],spec['theme']);pd.testing.assert_frame_equal(original,data);plt.close(fig)
        assert row['source_sha256']==digest(ROOT/row['source']) and row['input_sha256']==digest(base/(key+'.tsv'))
        if key=='VIS03':
            old=pd.read_csv(ROOT/row['source'],sep='\t',dtype={'series':str});pd.testing.assert_frame_equal(data,old,check_dtype=False)
        if key=='VIS02':
            old=pd.read_csv(ROOT/row['source'],sep='\t');assert data['value'].tolist()==old['value'].tolist()
        if key=='VIS05':
            old=pd.read_csv(ROOT/row['source'],sep='\t');assert data['x'].tolist()==old['x'].tolist() and data['y'].tolist()==old['y'].tolist()
        if key in ['VIS01','VIS02','VIS03']:
            operations={
              'VIS01':[lambda d:d.loc.__setitem__((d.record_type=='density','density'),-1),
                       lambda d:d.loc.__setitem__((d.record_type=='summary','inner_upper'),-99),
                       lambda d:d.loc.__setitem__((d.record_type=='density','x'),0)],
              'VIS02':[lambda d:d.loc.__setitem__((0,'value'),99),lambda d:d.loc.__setitem__((0,'row_group'),'inconsistent')],
              'VIS03':[lambda d:d.loc.__setitem__((0,'area'),-1),lambda d:d.loc.__setitem__((0,'value'),99999)]}[key]
            for mutation in operations:
                bad=data.copy();mutation(bad);refused(lambda:render(spec['renderer'],bad,spec['parameters'],spec['theme']));invalid+=1
            params=copy.deepcopy(spec['parameters']);params['options']['unknown']=1;refused(lambda:render(spec['renderer'],data,params,spec['theme']));invalid+=1
    # The same actual figure passes at its declared width and is blocked at 40mm.
    spec=json.loads((base/'VIS02.spec.json').read_text());spec['figure_id']='SIZE_PASS'
    render_plan(make_plan(spec,base),output);bundle=output/'SIZE_PASS'
    small=copy.deepcopy(spec);small['figure_id']='SIZE_HOLD';small['export']['target_width_mm']=40
    refused(lambda:render_plan(make_plan(small,base),output),'PRINT_SIZE_HOLD');assert not (output/'SIZE_HOLD').exists()
    checks={k:True for k in VISUAL_CHECKS};note='SYNTHETIC SOFTWARE TEST ONLY: injected checks test review scope and staleness, not a human visual acceptance.'
    for inspection in [None,dict(scope='contact_overview',width_mm=178,artifacts=['png']),dict(scope='individual_at_target_width',width_mm=89,artifacts=['png']),dict(scope='individual_at_target_width',width_mm=178,artifacts=[{}])]:
        refused(lambda:record_visual(bundle,'accepted',checks,note,output/'must-not-write.json',inspection))
    inspection=dict(scope='individual_at_target_width',width_mm=178,artifacts=['png'])
    record=record_visual(bundle,'accepted',checks,note,output/'software-review-test.json',inspection);assert verify_visual(bundle,record)['visual_acceptance']
    svg=bundle/'SIZE_PASS.svg';old=svg.read_bytes();svg.write_bytes(old+b'\n');assert verify_visual(bundle,record)['review_status']=='STALE_REVIEW';svg.write_bytes(old)
    report=dict(status='DESIGN_RUNTIME_PASS',frozen_views_rendered=5,invalid_channel_cases=invalid,size_gate_blocks_before_bundle=True,target_review_scope_enforced=True,changed_artifact_invalidates=True,scientific_acceptance=False,actual_visual_acceptance=False)
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main(sys.argv[1])
