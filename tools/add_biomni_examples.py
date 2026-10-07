"""Add five synthetic Biomni-discovered views, retaining every historical asset."""
from pathlib import Path
import sys,json,shutil,argparse
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';G=ROOT/'examples/gallery'
sys.path.insert(0,str(S/'scripts'))
from biomni_view_fixture import biomni_view_cases
from figure_core import export_figure,file_sha256
from render_frozen_table import render


def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main(output,refresh_new=False):
    output.mkdir(parents=True,exist_ok=False)
    catalog=json.loads((G/'catalog.json').read_text(encoding='utf8'));cases=biomni_view_cases()
    if set(cases)&{x['id'] for x in catalog['preserved_examples']} and not refresh_new:raise ValueError('Stable new IDs already exist')
    if refresh_new:
        catalog['preserved_examples']=[x for x in catalog['preserved_examples'] if x['id'] not in cases]
        for g in catalog['general_entries']:g['members']=[i for i in g['members'] if i not in cases]
    theme=json.loads((G/'project_theme.json').read_text(encoding='utf8'))
    for id_,c in cases.items():
        fig,audit=render(c['adapter'],c['data'],c['params'],theme)
        meta=dict(source='Original deterministic procedural software fixture, not a research dataset',palette=theme['palette_name'],input_unit=c['data_required'],experimental_unit='Synthetic display records, no biological inference',contrast='Frozen plotting demonstration',denominator='Complete supplied display table',model='No upstream scientific model executed',limits='Explicit saved plotting limits',filtering='No aesthetic exclusions',uncertainty='No inferential intervals',interpretation_limit=c['limitations'],synthetic=True,example_id=id_,layout_audit=audit)
        export_figure(fig,c['data'],output,id_,meta);plt.close(fig)
        prefix=output/id_/id_;write(prefix.with_suffix('.style.json'),dict(adapter=c['adapter'],module=c['function'].__module__,function=c['function'].__name__,params=c['params']))
        destination=G/'figures'/id_;shutil.copytree(prefix.parent,destination,dirs_exist_ok=refresh_new)
        write(G/'metadata'/f'{id_}.json',json.loads(prefix.with_suffix('.json').read_text(encoding='utf8')))
        relative=f'figures/{id_}/{id_}'
        item=dict(id=id_,title=c['title'],role='extension',family=c['family'],input_shape=c['data_required'],data_required=c['data_required'],expression=c['expression'],how_to_draw='读取已给结果表和明确坐标/单位；使用固定适配器，保存图例、输入、参数和输出。',aesthetic_controls='课题色卡、统一字体、物理坐标、显式顺序和独立图例；切片与图像对照支持横纵panel排列。',limitations=c['limitations'],reference=None,png=relative+'.png',pdf=relative+'.pdf',svg=relative+'.svg',tsv=relative+'.tsv',style=relative+'.style.json',meta=f'metadata/{id_}.json',png_sha256=file_sha256(prefix.with_suffix('.png')),pdf_sha256=file_sha256(prefix.with_suffix('.pdf')),curation=dict(decision='recommended',canonical=id_,reason='新增结果表与表达方式；相似结构合并为模式。'))
        catalog['preserved_examples'].append(item)
        group=next((g for g in catalog['general_entries'] if g['id']==c['family']),None)
        if group is None:raise ValueError('Unknown navigation group')
        group['members'].append(id_)
        print(id_+' saved',flush=True)
    catalog['version']='0.2.4';write(G/'catalog.json',catalog)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--refresh-new',action='store_true');a=p.parse_args();main(a.output,a.refresh_new)
