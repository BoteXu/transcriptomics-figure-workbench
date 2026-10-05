"""Verify local figure bundles and build an offline review gallery.

Review-list JSON maps PNG paths relative to the gallery directory to human review
notes. Only add an entry after actually inspecting that PNG. Source receipts are
never promoted or changed by the gallery.
"""
import argparse
import csv
import hashlib
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''): h.update(part)
    return h.hexdigest()

def main(output, roots, review_list=None):
    outputs=[output,output.with_suffix('.manifest.json'),output.with_suffix('.review.tsv')]
    if any(p.exists() for p in outputs): raise FileExistsError('New gallery output names required')
    reviews=json.loads(review_list.read_text(encoding='utf-8')) if review_list else {}
    entries=[]; cards=[]; seen=set()
    for root in roots:
        for receipt in sorted(root.rglob('*.json')):
            rec=json.loads(receipt.read_text(encoding='utf-8'))
            if rec.get('schema_version')!=2: continue
            for name,expected in rec['output_sha256'].items():
                target=receipt.parent/name
                if target.parent!=receipt.parent or not target.is_file() or sha(target)!=expected:
                    raise ValueError(f'Invalid bundle hash/path: {target}')
            figure_id=rec['figure_id']; png=receipt.with_suffix('.png')
            if rec['input_hash']!=rec['output_sha256'][figure_id+'.tsv']: raise ValueError('Input table hash mismatch')
            relative=Path(os.path.relpath(png,output.parent)).as_posix(); seen.add(relative)
            review='PNG_VISUALLY_INSPECTED_LAYOUT_ONLY' if relative in reviews else 'NOT_INSPECTED'
            entry=dict(root=root.name,figure_id=figure_id,png=relative,png_sha256=sha(png),
                       receipt_sha256=sha(receipt),synthetic=rec['synthetic'],review=review,notes=reviews.get(relative,''))
            entries.append(entry)
            links=' · '.join(f'<a href="{quote(Path(os.path.relpath(receipt.with_suffix(ext),output.parent)).as_posix())}">{ext[1:].upper()}</a>' for ext in ['.pdf','.svg','.tsv','.json'])
            kind='合成软件测试' if rec['synthetic'] else '来源数据绘图验收'
            cards.append(f'<article><h2>{html.escape(figure_id)}</h2><p>{html.escape(root.name)} · {kind}</p>'
                         f'<a href="{quote(relative)}"><img loading="lazy" src="{quote(relative)}" alt="{html.escape(figure_id)}"></a>'
                         f'<p>{links}</p><details><summary>查看审阅状态和解释边界</summary><p>{review}</p>'
                         f'<p>{html.escape(entry["notes"])}</p><p>{html.escape(rec["interpretation_limit"])}</p></details></article>')
    if set(reviews)-seen: raise ValueError('Review list contains unknown PNG paths')
    if not entries: raise ValueError('No v2 figure bundles found')
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>转录组绘图验收图册</title><style>
body{margin:0;background:#f2f5f7;color:#243341;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}
header{padding:28px 5vw;background:#173f70;color:white}h1{font-size:28px;margin:0 0 10px}h2{font-size:20px;margin:0}
main{max-width:1600px;margin:auto;padding:24px;display:grid;grid-template-columns:repeat(auto-fit,minmax(540px,1fr));gap:24px}
article{background:white;border:1px solid #d8e1e8;border-radius:10px;padding:20px;overflow:hidden}img{width:100%;height:auto}p{margin:8px 0}a{color:#24578a}summary{cursor:pointer}details{font-size:14px}
@media(max-width:600px){main{display:block;padding:12px}article{margin-bottom:18px}}
</style><header><h1>转录组绘图验收图册</h1><p>每张图的来源、模型、独立单位和解释边界以对应回执为准；版式验收不等于生物学结论放行。</p>'''
    doc+=f'<p>{len(entries)} 个完整图件包；每包哈希已复核。{len(reviews)} 张 PNG 有独立版式查看记录；PDF/SVG 未逐页视觉复核。</p></header><main>'
    doc+=''.join(cards)+'</main></html>'
    output.write_text(doc,encoding='utf-8')
    outputs[1].write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),entries=entries),ensure_ascii=False,indent=2),encoding='utf-8')
    with outputs[2].open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(entries[0]),delimiter='\t'); w.writeheader(); w.writerows(entries)
    print(f'PASS: {len(entries)} bundles, hashes verified, {len(reviews)} PNG review records; {output}')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('output',type=Path); p.add_argument('roots',nargs='+',type=Path); p.add_argument('--review-list',type=Path)
    a=p.parse_args(); main(a.output,a.roots,a.review_list)
