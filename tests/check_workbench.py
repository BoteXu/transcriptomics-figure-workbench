"""Observable v0.3 contracts, compatibility, lazy discovery and export review tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.registry import build_registry,read_registry
from figure_workbench.contracts import make_plan,check_plan,validate_spec
from workbench_fixtures import create_fixtures


def rejected(call):
    try:call()
    except (ValueError,FileNotFoundError,KeyError,TypeError):return
    raise AssertionError('Invalid input was accepted')


def main():
    registry=read_registry();assert registry==build_registry()
    probe="import sys;sys.path.insert(0,sys.argv[1]);import render_frozen_table;from figure_workbench.registry import read_registry;from figure_workbench.contracts import validate_spec;read_registry();assert not any(n in sys.modules for n in ['numpy','pandas','matplotlib'])"
    subprocess.run([sys.executable,'-c',probe,str(SKILL/'scripts')],check=True)
    checks=['dependency-free catalog and preflight imports','registry generated from actual source']
    with tempfile.TemporaryDirectory(prefix='figure-workbench-') as temporary:
        base=Path(temporary);cases=create_fixtures(base,SKILL)
        spec=cases['ma'];plan=make_plan(spec,base);assert check_plan(plan)==plan
        assert plan['rows']==4;checks.append('relative source survives saved plan round trip')
        for change in [lambda s:s.update(unknown=True),lambda s:s['parameters'].update(eval='x'),
                       lambda s:s['provenance'].pop('experimental_unit'),lambda s:s['input'].update(max_rows=2),
                       lambda s:s['input'].update(sha256='0'*64),lambda s:s['appearance'].update(pvalue=.05),
                       lambda s:s['theme']['group_slots'].update(G1=100)]:
            bad=copy.deepcopy(spec);change(bad);rejected(lambda:make_plan(bad,base))
        checks.append('seven malformed specs rejected before plotting')
        path=base/'ma.tsv';original=path.read_bytes();path.write_bytes(original.replace(b'1.4',b'1.5'))
        rejected(lambda:check_plan(plan));path.write_bytes(original);checks.append('changed input invalidates saved plan')
        bad=copy.deepcopy(plan);bad['source_identity']['fake.py']='0'*64;rejected(lambda:check_plan(bad));checks.append('changed renderer environment invalidates plan')
        for name,spec in cases.items():validate_spec(spec)
        # Caller-defined namespaces cannot become imports.
        bad=copy.deepcopy(cases['ma']);bad['renderer']='os.system';rejected(lambda:validate_spec(bad))
        checks.append('fixed callable allowlist blocks arbitrary import paths')
    print(json.dumps({'status':'WORKBENCH_CONTRACTS_PASS','checks':checks,'counts':registry['counts'],'scientific_acceptance':False}))


if __name__=='__main__':main()
