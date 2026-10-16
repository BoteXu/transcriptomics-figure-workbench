"""Question-led planning, privacy boundaries and physical-size contracts (stdlib)."""
from pathlib import Path
import copy,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.design import design_plan,ROUTES
from figure_workbench.contracts import validate_spec
from figure_workbench.registry import digest

def refused(call):
    try:call()
    except (ValueError,TypeError,KeyError,FileNotFoundError):return
    raise AssertionError('Invalid design was accepted')

def main():
    with tempfile.TemporaryDirectory(prefix='design-contract-') as tmp:
        base=Path(tmp);table=base/'matrix.tsv';table.write_text('gene\tsample\tscore\trow_group\tcolumn_group\nG1\tS1\t0.1\tA\tB\n',encoding='utf8')
        brief=dict(schema_version=1,question='Compare supplied groups',structure='matrix',input=dict(path='matrix.tsv',sha256=digest(table)),
            roles=dict(row='gene',column='sample',value='score',row_group='row_group',column_group='column_group'),
            context=dict(frozen_results=True,independent_unit='synthetic display unit',denominator='all supplied entries',uncertainty='not applicable: descriptive scores',upstream_qc='reviewed',selection='all rows',missingness='complete grid'),
            target=dict(width_mm=178,minimum_text_pt=7,medium='paper'))
        p=design_plan(brief,base);assert p['state']=='DESIGN_CANDIDATES' and p['preferred']['view']=='split_matrix'
        for field,value in [('upstream_qc','unknown'),('upstream_qc','failed'),('independent_unit','unknown'),('denominator','?'),('uncertainty','unassessed'),('missingness','tbd')]:
            q=copy.deepcopy(brief);q['context'][field]=value;r=design_plan(q,base);assert r['state']=='HOLD' and r['preferred'] is None
        q=copy.deepcopy(brief);q['structure']='uncertainty';q['roles']={'label':'gene','effect':'score','lower':'score','upper':'score'}
        assert design_plan(q,base)['preferred']['view']=='forest'
        q['roles'].pop('lower');assert design_plan(q,base)['state']=='HOLD'
        for mutate in [lambda b:b.update(extra=True),lambda b:b['roles'].update(typo='gene'),lambda b:b['roles'].update(value='absent'),
                       lambda b:b['input'].update(sha256='0'*64),lambda b:b['target'].update(width_mm=float('nan')),
                       lambda b:b['target'].update(width_mm=True),lambda b:b['context'].update(frozen_results=False)]:
            q=copy.deepcopy(brief);mutate(q);refused(lambda:design_plan(q,base))
        table.write_text('a\tb\n1\n',encoding='utf8');q=copy.deepcopy(brief);q['input']['sha256']=digest(table);refused(lambda:design_plan(q,base))
        # Every recommended alias actually exists; no scientific dependency loads.
        from figure_workbench.registry import resolve
        for candidates in ROUTES.values():
            for alias,*_ in candidates:resolve(alias)
        assert not any(m in sys.modules for m in ['numpy','pandas','matplotlib'])
    spec=json.loads((ROOT/'examples/design-v050/inputs/VIS02.spec.json').read_text())
    for settings in [dict(target_width_mm=0),dict(target_width_mm=True),dict(minimum_text_pt=float('nan')),dict(readability_policy='ignore'),dict(readability_policy='block'),dict(random=True)]:
        q=copy.deepcopy(spec);q['export']=settings;refused(lambda:validate_spec(q))
    print(json.dumps(dict(status='DESIGN_CONTRACT_PASS',structures=len(ROUTES),scope='semantic availability, context HOLD, source binding, malformed targets and lazy imports; not scientific validity')))

if __name__=='__main__':main()
