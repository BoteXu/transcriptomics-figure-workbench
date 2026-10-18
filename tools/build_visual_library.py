"""One lossless method index across scientific domains; no rendering or inference.

Existing catalogs remain authoritative for scientific scope. This index groups
display forms, never pools results, reassigns statistics or deletes old assets.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / 'skills/transcriptomics-figure-workbench'
OUT = S / 'assets/visual-library'


def read(p):
    return json.loads(p.read_text(encoding='utf8'))


def signature(spec):
    p = spec['parameters']
    # Renderer identity alone is insufficient: the palette renderer can draw
    # radar, geography, bars, or a schematic. Preserve the actual panel types.
    return (spec['renderer'], json.dumps(p.get('mode', p.get('view', '')), sort_keys=True),
            tuple(x.get('type', x.get('kind', '')) for x in p.get('panel_specs', [])))


# These are parent browsing families. Each original form keeps its own name,
# explicit mode and complete source files inside the parent.
PARENTS = {
    'correlation': 'heatmap', 'state-matrix': 'heatmap',
    'feature-correlation-projection': 'heatmap',
    'point-interval': 'forest', 'reference-strip-effects': 'forest',
    'effect-distribution': 'forest',
    'reference-group-beeswarm': 'raincloud', 'box': 'raincloud', 'violin': 'raincloud',
    'profile': 'ribbon', 'residue-confidence': 'ribbon',
    'reference-aligned-tracks': 'interval-tracks',
    'dashboards': 'composition',
}
EXTRA_TITLES = {
    'heatmap': '热图与矩阵 · 注释、相关、事件状态',
    'forest': '效应与区间 · 森林表、点区间与分布',
    'raincloud': '分布比较 · 云雨、小提琴、箱线与蜂群',
    'ribbon': '曲线与剖面 · 区间带、程序与残基',
    'composition': '配套组图 · 同一条目内选择分析与布局',
    'pca': 'PCA · 椭圆、边缘分布与解释方差',
    'annotation': '细胞身份图谱 · 定位与 Marker 证据',
    'subgroup': '逐亚群多 Marker · 定位、特异性与表达',
    'enrichment-story': '富集配套证据 · 统计量、分母与支持基因',
    'cluster-flow': '聚类流向与谱系 · 固定树和分支',
    'coexpression': '共表达网络诊断 · 拓扑、模块和保留性',
    'reference-surface-grid': '三维曲面与二维投影',
    'radar': '雷达图 · 叠加剖面与分面',
    'reference-parallel-trials': '平行坐标 · 多指标与试验记录',
    'distribution-ecdf': '累积分布 ECDF',
    'covariate-balance': '协变量平衡图',
    'bland-altman-supplied': 'Bland–Altman 一致性图',
    'swimmer-followup': '随访泳道图',
    'specification-curve': '规格曲线 · 模型选择敏感性',
    'supplied-vector-field': '向量场 · 方向与强度',
    'ternary-composition': '三元组成图',
    'genome-association-overview': '基因组关联概览 · Manhattan',
    'funnel-supplied-results': '漏斗图 · 效应与精度',
    'mass-spectrum-mirror': '镜像质谱 · 观察与参考峰',
    'pathway-quantity-overlay': '通路图上的数值叠加',
    'splice-tracks': '剪接轨道 · 覆盖、连接与转录本',
    'variant-posteriors': '变异后验 · 信号与位点',
    'contribution-waterfall': '贡献瀑布图 · 完整有符号分解',
    'sequence-logo': '序列 Logo · 位点与符号高度',
    'contact-tracks': '接触图与物理坐标轨道',
}
KIND_FORM = {
    'fraction': 'bars', 'matrix': 'heatmap', 'effects': 'forest',
    'profile': 'ribbon', 'bins': 'histogram', 'scatter': 'scatter',
    'raincloud': 'raincloud', 'paired': 'paired', 'locus': 'interval-tracks',
    'stack': 'stacked', 'curve': 'ribbon', 'interval': 'forest',
    'points': 'scatter', 'embedding': 'embedding', 'bubble': 'dot-matrix',
    'network': 'network', 'bars': 'bars', 'vector': 'supplied-vector-field',
}
INTEGRATED = dict(pca='pca', volcano='volcano', qc='raincloud', heatmap='heatmap',
                  effect_table='forest', ma='ma', marker_dot='dot-matrix',
                  unit_profile='bars', support='heatmap', design='heatmap', batch_facets='embedding')
COEXPRESSION = dict(module_effects='forest', program_profile='raincloud',
                    hub_network='network', module_dynamics='ribbon',
                    module_enrichment='dot-matrix', module_overlap='heatmap',
                    module_expression='heatmap', module_size='bars',
                    trait_scatter='scatter', projection='scatter',
                    connectivity_change='scatter', stability='forest',
                    preservation_attributes='coexpression', topology='coexpression')
WGCNA = dict(module_trait='heatmap', tom='heatmap', module_activity='embedding',
             eigengene_network='heatmap', eigengene_profiles='raincloud',
             membership_significance='scatter', hub_connectivity='bars',
             module_dendrogram='hierarchy', sample_tree='hierarchy',
             soft_threshold='coexpression', preservation='coexpression', metacell_qc='coexpression')
DOMAINS = dict(general='通用科研画法', bulk='Bulk 转录组', single_cell='单细胞与空间组学',
               multiomics='多组学与基因组证据', structure='结构与计算生物学',
               modelling='计算机建模与模型评估', spatial='空间、三维与几何剖面')
DOMAIN_FORMS = {
    'multiomics': set('feature-correlation-projection mass-spectrum-mirror pathway-quantity-overlay splice-tracks variant-posteriors genome-association-overview interval-tracks contact-tracks sequence-logo rainfall'.split()),
    'structure': set('structures residue-confidence sequence-logo network chord'.split()),
    'modelling': set('roc precision-recall calibration decision survival qq residual-diagnostics specification-curve contribution contribution-waterfall reference-parallel-trials bland-altman-supplied covariate-balance funnel-supplied-results'.split()),
    'spatial': set('radar reference-surface-grid spatial slice registration field maps geographic-links ternary-composition supplied-vector-field'.split()),
}


def classify(spec, native, fallback=None):
    renderer = spec['renderer']; p = spec['parameters']; mode = p.get('mode')
    if renderer.endswith('plot_analysis_evidence') or renderer.endswith('plot_transcriptomic_chapter'):
        kinds = [x['kind'] for x in p['panels']]
        # Repeated identical panels / rows / columns are extensions, not types.
        return KIND_FORM[kinds[0]] if len(set(kinds)) == 1 else 'composition'
    if renderer.endswith('plot_integrated_view'): return INTEGRATED[mode]
    if renderer.endswith('plot_annotation_evidence'): return 'subgroup' if mode == 'subgroup' else 'annotation'
    if renderer.endswith('plot_coexpression_evidence'): return COEXPRESSION[mode]
    if renderer.endswith('plot_wgcna_view'): return WGCNA[mode]
    if renderer.endswith('plot_enrichment_story'): return 'enrichment-story'
    if renderer.endswith('plot_lineage_view'): return 'cluster-flow'
    if renderer.endswith('plot_transcriptomic_overview'): return 'composition'
    if renderer.endswith('plot_diagnostic_panel'): return 'qq' if mode == 'qq' else 'residual-diagnostics'
    functions = dict(plot_annotated_heatmap='heatmap', plot_availability_counts='bars',
                     plot_recorded_evidence='dot-matrix', plot_feature_facets='feature-embedding',
                     plot_alluvial='flow', plot_vector_field='supplied-vector-field',
                     plot_loading_projection='feature-correlation-projection',
                     plot_composition_panels='composition', plot_sample_distribution='raincloud',
                     plot_polished_matrix='heatmap')
    functions['plot_gene_term_chord'] = 'chord'
    if renderer.split('.')[-1] in functions: return functions[renderer.split('.')[-1]]
    aliases = dict(gsea_tracks='gsea', gsea_nes='dot-matrix', gsea_leading_edge='heatmap', ora_terms='enrichment-summary')
    if renderer in aliases: return aliases[renderer]
    style_modes = {
        'package_style': dict(dot='dot-matrix', embedding='embedding', forest='forest', gsea='gsea', heatmap='heatmap',
                              leading='heatmap', module='heatmap', nes='dot-matrix', network='network', ora='enrichment-summary',
                              ridge='ridges', roc='roc', survival='survival', volcano='volcano'),
        'publication_plus': dict(halfeye='raincloud', profile='ribbon', split_matrix='heatmap'),
        'clarity': dict(estimation='raincloud', membership='heatmap', pixels='heatmap', precision_recall='precision-recall',
                        rank_stability='rank', shares='stacked'),
        'refined': dict(association='correlation', ribbon='ribbon', score_shift='scores'),
    }
    if renderer in style_modes and p.get('view') in style_modes[renderer]: return style_modes[renderer][p['view']]
    if signature(spec) in native: return native[signature(spec)]
    if fallback: return fallback
    raise ValueError('Unclassified actual plotting mode: ' + str(signature(spec)))


def build():
    forms = read(S / 'references/form-catalog.json')['forms']
    labels = {f['id']: f['title'] for f in forms}; labels.update(EXTRA_TITLES)
    legacy = {e['id']: f['id'] for f in forms for e in f['extensions']}
    source = read(S / 'assets/source-gallery/manifest.json')['records']
    native = {}
    for row in source:
        spec_path = row['assets'].get('example.spec.json', row['assets'].get('spec'))
        if not spec_path:
            continue  # Current fixed-reference views have no executable spec.
        spec = read(S / 'assets/source-gallery' / spec_path)
        # Source records already name the reviewed form; never guess radar from
        # its renderer or infer a surface from its numeric column names.
        native.setdefault(signature(spec), row['form'].split('__')[0])
    analysis = read(S / 'assets/analysis-library/manifest.json')
    chapter_labels = {s['id']: s['label'] for s in read(S / 'references/analysis-suites.json')['suites']}
    # Prefer current, richer exports. Historical/current versions all survive.
    folders = ['routine-gallery', 'analysis-library', 'source-gallery',
               'method-depth-gallery', 'wgcna-gallery', 'subgroup-gallery',
               'editorial-gallery', 'study-gallery', 'chapter-layouts-gallery',
               'chapter-gallery', 'analysis-gallery', 'companion-gallery',
               'routine-layouts', 'refined-gallery', 'design-gallery',
               'clarity-gallery', 'package-gallery', 'method-gallery', 'aesthetic-gallery']
    rows = []; coverage = []; by_path = {}; missing = []
    analysis_by_png = {str((S / 'assets/analysis-library' / r['assets']['png']).resolve()): r for r in analysis['records']}
    from rebuild_gallery_navigation import adapt_routine
    for folder in folders:
        base = S / 'assets' / folder
        manifest = read(base / 'manifest.json')
        records = adapt_routine(manifest['records']) if folder == 'routine-gallery' else manifest['records']
        for raw in records:
            key = raw.get('key', raw['id']); sid = folder + '/' + key
            a = dict(raw.get('assets', {}))
            if not a:
                a = {ext: raw['id'] + '/' + raw['id'] + '.' + ext for ext in ['png', 'svg', 'pdf', 'tsv']}
            if 'spec' not in a:
                candidate = a.get('example.spec.json', raw.get('spec', 'inputs/' + raw['id'] + '.spec.json'))
                if (base / candidate).is_file(): a['spec'] = candidate
                elif (base / raw['id'] / (raw['id'] + '.json')).is_file(): a['meta'] = raw['id'] + '/' + raw['id'] + '.json'
            assets = {k: '../' + (base / v).relative_to(S / 'assets').as_posix()
                      for k, v in a.items() if k in ['png', 'svg', 'pdf', 'tsv', 'spec', 'meta'] and (base / v).is_file()}
            if 'png' not in assets:
                missing.append(sid); continue
            image = (OUT / assets['png']).resolve()
            related = analysis_by_png.get(str(image), {})
            spec = read(OUT / assets['spec']) if 'spec' in assets else None
            form = raw.get('form') if raw.get('form') in labels else legacy.get(raw['id'])
            if folder == 'source-gallery': form = raw['form'].split('__')[0]
            if not form and spec: form = classify(spec, native)
            if not form: raise ValueError('Unclassified source: ' + sid)
            method = PARENTS.get(form, form)
            if method not in labels: raise ValueError('Unnamed family: ' + method)
            chapters = list(raw.get('chapters', related.get('chapters', [])))
            title = raw.get('title', spec['parameters'].get('title', labels[form]) if spec else labels[form])
            if spec and spec['parameters'].get('projection') == 'surface': title = '三维曲面 · 原始网格与固定视角'
            record = dict(id=sid, original_id=raw['id'], method=method, form=form, title=title,
                          chapters=chapters, assets=assets, renderer=spec['renderer'] if spec else None,
                          parameters=spec['parameters'] if spec else {}, history=False,
                          subtype=labels.get(form, form), origin=folder,
                          source_gallery='../' + folder + '/index.html#' + raw['id'],
                          definition=raw.get('definition', '已存在的冻结绘图示例；保留该示例原有数据、单位与显示范围。'),
                          review=raw.get('visual_review', raw.get('review', raw.get('review_state', raw.get('status')))),
                          executable_spec=bool(spec))
            pathkey = str(image)
            if pathkey in by_path:
                row = by_path[pathkey]; row['aliases'].append(sid)
                row['chapters'] = list(dict.fromkeys(row['chapters'] + chapters))
            else:
                record['aliases'] = [sid]; rows.append(record); by_path[pathkey] = record; row = record
            coverage.append(dict(source_id=sid, record_id=row['id'], method=row['method']))
    if missing: raise ValueError('Missing source pixels: ' + str(missing))
    from full_layout_cases import cases
    legacy_routes = {r['example']: r for r in cases(include_all=True)}
    # All 458 historical examples remain available, including reference-only
    # fixed geometry. Portable previews are local; exact archive downloads are
    # explicitly remote v0.8.0 links, never relabelled as current FigureSpecs.
    for f in forms:
        for e in f['extensions']:
            sid = 'legacy/' + e['id']; thumb = S / 'assets/forms-gallery' / (e['id'] + '.jpg')
            if not thumb.is_file(): raise FileNotFoundError(sid)
            prefix = 'https://github.com/BoteXu/transcriptomics-figure-workbench/blob/v0.8.0/'
            stem = 'examples/forms-v080/' + e['id'] + '/' + e['id']
            record = dict(id=sid, original_id=e['id'], method=PARENTS.get(f['id'], f['id']), form=f['id'],
                          title=e['label'] + ' · ' + e['id'], subtype=f['title'], chapters=[],
                          assets=dict(png='../forms-gallery/' + e['id'] + '.jpg',
                                      original_png=prefix + stem + '.png', svg=prefix + stem + '.svg',
                                      pdf=prefix + stem + '.pdf', meta=prefix + stem + '.json'),
                          renderer=None, parameters=e.get('options', {}), history=True, origin='forms-v080',
                          aliases=[sid], source_gallery='../forms-gallery/index.html#' + f['id'],
                          definition=e['scientific_channels'], executable_spec=False,
                          review='Historical preview and exact archived exports; not a new visual acceptance')
            route = legacy_routes.get(e['id'], {})
            record['renderer'] = route.get('adapter')
            record['parameters'] = route.get('parameters', record['parameters'])
            record['legacy_route'] = route.get('route', 'fixed_composition')
            rows.append(record); coverage.append(dict(source_id=sid, record_id=sid, method=record['method']))
    grouped = defaultdict(list)
    for r in rows: grouped[r['method']].append(r)
    entries = [dict(id=k, title=labels[k], member_ids=[r['id'] for r in rs],
                    default_id=next(r['id'] for r in rs if not r['history']),
                    forms=list(dict.fromkeys(r['form'] for r in rs))) for k, rs in grouped.items()]
    # Prefer current specialist examples and retain the old key as an alias.
    aliases = {a: r['id'] for r in rows for a in r['aliases']}
    for f in forms:
        preferred = next((r for r in rows if r['id'] == 'source-gallery/' + f['id']), None)
        preferred = preferred or next(r for r in rows if r['form'] == f['id'] and not r['history'])
        aliases[f['id']] = preferred['id']
        for e in f['extensions']: aliases[e['id']] = 'legacy/' + e['id']
    for row in source: aliases[row['id']] = aliases['source-gallery/' + row['id']]
    for r in rows:
        r['domains'] = ['general']
        r['domains'] += list(dict.fromkeys(c.split('.')[0] for c in r['chapters']))
        r['domains'] += [d for d, fs in DOMAIN_FORMS.items() if r['form'] in fs]
        r['domains'] = list(dict.fromkeys(r['domains']))
    order = list(dict.fromkeys(PARENTS.get(f['id'],f['id']) for f in forms)) + list(EXTRA_TITLES)
    entries.sort(key=lambda e: order.index(e['id']))
    registry = read(S / 'references/renderer-registry.json')['renderers']
    adapters = read(S / 'references/renderer-adapters.json')['adapters']
    backend = lambda r: adapters.get(r['renderer'], {}).get('renderer', r['renderer'])
    renderer_coverage = []
    for r in registry:
        matches = [x for x in rows if backend(x) == r['id']]
        renderer_coverage.append(dict(renderer=r['id'], title=r['display_name'],
            current_spec_examples=[x['id'] for x in matches if x['executable_spec']],
            historical_or_reference_examples=[x['id'] for x in matches if not x['executable_spec']],
            state='CURRENT_SPEC' if any(x['executable_spec'] for x in matches) else 'HISTORICAL_RECIPE' if matches else 'SOURCE_ONLY',
            runtime_acceptance='Not re-tested by navigation indexing'))
    wrapper = next(r for r in renderer_coverage if r['renderer']=='figure_palette_applications.plot_palette_panel')
    wrapper.update(state='DELEGATING_WRAPPER', delegates_to='figure_palette_applications.plot_palette_plate',
                   scope='Single panel wrapper; no additional scientific method or independent example claimed')
    manifest = dict(schema_version=1, scope='Multi-omics, computational biology and computer modelling drawing library',
                    entries=entries, records=rows, aliases=aliases,
                    form_labels={f['id']: f['title'] for f in forms} | EXTRA_TITLES,
                    domains=[dict(id=k, label=v) for k,v in DOMAINS.items()],
                    renderer_coverage=renderer_coverage,
                    chapters=[dict(id=k, label=v) for k,v in chapter_labels.items()],
                    coverage=coverage, counts=dict(source_records=len(coverage), actual_entries=len(rows),
                         method_families=len(entries), preserved_base_forms=len(forms),
                         historical_examples=458, galleries=len(folders), removed_assets=0,
                         registered_renderers=len(registry), renderers_with_examples=sum(bool(x['current_spec_examples'] or x['historical_or_reference_examples']) for x in renderer_coverage),
                         delegating_wrappers=1, unaccounted_renderers=sum(x['state']=='SOURCE_ONLY' for x in renderer_coverage)),
                    scientific_acceptance=False, aesthetic_approval=False)
    OUT.mkdir(exist_ok=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    template = (S / 'assets/studio/visual-library.html').read_text(encoding='utf8')
    (OUT / 'index.html').write_text(template.replace('/*DATA*/{}', json.dumps(manifest, ensure_ascii=False).replace('<','\\u003c')), encoding='utf8')
    lines = ['# 综合绘图库：方法保留与覆盖范围', '',
             '由实际目录和渲染器登记表生成。索引存在、代码存在、后端运行和视觉验收分别记录。', '',
             '## 计数', '', *[f'- {k}: {v}' for k,v in manifest['counts'].items()], '',
             f"{len(forms)} 个基础画法完整保留；相近画法作为{len(entries)}个父族中的具名扩展。{len(folders)}份目录含重叠来源，{len(coverage)}不是独立绘图方法数。", '',
             '## 渲染器对照', '', '|登记入口|现有 FigureSpec|历史／参考例|状态|', '|---|---:|---:|---|']
    for r in renderer_coverage:
        lines.append(f"|`{r['renderer']}`|{len(r['current_spec_examples'])}|{len(r['historical_or_reference_examples'])}|{r['state']}|")
    lines += ['', '## 全面性的边界', '',
              '这份清单核对的是现有实现，不代表所有科学可视化方法已经穷尽。三维曲面有实际原始网格、二维映射及三维视角实例；不据此宣称已提供三维散点、体渲染、分子轨迹动画或交互三维网格。雷达保留原始剖面及历史示例；大于四条剖面需分面。', '',
              '多组学索引含跨层关系、基因组轨道、变异后验、剪接、质谱和通路叠加；建模含ROC、PR、校准、决策、生存、残差、贡献与敏感性。结构固定参考与可运行数值图分别标记。原生软件包算法没有因绘图入口而被实现或重新验证。', '',
              '历史版本完整导出沿用既有公开 v0.8.0 归档链接，便携安装提供离线预览；当前 FigureSpec、输入和导出直接使用随包本地文件。']
    (S / 'references/visual-library-coverage.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
    print(json.dumps(manifest['counts']))


if __name__ == '__main__':
    build()
