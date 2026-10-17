"""Verify complete executable chapter packages and image-bound actual review."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan,read_json
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for base in [ROOT/'examples/chapters-v091',SKILL/'assets/chapter-gallery']:
        m=read_json(base/'manifest.json');assert len(m['records'])==58
        for r in m['records']:
            assert r['plot_capability']=='IMPLEMENTED_WITH_EXECUTABLE_EXAMPLE' and r['readability']['state']=='MEASUREMENT_PASS'
            assert r['visual_review']['png_sha256']==r['sha256']['png']
            for key,digest in r['sha256'].items():assert sha(base/r['assets'][key])==digest
            p=base/r['assets']['spec'];make_plan(read_json(p),p.parent)
            assert r['scientific_acceptance'] is False
    print(json.dumps(dict(status='CHAPTER_RELEASE_PASS',chapters=58,code_input_exports_review_bound=True,analysis_performed=False)))
if __name__=='__main__':main()
