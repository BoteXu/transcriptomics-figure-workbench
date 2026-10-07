"""Build and retain analysis-result modes and explicit linked compositions."""
from pathlib import Path
import sys,json,shutil,argparse
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';G=ROOT/'examples/gallery'
sys.path.insert(0,str(S/'scripts'))
from analysis_result_fixture import analysis_result_cases
from render_frozen_table import render
from figure_core import export_figure,file_sha256
from compose_panels import compose_bundles


def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
RECIPES=[
 ('K41','预测校准、评价支持量与决策价值',['E45','E46'],'G22','两个panel使用同一明确模型身份及评价群体。校准比例、分箱人数与净获益分别保留定义，参考策略不冒充另一个模型。'),
 ('K42','调控活性矩阵与指定样本的完整贡献',['E47','E51'],'G23','矩阵Regulator A / S01的值0.62对应右侧完整贡献加基线的总量0.62；选择身份和可加定义显式保存，其余样本与调控因子保留。'),
]


def main(output,refresh=False):
    output.mkdir(parents=True,exist_ok=False);cases=analysis_result_cases();theme=json.loads((G/'project_theme.json').read_text(encoding='utf8'));exports={}
    for id_,c in cases.items():
        fig,audit=render(c['adapter'],c['data'],c['params'],theme)
        meta=dict(source='Original deterministic procedural software fixture, not a research dataset',palette=theme['palette_name'],input_unit=c['data_required'],experimental_unit='Synthetic display records; independent units require actual analysis context',contrast='Frozen result visualization demonstration',denominator='Complete supplied table; model evaluation counts never summed across models',model='No upstream scientific model executed',limits='Saved drawing limits and result definitions',filtering='No aesthetic exclusions',uncertainty='Only supplied illustrative bounds; no inference performed',interpretation_limit=c['limitations'],synthetic=True,example_id=id_,layout_audit=audit)
        export_figure(fig,c['data'],output/'panels',id_,meta);plt.close(fig);prefix=output/'panels'/id_/id_
        write(prefix.with_suffix('.style.json'),dict(adapter=c['adapter'],module=c['function'].__module__,function=c['function'].__name__,params=c['params']))
        exports[id_]=prefix;print(id_+' saved',flush=True)
    composed=[]
    for id_,title,ids,family,relation in RECIPES:
        layout=dict(id=id_,title=title,size_pt=[1260,600],require_same_theme=True,panels=[dict(id=chr(65+j),label=chr(65+j),rect_pt=[25+j*625,45,610+j*625,555],crop_white_margins=True,crop_software_labels=True) for j in range(2)])
        receipt=compose_bundles([dict(prefix=str(exports[i]),metadata=str(exports[i].with_suffix('.json'))) for i in ids],layout,output/'compositions'/id_,preview_dpi=150)
        composed.append((id_,title,ids,family,relation,layout,receipt));print(id_+' composed',flush=True)
    catalog=json.loads((G/'catalog.json').read_text(encoding='utf8'));registry=json.loads((S/'references/combination-recipes.json').read_text(encoding='utf8'));newids=set(cases)|{r[0] for r in RECIPES}
    if newids&{x['id'] for x in catalog['preserved_examples']} and not refresh:raise ValueError('New stable IDs already exist')
    catalog['preserved_examples']=[x for x in catalog['preserved_examples'] if x['id'] not in newids];registry['recipes']=[x for x in registry['recipes'] if x['id'] not in newids]
    locations={}
    for id_,c in cases.items():
        shutil.copytree(exports[id_].parent,G/'figures'/id_,dirs_exist_ok=refresh);prefix=G/'figures'/id_/id_
        write(G/'metadata'/f'{id_}.json',json.loads(prefix.with_suffix('.json').read_text(encoding='utf8')));relative=f'figures/{id_}/{id_}'
        locations[id_]=dict(name=id_,prefix=relative,metadata=f'metadata/{id_}.json',table_sha256=file_sha256(prefix.with_suffix('.tsv')))
        catalog['preserved_examples'].append(dict(id=id_,title=c['title'],role='extension',family=c['family'],input_shape=c['data_required'],data_required=c['data_required'],expression=c['expression'],how_to_draw='读取结果表、显示顺序、量值及上下文定义；使用保存的固定适配器。',aesthetic_controls='课题主题统一色卡与字体；独立图例、共同坐标、按输入扩展。',limitations=c['limitations'],reference=None,png=relative+'.png',pdf=relative+'.pdf',svg=relative+'.svg',tsv=relative+'.tsv',style=relative+'.style.json',meta=f'metadata/{id_}.json',png_sha256=file_sha256(prefix.with_suffix('.png')),pdf_sha256=file_sha256(prefix.with_suffix('.pdf')),curation=dict(decision='recommended',canonical=id_,reason='新结果模式；相似视觉结构合并入口。')))
    for id_,title,ids,family,relation,layout,receipt in composed:
        shutil.copytree(output/'compositions'/id_,G/'figures'/id_,dirs_exist_ok=refresh);relative=f'figures/{id_}/{id_}';prefix=G/relative
        write(G/'metadata'/f'{id_}.json',dict(example_id=id_,synthetic=True,scientific_inference=False,relationship=relation,component_ids=ids,layout=layout,output_sha256=receipt['files']))
        catalog['preserved_examples'].append(dict(id=id_,title=title,role='combination',family=family,input_shape='明确身份对应的独立结果表',data_required='；'.join(cases[i]['data_required'] for i in ids),expression=relation,how_to_draw='先保存各panel及输入，再组合；关系以身份/定义连接，不强行共用不同量值的轴。',aesthetic_controls='独立图例、矢量排版、统一课题主题；提供横纵布局。',limitations=relation+' 软件构造示例不构成分析证据。',reference=None,png=relative+'.png',pdf=relative+'.pdf',svg=relative+'.svg',tsv=None,style=None,meta=f'metadata/{id_}.json',component_tables=[f'figures/{id_}/{panel["id"]}.tsv' for panel in layout['panels']],components=ids,component_links=[dict(name=i,label='Panel '+chr(65+j)+' · '+cases[i]['title'],url='#'+i) for j,i in enumerate(ids)],png_sha256=file_sha256(prefix.with_suffix('.png')),pdf_sha256=file_sha256(prefix.with_suffix('.pdf')),curation=dict(decision='recommended',canonical=id_,reason='新增明确的数据对应关系，独立panel完整保存。')))
        registry['recipes'].append(dict(id=id_,title=title,relation=relation,bundles=[locations[i] for i in ids],layout=layout))
    for group in catalog['general_entries']:
        group['members']=[i for i in group['members'] if i not in newids]+[x['id'] for x in catalog['preserved_examples'] if x['id'] in newids and x['family']==group['id']]
    if any(x['family'] not in {g['id'] for g in catalog['general_entries']} for x in catalog['preserved_examples']):raise ValueError('Unknown navigation group')
    write(G/'catalog.json',catalog);write(S/'references/combination-recipes.json',registry)
    write(output/'build-receipt.json',dict(status='EXPORTED_AND_COMPOSED',new_modes=9,new_compositions=2,upstream_analysis_executed=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--refresh-new',action='store_true');a=p.parse_args();main(a.output,a.refresh_new)
