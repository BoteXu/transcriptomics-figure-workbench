"""Portable artifact bindings and review scopes; standard library only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=ROOT/'examples/clarity-v070';m=json.loads((base/'manifest.json').read_text());reviews=json.loads((base/'self-review.json').read_text());current=json.loads((ROOT/'examples/review-v070/review-index.json').read_text());old=json.loads((ROOT/'examples/review-v060/review-index.json').read_text());warnings=json.loads((ROOT/'examples/review-v070/remaining-size-review.json').read_text())
    assert len(m['records'])==len(reviews['records'])==15 and len(current['records'])==458
    by={r['id']:r for r in reviews['records']};new={r['id']:r for r in current['records']};assert len(new)==458
    for r in m['records']:
        k=r['id'];spec=json.loads((base/'inputs'/(k+'.spec.json')).read_text());meta=json.loads((base/k/(k+'.json')).read_text());v=by[k]
        assert sha(base/k/(k+'.png'))==r['png_sha256']==v['png_sha256'] and sha(base/k/(k+'.pdf'))==v['pdf_sha256']
        assert v['scope']=='individual_full_pdf_page_nominal_178mm_on_screen' and v['inspected_artifacts']==['pdf'] and not v['calibrated_paper_proof'] and not v['scientific_acceptance']
        assert meta['workbench']['version']=='0.7.0' and meta['workbench']['print_readability']['state']=='MEASUREMENT_PASS'
        assert new[k]['print_screen']['at_target_p10_pt']>=7.5 and not new[k]['pdf_baseline_outside_page']
        assert sha(base/'inputs'/(k+'.tsv'))==spec['input']['sha256']==r['input_sha256']
        if r['source']:assert sha(ROOT/r['source'])==r['source_sha256']
    for p in base.rglob('*'):
        if p.is_file():assert p.read_bytes()==(SKILL/'assets/clarity-gallery'/p.relative_to(base)).read_bytes()
    for r in old['records']:assert new[r['id']]['assets']==r['assets'] and new[r['id']]['sha256']==r['sha256']
    assert len(warnings['records'])==140 and sum(r['print_screen']['status']=='REFLOW_OR_LARGER_FORMAT' for r in current['records'])==140
    assert set(r['id'] for r in warnings['records'])==set(r['id'] for r in old['records'] if r['print_screen']['status']=='REFLOW_OR_LARGER_FORMAT')
    assert len(set(r['view'] for r in m['records']))==10
    print(json.dumps(dict(status='CLARITY_RELEASE_BINDINGS_PASS',examples=15,modes=10,current_exports=458,original_size_warnings_retained=140,scientific_acceptance=False)))
if __name__=='__main__':main()
