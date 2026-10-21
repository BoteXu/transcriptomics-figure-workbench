"""Bounded handoff and coordinated-display contracts; no plotting imports."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.handoff import handoff_plan
from figure_workbench.handoff_contract import hash_value, validate_handoff
from figure_workbench.contracts import check_plan
from figure_workbench.linked import build_linked


def refused(call):
    try:call()
    except (ValueError,FileNotFoundError):return
    raise AssertionError('Invalid source or display contract was accepted')


def main():
    examples=SKILL/'assets/connected-examples'
    source=examples/'handoff/figure-handoff.json'
    p=handoff_plan(source);check_plan(p)
    assert p['rows']==96 and p['handoff']['execution_state']=='frozen_results_supplied'
    assert p['handoff']['caller_assertions_independently_verified'] is False
    with tempfile.TemporaryDirectory() as temporary:
        folder=Path(temporary);value=json.loads(source.read_text('utf8'))
        for name in ['small','medium','large','custom']:
            request_path=examples/name/'request.json';request=json.loads(request_path.read_text('utf8'))
            rendered=build_linked(request,request_path.parent,folder/('replay-'+name))
            assert (folder/('replay-'+name)/'index.html').read_bytes()==(examples/name/'index.html').read_bytes()
            assert rendered['html_sha256']==json.loads((examples/name/'manifest.json').read_text('utf8'))['html_sha256']
        (folder/'frozen.tsv').write_bytes((source.parent/'frozen.tsv').read_bytes())
        def save(v):
            (folder/'handoff.json').write_text(json.dumps(v),encoding='utf8');return folder/'handoff.json'
        path=save(value);p=handoff_plan(path)
        value['qc']['context_sha256']='0'*64
        value['binding_sha256']=hash_value({k:v for k,v in value.items() if k!='binding_sha256'})
        refused(lambda:handoff_plan(save(value)))
        refused(lambda:check_plan(p))
        value=json.loads(source.read_text('utf8'));value['execution']['state']='submitted'
        value['binding_sha256']=hash_value({k:v for k,v in value.items() if k!='binding_sha256'})
        refused(lambda:handoff_plan(save(value)))
        request=json.loads((examples/'small/request.json').read_text('utf8'))
        request['input']['path']=str(examples/'small/input.tsv')
        request['layout']={'columns':1,'width_px':900,'panel_height':300}
        result=build_linked(request,folder,folder/'single-column')
        assert result['rows']==48 and result['views']==3 and result['analysis_performed'] is False
        refused(lambda:build_linked(request,folder,folder/'single-column'))
        request['layout']['columns']=8;refused(lambda:build_linked(request,folder,folder/'bad-layout'))
        request['layout']['columns']=2;request['input']['sha256']='0'*64
        refused(lambda:build_linked(request,folder,folder/'bad-hash'))
        request['input']={'path':'fixture.tsv','sha256':''}
        text='object_id\tgroup\tx\ty\tz\nA\tState A\t1\t2\t3\nB\tState B\tNA\t4\t5\nC\tState C\t2\t3\t4\n'
        (folder/'fixture.tsv').write_text(text,encoding='utf8');request['input']['sha256']=hashlib.sha256((folder/'fixture.tsv').read_bytes()).hexdigest()
        result=build_linked(request,folder,folder/'missing')
        assert result['rows']==3 and sorted(result['unavailable_pairs'].values())==[0,1,1]
        (folder/'fixture.tsv').write_text(text.replace('B\tState B','A\tState B'),encoding='utf8');request['input']['sha256']=hashlib.sha256((folder/'fixture.tsv').read_bytes()).hexdigest()
        refused(lambda:build_linked(request,folder,folder/'ambiguous-identity'))
    print(json.dumps({'state':'CONNECTED_CONTRACTS_PASS','handoff_input_qc_source_mutations_refused':True,
                      'missing_pairs_explicit':True,'identity_and_layout_checked':True,'scientific_acceptance':False}))


if __name__=='__main__':main()
