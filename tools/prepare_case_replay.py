"""Author a fresh coherent frozen study and apply current display preferences.

All values are fictional fixture construction. No scientific backend is run.
The publication-preference step preserves the exact freshly authored TSVs.
"""
import argparse,copy,json
from pathlib import Path
from build_routine_study_audit import build
from prepare_publication_study import prepare

def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def prepare_case(output,seed):
    output.mkdir(parents=True,exist_ok=False);raw=output/'authored';build(raw,seed=seed)
    manifests={a:json.loads((raw/(a+'.manifest.json')).read_text(encoding='utf8')) for a in ['bulk','single_cell']}
    records=[]
    for assay,m in manifests.items():
        for r in m['results']:
            key=Path(r['spec']).parent.name;records.append(dict(id=key,assay=assay,stage=r['role'],variant=False,width=260 if key.startswith('Subgroup_') else 240,png_sha256=None,assets=dict(spec=r['spec'],tsv=key+'/'+key+'.tsv')))
    choices=[('bulk_GSEADetail','bulk',{},240),('single_cell_GSEADetail','single_cell',{},240),
             ('Subgroup_01','single_cell',dict(ncols=2,composition='evidence'),260),
             ('Subgroup_03','single_cell',dict(ncols=3,composition='grid'),297),
             ('EnrichmentTracks','bulk',dict(ncols=3,nrows=1,panel_width=4.2,panel_height=4),297)]
    for source,assay,change,width in choices:
        original=raw/source/(source+'.spec.json');s=json.loads(original.read_text(encoding='utf8'));key=source+('_Custom' if change else '_Reading');folder=raw/key;folder.mkdir()
        (folder/(key+'.tsv')).write_bytes((original.parent/s['input']['path']).read_bytes());s['figure_id']=key;s['input']['path']=key+'.tsv';s['parameters'].get('options',s['parameters']).update(change);s['export']['target_width_mm']=width
        write(folder/(key+'.spec.json'),s);records.append(dict(id=key,assay=assay,stage='reading',variant=True,width=width,png_sha256=None,assets=dict(spec=key+'/'+key+'.spec.json',tsv=key+'/'+key+'.tsv')))
    write(raw/'manifest.json',dict(records=records,ordinary_requests=[],source_stage='Authored frozen inputs; no earlier image acceptance'))
    styled=output/'inputs';prepare(raw,styled)
    for assay,m in manifests.items():write(styled/(assay+'.manifest.json'),m)
    write(output/'case.json',dict(study_id='mock-transcriptomic-study-'+str(seed),seed=seed,independent_donors=12,nested_cells=900,tested_genes=1200,identities=5,markers_per_identity=4,analysis_performed=False,source='Explicit fictional frozen drawing fixture construction'))
    print(json.dumps(dict(state='COHERENT_REPLAY_INPUTS_PREPARED',seed=seed,figures=len(records))))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=int,default=20261018);a=p.parse_args();prepare_case(a.output,a.seed)
