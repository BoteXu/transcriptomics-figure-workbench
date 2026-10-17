"""Revise display specifications while preserving every frozen source TSV byte.

New display-only cloud shapes are allowed exclusively for labelled synthetic
fixtures; real data must supply reviewed densities from its authorized backend.
"""
import argparse,copy,hashlib,json,shutil
from pathlib import Path


def prepare(source,out):
    import numpy as np,pandas as pd
    doc=json.loads((source/'manifest.json').read_text(encoding='utf8'));out.mkdir(parents=True,exist_ok=False)
    rows=doc['records'];by={r['id']:r for r in rows}
    def table(k):return pd.read_csv(source/by[k]['assets']['tsv'],sep='\t',float_precision='round_trip')
    atlas=table('CellTypes');emb=atlas[atlas.record_type=='embedding'];counts={str(k):int(v) for k,v in emb.group.value_counts(sort=False).items()}
    cell_identities=dict(zip(emb.object_id,emb.group));groups=json.loads((source/by['CellTypes']['assets']['spec']).read_text(encoding='utf8'))['parameters']['group_order']
    design=table('StudyDesign').pivot(index='label',columns='series',values='value')
    annotations={s:dict(condition='Treated' if row['Treated'] else 'Control',batch='Batch 2' if row['Batch 2'] else 'Batch 3' if row['Batch 3'] else 'Batch 1') for s,row in design.iterrows()}
    condition=table('ConditionAtlas');donor_annotations={r.donor_id:annotations[r.cell_id] if r.cell_id in annotations else dict(condition=r.group,batch=r.batch) for r in condition.drop_duplicates('donor_id').itertuples()}
    titles={'BulkQC':'Expression distributions','CellQC':'Single-cell quality distributions','BulkPCA':'Sample structure','BulkCorrelation':'Sample correlation',
        'LibrarySizes':'Library coverage','StudyDesign':'Study design and batch coding','CellStudyDesign':'Donor design and batch coding',
        'BulkDE':'Differential expression','BulkMA':'Expression level and effect size','CellBatches':'Batch representation across cell identities',
        'MarkerDot':'Marker identity and detection','GeneExpression':'Selected gene expression','DonorTypeSupport':'Cell support across independent donors',
        'ConditionAtlas':'Cell identities across conditions','DonorDE':'Myeloid · differential expression','DonorMA':'Myeloid · expression level and effect size',
        'BulkHeatmap':'Selected expression programs','DonorHeatmap':'Myeloid · selected expression programs','CellTypes':'Cell identities and marker evidence'}
    result=[]
    for row in rows:
        k=row['id'];p=source/row['assets']['spec'];s=json.loads(p.read_text(encoding='utf8'))
        if s['provenance'].get('synthetic') is not True:raise ValueError('This fixture preparation tool accepts explicitly synthetic inputs only')
        folder=out/k;folder.mkdir();raw=source/row['assets']['tsv'];shutil.copyfile(raw,folder/(k+'.tsv'));s['input']['path']=k+'.tsv'
        assert hashlib.sha256(raw.read_bytes()).hexdigest()==s['input']['sha256']
        params=s['parameters'];actual=params.get('options',params)
        if k in titles:actual['title']=titles[k]
        s['appearance'].update(label_pt=10.5,tick_pt=10,note_pt=9.5,title_pt=12)
        s['export']['target_width_mm']=240 if row['stage']!='reading' else row['width']
        if params.get('mode') in ['qc','pca','volcano','ma','unit_profile','marker_dot','batch_facets','effect_table']:params['presentation']='publication'
        if k=='BulkPCA':params['ellipse_definition']='Supplied 95% reference dispersion contours; illustrative, not mean confidence intervals or a separation test.'
        if k in ['BulkHeatmap','DonorHeatmap','BulkCorrelation']:
            params.update(presentation='publication',matrix_semantics='correlation' if k=='BulkCorrelation' else 'expression')
        if k in ['Pathways','DonorPathways','bulk_GSEASummary','single_cell_GSEASummary','bulk_GeneSupport','single_cell_GeneSupport']:
            params['presentation']='publication';params['title']=('Myeloid · ' if row['assay']=='single_cell' else '')+('Pathway enrichment' if params['mode']=='ora' else 'Pathway direction' if params['mode']=='gsea_comparison' else 'Gene–pathway support')
        if k in ['StudyDesign','CellStudyDesign','DonorTypeSupport']:
            params['presentation']='publication';params['scope_note']='12 simulated donors · six per condition'
            panel=params['panels'][0];panel['matrix_semantics']='cell_support' if k=='DonorTypeSupport' else 'design';panel['sample_annotations']=donor_annotations if k=='DonorTypeSupport' else annotations
            if k!='DonorTypeSupport':panel['reference_definition']='Control and Batch 1'
            if k=='DonorTypeSupport':panel['column_aliases']={d:d.replace('Donor ','') for d in donor_annotations}
        if k=='ConditionAtlas':
            params.update(presentation='publication',scope_note='900 cells nested within 12 donors · common coordinates')
            for panel in params['panels']:
                part=condition[condition.panel_id==panel['id']];panel['title']=panel['id']+' · '+str(part.donor_id.nunique())+' donors / '+str(len(part))+' cells'
        if k=='MarkerDot':params.update(group_counts=counts,expression_limits=[0,5]);s['export']['target_width_mm']=260
        if k=='MarkerFeatures':params.update(presentation='publication',title='Representative markers · shared coordinates and expression scale',point_size=10);s['export']['target_width_mm']=297;s['appearance'].update(label_pt=12,tick_pt=11,note_pt=11)
        if k=='CellBatches':params.update(identity_by_cell=cell_identities,identity_order=groups);s['export']['target_width_mm']=260
        if k.startswith('Subgroup_'):
            params['title']=params['focus_group']+' · marker evidence';s['export']['target_width_mm']=row['width']
        if k=='GeneExpression':
            params.update(presentation='publication',scope_note='Every point is one donor · six per condition')
            for panel in params['panels']:panel['title']=panel['title'].replace(' · raincloud','')
        if k=='DonorComposition':
            d=table(k);total=d.groupby('sample')['count'].sum();shapes={}
            for t in d.celltype.unique():
                shapes[t]={}
                for g in d.group.unique():
                    part=d[(d.celltype==t)&(d.group==g)];v=(part['count']/part['sample'].map(total)).to_numpy();grid=np.linspace(v.min(),v.max(),128);width=np.exp(-.5*((grid[:,None]-v[None,:])/.035)**2).sum(axis=1)
                    shapes[t][g]=dict(grid=grid.tolist(),width=width.tolist(),n=len(v),definition='Synthetic supplied display mixture; fixed bandwidth 0.035 fraction units, restricted to observed range; no inferential meaning')
            theme=s['theme'];colors={g:theme['palette_colors'][theme['group_slots'][g]] if g in theme['group_slots'] else theme['category_colors'][g] for g in groups}
            params.update(cloud_shapes=shapes,celltype_palette=colors)
        if params.get('view')=='gsea_strip':
            actual['contrast']='Treated vs Control';actual['gene_set_version']='Synthetic set definition v0.9';actual['metric_label']='log2 fold change'
            actual['title']=('Myeloid · ' if row['assay']=='single_cell' else '')+('Interferon response' if 'Reading' in k else 'Pathway enrichment profiles')
            if 'Reading' in k:actual['line_encoding']='pathway'
            if k=='EnrichmentTracks_Custom':actual['panel_width']=3.3
        s['provenance']['source']+='; publication v0.9.6 display revision with unchanged frozen table bytes'
        (folder/(k+'.spec.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        result.append(dict(id=k,assay=row['assay'],stage=row['stage'],variant=row['variant'],spec_path=k+'/'+k+'.spec.json',previous_png_sha256=row['png_sha256'],input_sha256=s['input']['sha256']))
    (out/'prepared.manifest.json').write_text(json.dumps(dict(records=result,requests=doc['ordinary_requests'],all_43_tsv_bytes_unchanged=True),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PUBLICATION_SPECS_PREPARED',len(result),'ALL_SOURCE_TSV_BYTES_UNCHANGED')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();prepare(a.source,a.output)
