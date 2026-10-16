"""Build one offline HTML Studio. No server, network client or plotting imports."""
import json
import os
from pathlib import Path
from .registry import SKILL,read_registry


def build_studio(output,gallery=None,demo_svg=None):
    output=Path(output)
    if output.exists():raise FileExistsError('Choose a new Studio output file')
    from .methods import catalog_methods
    data={'registry':read_registry(),'examples':[],'methods':[],'method_entries':catalog_methods(),'demo_svg':None}
    data['design_examples']=[]
    for gallery_name in ['clarity-gallery','refined-gallery','design-gallery']:
        designs=SKILL/'assets'/gallery_name
        if not designs.is_dir():continue
        prefix=Path(os.path.relpath(designs,output.resolve().parent)).as_posix()
        for row in json.loads((designs/'manifest.json').read_text(encoding='utf8'))['records']:
            key=row['id']
            data['design_examples'].append(dict(id=key,title=key+' · '+row['view'],input_shape='优选冻结结果画法；合成展示，不是科学验收',png=prefix+'/'+key+'/'+key+'.png',source=prefix+'/index.html#'+key))
    consolidated=SKILL/'assets/forms-gallery'
    if consolidated.is_dir():
        prefix=Path(os.path.relpath(consolidated,output.resolve().parent)).as_posix()
        forms=json.loads((SKILL/'references/form-catalog.json').read_text(encoding='utf8'))['forms']
        data['design_examples']=[dict(id=g['id'],title=g['title'],input_shape='基础图型与扩展；合成展示，单位与来源按所选实例核查',png=prefix+'/'+g['default']+'.jpg',source=prefix+'/index.html#'+g['id']) for g in forms]
    studies=SKILL/'assets/study-gallery'
    if studies.is_dir():
        prefix=Path(os.path.relpath(studies,output.resolve().parent)).as_posix()
        data['design_examples']=[dict(id=key,title=title,input_shape='完整冻结结果示例；主图与细节图配套，合成数据不是科学证据',png=prefix+'/'+key+'.jpg',source=prefix+'/index.html#'+key) for key,title in [('BulkMain','Bulk 转录组文章组图'),('SingleCellMain','单细胞文章组图')]]+data['design_examples']
    package_gallery=SKILL/'assets/package-gallery'
    if package_gallery.is_dir():
        prefix=Path(os.path.relpath(package_gallery,output.resolve().parent)).as_posix()
        for entry in data['method_entries']:
            key=entry['publication_example']
            entry['example_files']={extension:prefix+'/'+key+'/'+key+'.'+extension for extension in ['png','svg','pdf','tsv','json']}
            entry['example_files']['spec']=prefix+'/inputs/'+key+'.spec.json'
            entry['example_files']['gallery']=prefix+'/index.html#'+key
    if gallery is not None:
        gallery=Path(gallery).resolve()
        manifest=gallery/'catalog.json'
        if not manifest.is_file():raise ValueError('Select the existing complete gallery directory')
        items=json.loads(manifest.read_text(encoding='utf8'))
        if isinstance(items,dict):items=items['preserved_examples']
        prefix=Path(os.path.relpath(gallery,output.resolve().parent)).as_posix()
        for item in items:
            current=item.get('current_preview',item)
            data['examples'].append({'id':item['id'],'title':item.get('title',item['id']),
                'input_shape':item.get('input_shape',''),'png':prefix+'/'+current['png'],
                'source':prefix+'/index.html#'+item['id']})
        methods=SKILL/'references/drawing-methods.json'
        data['methods']=json.loads(methods.read_text(encoding='utf8'))['methods']
    if demo_svg is not None:
        path=Path(demo_svg)
        if path.stat().st_size>5*1024**2:raise ValueError('Demo SVG exceeds the bounded preview limit')
        data['demo_svg']=path.read_text(encoding='utf8')
    assets=SKILL/'assets/studio'
    template=(assets/'index.html').read_text(encoding='utf8')
    content=template.replace('/*__STUDIO_CSS__*/',(assets/'studio.css').read_text(encoding='utf8'))
    content=content.replace('/*__STUDIO_JS__*/',(assets/'publication-svg.js').read_text(encoding='utf8')+'\n'+(assets/'form-polish.js').read_text(encoding='utf8')+'\n'+(assets/'studio.js').read_text(encoding='utf8'))
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    content=content.replace('/*__STUDIO_DATA__*/',encoded)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf8') as stream:stream.write(content)
    return {'status':'OFFLINE_STUDIO_BUILT','output':str(output),'renderer_count':len(data['registry']['renderers']),
            'source_examples':len(data['examples']),'network_service_started':False,'private_data_uploaded':False}
