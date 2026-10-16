"""Study request, source, missing-result and independent-unit regression gates."""
from pathlib import Path
import copy,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'skills/transcriptomics-figure-workbench/scripts')]
from figure_workbench.study import study_plan,select_stages,render_study
from figure_workbench.contracts import read_json,check_plan


def rejected(fn):
    try:fn()
    except (ValueError,FileNotFoundError):return
    raise AssertionError('Invalid study operation accepted')


def main():
    from build_transcriptomic_study_examples import prepare
    checks=[]
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)/'fixtures';prepare(base)
        bulk=read_json(base/'bulk.manifest.json');sc=read_json(base/'single_cell.manifest.json')
        assert select_stages('bulk','画质控图')==['qc']
        assert select_stages('bulk','展示差异和通路')==['differential','pathways']
        assert select_stages('single_cell','展示细胞类型、marker和组成')==['markers','composition']
        for m,count in [(bulk,11),(sc,14)]:
            plan=study_plan(m,'做一套文章组图',base)
            assert plan['state']=='FIGURE_SET_PLANNED' and len(plan['panels'])==count
            assert len({p['role'] for p in plan['panels']})==count
            assert plan['analysis_performed'] is False and plan['visual_acceptance'] is False
        checks.append('Ordinary QC, difference/pathway, marker/composition and whole-study requests select complete declared roles')
        m=copy.deepcopy(bulk);m['upstream_qc']='unknown'
        assert study_plan(m,'画质控图',base)['state']=='FIGURE_SET_PLANNED'
        assert study_plan(m,'展示差异',base)['state']=='HOLD'
        m=copy.deepcopy(sc);m['independent_unit']='cells'
        assert study_plan(m,'展示差异',base)['state']=='HOLD'
        m=copy.deepcopy(bulk);m['results']=[r for r in m['results'] if r['role']!='differential_heatmap']
        assert study_plan(m,'展示差异',base)['state']=='HOLD'
        m=copy.deepcopy(bulk);m['results']=[r for r in m['results'] if r['role']!='gsea_curves']
        p=study_plan(m,'展示通路',base);assert p['state']=='FIGURE_SET_PLANNED' and any(r['role']=='gsea_curves' and not r['required'] for r in p['missing_results'])
        checks.append('Unknown QC, absent required results and cell-only DE units block; absent optional GSEA remains explicit')
        m=copy.deepcopy(bulk);m['results'].append(m['results'][0]);rejected(lambda:study_plan(m,'画质控图',base))
        spec_path=base/'BulkPCA/BulkPCA.spec.json';spec=read_json(spec_path);changed=copy.deepcopy(spec);changed['theme']['group_slots']['Control']=1
        spec_path.write_text(json.dumps(changed),encoding='utf8');rejected(lambda:study_plan(bulk,'画质控图',base));spec_path.write_text(json.dumps(spec),encoding='utf8')
        p=study_plan(bulk,'画质控图',base);source=base/'BulkPCA/BulkPCA.tsv';original=source.read_bytes();source.write_bytes(original+b'\n')
        rejected(lambda:check_plan(next(x['plan'] for x in p['panels'] if x['role']=='sample_embedding')));source.write_bytes(original)
        for role in ['../escape','qc_distribution']:
            bad=copy.deepcopy(p)
            if role=='../escape':bad['panels'][0]['role']=role
            else:bad['panels'].append(copy.deepcopy(bad['panels'][0]))
            dest=base/'must-not-create';rejected(lambda:render_study(bad,dest));assert not dest.exists()
        checks.append('Colour conflicts, duplicate roles, stale source bytes and unsafe or duplicated dispatch fail before output creation')
    print(json.dumps(dict(status='STUDY_FIGURE_GATES_PASS',checks=checks,scientific_acceptance=False)))


if __name__=='__main__':main()
