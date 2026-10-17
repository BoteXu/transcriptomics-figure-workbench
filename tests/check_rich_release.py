"""Check the current preferred study gallery and its portable exact inputs."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.study import study_plan
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for base in [ROOT/'examples/rich-v091',SKILL/'assets/study-gallery']:
        manifest=load(base/'manifest.json');assert len(manifest['records'])==25
        for row in manifest['records']:
            for name,digest in row['sha256'].items():assert sha(base/row['assets'][name])==digest
            s=load(base/row['assets']['spec']);assert sha((base/row['assets']['spec']).parent/s['input']['path'])==s['input']['sha256']
            assert row['visual_review']['png_sha256']==row['sha256']['png']
        for assay,number in [('bulk',11),('single_cell',14)]:
            p=base/'study-manifests'/(assay+'.json');plan=study_plan(load(p),'做一套文章组图',p.parent);assert plan['state']=='FIGURE_SET_PLANNED' and len(plan['panels'])==number
            assert not any(d['state']=='COMPARE_POLISHED_EXTENSIONS' for d in plan['presentation_decisions'])
    print(json.dumps(dict(status='RICH_RELEASE_PASS',figures=25,all_current_inputs_and_hashes_checked=True,scientific_acceptance=False)))
if __name__=='__main__':main()
