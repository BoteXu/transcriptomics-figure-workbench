"""Assemble actual review observations and source-bound display versions.

The baseline and rendered directories are explicit local inputs; no private
machine paths are serialized into public artifacts. This is not an auto-review.
"""
from pathlib import Path
import argparse, collections, copy, json, shutil
from audit_all_figures import ROOT, examine, sha
from build_review_browser import build
from PIL import Image, ImageDraw

NOTES={
 'R01':'Reduced overlapping fill and used distinct teal/coral/blue; individual revised image inspected. Radial comparison remains secondary to VIS03.',
 'R02':'Reduced muddy overlapping fill and aligned legend colours; exact geometry retained. Prefer VIS03 for precise category comparison.',
 'R03':'Moved all 28 state labels left to separate text from the first coloured points; individual revised image inspected.',
 'R07':'Neutralised nonsignificant edges and retained distinct significant colours; edge geometry and widths unchanged.',
 'R16':'Raised point opacity from 0.45 to 0.65; zero-centred colour values unchanged. Near-zero dots remain intentionally pale.',
 'P01':'Individual full image inspected: guide lane and labels legible; final physical-size review remains separate.',
 'K01':'Individual full composition inspected; preserve independent panel exports and review at intended page width.',
 'R04':'Individual full image inspected: dense legend needs a large format or question-led selection; not approved at paper width.',
 'R11':'Individual full image inspected: dense labels need a larger format; no label omission has been introduced.',
 'R22':'Individual full image inspected: labels and guides checked; target-size acceptance remains pending.'}
NEW_NOTES={
 'VIS01':'Restrained half-eye silhouettes, nested supplied display bounds and aligned numerical lane; shapes are frozen illustrative profiles, not inferred uncertainty.',
 'VIS02':'Separated row/column groups with narrow annotation strips and visible gaps; moved row labels clear of the strips; one shared signed colour scale.',
 'VIS03':'Three aligned linear profiles show the exact R02 primary and secondary quantities without overlapping radial fills; all categories retained.',
 'VIS04':'Point-and-interval replacement for P34 uses a compact numerical lane; supplied estimates and bounds unchanged.',
 'VIS05':'Six distinct category colours and explicit label anchors make the stored T19 coordinates easier to follow; no embedding was fitted.'}

# These observations apply only to the actual bytes inspected in this review.
# A rerender must not inherit the observations just because it kept the same ID.
REVIEWED_PNG={
 'VIS01':'2a453f9a275cec245300ac68439c08781b2345fbd3bf09e4fe42809d2521dd60',
 'VIS02':'ec9187803376d9de0fa35665a5605293e7091be54e1277dfde467ba38ab62429',
 'VIS03':'ee283a5bbaf2d7cd1403887cb5b4379394bf8d6365f62703aeab7fe8f52d2cb0',
 'VIS04':'0e8d0813ef652242d6881f1f5f6251af9a1dd6cf2b4312d54cd0c490f14c408f',
 'VIS05':'3a371e1098c69e40baacf8c034f80db1a117c4dc675737026ea5878588acb580',
 'R01':'0c3e3085ebbac1bcd18d16cbd068041bce292293d11db17986481df65b6627bf',
 'R02':'f3a9ceae28abe892a6cfa6967c4ddfe3756224ceae1823d83999ad6d4c94305b',
 'R03':'a9e51296994c1b8bd94b2c187d5007a9c283a87e643ce6eec11b2823efb7499b',
 'R07':'7644204dc27d121cb9b4eca5b969bc778e631a1688163745900d36526f752f94',
 'R16':'52dedfde0ef13cc7ee7e90863aa3c6ff5d48d7740d0744a0f3782bb8b5374cf1'}

def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def assemble(base,design,repairs):
    assert sha(base)=='8abd842837ecb788da5f66fbeabab593869abfba036277a6723b9eaf91bd44b3', 'Unknown baseline: perform a new visual review'
    assert sha(ROOT/'examples/gallery/publication-v030/source-plan.json')=='f2a80299098ea7c1467cfd0a2711efb77d77e8aa5cbaed5c5be33311cac7f3d1'
    for key,expected in REVIEWED_PNG.items():
        assert sha((design if key.startswith('VIS') else repairs)/key/(key+'.png'))==expected, 'Changed pixels require a new review'
    target=ROOT/'examples/design-v050';repair_target=ROOT/'examples/gallery/repairs-v050';review=ROOT/'examples/review-v050'
    for p in [target,repair_target,review]:
        if p.exists():raise FileExistsError('Preserve prior assembly; use a clean release checkout')
    shutil.copytree(design,target);shutil.copytree(repairs,repair_target);review.mkdir()
    baseline=json.loads(base.read_text(encoding='utf8'));records=copy.deepcopy(baseline['records'])
    assert len(records)==433
    plan=json.loads((ROOT/'examples/gallery/publication-v030/source-plan.json').read_text(encoding='utf8'))
    parts={r['id']:r['components'] for r in plan['compositions']}
    detail=set(NOTES)|{'PKG'+str(n).zfill(2) for n in range(1,26)}
    for r in records:
        key=r['id'];r['components']=parts.get(key,[]);r['preferred']=key.startswith('PKG') or key in NOTES and key.startswith('R0') or key=='R16'
        r['visual_review']=dict(status='INDIVIDUAL_SCREEN_REVIEWED' if key in detail else 'OVERVIEW_REVIEWED',
            scope='individual_full_image_on_screen' if key in detail else 'nine_per_contact_plate',
            note=NOTES.get(key,'Individual package example inspected for hierarchy, labels, guides, colour and clipping; no native analysis package run.' if key.startswith('PKG') else 'Overview screened for broad hierarchy, crowding, colour and blank/clipped regions; small labels and target-size acceptance remain unassessed.'),
            final_size_inspected=False,png_sha256=r['sha256']['png'])
        if key in ['R01','R02','R03','R07','R16']:
            r['previous_assets']=r['assets'];r['previous_sha256']=r['sha256']
            folder=repair_target/key
            now=examine(dict(id=key,collection='atlas repaired',paths={e:folder/(key+'.'+('json' if e=='meta' else e)) for e in ['png','svg','pdf','meta']},expected_sha256=sha(folder/(key+'.png'))),178)
            r.update({k:v for k,v in now.items() if k!='visual_review'})
            r['visual_review'].update(png_sha256=r['sha256']['png']);r['preferred']=True
        if r['print_screen']['status']=='REFLOW_OR_LARGER_FORMAT':r['visual_review']['note']+=' Font screen requests reflow or a larger format; no print-size approval.'
    design_manifest=json.loads((target/'manifest.json').read_text(encoding='utf8'))
    new_review=[]
    for item in design_manifest['records']:
        key=item['id'];folder=target/key
        assert sha(ROOT/item['source'])==item['source_sha256']
        r=examine(dict(id=key,collection='design alternative',paths={e:folder/(key+'.'+('json' if e=='meta' else e)) for e in ['png','svg','pdf','meta']},expected_sha256=item['png_sha256']),178)
        r.update(preferred=True,components=[])
        r['visual_review']=dict(status='INDIVIDUAL_SCREEN_REVIEWED',scope='individual_full_image_on_screen',note=NEW_NOTES[key],final_size_inspected=False,png_sha256=item['png_sha256'])
        records.append(r);new_review.append(dict(id=key,**r['visual_review'],scientific_acceptance=False))
        item['status']='INDIVIDUAL_SCREEN_REVIEWED'
    write(target/'manifest.json',design_manifest);write(target/'self-review.json',dict(schema_version=1,records=new_review,scope='Actual PNG screen inspection; PDF/SVG structural checks, not full pixel parity or a paper proof',scientific_acceptance=False))
    allids={r['id'] for r in records};assert len(allids)==len(records)==438
    assert all(set(r['components'])<=allids for r in records)
    report=dict(schema_version=1,version='0.5.0',scope='433 baseline exports overview-screened; 5 additional alternatives; 5 repaired versions replace current pointers while old bytes remain',
        counts=dict(current_exports=438,baseline_exports=433,new_alternatives=5,repaired_current_versions=5,overview_plates_inspected=49,
            individual_screen_inspected=sum(r['visual_review']['scope']=='individual_full_image_on_screen' for r in records),
            physical_size_visually_accepted=0,print_screen=dict(collections.Counter(r['print_screen']['status'] for r in records))),
        automatic_checks=baseline['automatic_checks'],limitations=baseline['limitations']+['No claim that all 438 figures received final-size individual inspection','Individual full-image views may be resized by the image viewer','Historical atlas is immutable; the v0.5 review browser selects current repairs'],records=records,scientific_acceptance=False)
    write(review/'review-index.json',report);write(review/'baseline-index.json',baseline)
    build(review/'review-index.json',review/'index.html')
    # Compact contact preview, not another visual-acceptance claim.
    canvas=Image.new('RGB',(1800,1450),'#edf1f3');draw=ImageDraw.Draw(canvas)
    for i,item in enumerate(design_manifest['records']):
        x,y=(i%3)*600,(i//3)*725;key=item['id'];draw.text((x+20,y+15),key+' | '+item['view'],fill='#243449')
        with Image.open(target/key/(key+'.png')) as im:
            im.thumbnail((570,665));tile=im.convert('RGB');canvas.paste(tile,(x+15+(570-tile.width)//2,y+45));tile.close()
    canvas.save(ROOT/'docs/design-alternatives-v050.jpg',quality=94);canvas.close()
    portable=ROOT/'skills/transcriptomics-figure-workbench/assets/design-gallery';shutil.copytree(target,portable)
    print(json.dumps(report['counts']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True,type=Path);p.add_argument('--design',required=True,type=Path);p.add_argument('--repairs',required=True,type=Path);a=p.parse_args();assemble(a.baseline,a.design,a.repairs)
