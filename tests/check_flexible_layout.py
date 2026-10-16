"""Flexible layout coverage and rejection checks, without scientific dependencies."""
from pathlib import Path
import copy,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.layout import make_layout,export_layout,digest,inspect_layout
from xml.etree import ElementTree as ET

def reject(call):
    try:call()
    except (ValueError,FileExistsError):return
    raise AssertionError('Invalid layout accepted')
def main():
    with tempfile.TemporaryDirectory() as t:
        d=Path(t);src=d/'source.svg';src.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><style>.point{fill:red}</style><defs><clipPath id="clip"><rect width="190" height="90"/></clipPath></defs><g clip-path="url(#clip)"><circle class="point" cx="12" cy="20" r="3"/><text x="20" y="40">NES 1.92; FDR 0.0008</text></g></svg>')
        panels=[dict(id='P'+str(i),svg='source.svg') for i in range(19)]
        request=dict(id='FlexibleTest',columns=5,canvas_width_pt=1500,panels=panels)
        p=make_layout(request,d);assert p['panel_count']==19 and p['pages'][0]['columns']==5 and p['pages'][0]['rows']==4
        assert len([x for page in p['pages'] for x in page['panels']])==19
        # Weighted columns, asymmetric spans and fixed physical height.
        r=dict(id='Spans',columns=3,column_weights=[2,1,1],canvas_width_pt=1000,canvas_height_pt=900,panels=[dict(id='Wide',svg='source.svg',row=0,column=0,column_span=2,row_span=2),dict(id='Right',svg='source.svg',row=0,column=2),dict(id='Low',svg='source.svg',row=1,column=2)])
        spans=make_layout(r,d);assert spans['pages'][0]['height_pt']==900
        assert spans['pages'][0]['column_widths_pt'][0]==2*spans['pages'][0]['column_widths_pt'][1]
        receipt=export_layout(spans,d/'exports');assert receipt['status']=='FLEXIBLE_LAYOUT_EXPORTED_UNREVIEWED'
        out=(d/'exports/Spans-page-01.svg').read_text();assert out.count('NES 1.92; FDR 0.0008')==3 and '#Wide_scope .point' in out and 'url(#Wide_clip)' in out
        assert src.read_text().count('NES 1.92; FDR 0.0008')==1
        reject(lambda:export_layout(spans,d/'exports'))
        checked=inspect_layout(d/'exports');assert not checked['issues'] and checked['review_status']=='UNREVIEWED'
        review=dict(layout_sha256=checked['layout_sha256'],screen_review_completed=True)
        assert inspect_layout(d/'exports',review)['review_status']=='SCREEN_REVIEWED'
        selected=d/'exports/Spans-page-01.svg';raw=selected.read_bytes();selected.write_bytes(raw+b'\n')
        assert inspect_layout(d/'exports',review)['review_status']=='STALE_REVIEW';selected.write_bytes(raw)
        late=make_layout(dict(id='Reserved',columns=2,panels=[dict(id='Auto',svg='source.svg'),dict(id='Fixed',svg='source.svg',row=0,column=0)]),d)
        assert late['pages'][0]['panels'][0]['column']==1
        masonry=make_layout(dict(id='Natural',columns=2,packing='masonry',label_order='reading',panels=panels[:5]),d)
        assert masonry['pages'][0]['packing']=='masonry' and len(masonry['pages'][0]['panels'])==5
        export_layout(masonry,d/'natural');assert not inspect_layout(d/'natural')['issues']
        reject(lambda:make_layout(dict(id='InvalidNatural',columns=2,packing='masonry',rows=2,panels=panels[:5]),d))
        paged=make_layout(dict(request,columns=2,max_rows_per_page=3),d);assert len(paged['pages'])==4 and paged['panel_count']==19
        auto=make_layout(dict(request,columns='auto',canvas_width_pt=1200),d);assert auto['pages'][0]['columns']==3
        overlap=copy.deepcopy(r);overlap['panels'][1].update(row=0,column=1);reject(lambda:make_layout(overlap,d))
        reject(lambda:make_layout(dict(request,columns=2,rows=2),d))
        reject(lambda:make_layout(dict(id='Draft',panels=[dict(id='P',svg=None)]),d))
        wrong=copy.deepcopy(spans);wrong['pages'][0]['panels'][0]['rect_pt'][0]=-1;reject(lambda:export_layout(wrong,d/'outside'))
        bad=d/'active.svg';bad.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><script>alert(1)</script></svg>')
        reject(lambda:make_layout(dict(id='Bad',panels=[dict(id='P',svg='active.svg')]),d))
        remote=d/'remote.svg';remote.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><image href="https://example.invalid/pixel"/></svg>')
        reject(lambda:make_layout(dict(id='Bad',panels=[dict(id='P',svg='remote.svg')]),d))
        remote.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" xml:base="https://example.invalid/"><use href="#item"/></svg>')
        reject(lambda:make_layout(dict(id='Bad',panels=[dict(id='P',svg='remote.svg')]),d))
        src.write_text(src.read_text().replace('1.92','2.34'));reject(lambda:export_layout(spans,d/'stale'))
        # Real hybrid Matplotlib source: exact embedded pixels and working xlink prefix.
        real=ROOT/'examples/forms-v080/PKG13/PKG13.svg'
        real_plan=make_layout(dict(id='Hybrid',title='Effect \u2212 difference',panels=[dict(id='Panel',svg=str(real))]),d)
        export_layout(real_plan,d/'hybrid');hybrid=d/'hybrid/Hybrid-page-01.svg'
        parsed=ET.parse(hybrid).getroot();original=ET.parse(real).getroot()
        raster=lambda root:[next(v for k,v in n.attrib.items() if k.endswith('href')) for n in root.iter() if n.tag.endswith('}image')]
        assert raster(parsed)==raster(original) and raster(parsed)
        assert 'xlink:href=' in hybrid.read_text(encoding='utf8') and 'Effect \u2212 difference' in ''.join(parsed.itertext())
        assert not any(n in sys.modules for n in ['numpy','pandas','matplotlib','fitz'])
    print(json.dumps(dict(status='FLEXIBLE_LAYOUT_PASS',checks=['19 panels / 5 columns','weighted asymmetric spans','automatic row growth','four-page coverage','full-source text and reference preservation','source mutation rejected','overlap/capacity/active/external content rejected'],scientific_analysis=False)))
    examples=ROOT/'examples/layout-v080';manifest=json.loads((examples/'manifest.json').read_text())
    assert len(manifest['records'])==3 and sum(len(r['panels']) for r in manifest['records'])==10
    for row in manifest['records']:
        svg=examples/row['file'];ET.parse(svg)
        for ext,h in row['sha256'].items():assert digest(svg.with_suffix('.'+ext))==h
        assert row['screen_review']['status']=='SCREEN_REVIEWED' and not row['screen_review']['target_size_assessed']
    print(json.dumps(dict(status='FLEXIBLE_EXAMPLE_BINDINGS_PASS',layouts=2,pages=3,complete_panel_uses=10,target_size_assessed=False)))
if __name__=='__main__':main()
