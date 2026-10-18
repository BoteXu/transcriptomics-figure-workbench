"""Synchronize analysis navigation from real view specifications and packaged files."""
import json
from pathlib import Path
from analysis_gallery_page import page
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'

LABELS={
'bulk.design':'设计与独立样本','bulk.reads':'测序读段质控','bulk.alignment':'比对与覆盖','bulk.filtering':'基因检出与过滤','bulk.normalization':'标准化与均值方差','bulk.batch':'样本关系与批次','bulk.differential':'差异表达','bulk.interaction':'交互效应','bulk.model_qc':'模型诊断','bulk.programs':'基因程序与效应','bulk.ora':'ORA 功能富集','bulk.gsea':'GSEA 完整证据','bulk.pathway_contrasts':'通路跨对比','bulk.gene_support':'通路支持基因','bulk.gsea_multitrack':'多通路 GSEA','bulk.gsva':'GSVA／基因集评分','bulk.wgcna':'WGCNA 共表达网络','bulk.tf_activity':'转录因子活性','bulk.deconvolution':'细胞组成反卷积','bulk.splicing':'可变剪接','bulk.dtu':'转录本使用','bulk.timecourse':'时间与纵向变化','bulk.replication':'独立队列复现','bulk.survival':'生存与临床关联','bulk.ppi':'蛋白互作 PPI','bulk.connectivity':'扰动签名匹配','bulk.noncoding':'非编码 RNA','bulk.fusions':'融合与转录本结构',
'single_cell.design':'供体与单细胞设计','single_cell.barcode':'Barcode 与检出','single_cell.qc':'单细胞质控','single_cell.ambient_doublet':'环境 RNA 与双细胞','single_cell.integration':'整合与批次','single_cell.hvg_pca':'高变基因与 PCA','single_cell.resolution':'分辨率与聚类流向','single_cell.annotation':'细胞注释证据','single_cell.subcluster':'逐亚群与多 marker','single_cell.markers':'Marker 特异性','single_cell.composition':'供体层面细胞组成','single_cell.abundance':'差异丰度','single_cell.pseudobulk':'供体级伪 bulk','single_cell.multi_contrast':'多细胞类型与多对比','single_cell.pathways':'单细胞通路','single_cell.gene_support':'通路与支持基因','single_cell.states':'细胞状态与程序','single_cell.hdwgcna':'hdWGCNA 共表达网络','single_cell.trajectory':'轨迹与程序变化','single_cell.velocity':'RNA velocity','single_cell.communication':'细胞通讯','single_cell.ligand_target':'配体靶基因支持','single_cell.regulons':'Regulon 与 TF 活性','single_cell.cnv':'拷贝数变化 CNV','single_cell.vdj':'VDJ 与克隆','single_cell.splicing':'单细胞剪接','single_cell.perturbseq':'Perturb-seq','single_cell.replication':'单细胞独立复现','single_cell.spatial':'空间转录组','single_cell.multiome':'多组学与调控连接'}

def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

def build():
    completion=read(SKILL/'assets/analysis-gallery/manifest.json')['records']
    full=(SKILL/'assets/companion-gallery/manifest.json').is_file()
    version='0.10.0' if full else '0.9.7'
    old=read(SKILL/'references/analysis-views.json')
    # Rerunning is idempotent. Stable legacy IDs are retained for the re-rendered core.
    views={r['id']:r for r in old['views'] if r.get('catalog_origin') not in ['analysis_completion_v097','analysis_companions_v100']}
    # Existing stable IDs follow the actual revised spec rather than old prose.
    for view in views.values():
        path=SKILL/view['spec'];spec=read(path);params=spec['parameters']
        panel=next((p for p in params.get('panels',[]) if p.get('id')==view.get('panel_id')),None)
        view['title']=(panel or params).get('title',view['title'])
        with (path.parent/spec['input']['path']).open(encoding='utf8') as handle:view['input_channels']=handle.readline().rstrip('\r\n').split('\t')
    sources=[(row,'analysis-gallery','analysis_completion_v097') for row in completion]
    if full:sources += [(row,'companion-gallery','analysis_companions_v100') for row in read(SKILL/'assets/companion-gallery/manifest.json')['records']]
    for row,folder,origin in sources:
        key=row['id'].removeprefix('Core_')
        views[key]=dict(id=key,chapters=row['chapters'],title=row['title'],form=row['family'],renderer=row['renderer'],panel_id=None,
                        spec='assets/'+folder+'/'+row['assets']['spec'],input_channels=row['requirements'],meaning=row['parameters'],
                        example='assets/'+folder+'/index.html#'+row['id'],review_scope='Exact exported PNG individually screen-reviewed; changed inputs/layout need new review',
                        stage=row['stage'],variant=row['variant'],catalog_origin=origin)
    write(SKILL/'references/analysis-views.json',dict(schema_version=1,version=version,views=list(views.values()),analysis_performed=False))
    chapters=read(SKILL/'references/transcriptomic-chapters.json')['chapters'];suites=[];display={}
    for chapter in chapters:
        candidates=[v for v in views.values() if chapter['id'] in v['chapters']]
        primary=[];variants=[]
        for v in candidates:
            duplicate=(v['id'].endswith('.complete') and chapter['id'] in ['bulk.wgcna','single_cell.hdwgcna'])
            replaced=v['id'] in ['WGCNA_EigengeneProfiles','WGCNA_SoftPower','WGCNA_TOM']
            variant=v.get('variant',False) or duplicate or replaced or v['id'].endswith(('_Absolute','_Dissimilarity','_1Column'))
            (variants if variant else primary).append(v['id'])
            spec_path=SKILL/v['spec'];spec=read(spec_path)
            # Chapter panel entry IDs share one actual chapter figure; no duplicate thumbnails.
            image=spec_path.parent.parent/'example.png'
            if not image.is_file():raise FileNotFoundError('A catalog view has no actual exported pixels: '+v['id'])
            identity=image.relative_to(SKILL/'assets').as_posix()
            if identity not in display:
                stage=v.get('stage','chapter')
                display[identity]=dict(id=v['id'],view_ids=[],chapters=[],title=spec['parameters'].get('title',v['title']),
                    stage=stage,variant=variant,order=len(display),renderer=v['renderer'],parameters=spec['parameters'],
                    assets={k:'../'+image.with_suffix('.'+k).relative_to(SKILL/'assets').as_posix() for k in ['png','svg','pdf','tsv']},
                    definition=spec['parameters'].get('definition',spec['parameters'].get('scope_note','完整章节示例；选择单面板用 view-template，重新导出后重新审图。')),
                    requirements=[],keywords=[],review='Original exact-image review is in the linked packaged review.json; changed exports require new review')
                display[identity]['assets']['spec']='../'+spec_path.relative_to(SKILL/'assets').as_posix()
                if image.with_name('review.json').is_file():display[identity]['assets']['review']='../'+image.with_name('review.json').relative_to(SKILL/'assets').as_posix()
            row=display[identity]
            if v['id'] not in row['view_ids']:row['view_ids'].append(v['id'])
            if chapter['id'] not in row['chapters']:row['chapters'].append(chapter['id'])
            row['variant']=row['variant'] and variant
            row['requirements']=sorted(set(row['requirements']+v['input_channels']))
            row['keywords']=sorted(set(row['keywords']+[LABELS[chapter['id']],chapter['title']]))
        stages=['qc','network','interpretation','function','validation','extension','layout','chapter']
        primary.sort(key=lambda key:stages.index(views[key].get('stage','chapter')))
        variants.sort(key=lambda key:stages.index(views[key].get('stage','chapter')))
        coverage={stage:[k for k in primary+variants if views[k].get('stage','chapter')==stage] for stage in stages}
        suites.append(dict(id=chapter['id'],label=LABELS[chapter['id']],title=chapter['title'],assay=chapter['assay'],
            primary_views=primary,alternative_views=variants,required_results=chapter['required_results'],
            coverage=coverage,required_context=chapter['specific_qc_and_limit'],
            scope='Drawing templates only. Select views using actual returned results, assay, independent units and the stated question.',
            backend_analysis_performed=False))
    write(SKILL/'references/analysis-suites.json',dict(schema_version=1,version=version,suites=suites,analysis_performed=False))
    out=SKILL/'assets/analysis-library';out.mkdir(parents=True,exist_ok=True)
    from curate_analysis_navigation import curated_entries,form_navigation
    import copy,hashlib
    for row in display.values():
        s=read(SKILL/'assets/analysis-library'/row['assets']['spec']);p=copy.deepcopy(s['parameters']);p.pop('title',None)
        row['drawing_fingerprint']=hashlib.sha256(json.dumps(dict(renderer=s['renderer'],input=s['input']['sha256'],parameters=p),sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    navigation=curated_entries(list(display.values()),suites)
    write(out/'manifest.json',dict(version=version,chapters=len(suites),callable_views=len(views),actual_pages=len(display),records=list(display.values()),navigation=navigation,forms=form_navigation(list(display.values()),suites)))
    (out/'index.html').write_text(page(list(display.values()),suites,f'{len(suites)} 个分析章节 · {len(views)} 个调用视图 · {len(display)} 份源文件页。按章节固定顺序阅读，扩展收在同一条目中。'),encoding='utf8')
    lines=['# 按分析导出整套绘图模板','','从实际 FigureSpec 生成；章节、图页、调用视图与科学算法数量分别统计。所有示例均为冻结合成绘图材料，没有运行分析后端。','','|分析|默认配套视图|替代／布局|','|---|---:|---:|']
    for s in suites:lines.append('|'+s['label']+' (`'+s['id']+'`)|'+str(len(s['primary_views']))+'|'+str(len(s['alternative_views']))+'|')
    lines+=['','## 使用','','`analysis-library --search WGCNA` 列出对应整套路线。`analysis-suite --chapter bulk.wgcna --output <fresh-directory>` 导出该分析的全部默认合成模板、准确 TSV 和批量绘图 manifest；加 `--include-variants` 才导出相近替代与布局。`analysis-render --manifest <fresh-directory>/manifest.json --output <fresh-render-directory>` 串行绘制这些合成模板。实际项目应使用 `book-plan`，逐项绑定已经完成且 QC 审核的真实结果。','','默认与替代由实际数据语义决定；没有云形时不估算密度，没有完整命中时不冒充完整 GSEA，没有模块结果时不生成 WGCNA 结论。模板完整性与真实结果可用性是不同状态。各章节的主图和诊断／验证视图不是所有分析方法已穷尽的声明。']
    (SKILL/('references/analysis-library-v100.md' if full else 'references/analysis-library-v097.md')).write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(analysis_chapters=len(suites),callable_views=len(views),actual_pages=len(display),wgcna_primary=len(next(s for s in suites if s['id']=='bulk.wgcna')['primary_views']))))

if __name__=='__main__':build()
