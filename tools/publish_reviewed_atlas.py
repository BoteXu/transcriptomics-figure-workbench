"""Copy exact individually inspected exports; publish only portable source bindings."""
import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / 'examples/gallery'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main(plan_path, review_path):
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    reviews = json.loads(review_path.read_text(encoding='utf8'))
    entries = plan['items'] + plan['compositions']
    assert len(entries) == len(reviews) == 400
    assert {x['id'] for x in entries} == set(reviews)
    out = G / 'publication-v030'
    out.mkdir(exist_ok=False)
    records = []
    for entry in entries:
        key = entry['id']
        assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', key)
        review = reviews[key]
        assert review['status'] == 'VISUALLY_REVIEWED'
        source = Path(review['bundle'])
        receipt = json.loads((source / (key + '.json')).read_text(encoding='utf8'))
        assert sha(source / (key + '.png')) == review['png_sha256']
        for name, digest in receipt['output_sha256'].items():
            assert Path(name).name == name and sha(source / name) == digest
        if entry.get('tsv'):
            assert sha(source / (key + '.tsv')) == entry['input_sha256'] == sha(ROOT / entry['tsv'])
        dest = out / key
        dest.mkdir()
        for ext in ('png', 'svg', 'pdf', 'tsv'):
            file = source / (key + '.' + ext)
            if file.exists():
                shutil.copyfile(file, dest / file.name)
        visual = dict(status='SELF_REVIEWED', inspection=review['inspection'], note=review['note'],
                      png_sha256=review['png_sha256'], inspected_artifact='PNG',
                      associated_exports=receipt['output_sha256'], independent_second_reviewer=False,
                      pdf_pixel_inspection=False, paper_print_proof=False)
        receipt.update(status='VISUALLY_SELF_REVIEWED', visual_acceptance=True,
                       scientific_acceptance=False, visual_review=visual)
        write(dest / (key + '.json'), receipt)
        prefix = 'publication-v030/' + key + '/' + key
        assets = {ext: prefix + '.' + ext for ext in ('png', 'svg', 'pdf')}
        assets['meta'] = prefix + '.json'
        if (dest / (key + '.tsv')).exists():
            assets['tsv'] = prefix + '.tsv'
        assets['png_sha256'] = review['png_sha256']
        records.append(dict(id=key, type='composition' if 'components' in entry else entry['context']['role'],
                            assets=assets, visual_review=visual,
                            automatic_geometry_issues=receipt['geometry_audit']['issues'],
                            automatic_issue_disposition='Reviewed in actual PNG; mathematical subscript proximity may be a text-box false positive. Dense layouts require native-size vector zoom.' if receipt['geometry_audit']['issues'] else None,
                            scientific_acceptance=False))
    write(out / 'review-index.json', dict(version='0.3.0', counts=plan['counts'],
          scope='All saved source IDs, auxiliary panels, layouts, QC/DE and twelve new examples',
          actual_individual_png_inspections=400, records=records,
          limitation='Self-review of display fixtures; not independent peer review or biological validation.'))
    write(out / 'source-plan.json', plan)
    by = {x['id']: x for x in records}
    catalog = json.loads((G / 'catalog.json').read_text(encoding='utf8'))
    catalog['version'] = '0.3.0'
    for item in catalog['preserved_examples']:
        item['current_preview'] = by[item['id']]['assets']
        for alt in item.get('layout_alternatives', []):
            key = 'ALT_' + item['id'] + '_' + alt['orientation']
            alt.update(by[key]['assets'])
    write(G / 'catalog.json', catalog)
    rows = []
    for record in records:
        a = record['assets']
        source_entry = next(x for x in entries if x['id'] == record['id'])
        original = source_entry.get('svg')
        original = '../../' + original if original else '../layout_review/index.html#' + source_entry['source_id']
        rows.append(dict(id=record['id'], kind=record['type'], png='../' + a['png'],
                         pdf='../' + a['pdf'], svg='../' + a['svg'], meta='../' + a['meta'],
                         original=original, note=record['visual_review']['note'], sha=a['png_sha256']))
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'">
<title>400 个图与排版 · v0.3.0</title><style>body{font:16px/1.6 Arial,sans-serif;color:#273540;margin:0;background:#f3f5f7}header,main{max-width:1400px;margin:auto;padding:24px}header{position:sticky;top:0;background:#fff;z-index:1;border-bottom:1px solid #dbe2e8}h1{font-size:24px;margin:0}input,select,button{font:inherit;padding:7px}article{background:white;margin:25px 0;padding:24px;border-radius:12px}img{display:block;max-width:100%;max-height:850px;margin:auto}a{color:#315a89;margin-right:14px}.meta{font-size:13px;color:#566573;overflow-wrap:anywhere}main p{margin:8px 0}</style>
<header><h1>400 个图与排版 · 逐图检查版</h1><p>274 个独立导出与 126 个组合排版；合成示例用于选图。自检通过不代表真实科研验收。</p><input id="q" placeholder="搜索稳定编号、备注、类别" aria-label="搜索图例"><select id="kind" aria-label="筛选类别"><option value="all">全部</option></select> <span id="count"></span><p><a href="../index.html">返回去重主目录</a><a href="review-index.json">精确哈希与逐图记录</a><a href="source-plan.json">源文件与参数绑定</a></p></header><main id="list"></main>
<script>const rows=__ROWS__;const q=document.getElementById('q'),kind=document.getElementById('kind'),list=document.getElementById('list');for(const k of new Set(rows.map(r=>r.kind))){const o=document.createElement('option');o.value=o.textContent=k;kind.append(o)}function render(){list.replaceChildren();const found=rows.filter(r=>(kind.value==='all'||r.kind===kind.value)&&JSON.stringify(r).toLowerCase().includes(q.value.toLowerCase()));document.getElementById('count').textContent=found.length+' 个';for(const r of found){const a=document.createElement('article');a.id=r.id;const h=document.createElement('h2');h.textContent=r.id+' · '+r.kind;const im=document.createElement('img');im.src=r.png;im.alt=r.id;im.loading='lazy';const p=document.createElement('p');p.textContent=r.note;const links=document.createElement('p');for(const [label,url] of [['PNG',r.png],['SVG',r.svg],['PDF',r.pdf],['检查记录',r.meta],['原始版本',r.original]]){const l=document.createElement('a');l.textContent=label;l.href=url;l.target='_blank';l.rel='noopener';links.append(l)}const s=document.createElement('p');s.className='meta';s.textContent='自检图像 SHA256: '+r.sha;a.append(h,im,p,links,s);list.append(a)}}q.oninput=kind.onchange=render;const id=location.hash.slice(1);if(rows.some(r=>r.id===id))q.value=id;render();</script></html>'''
    # Paths are relative to the publication page (one level below gallery).
    for row in rows:
        if row['original'].startswith('../../examples/'):
            row['original'] = '../' + row['original'].removeprefix('../../examples/gallery/') if row['original'].startswith('../../examples/gallery/') else '../../../' + row['original'].removeprefix('../../')
    (out / 'index.html').write_text(page.replace('__ROWS__', json.dumps(rows, ensure_ascii=False).replace('<', '\\u003c')), encoding='utf8')
    layout = json.loads((G / 'layout_review/manifest.json').read_text(encoding='utf8'))
    for row in layout['records']:
        for alt in row['alternatives']:
            alt.update(by['ALT_' + row['id'] + '_' + alt['orientation']]['assets'])
    write(G / 'layout_review/manifest.json', layout)
    parts = ['<!doctype html><meta charset="utf-8"><title>完整横纵排版</title><style>body{font:16px Arial;color:#273540;margin:30px}img{max-width:100%;max-height:700px}section{display:grid;grid-template-columns:1fr 1fr;gap:25px}article{margin:40px 0}</style><h1>完整面板横纵排版 · v0.3.0</h1><p>均已逐张自检。大画布保持原物理字号；投稿前需按目标版心重新选择、排版与检查。</p>']
    for row in layout['records']:
        parts.append('<article id="' + row['id'] + '"><h2>' + html.escape(row['id'] + ' ' + row['title']) + '</h2><section>')
        for alt in row['alternatives']:
            parts.append('<div><h3>' + alt['orientation'] + '</h3><a href="../' + alt['pdf'] + '"><img loading="lazy" src="../' + alt['png'] + '"></a></div>')
        parts.append('</section></article>')
    (G / 'layout_review/index.html').write_text('\n'.join(parts), encoding='utf8')
    print(json.dumps(dict(status='EXACT_REVIEWED_EXPORTS_COPIED', individual_png_reviews=len(records))))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--reviews', type=Path, required=True)
    a = p.parse_args()
    main(a.plan, a.reviews)
