"""Group equivalent drawings and named extensions without discarding assets.

Groups are an editorial navigation decision. A declared layout/sample-size
extension is not claimed to contain identical scientific data.
"""
import hashlib,json,re

FORM_LABELS={
 'fraction':'比例与分母', 'matrix':'热图与矩阵注释', 'effects':'效应与区间',
 'profile':'曲线与参考带', 'bins':'完整分布直方图', 'scatter':'散点与参考线',
 'raincloud':'云雨图', 'paired':'配对变化', 'locus':'基因组区域与结构',
 'stack':'堆积组成', 'curve':'变化曲线', 'interval':'区间估计', 'points':'观测点',
 'embedding':'降维嵌入', 'bubble':'点阵证据', 'network':'网络', 'bars':'条形统计', 'vector':'向量场'}

def form_navigation(rows,chapters):
    """A reusable drawing family is one entry; scoped datasets are examples.

    This is deliberately NOT scientific-result deduplication. For example, an
    odds-ratio table and a log2FC table remain separate callable specifications
    and retain their original scales, units, context and assets in the selector.
    """
    rank={c['id']:i for i,c in enumerate(chapters)};groups={}
    for r in rows:
        p=r['parameters'];kinds=[x['kind'] for x in p.get('panels',[])]
        # Layout/order variants of the same panel set belong to one drawing.
        signature=(r['renderer'],tuple(sorted(kinds)) if kinds else (p.get('mode',p.get('view',r['renderer'].split('.')[-1])),))
        groups.setdefault(signature,[]).append(r)
    entries=[];aliases={}
    for signature,members in groups.items():
        key='form_'+hashlib.sha256(json.dumps(signature).encode()).hexdigest()[:12]
        members.sort(key=lambda r:(bool(r.get('variant')),r.get('order',0),r['id']))
        main=members[0];kinds=signature[1]
        if signature[0].endswith('plot_analysis_evidence') or signature[0].endswith('plot_transcriptomic_chapter'):
            title=' + '.join(FORM_LABELS.get(k,k) for k in kinds)
            if len(kinds)>1:title='组图 · '+title
        else:title=main['title']
        entry=dict(id=key,title=title,stage=main['stage'],default_id=main['id'],member_ids=[r['id'] for r in members],
                   chapters=list(dict.fromkeys(c for r in members for c in r['chapters'])),variant=all(r.get('variant',False) for r in members),
                   keywords=list(dict.fromkeys(k for r in members for k in r.get('keywords',[]))),
                   merge_reason='One configurable drawing family; scoped examples retain distinct data, units, titles and exact assets',
                   original_order=min(r.get('order',0) for r in members))
        entries.append(entry)
        for r in members:aliases[r['id']]=key
    entries.sort(key=lambda r:(min(rank.get(c,999) for c in r['chapters']),r['original_order'],r['id']))
    for i,r in enumerate(entries):r['order']=i
    return dict(entries=entries,aliases=aliases,source_pages=len(rows),navigation_entries=len(entries),
                folded_extensions=len(rows)-len(entries),default_entries=sum(not r['variant'] for r in entries),
                asset_files_removed=0,policy='Reusable form families, with scoped scientific examples and layouts inside each entry; no scientific result merging')

PREFERRED={
 'bulk.wgcna.complete':'WGCNA_ModuleTrait','single_cell.hdwgcna.complete':'hdWGCNA_MetacellQC',
 'WGCNA_SoftPower':'SoftPower_CompleteDiagnostics','WGCNA_TOM':'TOM_AlignedHierarchy',
 'WGCNA_TOM_Dissimilarity':'TOM_AlignedHierarchy','WGCNA_MM_GS_Absolute':'WGCNA_MM_GS',
 'WGCNA_EigengeneProfiles':'Eigengenes_DonorRainclouds','Layout_OneModule_8Donors':'Eigengenes_DonorRainclouds',
 'Layout_ThreeModules_OneColumn':'Eigengenes_DonorRainclouds','Layout_ThreeModules_ThreeColumns':'Modules_BranchDynamics',
 'Layout_Expression_OneColumn':'Modules_ExpressionAndEigengenes','Layout_Contrasts_OneColumn':'Eigengenes_DonorContrasts',
 'Layout_Enrichment_12Modules':'Modules_FunctionAndGeneSupport',
 'single_cell.resolution.complete':'ClusterFlow_2Column'}

def curated_entries(rows,chapters):
    by={r['id']:r for r in rows};chapter_rank={r['id']:i for i,r in enumerate(chapters)}
    grouped={};exact={};alias_map={}
    for r in rows:
        key=PREFERRED.get(r['id'],r['id'])
        if r['id'].endswith('_Custom') and r['id'][:-7] in by:key=r['id'][:-7]
        detail={'bulk_GSEADetail_Reading':'EnrichmentTracks','single_cell_GSEADetail_Reading':'DonorEnrichmentTracks'}.get(r['id'])
        if detail in by:key=detail
        if key not in by:key=r['id']
        if re.search(r'_(Layout|ThreeColumns)$',r['id']):
            candidate=re.sub(r'_(Layout|ThreeColumns)$','_Evidence',r['id'])
            if candidate in by:key=candidate
        # Exact equality supplied by the builder includes parameters and input.
        fingerprint=r.get('drawing_fingerprint')
        if fingerprint:
            fingerprint=(fingerprint,tuple(sorted(r['chapters'])))
            if fingerprint in exact:key=exact[fingerprint]
            else:exact[fingerprint]=key
        alias_map[r['id']]=key
    # Resolve chains so preferred IDs do not reappear as a second main entry.
    for key in alias_map:
        dest=alias_map[key];seen={key}
        while dest in alias_map and alias_map[dest]!=dest and dest not in seen:
            seen.add(dest);dest=alias_map[dest]
        alias_map[key]=dest
    for r in rows:grouped.setdefault(alias_map[r['id']],[]).append(r)
    stages=['qc','network','interpretation','function','validation','extension','chapter','layout']
    entries=[]
    for key,members in grouped.items():
        main=by.get(key,members[0]);order=[main]+[r for r in members if r['id']!=main['id']]
        chapters_for=list(dict.fromkeys(c for r in order for c in r['chapters']))
        entry=dict(id=key,title=main['title'],stage=main['stage'],chapters=chapters_for,
                   default_id=main['id'],member_ids=[r['id'] for r in order],
                   variant=all(r.get('variant',False) for r in members),
                   keywords=sorted({str(k) for r in members for k in r.get('keywords',[])}),
                   merge_reason='Exact content alias or explicitly named alternative, reading layout or sample-size extension',
                   original_order=min(r.get('order',0) for r in members))
        entries.append(entry)
    entries.sort(key=lambda r:(min(chapter_rank.get(c,999) for c in r['chapters']),stages.index(r['stage']) if r['stage'] in stages else 6,r['original_order'],r['id']))
    for i,r in enumerate(entries):r['order']=i
    assert sum(len(e['member_ids']) for e in entries)==len(rows)
    return dict(entries=entries,aliases=alias_map,source_pages=len(rows),navigation_entries=len(entries),
                folded_extensions=len(rows)-len(entries),default_entries=sum(not e['variant'] for e in entries),
                asset_files_removed=0,policy='Stable chapter then evidence-stage order; extensions remain inside their canonical entry')
