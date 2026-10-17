"""Scientific question and semantic channels precede visual complexity.

Descriptors are caller declarations, not scientific validation. Actual FigureSpec
and frozen-table checks still precede drawing. No data discovery or inference.
"""
import math
from .book import chapters

METHODS={'pca','umap','annotation','subcluster','subgroup_markers','ora','gsea','differential','composition','abundance','trajectory','velocity','communication','regulon','splicing','replication','wgcna','hdwgcna'}|{r['id'].split('.')[1] for r in chapters()}

def select_figure(request):
    required={'schema_version','assay','method','question','independent_unit','channels','counts','purpose'}
    if not isinstance(request,dict) or set(request)!=required or request['schema_version']!=1:raise ValueError('Use the complete FigureChoiceRequest')
    if not isinstance(request['independent_unit'],str):raise ValueError('Name the biological independent unit')
    assay=request['assay'];method=request['method'];unit=request['independent_unit'].strip().casefold()
    if assay not in ['bulk','single_cell'] or method not in METHODS or not isinstance(request['question'],str) or not request['question'].strip():raise ValueError('Explicit supported assay, method and research question required')
    channels=request['channels'];counts=request['counts'];purpose=request['purpose']
    if not isinstance(channels,list) or len(channels)!=len(set(channels)) or any(not isinstance(x,str) or not x.strip() for x in channels):raise ValueError('Explicit unique semantic channels required')
    allowed={'observations','features','groups','contrasts','panels','independent_units','labels'}
    if not isinstance(counts,dict) or set(counts)!=allowed or any(type(v) is not int or not (0 if k=='labels' else 1)<=v<=100000000 for k,v in counts.items()):raise ValueError('Explicit integer display counts required; labels may be zero')
    if purpose not in ['main','exploration','reading']:raise ValueError('Choose main, exploration or reading')
    have=set(channels);missing=[];reasons=[];excluded=[];prefix=assay+'.';mode=None;renderer=None
    def need(*names):missing.extend(x for x in names if x not in have)
    if method=='pca':
        need('frozen_sample_coordinates','explained_variance','sample_identity')
        chapter='bulk.batch' if assay=='bulk' else 'single_cell.hvg_pca'
        if {'ellipse_geometry','ellipse_definition','marginal_counts'}.issubset(have):
            renderer='figure_integrated_views.plot_integrated_view';mode='pca';reasons.append('PCA supports supplied sample-level ellipses, checked marginal counts and variance; ellipse meaning must remain explicit')
        else:
            renderer='figure_general.plot_xy_points';mode='sample_coordinates';reasons.append('Preserve PCA samples and explained variance; no supplied contour is invented. Use labelled samples and available companion variance/loading panels')
        excluded.append('UMAP/tSNE annotation contours are not interchangeable with PCA uncertainty')
    elif method=='umap':
        if assay!='single_cell':raise ValueError('Stored cell UMAP uses the single-cell route')
        need('frozen_cell_coordinates','donor_mapping');chapter='single_cell.integration'
        if 'batch_labels' in have:renderer='figure_integrated_views.plot_integrated_view';mode='batch_facets';reasons.append('Declared batch labels support shared-coordinate batch highlights')
        else:need('annotation_labels');renderer='figure_core.plot_embedding';mode='labelled_categories';reasons.append('Use complete stored cell coordinates and explicit category labels; a generic UMAP request does not imply batch facets')
        excluded.append('No PCA confidence ellipse or invented marker evidence on UMAP')
    elif method in ['annotation','subcluster','subgroup_markers']:
        if assay!='single_cell':raise ValueError('Annotation requires single-cell context')
        need('frozen_cell_coordinates','annotation_labels','marker_means','marker_fractions','donor_mapping')
        if method=='subcluster':need('parent_selection','child_annotation');chapter='single_cell.subcluster'
        else:chapter='single_cell.annotation'
        renderer='figure_annotation_views.plot_annotation_evidence';mode='subgroup' if method=='subgroup_markers' else 'atlas'
        if method=='subgroup_markers':need('focus_identity','explicit_marker_assignment','shared_coordinate_feature_maps','common_expression_scale')
        reasons.append('One scope per page: atlas identity/specificity, or one subgroup with multiple assigned markers and all-identity specificity; keep expression and detection scales distinct')
        excluded.append('A renamed whole-atlas embedding cannot stand in for a lineage-specific subcluster result')
    elif method=='ora':
        need('tested_universe','query_size','overlap_count','gene_ratio','adjusted_probability','gene_set_version')
        chapter=prefix+('ora' if assay=='bulk' else 'gene_support');renderer='figure_enrichment_story.plot_enrichment_story';mode='ora'
        need('gene_term_membership','selected_gene_effects')
        reasons.append('GeneRatio, hit count and FDR answer distinct questions; supporting genes identify the source of a selected enrichment theme')
        excluded.extend(['No signed NES interpretation for ORA','No circular decoration that hides pathway labels or count denominators'])
    elif method=='gsea':
        need('NES','adjusted_probability','gene_set_version','complete_ranked_universe')
        tracks={'ES_curve','hit_ranks','rank_metric','leading_edge'}.issubset(have)
        if counts['contrasts']>1:
            chapter=prefix+('pathway_contrasts' if assay=='bulk' else 'pathways');renderer='figure_enrichment_story.plot_enrichment_story';mode='gsea_comparison';need('complete_contrast_grid','gene_term_membership','selected_gene_effects','support_contrast')
            reasons.append('Multiple contrasts need a declared common NES scale; genes on the companion panel belong to one explicitly named support contrast')
        elif tracks:
            chapter=('bulk.gsea_multitrack' if counts['groups']>1 else 'bulk.gsea') if assay=='bulk' else 'single_cell.pathways';renderer='figure_refined_views.plot_refined_views';mode='gsea_strip'
            reasons.append('Complete supplied ES, hits, rank metric and leading-edge support aligned full tracks; pagination follows actual pathway count')
        else:
            chapter=prefix+('pathway_contrasts' if assay=='bulk' else 'pathways');renderer='figure_gsea.plot_gsea_nes';mode='summary';reasons.append('Summary-only NES/FDR supports a summary comparison; ES tracks cannot be reconstructed from summary statistics')
        excluded.append('Do not draw invented smooth ES curves, fabricate untested contrasts or swap ES and NES')
    elif method=='differential':
        need('complete_tested_effects','adjusted_probability','contrast_definition','design_and_units')
        chapter=prefix+('differential' if assay=='bulk' else 'pseudobulk')
        if 'marginal_counts' in have:renderer='figure_integrated_views.plot_integrated_view';mode='volcano'
        else:renderer='figure_styles.plot_volcano_editorial';mode='complete_volcano'
        reasons.append('Full effect/significance scope precedes selected labels; marginals must be exact display summaries of those same points')
        excluded.append('A marker-ranking table is not automatically donor-level differential evidence')
    elif method in ['composition','abundance']:
        if assay!='single_cell':raise ValueError('Use the separately scoped bulk deconvolution recipe for estimated mixtures')
        need('donor_type_counts','complete_donor_denominators');chapter=prefix+('composition' if method=='composition' else 'abundance')
        renderer='figure_styles.plot_composition_panels' if method=='composition' else 'figure_chapter_views.plot_transcriptomic_chapter';mode=method
        if method=='abundance':need('donor_aware_abundance_effects','interval_definition','comparison_family')
        reasons.append('Show donor distributions with complete compositional denominators; abundance and within-cell expression have different estimands')
        excluded.append('A pooled stacked cell fraction does not provide biological replication')
    elif method in ['wgcna','hdwgcna']:
        if method=='hdwgcna' and assay!='single_cell':raise ValueError('hdWGCNA requires the single-cell assay context')
        chapter='bulk.wgcna' if assay=='bulk' else 'single_cell.hdwgcna';renderer='figure_wgcna_views.plot_wgcna_view';need('network_context','independent_units','module_version')
        options=[('module_trait',{'module_trait_coefficients','probability_semantics','effective_n'}),('soft_threshold',{'candidate_powers','signed_fit','mean_connectivity','preselected_power'}),('membership_significance',{'gene_membership','gene_significance','coefficient_semantics'}),('preservation',{'module_size','Zsummary','medianRank'}),('module_dendrogram',{'frozen_merge_tree','leaf_order','dynamic_and_merged_modules'})]
        if method=='hdwgcna':options=[('metacell_qc',{'metacell_donor_map','constituent_cell_counts','overlap_counts'}),('module_activity',{'module_cell_scores','shared_cell_coordinates','common_score_scale'})]+options
        mode=next((m for m,needs in options if needs<=have),None)
        if mode is None:missing.append('one_complete_WGCNA_view_contract');mode='module_trait'
        reasons.append('Choose a dedicated supplied network view; show power fit/connectivity, complete trees, actual r/p/q/n, signed/absolute MM-GS and preservation with their own meanings')
        excluded.append('A generic module summary and decorative small graph do not cover WGCNA diagnostics; metacells do not increase donor n')
    else:
        key={'regulon':'regulons','replication':'replication'}.get(method,method)
        if method in ['trajectory','velocity','communication','regulon'] and assay!='single_cell':raise ValueError('Select the appropriate assay-specific chapter')
        chapter=prefix+key;renderer='figure_chapter_views.plot_transcriptomic_chapter';mode=method
        requirements={'trajectory':['frozen_trajectory','root_and_branches','gene_trends'],
          'velocity':['spliced_unspliced_assay','fitted_vectors','phase_diagnostics','vector_scale'],
          'communication':['sender_receiver','ligand_receptor_scores','method_and_null','donor_context'],
          'regulon':['regulon_scores','target_evidence','motif_and_reference'],
          'splicing':['frozen_junctions','event_coordinates','donor_support','usage_effects'],
          'replication':['independent_cohorts','matched_features','common_effect_scale']}
        if method in requirements:need(*requirements[method])
        else:
            entry=next((r for r in chapters(assay) if r['id']==chapter),None)
            if entry is None:raise ValueError('This method is not a chapter for the declared assay')
            need(*entry['required_results'])
        reasons.append('Use complementary evidence channels from the declared method; plotting performs no inference')
    if unit in ['', '?','unknown','cell','cells','spot','spots','细胞','未确定']:missing.append('biological_independent_unit')
    if method in ['differential','abundance','replication'] and counts['independent_units']<3:missing.append('review_independent_replication_and_descriptive_scope')
    # A 20,000-gene volcano and a 20,000-row heatmap have different density.
    # Never turn complete point count into hundreds of arbitrary figure pages.
    density=max(counts['labels']/24,counts['contrasts']/6,counts['panels']/(4 if purpose=='main' else 8))
    if method in ['ora','annotation','subcluster','communication','regulon','splicing','replication']:density=max(density,counts['features']/24,counts['groups']/8)
    if method=='gsea':density=max(density,counts['groups']/(3 if mode=='gsea_strip' else 12))
    reading_pages=max(1,math.ceil(density))
    layout=dict(strategy='selected complementary main plus complete paginated companions' if reading_pages>1 else 'complete adaptive chapter',suggested_reading_pages=reading_pages,
        no_silent_truncation=True,colour='explicit identity palette and separately declared continuous units',guides='exact definitions, units, FDR/count/size meanings, scope and denominators',
        physical_review='Actual target width and exports must pass measured and visual review; more channels do not imply a better figure')
    entry=next((x for x in chapters() if x['id']==chapter),None)
    recipe=entry['example'] if entry else None
    if method=='subgroup_markers':recipe='assets/subgroup-gallery/Subgroup_01/input/example.spec.json'
    if method=='gsea' and mode=='gsea_strip' and assay=='single_cell':recipe='assets/study-gallery/study/DonorEnrichmentTracks/input/DonorEnrichmentTracks.spec.json'
    return dict(schema_version=1,state='INPUT_CONTRACT_REQUIRED' if missing else 'DESIGN_SELECTED',chapter=chapter,renderer=renderer,mode=mode,
        recipe=recipe,selection_reasons=reasons,excluded_misleading_choices=excluded,required_channels=sorted(set(missing)),layout=layout,
        semantics='Caller-declared; verify against selected frozen tables and source method before drawing',analysis_performed=False,visual_acceptance=False,scientific_acceptance=False)
