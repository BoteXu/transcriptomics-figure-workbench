"""Render one reviewed result table with a fixed adapter and project theme.

Only named local renderers are callable. No model fitting, analysis, installation
or external service occurs. Identifier strings and declared numeric fields stay
separate; mixed-record tables may contain empty fields in other record types.
"""
from pathlib import Path
import argparse, inspect, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import figure_method_extensions as methods
import figure_core as core
import figure_general as general
import figure_publication as publication
import figure_network_extensions as network
import figure_multiscale as multiscale
import figure_multiomics_views as multiomics
import figure_multimodal as multimodal
import figure_linked_evidence as linked
import figure_biomni_views as biomni_views
import figure_analysis_results as analysis_views
from project_theme import validate_theme, render_with_theme
from panel_layout_audit import audit_panel_layout

# Fixed functions, not user-supplied import paths or executable expressions.
ADAPTERS={
    'splice_tracks':(analysis_views.plot_splice_tracks,'start end value count lane','argument'),
    'variant_posteriors':(analysis_views.plot_variant_posteriors,'position pip','argument'),
    'contribution_waterfall':(analysis_views.plot_contribution_waterfall,'contribution','argument'),
    'calibration_counts':(multimodal.plot_calibration_counts,'bin_left bin_right predicted estimate lower upper n','wrapper'),
    'sequence_logo':(biomni_views.plot_sequence_logo,'height','argument'),
    'contact_tracks':(biomni_views.plot_contact_tracks,'start end value','argument'),
    'branch_tree':(biomni_views.plot_branch_tree,'branch_length','argument'),
    'slice_overlay':(biomni_views.plot_slice_overlay,'u v intensity label','argument'),
    'registration_check':(biomni_views.plot_registration_check,'u v fixed registered','argument'),
    'alluvial':(network.plot_alluvial,'weight','argument'),
    'weighted_chord':(network.plot_weighted_chord,'weight','argument'),
    'heatmap':(core.plot_heatmap,'value','wrapper'),
    'dot_matrix':(core.plot_dot,'fraction value','wrapper'),
    'polished_matrix':(__import__('figure_polish').plot_polished_matrix,'value','wrapper'),
    'membership_ribbons':(linked.plot_membership_ribbons,'effect ratio padj count','argument'),
    'split_metric_matrix':(linked.plot_split_metric_matrix,'association pvalue','argument'),
    'hierarchy_tracks':(linked.plot_hierarchy_tracks,'height','argument'),
    'radial_hierarchy':(linked.plot_radial_hierarchy,'height metric outer_value area_value','argument'),
    'stacked_values':(linked.plot_stacked_values,'value','argument'),
    'frozen_dynamics':(multimodal.plot_frozen_dynamics,'time estimate lower upper','wrapper'),
    'composition':(core.plot_composition,'count','wrapper'),
    'ternary':(multiscale.plot_ternary_composition,'','argument'),
    'genome_overview':(multiscale.plot_genome_overview,'position pvalue','argument'),
    'locus_tracks':(multiscale.plot_locus_tracks,'position pvalue ld_r2 start end lane rate','argument'),
    'funnel':(multiscale.plot_funnel_result,'estimate se','argument'),
    'hierarchy_area':(multiscale.plot_hierarchy_partition,'value x0 y0 x1 y1','argument'),
    'uncertainty_fan':(multiscale.plot_uncertainty_fan,'x coverage center lower upper','argument'),
    'spatial_overlay':(multiscale.plot_spatial_overlay,'x y red green blue radius value','argument'),
    'cross_effects':(multiomics.plot_cross_effects,'effect_x effect_y q_x q_y','argument'),
    'aligned_views':(multiomics.plot_aligned_views,'x y','argument'),
    'loading_projection':(multiomics.plot_loading_projection,'x y','argument'),
    'mass_spectrum':(multiomics.plot_mass_spectrum,'mz intensity','argument'),
    'genomic_links':(multiomics.plot_genomic_links,'start end value score','argument'),
    'pathway_overlay':(multiomics.plot_pathway_overlay,'x y value','argument'),
    'model_diagnostic':(multiomics.plot_diagnostic_panel,'fitted residual standard_residual leverage cook reference_quantile ordered_residual','argument'),
    'enrichment_grid':(methods.plot_enrichment_grid,'padj gene_ratio','argument'),
    'term_effect_circle':(methods.plot_term_effect_circle,'padj zscore effect','argument'),
    'term_key':(methods.plot_term_key,'','argument'),
    'two_set_overlap':(methods.plot_two_set_overlap,'','argument'),
    'gene_term_chord':(methods.plot_gene_term_chord,'effect','argument'),
    'distribution':(methods.plot_distribution_result,'x y','argument'),
    'balance':(methods.plot_balance,'smd','argument'),
    'agreement':(methods.plot_agreement,'mean difference','argument'),
    'survival':(methods.plot_survival_result,'time survival lower upper at_risk','argument'),
    'swimmer':(methods.plot_swimmer,'start end time','argument'),
    'specification_curve':(methods.plot_specification_curve,'estimate lower upper included','argument'),
    'vector_field':(methods.plot_vector_field,'x y vx vy','argument'),
    'bivariate_tiles':(methods.plot_bivariate_tiles,'metric_x metric_y','argument'),
    'forest':(publication.plot_publication_forest,'estimate lower upper','wrapper'),
    'density_ridges':(general.plot_density_ridges,'x density','wrapper'),
    'annotated_matrix':(publication.plot_aligned_matrix,'value row_count','wrapper'),
    'typed_network':(network.plot_typed_network,'x y area weight sign','argument'),
    'multistate_matrix':(network.plot_multistate_matrix,'','argument'),
    'xy_points':(general.plot_xy_points,'x y','wrapper'),
    'embedding':(core.plot_embedding,'x y','wrapper'),
    'feature_facets':(publication.plot_feature_facets,'x y value','wrapper'),
    'grouped_estimates':(general.plot_grouped_estimates,'estimate lower upper','wrapper'),
}


def load_table(path,adapter,params):
    data=pd.read_csv(path,sep='\t',dtype=str,keep_default_na=False).replace('',np.nan)
    numeric=ADAPTERS[adapter][1].split()
    if adapter=='two_set_overlap':numeric+=list(params.get('set_columns',[]))
    if adapter=='ternary':numeric+=list(params.get('components',[]))
    # Matrix renderers may rename their axes/value field or accept an explicit
    # wide value-column list.  Parse only declared numeric channels; identifier
    # columns remain strings (including leading-zero IDs).
    for key in ('value_field','value_column','row_count_field','effect_field','estimate_field','lower_field','upper_field','padj_field','weight_field','fraction_field'):
        value=params.get(key)
        if isinstance(value,str):numeric.append(value)
    if isinstance(params.get('value_columns'),(list,tuple)):numeric.extend(params['value_columns'])
    for c in set(numeric)&set(data.columns):data[c]=pd.to_numeric(data[c],errors='raise')
    return data


def render(adapter,data,params,theme):
    if adapter not in ADAPTERS:raise ValueError('Unknown fixed renderer')
    validate_theme(theme);fn,_,mode=ADAPTERS[adapter];params=dict(params);page_layout=params.pop('page_layout',None)
    accepted=set(inspect.signature(fn).parameters)-{'data','theme'}
    if set(params)-accepted:raise ValueError('Unknown drawing parameters: '+str(sorted(set(params)-accepted)))
    if mode=='wrapper':fig=render_with_theme(fn,data,params,theme)
    else:fig=fn(data,theme,**params)
    if adapter in ['xy_points','embedding','frozen_dynamics','composition','grouped_estimates']:
        fig.set_layout_engine(None);ax=fig.axes[0];ax.set_position([.12,.30,.60,.50] if adapter=='frozen_dynamics' else [.12,.20,.60,.62]);legend=ax.get_legend()
        if legend:legend.set_bbox_to_anchor((1.07,1));legend.set_loc('upper left')
    if fig._suptitle is not None and fig._suptitle.get_text().startswith('SYNTHETIC DEMO'):fig._suptitle.set_text('')
    fig._omics_spec['demo_label_style']='compact'
    if page_layout:
        from figure_layout import apply_page_layout
        fig=apply_page_layout(fig,page_layout)
    audit=audit_panel_layout(fig)
    if audit['issues']:plt.close(fig);raise ValueError('Guide layout requires repair: '+str(audit['issues']))
    return fig,audit


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('adapter',choices=sorted(ADAPTERS));p.add_argument('--input',required=True,type=Path)
    p.add_argument('--style',required=True,type=Path);p.add_argument('--meta',required=True,type=Path)
    p.add_argument('--theme',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--id',required=True)
    a=p.parse_args();style=json.loads(a.style.read_text(encoding='utf8'));params=style.get('params',style)
    # Gallery style records identify their callable; a mismatch must not silently replay.
    fn=ADAPTERS[a.adapter][0]
    for field,value in [('module',fn.__module__),('function',fn.__name__)]:
        if field in style and style[field]!=value:raise ValueError('Style does not match selected adapter')
    theme=json.loads(a.theme.read_text(encoding='utf8'));meta=json.loads(a.meta.read_text(encoding='utf8'))
    # A saved gallery receipt can supply context only after its original table is verified.
    # Newly minted export hashes/settings must describe this render, never a copied receipt.
    if 'input_hash' in meta and meta['input_hash']!=core.file_sha256(a.input):
        raise ValueError('Saved metadata does not match supplied source table')
    for field in ['input_hash','input_hash_algorithm','input_hash_scope','output_sha256','figure_spec','source_file','source_file_sha256','schema_version','status','figure_id']:
        meta.pop(field,None)
    meta['palette']=theme['palette_name']
    data=load_table(a.input,a.adapter,params);fig,audit=render(a.adapter,data,params,theme)
    meta['layout_audit']=audit
    try:files=core.export_figure(fig,data,a.output,a.id,meta,source_file=a.input,expected_source_sha256=core.file_sha256(a.input))
    finally:plt.close(fig)
    print(json.dumps({'renderer':a.adapter,'rows':len(data),'files':[str(x) for x in files],'manual_export_review_required':True},ensure_ascii=True))


if __name__=='__main__':main()
