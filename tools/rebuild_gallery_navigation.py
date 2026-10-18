"""Rebuild offline navigation without touching any frozen image or table."""
import json
from pathlib import Path
from analysis_gallery_page import page
from curate_analysis_navigation import curated_entries,form_navigation
from build_analysis_library import LABELS
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench'
ROLE_CHAPTER={'qc_distribution':'qc','sample_embedding':'batch','sample_correlation':'batch','library_summary':'reads','design_map':'design','differential_expression':'differential','differential_heatmap':'programs','effect_intervals':'differential','ma':'differential','gene_expression':'programs','enrichment_summary':'ora','gsea_curves':'gsea_multitrack','study_overview':'design','enrichment_contrasts':'pathway_contrasts','pathway_gene_support':'gene_support','donor_summary':'design','batch_embedding':'integration','celltype_embedding':'annotation','marker_dot':'markers','marker_features':'markers','donor_composition':'composition','donor_differential':'pseudobulk','marker_subgroup':'subcluster','condition_embedding':'annotation','donor_cell_support':'composition'}
ID_ROLES={}
for role,ids in {
 'qc_distribution':['BulkQC','CellQC'],'sample_embedding':['BulkPCA'],'sample_correlation':['BulkCorrelation'],
 'library_summary':['LibrarySizes'],'design_map':['StudyDesign','CellStudyDesign'],'study_overview':['BulkMain'],
 'differential_expression':['BulkDE'],'donor_differential':['DonorDE'],'differential_heatmap':['BulkHeatmap','DonorHeatmap'],
 'effect_intervals':['GeneEffects','DonorEffects'],'ma':['BulkMA','DonorMA'],'gene_expression':['GeneExpression'],
 'enrichment_summary':['Pathways','DonorPathways'],'gsea_curves':['EnrichmentTracks','DonorEnrichmentTracks','bulk_GSEADetail_Reading','single_cell_GSEADetail_Reading','EnrichmentTracks_Custom'],
 'enrichment_contrasts':['bulk_GSEASummary','single_cell_GSEASummary'],'pathway_gene_support':['bulk_GeneSupport','single_cell_GeneSupport'],
 'donor_summary':['DonorCounts'],'batch_embedding':['CellBatches'],'celltype_embedding':['CellTypes'],
 'marker_dot':['MarkerDot'],'marker_features':['MarkerFeatures'],'donor_composition':['DonorComposition'],
 'condition_embedding':['ConditionAtlas'],'donor_cell_support':['DonorTypeSupport']}.items():
    for key in ids:ID_ROLES[key]=role
def adapt_routine(rows):
    mapped=[]
    for i,raw in enumerate(rows):
        r=dict(raw);role=r.get('role',ID_ROLES.get(r['id'],r['stage']));a=r['assay'];suffix=ROLE_CHAPTER.get(role,'gsea' if 'GSEA' in r['id'] or 'EnrichmentTracks' in r['id'] else 'subcluster' if r['id'].startswith('Subgroup') else 'design')
        if a=='bulk' and suffix=='qc':suffix='normalization'
        if a=='single_cell':suffix={'programs':'pseudobulk','differential':'pseudobulk','ora':'pathways','gsea':'pathways','gsea_multitrack':'pathways','pathway_contrasts':'pathways'}.get(suffix,suffix)
        c=a+'.'+suffix
        r.update(chapters=[c],stage='layout' if r['stage']=='reading' else 'qc' if r['stage']=='qc' else 'function' if r['stage']=='pathways' else 'interpretation',variant=bool('Custom' in r['id'] or 'Reading' in r['id']),order=i,renderer='',definition=r.get('note','Explicit frozen drawing example'),requirements=[],review=r.get('review_state','Existing image review retained'))
        mapped.append(r)
    return mapped
def rebuild():
    chapters=[dict(id=k,label=v) for k,v in LABELS.items()]
    for name in ['analysis-gallery','companion-gallery','routine-gallery']:
        base=S/'assets'/name;path=base/'manifest.json';m=json.loads(path.read_text(encoding='utf8'));rows=m['records']
        if name=='routine-gallery':rows=adapt_routine(rows)
        for r in rows:
            spec=json.loads((base/r['assets']['spec']).read_text(encoding='utf8'));r['renderer']=spec['renderer']
        used={c for r in rows for c in r['chapters']};cc=[c for c in chapters if c['id'] in used]
        m['navigation']=curated_entries(rows,cc);m['forms']=form_navigation(rows,cc)
        path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        (base/'index.html').write_text(page(rows,cc,'已合并近似画法及布局；分析示例保留独立来源与含义。'),encoding='utf8')
        print(json.dumps(dict(gallery=name,sources=len(rows),forms=m['forms']['navigation_entries'])))
if __name__=='__main__':rebuild()
