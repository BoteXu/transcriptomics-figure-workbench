"""Plan coherent figure sets from selected, frozen transcriptomic results.

No expression analysis, cell annotation, enrichment, fitting or file discovery.
The host interprets the research question; this bounded vocabulary covers common
requests and binds every selected panel to an actual FigureSpec and source.
"""
import re
from pathlib import Path
from .contracts import read_json, local_path, make_plan, hash_value, write_new, check_plan


STAGES = {
    'bulk': {
        'overview': [('study_overview', False)],
        'qc': [('qc_distribution', True), ('sample_embedding', True), ('sample_correlation', True), ('library_summary', False), ('design_map', False)],
        'differential': [('differential_expression', True), ('differential_heatmap', True), ('effect_intervals', False), ('ma', False)],
        'pathways': [('enrichment_summary', True), ('gsea_curves', False), ('enrichment_contrasts', False)],
    },
    'single_cell': {
        'overview': [('study_overview', False)],
        'qc': [('qc_distribution', True), ('donor_summary', True), ('batch_embedding', False)],
        'markers': [('celltype_embedding', True), ('marker_dot', True), ('marker_features', True), ('marker_heatmap', False)],
        'composition': [('donor_composition', True), ('donor_summary', False)],
        'differential': [('donor_differential', True), ('effect_intervals', False), ('differential_heatmap', False), ('ma', False)],
        'pathways': [('enrichment_summary', True), ('gsea_curves', False), ('enrichment_contrasts', False)],
    },
}

INTENTS = [
    ('qc', r'质控|质量|\bqc\b|quality'),
    ('markers', r'标记|注释|细胞类型|markers?|annotation'),
    ('composition', r'组成|比例|composition|proportion'),
    ('differential', r'差异|差別|differential|pseudobulk'),
    ('pathways', r'通路|富集|pathway|enrich|gsea'),
]


def select_stages(assay, request):
    if not isinstance(request, str) or not request.strip():
        raise ValueError('State the requested comparison or figure set')
    if re.search(r'文章|论文|全套|一套|成套|整体|全部|overview|manuscript|whole|complete', request, re.I):
        return list(STAGES[assay])
    selected=[stage for stage, pattern in INTENTS if re.search(pattern, request, re.I)]
    return [s for s in STAGES[assay] if s in selected]


def study_plan(manifest, request, base):
    required={'schema_version','assay','title','contrast','independent_unit','denominator','frozen_results','upstream_qc','results'}
    if not isinstance(manifest, dict) or set(manifest)!=required or manifest['schema_version']!=1:
        raise ValueError('Use the complete documented StudyFigureManifest')
    assay=manifest['assay']
    if assay not in STAGES or manifest['frozen_results'] is not True:
        raise ValueError('Choose bulk or single_cell and explicitly frozen results')
    for field in ['title','contrast','independent_unit','denominator']:
        if not isinstance(manifest[field], str) or not manifest[field].strip():
            raise ValueError('Complete study identity, contrast, unit and denominator required')
    if manifest['upstream_qc'] not in ['reviewed','unknown','failed']:
        raise ValueError('Declare actual upstream QC state')
    results=manifest['results'];allowed={r for stages in STAGES.values() for roles in stages.values() for r,_ in roles}
    if not isinstance(results,list) or len(results)>50:
        raise ValueError('Select at most fifty explicit result specifications')
    by={}
    for result in results:
        if not isinstance(result,dict) or set(result)!={'role','spec'} or result['role'] not in allowed or result['role'] in by:
            raise ValueError('One selected FigureSpec per known result role; no ambiguous duplicate')
        path=local_path(result['spec'],base);by[result['role']]=path
    stages=select_stages(assay,request);blocking=[];missing=[];panels=[];sections=[];seen=set();slots={}
    if not stages:blocking.append('Request does not match a documented figure-set intent; the host must clarify the comparison')
    if manifest['upstream_qc']!='reviewed' and stages!=['qc']:blocking.append('Upstream design and QC are not declared reviewed')
    if manifest['independent_unit'].strip().casefold() in ['unknown','cell','cells','spot','spots','细胞','未确定','?'] and 'differential' in stages:
        blocking.append('Differential inference requires an explicit biological independent unit; cells or spots alone are insufficient')
    for stage in stages:
        keys=[]
        for role,mandatory in STAGES[assay][stage]:
            if role not in by:
                missing.append({'stage':stage,'role':role,'required':mandatory,'state':'NOT_SUPPLIED'})
                if mandatory:blocking.append('Missing required frozen result: '+role)
                continue
            keys.append(role)
            if role in seen:continue
            seen.add(role);path=by[role];spec=read_json(path);plan=make_plan(spec,path.parent)
            colours={label:spec['theme']['palette_colors'][slot] for label,slot in spec['theme']['group_slots'].items()}
            colours.update(spec['theme'].get('category_colors',{}))
            for label,color in colours.items():
                if label in slots and slots[label]!=color:raise ValueError('Inconsistent category colour across the selected figure set: '+label)
                slots[label]=color
            panels.append({'role':role,'stage':stage,'spec_sha256':hash_value(spec),'plan':plan})
        sections.append({'stage':stage,'panels':keys})
    return {'schema_version':1,'state':'HOLD' if blocking else 'FIGURE_SET_PLANNED',
        'assay':assay,'title':manifest['title'],'request':request,'contrast':manifest['contrast'],
        'independent_unit':manifest['independent_unit'],'denominator':manifest['denominator'],
        'manifest_sha256':hash_value(manifest),'sections':sections,'panels':panels,
        'missing_results':missing,'blocking_reasons':blocking,'category_colours':slots,
        'presentation':'Question-led sections; complete individual figures, then an explicitly sized composition or paginated reading edition',
        'review_requirements':['Inspect every single figure and every composition page at the actual target size',
            'Review hierarchy, complementary information, redundant panels, scale/units, colour meaning, labels and balance',
            'Missing upstream results remain missing; an attractive export never certifies the analysis'],
        'analysis_performed':False,'visual_acceptance':False,'scientific_acceptance':False}


def render_study(plan, output):
    if plan.get('state')!='FIGURE_SET_PLANNED':raise ValueError('Resolve every figure-set HOLD before rendering')
    assay=plan.get('assay');panels=plan.get('panels')
    if assay not in STAGES or not isinstance(panels,list) or not 1<=len(panels)<=50:raise ValueError('A selected supported figure set is required')
    seen=set()
    for p in panels:
        if p.get('stage') not in STAGES[assay] or p.get('role') not in {r for r,_ in STAGES[assay][p['stage']]} or p['role'] in seen:raise ValueError('Unknown, duplicate or unsafe figure-set panel identity')
        seen.add(p['role']);check_plan(p['plan'])
        if p.get('spec_sha256')!=p['plan']['spec_sha256']:raise ValueError('Figure-set source binding changed')
    from .pipeline import render_plan
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rows=[]
    try:
        for panel in plan['panels']:
            result=render_plan(panel['plan'],output/panel['role'])
            rows.append({'role':panel['role'],'stage':panel['stage'],'result':result})
            print('FIGURE_SET_PANEL '+panel['role'],flush=True)
    except Exception:
        write_new(output/'partial-receipt.json',{'state':'PARTIAL_FAILED','completed':rows,'automatic_retry':False})
        raise
    receipt={'state':'RENDERED_REVIEW_REQUIRED','assay':plan['assay'],'request':plan['request'],
        'plan_sha256':hash_value(plan),'panels':rows,'missing_results':plan['missing_results'],
        'analysis_performed':False,'visual_acceptance':False,'scientific_acceptance':False}
    write_new(output/'figure-set-receipt.json',receipt)
    return receipt
