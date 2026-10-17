"""Scientific choice contracts: wrong semantics must not select a prettier lie."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.selection import select_figure
def run():
    base=dict(schema_version=1,assay='bulk',method='differential',question='Compare the complete treatment response',independent_unit='donor',channels=['complete_tested_effects','adjusted_probability','contrast_definition','design_and_units','marginal_counts'],counts=dict(observations=20000,features=20000,groups=2,contrasts=1,panels=2,independent_units=12,labels=8),purpose='main')
    def choose(**kw):r=copy.deepcopy(base);r.update(kw);return select_figure(r)
    def bad(**kw):
        try:choose(**kw)
        except ValueError:return
        raise AssertionError('Invalid request accepted')
    r=choose();assert r['state']=='DESIGN_SELECTED' and r['layout']['suggested_reading_pages']==1 and r['mode']=='volcano'
    r=choose(independent_unit='cells');assert r['state']=='INPUT_CONTRACT_REQUIRED' and 'biological_independent_unit' in r['required_channels']
    bad(independent_unit=None);bad(assay='bulk',method='umap')
    r=choose(assay='single_cell',method='umap',channels=['frozen_cell_coordinates','donor_mapping','annotation_labels']);assert r['mode']=='labelled_categories'
    r=choose(assay='single_cell',method='umap',channels=['frozen_cell_coordinates','donor_mapping','batch_labels']);assert r['mode']=='batch_facets'
    r=choose(method='gsea',channels=['NES','adjusted_probability','gene_set_version','complete_ranked_universe']);assert r['mode']=='summary' and all('ES_curve' not in k for k in r['required_channels'])
    r=choose(method='ora',channels=['NES','adjusted_probability']);assert r['state']=='INPUT_CONTRACT_REQUIRED' and 'query_size' in r['required_channels']
    r=choose(method='pca',channels=['frozen_sample_coordinates','explained_variance','sample_identity']);assert r['mode']=='sample_coordinates'
    r=choose(method='pca',channels=['frozen_sample_coordinates','explained_variance','sample_identity','ellipse_geometry','ellipse_definition','marginal_counts']);assert r['mode']=='pca'
    r=choose(assay='single_cell',method='subcluster',channels=['frozen_cell_coordinates','annotation_labels','marker_means','marker_fractions','donor_mapping','shared_coordinate_feature_maps']);assert 'parent_selection' in r['required_channels'] and 'child_annotation' in r['required_channels']
    r=choose(method='wgcna',channels=['network_context','independent_units','module_version','candidate_powers','signed_fit','mean_connectivity','preselected_power']);assert r['state']=='DESIGN_SELECTED' and r['mode']=='soft_threshold'
    r=choose(method='wgcna',channels=[]);assert r['state']=='INPUT_CONTRACT_REQUIRED'
    print(json.dumps(dict(status='SELECTION_SEMANTICS_PASS',checks=['large gene point count does not trigger fake pagination','cells are not independent donors','UMAP batch facets need batch labels','summary GSEA never invents ES tracks','ORA needs an actual query and universe','PCA contours need supplied meaning and geometry','subclusters require explicit parent and child scope'])))
if __name__=='__main__':run()
