"""Bind actual screen observations to current exports; never infer acceptance."""
from pathlib import Path
import argparse,copy,json,shutil
from audit_all_figures import ROOT,examine,sha
from build_review_browser import build

def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def stage(refined,repairs):
    target=ROOT/'examples/refined-v060';repair_target=ROOT/'examples/gallery/repairs-v060';review=ROOT/'examples/review-v060'
    for p in [target,repair_target,review]:
        if p.exists():raise FileExistsError('Preserve prior assembly; use a fresh destination')
    shutil.copytree(refined,target);shutil.copytree(repairs,repair_target);review.mkdir()
    report=json.loads((ROOT/'examples/review-v050/review-index.json').read_text(encoding='utf8'))
    rows=copy.deepcopy(report['records']);changed={r['id'] for r in json.loads((repairs/'render-manifest.json').read_text())['records']}
    for r in rows:
        key=r['id'];r['visual_review']=dict(status='COMPOSITION_OVERVIEW_REVIEWED' if r['components'] else 'INDIVIDUAL_SCREEN_REVIEWED',
            scope='composition_overview_and_component_identity' if r['components'] else 'individual_full_image_on_screen',
            note='Actual two-independent-image screen inspection; viewer may resize. Final paper size remains unassessed.',png_sha256=r['sha256']['png'],final_size_inspected=False)
        if r['components']:
            r['visual_review']['note']+=' Master retains its original component versions and colours; expanded components use separately versioned current exports.'
            r['frozen_master_components']=r['components'][:]
        if key in changed:
            r['previous_assets']=r['assets'];r['previous_sha256']=r['sha256'];folder=repair_target/key
            r.update(examine(dict(id=key,collection='refined display repair',paths={e:folder/(key+'.'+('json' if e=='meta' else e)) for e in ['png','svg','pdf','meta']},expected_sha256=sha(folder/(key+'.png'))),178))
            r['preferred']=True;r['components']=[]
    manifest=json.loads((target/'manifest.json').read_text())
    for item in manifest['records']:
        key=item['id'];folder=target/key
        r=examine(dict(id=key,collection='community design alternative',paths={e:folder/(key+'.'+('json' if e=='meta' else e)) for e in ['png','svg','pdf','meta']},expected_sha256=item['png_sha256']),178)
        r.update(components=[],preferred=True);rows.append(r)
    report.update(version='0.6.0',scope='438 existing full image/overview inspections, 32 separately revised exports and five new community-informed alternatives',records=rows,
        counts=dict(current_exports=len(rows),baseline_exports=438,repaired_current_versions=32,new_alternatives=5),
        limitations=['Screen inspection is not calibrated paper proof','126 composition masters preserve historical component bytes; current components are separately versioned','All measurable PDF spans can be enlarged in a separate reading edition; this does not make an oversized master a usable manuscript figure','No native R package analysis or biological inference executed'])
    write(review/'figure-index.json',report);print(json.dumps(report['counts']))

def finalize(observations):
    review=ROOT/'examples/review-v060';report=json.loads((review/'figure-index.json').read_text());obs=json.loads(observations.read_text(encoding='utf8'))
    bound={r['id']:r for r in obs['records']};assert len(bound)==37
    for r in report['records']:
        if r['collection'] in ['refined display repair','community design alternative']:
            record=bound.pop(r['id']);assert record['png_sha256']==r['sha256']['png'] and record['scope']=='individual_full_image_on_screen'
            r['visual_review']=dict(record,status='INDIVIDUAL_SCREEN_REVIEWED',final_size_inspected=False)
    assert not bound
    report['counts'].update(individual_screen_inspected=sum(not r['components'] for r in report['records']),composition_overviews_inspected=126,physical_size_visually_accepted=0)
    write(review/'figure-index.json',report);write(review/'review-index.json',report)
    portable=ROOT/'skills/transcriptomics-figure-workbench/assets/refined-gallery';shutil.copytree(ROOT/'examples/refined-v060',portable)
    print(json.dumps(report['counts']))

def navigation():
    review=ROOT/'examples/review-v060';report=json.loads((review/'figure-index.json').read_text());reading=json.loads((ROOT/'examples/reading-v060/reading-index.json').read_text())
    assert sha(review/'figure-index.json')==reading['source_index_sha256']
    for r in report['records']:
        q=next(x for x in reading['records'] if x['id']==r['id']);assert q['source_sha256']==r['sha256']['pdf']
        r['reading']=dict(pdf='examples/reading-v060/'+q['file'],page=q['start_page'],pages=q['page_count'],strategy=q['strategy'],source_pdf_sha256=q['source_sha256'])
    write(review/'review-index.json',report);build(review/'review-index.json',review/'index.html')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refined',type=Path);p.add_argument('--repairs',type=Path);p.add_argument('--observations',type=Path);p.add_argument('--navigation',action='store_true');a=p.parse_args()
    if a.navigation:navigation()
    elif a.observations:finalize(a.observations)
    else:stage(a.refined,a.repairs)
