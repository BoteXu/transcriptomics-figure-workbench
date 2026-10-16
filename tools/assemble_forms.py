"""Copy the entire revised library with immutable history and honest review state."""
import argparse, copy, hashlib, json, re, shutil, struct, zlib
from pathlib import Path
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def set_dpi(path,dpi):
    raw=path.read_bytes();ppm=round(dpi/0.0254);data=b'pHYs'+struct.pack('>IIB',ppm,ppm,1)
    part=struct.pack('>I',9)+data+struct.pack('>I',zlib.crc32(data)&0xffffffff)
    chunks=[raw[:8]];at=8
    while at<len(raw):
        n=struct.unpack('>I',raw[at:at+4])[0];kind=raw[at+4:at+8]
        if kind!=b'pHYs':chunks.append(raw[at:at+n+12])
        if kind==b'IHDR':chunks.append(part)
        at+=n+12
    path.write_bytes(b''.join(chunks))


def label_audit(source,revised,title):
    old=E.parse(source).getroot();new=E.parse(revised).getroot();parent={c:p for p in old.iter() for c in p}
    norm=lambda s:re.sub(r'\s+',' ',s).strip()
    texts=[n for n in old.iter() if n.tag.endswith('}text')]
    after=norm(' '.join(' '.join(n.itertext()) for n in new.iter() if n.tag.endswith('}text')))
    absent=[]
    for n in texts:
        s=norm(' '.join(n.itertext()))
        if not s or s in after:continue
        furniture=bool(re.match(r'^(?:SYNTHETIC|PUBLIC COORDINATES|REFERENCE COLOR|Frozen display|Exact declared|Original structure|Software test fixture|Synthetic software fixture)',s))
        chain=[];p=n
        while p in parent:p=parent[p];chain.append(p.get('id',''))
        style=n.get('style','');size=re.search(r'(?:font-size:|font:)\s*([\d.]+)',style);size=float(size.group(1)) if size else float(n.get('font-size','0'))
        page_title='axes_' not in ' '.join(chain) and size>=10.5
        if not furniture and not page_title and s!=title:absent.append(s)
    return dict(status='PASS' if not absent else 'REPAIR_REQUIRED',missing_labels=absent,scope='literal text retention; no scientific assertion validation')


def prepare(source,compositions,plan):
    out=ROOT/'examples/forms-v080';out.mkdir(exist_ok=False)
    old=json.loads((ROOT/'examples/review-v070/review-index.json').read_text());bound=json.loads(plan.read_text());by={r['id']:r for r in bound['items']};rows=[];missing=[]
    engine=sha(SKILL/'assets/studio/form-polish.js')
    for original in old['records']:
        k=original['id'];base=compositions if original.get('components') else source;src=base/k;target=out/k;shutil.copytree(src,target)
        meta=target/(k+'.json');m=json.loads(meta.read_text());set_dpi(target/(k+'.png'),m['raster_dpi'])
        for ext in ['png','svg','pdf']:m['output_sha256'][k+'.'+ext]=sha(target/(k+'.'+ext))
        m['finisher_sha256']=engine;m['visual_acceptance']=False
        if not original.get('components'):
            a=label_audit(ROOT/original['assets']['svg'],target/(k+'.svg'),by[k]['context'].get('title_en',''))
            m['scientific_label_retention']=a
            if a['missing_labels']:missing.append(dict(id=k,**a))
        write(meta,m)
        r=copy.deepcopy(original);r['previous_assets']=original['assets'];r['previous_sha256']=original['sha256']
        r['assets']={e:(target/(k+('.json' if e=='meta' else '.'+e))).relative_to(ROOT).as_posix() for e in ['png','svg','pdf','meta']}
        r['sha256']={e:sha(ROOT/p) for e,p in r['assets'].items()};r['collection']='same-form revision';r['visual_review']=dict(status='PENDING_FINAL_SCREEN_REVIEW',scope='pending',png_sha256=r['sha256']['png'],final_size_inspected=False)
        r['preferred']=True;r['scientific_acceptance']=False;r.pop('reading',None);r['size_pt']=[m['width_pt'],m['height_pt']]
        r['print_screen']=dict(status='TARGET_SIZE_UNASSESSED',target_width_mm=178,source_size_note='Per-export physical width retained; complete components available')
        rows.append(r)
    write(out/'manifest.json',dict(schema_version=1,version='0.8.0',records=rows,failures=[],scientific_label_findings=missing,visual_acceptance=False,scientific_acceptance=False))
    print(json.dumps(dict(copied=len(rows),label_findings=len(missing),output=out.relative_to(ROOT).as_posix())))
    if missing:write(out/'label-findings.json',dict(records=missing))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--compositions',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);a=p.parse_args();prepare(a.source,a.compositions,a.plan)
