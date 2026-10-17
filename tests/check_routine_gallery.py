"""Check portable inputs, review bindings and selected set coverage, not beauty."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/transcriptomics-figure-workbench/scripts';sys.path.insert(0,str(SCRIPTS))


def main():
    from figure_workbench.contracts import make_plan
    from figure_workbench.study import study_plan
    from pypdf import PdfReader
    base=ROOT/'skills/transcriptomics-figure-workbench/assets/routine-gallery'
    doc=json.loads((base/'manifest.json').read_text(encoding='utf8'))
    proof=json.loads((base/'visual-review.json').read_text(encoding='utf8'))
    records=doc['records'];assert len(records)==43
    assert len([r for r in records if r['stage']!='reading' and r['assay']=='bulk'])==15
    assert len([r for r in records if r['stage']!='reading' and r['assay']=='single_cell'])==23
    by={r['id']:r for r in proof['records']};assert len(by)==43
    assert not proof['universal_aesthetic_approval'] and not proof['scientific_acceptance']
    for row in records:
        for name,relative in row['assets'].items():
            p=(base/relative).resolve();assert base.resolve() in p.parents and p.is_file()
        png=base/row['assets']['png'];sha=hashlib.sha256(png.read_bytes()).hexdigest()
        assert sha==row['png_sha256']==by[row['id']]['png_sha256']
        assert by[row['id']]['notes'] and not by[row['id']]['scientific_acceptance']
        p=base/row['assets']['spec'];s=json.loads(p.read_text(encoding='utf8'));make_plan(s,p.parent)
    for assay,count in [('bulk',15),('single_cell',23)]:
        m=json.loads((base/(assay+'.manifest.json')).read_text(encoding='utf8'))
        plan=study_plan(m,'帮我把结果画成整套图',base)
        assert plan['state']=='FIGURE_SET_PLANNED' and len(plan['panels'])==count
    assert len(PdfReader(base/'Bulk_and_SingleCell_FigureBook.pdf').pages)==43
    print(json.dumps(dict(state='ROUTINE_GALLERY_BINDINGS_PASS',portable_specs=43,screen_review_bindings=43,pdf_pages=43,aesthetic_approval=False,scientific_acceptance=False)))


if __name__=='__main__':main()
