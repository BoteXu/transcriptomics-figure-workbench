"""Bind already performed screen inspection to the exact final gallery bytes."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main(log):
    attestation=json.loads(log.read_text(encoding='utf8'))
    assert attestation.get('actual_screen_inspection_completed') is True,'Requires actual completed inspection, not prepared sheets'
    assert attestation['single_sheets_inspected']==list(range(1,57)) and attestation['composition_sheets_inspected']==list(range(1,22))
    base=ROOT/'examples/forms-v080';m=json.loads((base/'manifest.json').read_text(encoding='utf8'));reviews=[]
    enlarged=set(attestation['enlarged_ids'])
    dense={'R03','R04','R07','R09','R10','R11','R14','R15','R16','R20','R22','R24','R25','E01','E34','E41','E42'}
    for r in m['records']:
        k=r['id'];note='完整画面已在独立框中屏幕查看；并非原像素逐字检查或最终印刷尺寸验收。'
        if k in dense:note+=' 密集内容已另行放大；正式使用应选足够画布或独立面板。'
        if r.get('components'):note+=' 组合按概览与面板身份检查，完整独立组件可分别阅读。'
        v=dict(status='SCREEN_REVIEWED',reviewer='Codex self-review',scope='complete_images_separately_framed_on_screen_sheets',additional_enlarged_screen_review=k in enlarged,png_sha256=sha(ROOT/r['assets']['png']),svg_sha256=sha(ROOT/r['assets']['svg']),note=note,final_size_inspected=False,calibrated_paper_proof=False,independent_second_review=False,scientific_acceptance=False)
        r['visual_review']=v;r['preferred']=not bool(r.get('components'));meta=ROOT/r['assets']['meta'];d=json.loads(meta.read_text(encoding='utf8'));d['status']='SCREEN_REVIEWED_TARGET_SIZE_UNASSESSED';d['visual_review']=v;d['visual_acceptance']=False;write(meta,d);r['sha256']['meta']=sha(meta);reviews.append(dict(id=k,**v))
    m['screen_review_complete']=True;m['visual_acceptance']=False;m['review_limits']='All complete images viewed in separately framed screen sheets; selected dense images enlarged. Not exhaustive native text review, paper proof, independent review or scientific acceptance.'
    write(base/'manifest.json',m);write(base/'screen-review.json',dict(records=reviews,total=458,standalone=332,compositions=126,review_limits=m['review_limits'],scientific_acceptance=False))
    print(json.dumps(dict(status='PERFORMED_SCREEN_REVIEW_BOUND',exports=len(reviews),enlarged=len(enlarged))))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inspection-log',required=True,type=Path);a=p.parse_args();main(a.inspection_log)
