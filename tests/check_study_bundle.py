"""Scoped whole-study selection and conservative exact-output deduplication."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'skills/transcriptomics-figure-workbench/scripts')]
from figure_workbench.study import study_plan

def run(base):
    routine=json.loads((base/'bulk.manifest.json').read_text(encoding='utf8'))
    scope=dict(contrast=routine['contrast'],cell_type='not-applicable',cohort='fixture-study',independent_unit=routine['independent_unit'],denominator=routine['denominator'])
    row=dict(id='ExtraSummary',chapter='bulk.gsea',view='summary',scope=scope,spec='bulk_GSEASummary/bulk_GSEASummary.spec.json',frozen_results=True,upstream_qc='reviewed')
    m=dict(schema_version=2,study_id='fixture-study',routine=routine,analysis_book=dict(schema_version=1,assay='bulk',title='Explicit available study analyses',chapters=['bulk.gsea'],results=[row]),result_stages={'ExtraSummary':'function'},variants=[])
    p=study_plan(m,'整套图，包括 GSEA',base)
    assert p['state']=='STUDY_BUNDLE_PLANNED' and len(p['panels'])==15 and len(p['aliases'])==1
    assert p['analysis_coverage'][0]['chapter']=='bulk.gsea'
    # The same numbers in another cohort cannot be dropped as a duplicate.
    different=copy.deepcopy(m);different['analysis_book']['results'][0]['scope']['cohort']='another-fixture-cohort'
    assert len(study_plan(different,'整套图',base)['panels'])==16
    pathway_plan=study_plan(m,'GSEA',base)
    assert pathway_plan['state']=='STUDY_BUNDLE_PLANNED' and len(pathway_plan['panels'])<15
    absent=study_plan(m,'WGCNA',base);assert absent['state']=='HOLD' and not absent['panels']
    extended=copy.deepcopy(m);extended['analysis_book']['results'].append(dict(copy.deepcopy(row),id='ReadingSummary',view='reading'))
    extended['result_stages']['ReadingSummary']='layout';extended['variants']=['ReadingSummary']
    p=study_plan(extended,'整套图',base);assert 'ReadingSummary' not in str(p['analysis_coverage'])
    p=study_plan(extended,'整套图与自定义布局',base);assert 'ReadingSummary' in str(p['aliases'])
    views=json.loads((ROOT/'skills/transcriptomics-figure-workbench/references/analysis-views.json').read_text(encoding='utf8'))['views']
    wgcna=next(v for v in views if v['id']=='WGCNA_ModuleTrait')
    named=copy.deepcopy(m);named['analysis_book']['chapters']=['bulk.wgcna'];r=named['analysis_book']['results'][0]
    r.update(chapter='bulk.wgcna',spec=str(ROOT/'skills/transcriptomics-figure-workbench'/wgcna['spec']))
    r['scope'].update(cohort='separate-24-donor-template',independent_unit='fictional donors; n=24')
    assert len(study_plan(named,'WGCNA',base)['panels'])==1
    bad=copy.deepcopy(named);bad['routine']['upstream_qc']='failed';assert study_plan(bad,'WGCNA',base)['state']=='HOLD'
    bad=copy.deepcopy(m);bad['routine']['extra']='unknown'
    try:study_plan(bad,'WGCNA',base)
    except ValueError:pass
    else:raise AssertionError('Invalid routine bypassed a named-analysis request')
    print(json.dumps(dict(state='SCOPED_STUDY_BUNDLE_PASS',whole_study_includes_named_results=True,exact_aliases=True,changed_cohort_preserved=True,missing_analysis_hold=True,variants_opt_in=True)))
if __name__=='__main__':
    if len(sys.argv)>1:run(Path(sys.argv[1]))
    else:
        import tempfile
        from prepare_case_replay import prepare_case
        with tempfile.TemporaryDirectory() as temp:
            case=Path(temp)/'case';prepare_case(case,20261018);run(case/'inputs')
