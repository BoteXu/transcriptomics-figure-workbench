"""CI rendering of the real shared handoff; scientific analysis is not performed."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.handoff import handoff_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.review import inspect_bundle


def main(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    p=handoff_plan(SKILL/'assets/connected-examples/handoff/figure-handoff.json')
    result=render_plan(p,out);fid=p['spec']['figure_id'];bundle=out/fid
    receipt=json.loads((bundle/(fid+'.json')).read_text('utf8'))
    assert result['rows']==96 and not inspect_bundle(bundle)['issues']
    lineage=receipt['workbench']['handoff']
    assert lineage['binding_sha256']==p['handoff']['binding_sha256'] and 'path' not in lineage
    assert lineage['execution_state']=='frozen_results_supplied' and lineage['caller_assertions_independently_verified'] is False
    report={'state':'HANDOFF_RENDER_PASS','objects':96,'input_qc_source_lineage_preserved':True,'analysis_performed':False,'visual_acceptance':False}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))


if __name__=='__main__':main(sys.argv[1])
