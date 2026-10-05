"""Explicitly build and add bounded synthetic linked-display examples."""
from pathlib import Path
import argparse,json,shutil,sys,copy
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'skills/transcriptomics-figure-workbench';G=ROOT/'examples/gallery'
sys.path.insert(0,str(S/'scripts'))
from linked_evidence_fixture import linked_cases
from render_frozen_table import render
from figure_core import export_figure,file_sha256
from compose_panels import compose_bundles

def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

RECIPES=[
 ('K37','集合、条目、成员与整体／局部网络',['c37_sets','c37_terms','E34','c37_network','c37_local'],[1500,1130],[[25,45,430,405],[470,45,1475,405],[25,455,755,1070],[780,460,1120,1020],[1140,460,1480,1020]],'G15','同一成员ID与条目结果对应；局部网络是明确节点集合诱导的子图，不重新估计边。'),
 ('K38','已有诊断、层次树、关联矩阵与成员评分',['c38_fit','c38_degree','E36','E35','c38_scores'],[1200,1370],[[25,45,575,360],[625,45,1175,360],[25,425,1175,815],[25,875,610,1315],[650,875,1175,1315]],'G56','诊断值、树、模块身份、性状关系和成员评分均为已有结果；对象ID与模块身份有显式对应。'),
 ('K39','环形层级量值与同对象堆叠贡献',['E37','c39_stack'],[1250,780],[[25,45,590,720],[620,80,1225,690]],'G14','两个panel共用叶端ID；标记指标与可加数量分别保留单位，不能把独立对接能量相加解释亲和力。'),
 ('K40','模块结构、相似矩阵、代表值网络与性状',['E36','c40_matrix','c40_network','E35','c38_scores'],[1450,1200],[[25,45,1425,380],[25,430,475,760],[510,430,945,760],[980,430,1425,780],[290,825,1170,1140]],'G56','叶ID、矩阵行列与成员评分对应；模块ID对应条目关联与代表值网络。TOM/adjacency/kME定义与网络版本由上游明确给定。'),
]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--replace-new',action='store_true',help='Refresh only the fixed E34-E37/K37-K40 increment after review');a=p.parse_args();a.output.mkdir(exist_ok=False)
    theme=json.loads((G/'project_theme.json').read_text(encoding='utf8'));cases=linked_cases();exports={}
    for id_,c in cases.items():
        fig,audit=render(c['adapter'],c['data'],c['params'],theme)
        meta=dict(source='Deterministic bounded synthetic linked-display fixture; no research analysis',palette=theme['palette_name'],input_unit=c['data_required'],experimental_unit='Synthetic display IDs; no biological inference',contrast='Frozen display demonstration',denominator='All supplied records; explicit membership background and additive quantities',model='No scientific model, network or clustering fitted',limits='Explicit drawing settings',filtering='No aesthetic exclusions; selected network subset explicitly declared',uncertainty='Given illustrative values; no inferential uncertainty calculated',interpretation_limit=c['limitations'],synthetic=True,layout_audit=audit,example_id=id_)
        try:export_figure(fig,c['data'],a.output/'panels',id_,meta)
        finally:plt.close(fig)
        prefix=a.output/'panels'/id_/id_
        write(prefix.with_suffix('.style.json'),dict(adapter=c['adapter'],module=c['function'].__module__,function=c['function'].__name__,params=c['params']))
        exports[id_]=prefix;print(id_+' exported',flush=True)
    built=[]
    (a.output/'compositions').mkdir()
    for id_,title,ids,size,rects,family,relation in RECIPES:
        layout=dict(id=id_,title=title,size_pt=size,require_same_theme=True,panels=[dict(id=str(i+1),label=chr(65+i),rect_pt=r,crop_software_labels=True) for i,r in enumerate(rects)])
        receipt=compose_bundles([dict(prefix=str(exports[i]),metadata=str(exports[i].with_suffix('.json'))) for i in ids],layout,a.output/'compositions'/id_)
        built.append((id_,title,ids,family,relation,layout,receipt));print(id_+' composed',flush=True)
    # Nothing is copied into the public gallery until all exports/compositions succeed.
    catalog=json.loads((G/'catalog.json').read_text(encoding='utf8'));items=catalog['preserved_examples'];newids={'E34','E35','E36','E37'}|{r[0] for r in RECIPES}
    existing=newids&{x['id'] for x in items}
    if existing and not a.replace_new:raise ValueError('These stable IDs already exist; explicit increment refresh required')
    if a.replace_new:
        if existing!=newids:raise ValueError('Refresh requires the complete fixed increment')
        items[:]=[x for x in items if x['id'] not in newids]
    registry=json.loads((S/'references/combination-recipes.json').read_text(encoding='utf8'))
    if a.replace_new:
        registry['recipes']=[x for x in registry['recipes'] if x['id'] not in newids]
        registry['supplemental_components']=[x for x in registry['supplemental_components'] if x['id'] not in cases]
    locations={}
    for id_,c in cases.items():
        standalone=id_.startswith('E');dest=G/('figures' if standalone else 'components')/id_;shutil.copytree(exports[id_].parent,dest,dirs_exist_ok=a.replace_new)
        prefix=dest/id_;meta=json.loads(prefix.with_suffix('.json').read_text(encoding='utf8'));meta['example_id']=id_
        if standalone:
            write(G/'metadata'/f'{id_}.json',meta);metadata=f'metadata/{id_}.json'
        else:metadata=prefix.with_suffix('.json').relative_to(G).as_posix()
        locations[id_]=dict(name=id_,prefix=prefix.relative_to(G).as_posix(),metadata=metadata,table_sha256=file_sha256(prefix.with_suffix('.tsv')))
        if not standalone:
            registry['supplemental_components'].append(dict(id=id_,prefix=locations[id_]['prefix'],metadata=metadata,source_script_saved=True,adapter=c['adapter'],style=prefix.with_suffix('.style.json').relative_to(G).as_posix()))
            continue
        items.append(dict(id=id_,title=c['title'],role='extension',family=c['family'],input_shape=c['data_required'],data_required=c['data_required'],expression=c['expression'],how_to_draw='读取冻结结果、显式顺序和各通道定义；使用已保存的固定适配器与统一课题主题。',aesthetic_controls='课题色卡、固定身份、字体层级、标签、图例区域与最终尺寸。',limitations=c['limitations'],reference=None,png=locations[id_]['prefix']+'.png',pdf=locations[id_]['prefix']+'.pdf',svg=locations[id_]['prefix']+'.svg',tsv=locations[id_]['prefix']+'.tsv',style=locations[id_]['prefix']+'.style.json',meta=metadata,png_sha256=file_sha256(prefix.with_suffix('.png')),pdf_sha256=file_sha256(prefix.with_suffix('.pdf')),curation=dict(decision='recommended',canonical=id_,reason='新增明确的视觉结构与冻结数据契约。')))
    for id_,title,ids,family,relation,layout,receipt in built:
        dest=G/'figures'/id_;shutil.copytree(a.output/'compositions'/id_,dest,dirs_exist_ok=a.replace_new);prefix=dest/id_
        meta=dict(example_id=id_,synthetic=True,scientific_inference=False,relationship=relation,component_ids=ids,layout=layout,output_sha256=receipt['files']);write(G/'metadata'/f'{id_}.json',meta)
        items.append(dict(id=id_,title=title,role='combination',family=family,input_shape='独立panel结果表与明确ID对应',data_required='；'.join(cases[i]['data_required'] for i in ids),expression=relation,how_to_draw='先分别画并检查每个panel，再按已保存布局组合；不共享不同量值的图例或擅自计算缺失结果。',aesthetic_controls='各panel独立图例，矢量组合，统一主题和字体。',limitations=relation+' 合成示例仅演示图形表达。',reference=None,png=f'figures/{id_}/{id_}.png',pdf=f'figures/{id_}/{id_}.pdf',svg=f'figures/{id_}/{id_}.svg',tsv=None,style=None,meta=f'metadata/{id_}.json',component_tables=[f'figures/{id_}/{i+1}.tsv' for i in range(len(ids))],components=ids,component_links=[dict(name=i,label='Panel '+chr(65+j)+' · '+cases[i]['title'],url='#'+i if i.startswith('E') else locations[i]['prefix']+'.png') for j,i in enumerate(ids)],png_sha256=file_sha256(prefix.with_suffix('.png')),pdf_sha256=file_sha256(prefix.with_suffix('.pdf')),curation=dict(decision='recommended',canonical=id_,reason='按冻结ID和关系组合，单独panel保存。')))
        registry['recipes'].append(dict(id=id_,title=title,relation=relation,bundles=[locations[i] for i in ids],layout=layout))
    for group in catalog['general_entries']:
        group['members']=[id_ for id_ in group['members'] if id_ not in newids]
        group['members'].extend(x['id'] for x in items if x['id'] in newids and x['family']==group['id'])
    write(G/'catalog.json',catalog);write(S/'references/combination-recipes.json',registry)
    write(a.output/'build-receipt.json',dict(status='EXPORTED_AND_COMPOSED_REVIEW_REQUIRED',panels=len(cases),compositions=len(built),scientific_analysis=False,new_ids=sorted(newids)))
    print(json.dumps(dict(saved_panels=len(cases),new_stable_sources=len(newids))))

if __name__=='__main__':main()
