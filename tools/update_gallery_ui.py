"""Keep gallery source manifests inline and UI behavior in a readable file."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'examples/gallery/index.html'
html=p.read_text(encoding='utf8');c=json.loads((p.parent/'catalog.json').read_text(encoding='utf8'));methods=c['drawing_methods']
draw=sum(m['role'] in ['figure','combination'] for m in methods)
old='<p>43 个数据绘图／组合入口 · 236 个完整预览 · 15 套课题色卡</p>'
new=f'<p>{draw} 个去重画法／组合 · 15 套课题色卡 · 原编号与数据契约保留</p>'
if old in html:html=html.replace(old,new)
else:
    import re
    html=re.sub(r'<p>\d+ 个去重画法／组合.*?</p>',new,html,count=1)
html=html.replace('<a href="../overview/all-previews.pdf">全部236图PDF总览</a> · <a href="../overview/all-previews.jpg">全部示意图长图</a> · <a href="../overview/general-patterns.jpg">通用画法总览</a>',
 '<a href="../overview/visualization-overview.pdf">去重后的画法与组合PDF</a> · <a href="../overview/visualization-overview.jpg">去重示意长图</a> · <a href="../../skills/transcriptomics-figure-workbench/references/drawing-methods.md">逐项合并索引</a><p><a href="../overview/all-previews.pdf">来源档案（包含重复示例）</a> · <a href="../../skills/transcriptomics-figure-workbench/references/wgcna-visualization-router.md">WGCNA数据与绘图路由</a></p>')
html=html.replace('显示参数示例与旧样式','查看原编号来源档案')
if 'href="analysis_modules.html"' not in html:
    html=html.replace('<main>','<main><p><a href="analysis_modules.html">按分析结果模块查看新模式与组合</a> · <a href="layout_review/index.html">全部组合横纵排版</a></p>',1)
html=html.replace('href="../overview/all-previews.pdf"','href="../overview/source-archive-v021.pdf"')
import re
html=re.sub(r'<option value="support">说明附表</option>','',html)
html=html.replace('<option value="protein">真实结构画法</option>','<option value="protein">真实结构画法</option><option value="support">说明附表</option>')
html=html.replace('<div class="toolbar"><label>变体与来源例子 <select id="variants" aria-label="选择变体与参考例子"></select></label></div>',
 '<div class="toolbar"><label>数据／编码与布局模式 <select id="mode" aria-label="选择画法模式"></select></label></div><div class="toolbar hidden" id="source-options"><label>保留的来源例子 <select id="variants" aria-label="选择来源例子"></select></label></div>')
start=html.index('<script>const items=')
data='<script>const items='+json.dumps(c['preserved_examples'],ensure_ascii=False)+';const groups='+json.dumps(c['general_entries'],ensure_ascii=False)+';const groupAliases='+json.dumps(c['group_aliases'],ensure_ascii=False)+';const methods='+json.dumps(methods,ensure_ascii=False)+';</script><script src="workbench.js"></script></html>\n'
html=html[:start]+data
p.write_text(html,encoding='utf8')
print('Gallery primary entries:',draw)
