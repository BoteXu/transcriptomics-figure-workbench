"""Rebind a source-only regression fix only when every final PNG is identical."""
import argparse, json, shutil
from pathlib import Path
from package_editorial_review import ROOT, SKILL, load, write, sha, inline_rows

def refresh(rendered,fixtures):
    fresh=load(rendered/'manifest.json')['records']
    changes={r['id']:(r,next(Path(x).with_suffix('') for x in r['result']['files'] if x.endswith('.png'))) for r in fresh}
    origins={r['id']:r.get('origin_spec') for r in load(fixtures/'manifest.json')['records']}
    for base in [ROOT/'examples/editorial-v092',SKILL/'assets/editorial-gallery']:
        doc=load(base/'manifest.json')
        for row in doc['records']:
            if row['id'] not in changes:continue
            result,stem=changes[row['id']]
            assert sha(stem.with_suffix('.png'))==row['sha256']['png'],'Changed pixels require a new actual review: '+row['id']
            for ext in ['svg','pdf','png','tsv']:
                target=base/row['assets'][ext];shutil.copyfile(stem.with_suffix('.'+ext),target);row['sha256'][ext]=sha(target)
            row['readability']=result['result']['print_readability']
            write((base/row['assets']['png']).parent/'review.json',row)
        write(base/'manifest.json',doc);inline_rows(base/'index.html',doc['records'])
    for name in ['study','chapter','subgroup','chapter-layouts']:
        base=SKILL/('assets/'+name+'-gallery');doc=load(base/'manifest.json')
        for row in doc['records']:
            spec=(base/row['assets']['spec']).resolve()
            matches=[k for k,v in origins.items() if v and (SKILL/v).resolve()==spec and k in changes]
            if not matches:continue
            assert len(matches)==1;k=matches[0];result,stem=changes[k]
            assert sha(stem.with_suffix('.png'))==row['sha256']['png']
            for ext in ['svg','pdf','png','tsv']:
                target=base/row['assets'][ext];shutil.copyfile(stem.with_suffix('.'+ext),target);row['sha256'][ext]=sha(target)
            row['readability']=result['result']['print_readability']
            review=base/row['review'] if 'review' in row else (base/row['assets']['png']).parent/'review.json'
            write(review,row)
        write(base/'manifest.json',doc);inline_rows(base/'index.html',doc['records'])
    print(json.dumps(dict(status='IDENTICAL_FINAL_PIXELS_REBOUND',figures=len(changes),new_visual_acceptance_claimed=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rendered',type=Path,required=True);p.add_argument('--fixtures',type=Path,required=True);a=p.parse_args();refresh(a.rendered,a.fixtures)
