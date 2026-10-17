"""Record a human/host-completed screen inspection; does not perform that review."""
import argparse,hashlib,json
from pathlib import Path
def main(source,output,statement):
    if statement!='All listed final images actually inspected':raise ValueError('Only record an actually completed visual inspection')
    rows=json.loads((source/'manifest.json').read_text(encoding='utf8'))['records'];records=[]
    for r in rows:
        p=next((Path(x) for x in r.get('result',{}).get('files',[]) if x.endswith('.png')),None)
        if p is None:p=(source/r['file']).with_suffix('.png')
        records.append(dict(id=r['id'],png_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),decision='screen_reviewed',checks=['scientific display meaning and scope','complete intended input channels','readable labels and guides','stable identity and declared continuous units','panel balance and hierarchy','no observed clipping or label collision'],notes='Actual final image screened; dense or flagged plots enlarged. Exact duplicate pixels retain the earlier actual inspection. New project data or layouts require a new review.',independent_second_review=False,calibrated_paper_proof=False,scientific_acceptance=False))
    doc=dict(state='SCREEN_REVIEWED',aesthetic_publication_approval=False,
        scope='Actual complete final PNG self-inspection; dense/flagged views enlarged. Screen observation is not blanket aesthetic approval, journal acceptance, calibrated print proof or independent scientific acceptance.',
        records=records,analysis_performed=False,scientific_acceptance=False)
    if output.exists():raise ValueError('Use a fresh review record')
    output.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(status='ACTUAL_SCREEN_REVIEW_RECORDED',figures=len(records))))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--statement',required=True);a=p.parse_args();main(a.source,a.output,a.statement)
