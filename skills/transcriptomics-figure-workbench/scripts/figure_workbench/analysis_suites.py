"""Source-bound multi-view discovery and explicit synthetic template export."""
from pathlib import Path
from .contracts import read_json,write_new,local_path,make_plan
from .views import chapter_views,view_template
SKILL=Path(__file__).resolve().parents[2]

def analysis_library(search=''):
    rows=read_json(SKILL/'references/analysis-suites.json')['suites']
    query=search.casefold().strip()
    if query=='wgcna':return [r for r in rows if r['id'] in ['bulk.wgcna','single_cell.hdwgcna']]
    return [r for r in rows if query in str(r).casefold()]

def analysis_suite(chapter,output,include_variants=False):
    row=next((r for r in analysis_library() if r['id']==chapter),None)
    if row is None:raise ValueError('Choose a shipped analysis chapter')
    if type(include_variants) is not bool:raise ValueError('Variant inclusion must be explicit')
    selected=row['primary_views']+(row['alternative_views'] if include_variants else [])
    known={v['id']:v for v in chapter_views()}
    if not selected or len(selected)!=len(set(selected)) or set(selected)-set(known):raise ValueError('Stale or ambiguous analysis suite')
    output=Path(output);output.mkdir(parents=True,exist_ok=False);records=[]
    for key in selected:
        safe=key.replace('.','_');dest=output/safe;view_template(key,dest)
        records.append(dict(id=safe,spec=safe+'/example.spec.json',chapters=[chapter],stage=known[key].get('stage','chapter'),
                            family=known[key]['form'],variant=key in row['alternative_views']))
    write_new(output/'manifest.json',dict(schema_version=1,chapter=chapter,records=records,analysis_performed=False,
                                         scope='Exact selected synthetic drawing templates. No private project discovery, backend execution or scientific acceptance.'))
    write_new(output/'analysis-suite.json',row)
    return dict(state='EXPLICIT_SYNTHETIC_ANALYSIS_SUITE_EXPORTED',chapter=chapter,figures=len(records),analysis_performed=False,visual_acceptance=False)


def render_analysis_suite(manifest,base,output):
    """Execute only explicit synthetic drawing templates, serially, into a new bundle."""
    import re
    if not isinstance(manifest,dict) or manifest.get('schema_version')!=1 or manifest.get('analysis_performed') is not False:
        raise ValueError('Use an exported synthetic analysis-suite manifest')
    if manifest.get('chapter') not in {r['id'] for r in analysis_library()}:
        raise ValueError('Choose one actual analysis chapter')
    rows=manifest.get('records');plans=[];ids=set()
    if not isinstance(rows,list) or not 1<=len(rows)<=100:raise ValueError('Explicit bounded template records required')
    for row in rows:
        if not isinstance(row,dict) or not {'id','spec'}<=set(row):raise ValueError('Explicit template identity and local specification required')
        key=row.get('id')
        if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',key) or key in ids:raise ValueError('Unique safe drawing IDs required')
        ids.add(key);path=local_path(row['spec'],base);spec=read_json(path)
        if spec['provenance'].get('synthetic') is not True:raise ValueError('Use book-plan for real frozen results and reviewed upstream QC')
        plans.append((key,make_plan(spec,path.parent)))
    output=Path(output);output.mkdir(parents=True,exist_ok=False);completed=[]
    from .pipeline import render_plan
    for key,plan in plans:
        try:
            result=render_plan(plan,output/key);completed.append(dict(id=key,result=result))
            write_new(output/(key+'.receipt.json'),completed[-1])
        except Exception as exc:
            write_new(output/'manifest.json',dict(state='PARTIAL_FAILURE',completed=completed,failed_id=key,error=str(exc),analysis_performed=False,visual_acceptance=False))
            raise
    receipt=dict(state='SYNTHETIC_ANALYSIS_SUITE_RENDERED_UNREVIEWED',completed=completed,analysis_performed=False,visual_acceptance=False)
    write_new(output/'manifest.json',receipt)
    return receipt


def named_analysis_chapters(assay,request):
    """Bounded named-method routing; never infer result availability or execute an analysis."""
    import re
    if assay not in ['bulk','single_cell'] or not isinstance(request,str) or not request.strip():raise ValueError('Explicit assay and nonempty drawing request required')
    choices=[(r'hd\s*wgcna|单细胞.*wgcna','single_cell.hdwgcna'),(r'(?<![a-z])wgcna(?![a-z])','bulk.wgcna' if assay=='bulk' else 'single_cell.hdwgcna'),
             (r'gsva|ssgsea','bulk.gsva' if assay=='bulk' else 'single_cell.pathways'),(r'regulon|调控子','single_cell.regulons' if assay=='single_cell' else 'bulk.tf_activity'),
             (r'cellchat|cellphonedb|细胞通讯','single_cell.communication'),(r'拟时序|trajectory','single_cell.trajectory'),
             (r'velocity','single_cell.velocity'),(r'可变剪接|splicing','bulk.splicing' if assay=='bulk' else 'single_cell.splicing'),
             (r'(?<![a-z])ppi(?![a-z])|蛋白互作','bulk.ppi'),(r'(?<![a-z])cnv(?![a-z])','single_cell.cnv'),(r'(?<![a-z])vdj(?![a-z])','single_cell.vdj')]
    matched=[]
    for pattern,chapter in choices:
        if re.search(pattern,request,re.I) and chapter not in matched:matched.append(chapter)
    return matched
