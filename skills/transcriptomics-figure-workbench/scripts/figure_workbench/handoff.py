"""Consume a frozen result handoff using the existing FigureSpec preflight."""
from pathlib import Path
from .contracts import make_plan, read_json
from .handoff_contract import validate_handoff
from .registry import digest


def handoff_plan(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file(): raise ValueError('Select an existing handoff JSON')
    path = path.resolve(); before = digest(path); value = read_json(path)
    check = validate_handoff(value, path.parent)
    plan = make_plan(value['figure_spec'], path.parent)
    if digest(path)!=before: raise ValueError('Handoff changed during preflight')
    plan['handoff'] = {'path':str(path), 'sha256':before, 'binding_sha256':check['binding_sha256'],
                       'context_sha256':check['context_sha256'], 'qc_state':'passed',
                       'execution_state':value['execution']['state'], 'source_records':value['sources'],
                       'caller_assertions_independently_verified':False}
    return plan
