"""Visible module routes into canonical modes; no extra drawing-family count."""
from pathlib import Path
import json,html
ROOT=Path(__file__).resolve().parents[1];G=ROOT/'examples/gallery'
MODULES=[('剪接与异构体',['E43']),('精细定位与位置证据',['E44','E28','E29']),('校准与决策评价',['K41','E45','E46']),('调控活性与完整贡献',['K42','E47','E51']),('通路共享与网络稳定性',['E48','E49','E34']),('WGCNA已有模块结果',['K38','K40']),('独立轨迹与时间范围',['E50','E32']),('染色质接触与序列位点',['E39','E38']),('已有树与真实蛋白结构',['E40','S01']),('影像切面与配准对照',['E41','E42'])]
def main():
    c=json.loads((G/'catalog.json').read_text(encoding='utf8'));by={x['id']:x for x in c['preserved_examples']}
    lines=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>分析结果的可视化表达</title><style>body{font:16px Arial,sans-serif;max-width:1400px;margin:28px auto;padding:0 24px;color:#25364a}a{color:#395d9b}h1{font-size:28px}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:24px}article{border:1px solid #dce3ec;border-radius:8px;padding:18px;margin-bottom:24px}img{width:100%;height:290px;object-fit:contain}dt{font-weight:bold}dd{margin:4px 0 14px;line-height:1.5}</style><h1>分析结果的可视化表达</h1><p><a href="index.html">完整去重目录</a> · <a href="layout_review/index.html">完整横纵排版</a> · <a href="../../skills/transcriptomics-figure-workbench/references/analysis-modules-router.md">数据契约和组合路线</a></p><p>按结果结构与需要表达的量选图。相似画法复用已有入口；每个panel保存输入和参数。预览使用合成数据，结构示例使用标注的公共坐标。</p>']
    for title,ids in MODULES:
        lines.append('<h2>'+html.escape(title)+'</h2><section>')
        for id_ in ids:
            x=by[id_];lines.append('<article><h3><a href="index.html#'+id_+'">'+id_+' '+html.escape(x['title'])+'</a></h3><a href="index.html#'+id_+'"><img loading="lazy" src="'+x['png']+'" alt="'+html.escape(x['title'],quote=True)+'"></a><dl>')
            for field,label in [('data_required','需要的数据'),('expression','能表达什么')]:lines.append('<dt>'+label+'</dt><dd>'+html.escape(x[field])+'</dd>')
            link=x.get('pdf') or x['png'];label='完整PDF' if x.get('pdf') else '高清PNG'
            lines.append('</dl><a href="'+link+'">'+label+'</a> · <a href="index.html#'+id_+'">参数、数据与独立panel</a></article>')
        lines.append('</section>')
    lines.append('</html>');(G/'analysis_modules.html').write_text('\n'.join(lines),encoding='utf8')
    print('Analysis module routes saved: '+str(sum(len(x[1]) for x in MODULES)))
if __name__=='__main__':main()
