"""Exercise multiple-scope books, source bindings and scientific drawing contracts."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.book import chapters,book_plan,chapter_template

def reject(fn):
    try:fn()
    except (ValueError,FileNotFoundError):return
    raise AssertionError('Invalid request accepted')

def main():
    all_rows=chapters();assert len(all_rows)==58 and len({x['id'] for x in all_rows})==58
    assert len(chapters('bulk'))==28 and len(chapters('single_cell'))==30
    assert all(x['plot_capability']=='IMPLEMENTED_WITH_EXECUTABLE_EXAMPLE' for x in all_rows)
    for row in all_rows:
        p=SKILL/row['example'];assert p.is_file();s=json.loads(p.read_text(encoding='utf8'));assert (p.parent/s['input']['path']).is_file()
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp);chapter_template('single_cell.pseudobulk',base/'example')
        scope=dict(contrast='A versus B',cell_type='Myeloid',cohort='Illustrative cohort',independent_unit='Donor',denominator='Complete selected genes and 12 declared donors')
        m=dict(schema_version=1,assay='single_cell',title='Scoped fictional book',chapters='all',results=[dict(id='Myeloid_A',chapter='single_cell.pseudobulk',scope=scope,spec='example/example.spec.json',frozen_results=True,upstream_qc='reviewed')])
        m['results'].append(dict(m['results'][0],id='Tcell_A',scope=dict(scope,cell_type='T cells')))
        m['results'].append(dict(m['results'][0],id='Myeloid_B',scope=dict(scope,contrast='C versus B')))
        p=book_plan(m,base);assert p['state']=='CHAPTER_BOOK_PLANNED' and len(p['panels'])==3 and p['implemented_chapters']==30
        assert all(s['plot_capability']=='IMPLEMENTED_WITH_EXECUTABLE_EXAMPLE' for s in p['sections'])
        assert any(s['project_input_state']=='INPUT_REQUIRED' for s in p['sections'])
        bad=copy.deepcopy(m);bad['results'][1]['scope']=copy.deepcopy(scope);reject(lambda:book_plan(bad,base))
        different_view=copy.deepcopy(bad);different_view['results'][1]['view']='MA_reading_page';assert len(book_plan(different_view,base)['panels'])==3
        bad=copy.deepcopy(m);bad['results'][0]['upstream_qc']='unknown';reject(lambda:book_plan(bad,base))
        bad=copy.deepcopy(m);bad['results'][0]['scope']['independent_unit']='cells';reject(lambda:book_plan(bad,base))
        bad=copy.deepcopy(m);bad['results'][0]['id']='../escape';reject(lambda:book_plan(bad,base))
    print(json.dumps(dict(status='CHAPTER_CONTRACTS_PASS',chapters=58,multiple_celltypes_contrasts=True,scientific_acceptance=False)))
if __name__=='__main__':main()
