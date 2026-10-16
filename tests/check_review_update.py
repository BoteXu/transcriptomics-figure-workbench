"""Verify the exact reviewed bytes, source preservation and portable new gallery."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    report=json.loads((ROOT/'examples/review-v050/review-index.json').read_text(encoding='utf8'));rows=report['records'];by={r['id']:r for r in rows}
    assert len(rows)==len(by)==438 and report['counts']['individual_screen_inspected']==40
    assert sum(r['print_screen']['status']=='REFLOW_OR_LARGER_FORMAT' for r in rows)==139
    for r in rows:
        for ext,p in r['assets'].items():assert sha(ROOT/p)==r['sha256'][ext]
        assert r['visual_review']['png_sha256']==r['sha256']['png'] and r['scientific_acceptance'] is False
        assert set(r['components'])<=set(by)
        for ext,p in r.get('previous_assets',{}).items():assert sha(ROOT/p)==r['previous_sha256'][ext]
    assert sum(bool(r['components']) for r in rows)==126
    for row in json.loads((ROOT/'examples/design-v050/manifest.json').read_text())['records']:
        key=row['id'];folder=ROOT/'examples/design-v050'/key;assert sha(ROOT/row['source'])==row['source_sha256']
        portable=ROOT/'skills/transcriptomics-figure-workbench/assets/design-gallery'/key
        for file in folder.iterdir():assert sha(file)==sha(portable/file.name)
    old=json.loads((ROOT/'examples/gallery/publication-v030/review-index.json').read_text())['records'];oldby={r['id']:r for r in old}
    for key in ['R01','R02','R03','R07','R16']:
        receipt=json.loads((ROOT/by[key]['assets']['meta']).read_text());previous=json.loads((ROOT/'examples/gallery'/oldby[key]['assets']['meta']).read_text())
        assert receipt['frozen_graphical_geometry_sha256']==previous['frozen_graphical_geometry_sha256']
        assert receipt['input_sha256']==previous['input_sha256'] and receipt['coordinates_and_shapes_retained'] is True
    print(json.dumps(dict(status='REVIEW_UPDATE_BINDINGS_PASS',current_exports=438,legacy_preserved=True,repaired_geometry_preserved=5,scientific_acceptance=False)))
if __name__=='__main__':main()
