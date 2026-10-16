"""Check the exact public review ledger and runnable portable study manifests."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';BASE=ROOT/'examples/validated-v090'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.study import study_plan

def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=load(BASE/'manifest.json');assert m['counts']==dict(source=313,volume=261,composition=146,reference=38,study=25,**{'study-layout':8},special=12)
    assert len({r['key'] for r in m['records']})==803
    for row in m['records']:
        for kind,digest in row['sha256'].items():assert sha(BASE/row['assets'][kind])==digest,row['key']+' '+kind
        assert row['visual_review']['png_sha256']==row['sha256']['png']
        assert not row['visual_review']['independent_second_review'] and not row['visual_review']['calibrated_paper_proof']
        if row['section'] in ['study','study-layout']:
            s=load(BASE/row['assets']['spec']);assert sha((BASE/row['assets']['spec']).parent/s['input']['path'])==s['input']['sha256']
    for base in [BASE,SKILL/'assets/study-gallery']:
        for assay,number in [('bulk',11),('single_cell',14)]:
            path=base/'study-manifests'/(assay+'.json');manifest=load(path)
            for request in ['画质控图','展示差异和通路','做一套文章组图']:
                plan=study_plan(manifest,request,path.parent);assert plan['state']=='FIGURE_SET_PLANNED'
            assert len(plan['panels'])==number
    assert 'fetch(' not in (BASE/'index.html').read_text(encoding='utf8'),'Offline gallery must not require a JSON request'
    print(json.dumps(dict(status='V090_REVIEW_RELEASE_PASS',pages=803,study_sets=2,ordinary_requests=6,scientific_acceptance=False)))

if __name__=='__main__':main()
