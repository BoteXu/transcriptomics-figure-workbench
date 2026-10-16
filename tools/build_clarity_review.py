"""Assemble export checks with an explicit artifact-bound human/model review file."""
from pathlib import Path
import argparse,copy,json,sys
from audit_all_figures import examine,sha
ROOT=Path(__file__).resolve().parents[1]

def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main(observations):
    manual=json.loads(observations.read_text(encoding='utf8'));base=ROOT/'examples/clarity-v070';rows=json.loads((base/'manifest.json').read_text())['records'];assert len(rows)==15
    observed={r['id']:r for r in manual['records']};assert set(observed)=={r['id'] for r in rows}
    old=json.loads((ROOT/'examples/review-v060/review-index.json').read_text(encoding='utf8'));report=copy.deepcopy(old);old_by={r['id']:r for r in old['records']};current=[]
    replacements={'T35':['CLR01'],'R16':['CLR02'],'R11':['CLR03','CLR04','CLR05','CLR06','CLR07','CLR08'],'E34':['CLR09'],'E41':['CLR10'],'E42':['CLR11']}
    for r in rows:
        k=r['id'];paths={e:base/k/(k+('.json' if e=='meta' else '.'+e)) for e in ['png','svg','pdf','meta']};review=copy.deepcopy(observed[k]);assert review['pdf_sha256']==sha(paths['pdf']) and review['png_sha256']==sha(paths['png'])
        assert review['scope']=='individual_full_pdf_page_nominal_178mm_on_screen' and review['target_width_mm']==178 and all(review['checks'].values()) and len(review['checks'])==6
        item=examine(dict(id=k,collection='clarity and extension',paths=paths,expected_sha256=r['png_sha256']),178)
        assert not item['pdf_baseline_outside_page'] and item['print_screen']['at_target_p10_pt']>=7.5
        receipt=json.loads(paths['meta'].read_text());assert receipt['workbench']['print_readability']['state']=='MEASUREMENT_PASS'
        # A second check uses the exported PDF page width, after guide layout.
        review.update(status='INDIVIDUAL_PDF_SCREEN_REVIEWED',calibrated_paper_proof=False,scientific_acceptance=False)
        item.update(visual_review=review,components=[],preferred=True,reading=dict(pdf=item['assets']['pdf'],page=1,pages=1,strategy='standalone_reflow',source_pdf_sha256=item['sha256']['pdf']))
        oldid=next((a for a,b in replacements.items() if k in b),None)
        if oldid:item.update(previous_assets=old_by[oldid]['assets'],previous_sha256=old_by[oldid]['sha256'],alternative_to=oldid)
        current.append(item)
    for r in report['records']:
        if r['id'] in replacements:r['preferred']=False;r['alternative_ids']=replacements[r['id']]
    report['records']+=current;report.update(version='0.7.0',scope='Historical review retained verbatim except preferred alternatives; fifteen new individually inspected PDF pages',counts=dict(current_exports=458,historical_exports=443,new_examples=15,new_modes=10,original_sources_with_alternatives=6,individual_screen_inspected=332,composition_overviews_inspected=126,nominal_178mm_pdf_pages_inspected=15,calibrated_paper_proofs=0),scientific_acceptance=False)
    report['limitations']=old['limitations']+['The fifteen new PDF pages were inspected on screen at nominal 178 mm/96 dpi; no calibrated print or independent second review.','140 old 178 mm size warnings remain attached to their original wide exports. New alternatives do not erase old warnings.']
    out=ROOT/'examples/review-v070';out.mkdir(exist_ok=False);write(out/'review-index.json',report);write(base/'self-review.json',dict(version='0.7.0',records=[r['visual_review'] for r in current],scientific_acceptance=False))
    pending=[]
    for r in old['records']:
        if r['print_screen']['status']=='REFLOW_OR_LARGER_FORMAT':pending.append(dict(id=r['id'],source_pdf_sha256=r['sha256']['pdf'],warning=r['print_screen'],alternative_ids=replacements.get(r['id'],[]),state='ALTERNATIVE_AVAILABLE_ORIGINAL_WARNING_RETAINED' if r['id'] in replacements else 'REMAINS_OPEN',next_action='Compare actual whole-panel reflow or selected complete exports at intended size; do not clear the original warning from a reading overview.'))
    assert len(pending)==140
    write(out/'remaining-size-review.json',dict(records=pending,count=140,priority_examples=['R04','R24','P10'],scientific_acceptance=False))
    from build_review_browser import build
    build(out/'review-index.json',out/'index.html')
    summary=dict(status='CLARITY_EXPORTS_AND_BOUND_REVIEW_ASSEMBLED',new_exports=15,modes=10,individual_PDF_pages_inspected=15,nominal_width_mm=178,minimum_exported_body_p10_pt=min(r['print_screen']['at_target_p10_pt'] for r in current),old_size_warnings_retained=140,original_sources_with_alternatives=6,current_exports=458,scientific_acceptance=False,calibrated_paper_proof=False)
    write(ROOT/'docs/validation-summary-v070.json',summary);print(json.dumps(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--observations',required=True,type=Path);main(p.parse_args().observations)
