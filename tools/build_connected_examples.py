"""Reuse published frozen coordinates to exercise handoffs and coordinated views; fit nothing."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.linked import build_linked
from figure_workbench.handoff_contract import prepare_handoff, hash_value
from figure_workbench.handoff import handoff_plan
from figure_workbench.registry import digest


def build(output):
    output=Path(output)
    if output.exists():raise ValueError('Choose a fresh example directory')
    output.mkdir(parents=True)
    records=[]
    for size in ['Small','Medium','Large','Custom']:
        original='Medium' if size=='Custom' else size
        folder=SKILL/'assets/method-scale-gallery'/('Scale_D01_Scatter3D_'+original)
        table=folder/(folder.name+'.tsv')
        spec=json.loads((folder/'example.spec.json').read_text('utf8'))
        request={'schema_version':1,'title':'One state geometry, three coordinated views',
                 'subtitle':'Inspect the supplied X, Y and Z coordinates together. Select an object in any panel to trace the same identity across the other projections and its exact stored values.',
                 'input':{'path':str(table),'sha256':digest(table)},'id_column':'object_id','group_column':'group',
                 'views':[{'id':a+b,'title':title,'x':a,'y':b,'x_label':a.upper()+' coordinate (a.u.)','y_label':b.upper()+' coordinate (a.u.)'}
                          for a,b,title in [('x','y','XY · state separation'),('x','z','XZ · depth and overlap'),('y','z','YZ · complementary structure')]],
                 'colors':{group:spec['theme']['palette_colors'][slot] for group,slot in spec['theme']['group_slots'].items()},
                 'context':{'independent_unit':'Synthetic objects; no donors or biological inference',
                            'scope':'Every stored object from the selected published scale fixture; no coordinate fitting or thinning',
                            'missingness':'All coordinate pairs supplied in this example. NA pairs in other data remain unavailable.',
                            'synthetic':True},
                 'layout':{'columns':2 if size=='Custom' else 'auto','width_px':1140 if size=='Custom' else 1440,'panel_height':350 if size=='Custom' else 320}}
        result=build_linked(request,folder,output/size.lower());records.append({'id':size,'page':size.lower()+'/index.html','rows':result['rows'],'layout':request['layout']})
    folder=SKILL/'assets/method-scale-gallery/Scale_D01_Scatter3D_Medium'
    spec=json.loads((folder/'example.spec.json').read_text('utf8'));spec['figure_id']='ConnectedHandoff_D01'
    context={'independent_unit':spec['provenance']['experimental_unit'],'contrast':spec['provenance']['contrast'],
             'method_version':'Frozen display fixture v0.11.0; no scientific model fitted','reference_version':'Authored D01 coordinate fixture v1',
             'units':'All X, Y and Z coordinates: arbitrary units','selected_scope':'All 96 supplied objects',
             'limitations':'Synthetic result-display integration test; neither biological evidence nor engine validation'}
    qc={'state':'passed','input_sha256':spec['input']['sha256'],'context_sha256':hash_value(context),
        'review_reference':'Fixture identity, schema, units and exact-byte check; no scientific QC acceptance'}
    prepare_handoff(folder/spec['input']['path'],spec,context,qc,
                    {'state':'frozen_results_supplied','source_reference':'Published authored frozen fixture; no server job claimed'},
                    [{'id':'fixture','reference':'method-scale-gallery / D01 / Medium','version':'0.11.0','locator':'complete frozen TSV','sha256':spec['input']['sha256']}],output/'handoff')
    plan=handoff_plan(output/'handoff/figure-handoff.json')
    # Plans contain local paths and source identity; keep them out of public examples.
    assert plan['rows']==96 and plan['state']=='PREFLIGHT_ONLY'
    index='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Coordinated frozen result examples</title><style>body{max-width:950px;margin:50px auto;padding:0 24px;font:16px/1.7 Arial;color:#294653;background:#f3f6f7}a{color:#087b83}li{padding:10px 0}small{color:#6e818b}</style><h1>Coordinated frozen result examples</h1><p>Existing three-dimensional state geometry, extended with shared-identity inspection. No new analysis, embedding or data reduction.</p><ul>'
    for r in records:index+='<li><a href="'+r['page']+'">'+r['id']+' · '+str(r['rows'])+' objects</a> — '+str(r['layout']['columns'])+' columns</li>'
    index+='</ul><p><a href="handoff/figure-handoff.json">Portable result/QC/source handoff example</a> · <a href="../method-scale-gallery/index.html#Scale_D01_Scatter3D_Medium">Original three-dimensional chart remains available</a></p><small>Synthetic display fixtures. Export and browser success are separate from visual review and scientific validity.</small></html>'
    (output/'index.html').write_bytes(index.encode('utf8'))
    (output/'manifest.json').write_text(json.dumps({'schema_version':1,'records':records,'handoff':'handoff/figure-handoff.json','analysis_performed':False,'visual_acceptance':False},indent=2)+'\n',encoding='utf8')
    return {'state':'CONNECTED_EXAMPLES_PREPARED','examples':records,'handoff_preflight':True,'analysis_performed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    print(json.dumps(build(a.output)))
