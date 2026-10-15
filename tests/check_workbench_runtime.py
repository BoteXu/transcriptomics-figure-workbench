"""Render frozen fixtures serially; verify real exports and stale visual decisions."""
import copy
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan,read_json
from figure_workbench.pipeline import render_plan,restyle_spec
from figure_workbench.review import inspect_bundle,record_visual,verify_visual,VISUAL_CHECKS
from workbench_fixtures import create_fixtures


def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    inputs=output/'inputs';cases=create_fixtures(inputs,SKILL)
    rendered=[];geometry={}
    for name,spec in cases.items():
        result=render_plan(make_plan(spec,inputs),output)
        bundle=output/spec['figure_id'];receipt_path=bundle/(spec['figure_id']+'.json')
        receipt=read_json(receipt_path)
        # Public synthetic examples use portable source labels, never machine paths.
        receipt['source_file']='inputs/'+name+'.tsv'
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        assert not inspect_bundle(bundle)['issues']
        if name=='matrix':
            from PIL import Image
            for extension in ['png','tiff']:
                with Image.open(bundle/(spec['figure_id']+'.'+extension)) as image:
                    assert abs(image.info['dpi'][0]-600)<1
        geometry[name]=receipt['workbench']['quantitative_geometry_sha256']
        rendered.append({'name':name,'figure_id':spec['figure_id'],'rows':result['rows']})
    for name,preset in [('ma','presentation'),('forest','compact')]:
        spec=restyle_spec(cases[name],{'preset':preset,'font_family':'DejaVu Sans'},'WB_'+name+'_'+preset)
        render_plan(make_plan(spec,inputs),output)
        bundle=output/spec['figure_id'];receipt_path=bundle/(spec['figure_id']+'.json');receipt=read_json(receipt_path)
        receipt['source_file']='inputs/'+name+'.tsv'
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        assert receipt['workbench']['quantitative_geometry_sha256']==geometry[name]
        (inputs/(name+'-'+preset+'.spec.json')).write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
        rendered.append({'name':name+'-'+preset,'figure_id':spec['figure_id'],'geometry_preserved':True})
    bundle=output/'WB_ma'
    with tempfile.TemporaryDirectory(prefix='visual-record-test-') as temporary:
        record_path=Path(temporary)/'review.json'
        record=record_visual(bundle,'accepted',{k:True for k in VISUAL_CHECKS},
            'SYNTHETIC SOFTWARE TEST ONLY: checks are injected to exercise stale-review behavior, not actual visual acceptance.',record_path)
        assert verify_visual(bundle,record)['visual_acceptance']
        image=bundle/'WB_ma.svg';old=image.read_bytes();image.write_bytes(old+b'\n')
        assert verify_visual(bundle,record)['review_status']=='STALE_REVIEW'
        image.write_bytes(old)
        assert verify_visual(bundle,record)['visual_acceptance']
    try:render_plan(make_plan(cases['ma'],inputs),output)
    except FileExistsError:pass
    else:raise AssertionError('An existing figure bundle was overwritten')
    assert not inspect_bundle(bundle)['issues']
    html='<!doctype html><meta charset="utf-8"><title>Workbench v0.3 frozen previews</title><h1>SYNTHETIC DEMO · Workbench 0.3</h1><p>Frozen inputs only. Every image remains unreviewed until separately inspected.</p>'
    for row in rendered:
        fid=row['figure_id'];html+='<h2>'+row['name']+'</h2><a href="'+fid+'/'+fid+'.pdf"><img width="760" src="'+fid+'/'+fid+'.png" alt="'+row['name']+'"></a>'
    (output/'index.html').write_text(html,encoding='utf8')
    report={'status':'WORKBENCH_RUNTIME_PASS','rendered':rendered,'restyles_preserve_geometry':True,
            'changed_exports_invalidate_visual_review':True,'existing_outputs_preserved':True,
            'scientific_analysis_executed':False,'actual_visual_acceptance':False}
    (output/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))


if __name__=='__main__':main(sys.argv[1])
