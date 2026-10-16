"""File integrity and explicitly recorded visual decisions; no scientific endorsement."""
from datetime import datetime,timezone
from pathlib import Path
import math
from .contracts import hash_value,read_json,write_new
from .registry import digest

VISUAL_CHECKS={'labels_readable','units_and_denominators_visible','guides_clear',
               'no_clipping','color_roles_consistent','final_size_inspected'}


def inspect_bundle(directory):
    directory=Path(directory).resolve()
    receipt_path=directory/(directory.name+'.json')
    receipt=read_json(receipt_path)
    figure_id=receipt.get('figure_id')
    if figure_id!=directory.name:
        raise ValueError('Select the exact per-figure export directory')
    recorded=receipt.get('output_sha256',{})
    expected={figure_id+suffix for suffix in ['.svg','.pdf','.png','.tsv','_session.txt']}
    if receipt.get('workbench',{}).get('export',{}).get('tiff'):expected.add(figure_id+'.tiff')
    if set(recorded)!=expected:
        raise ValueError('Export does not contain the complete known output set')
    issues=[];observed={}
    for name,expected_sha in recorded.items():
        path=directory/name
        if Path(name).name!=name or '/' in name or '\\' in name or path.is_symlink():
            raise ValueError('Unsafe output reference')
        if not path.is_file():issues.append({'file':name,'issue':'missing'});continue
        observed[name]=digest(path)
        if observed[name]!=expected_sha:issues.append({'file':name,'issue':'changed'})
    if receipt.get('input_hash')!=recorded.get(figure_id+'.tsv'):
        issues.append({'issue':'table_receipt_disagrees'})
    bundle_hash=hash_value({'receipt_sha256':digest(receipt_path),'outputs':observed})
    return {'status':'FILES_VERIFIED' if not issues else 'FILES_CHANGED','issues':issues,
            'figure_id':figure_id,'bundle_sha256':bundle_hash,'visual_acceptance':False,
            'print_readability':receipt.get('workbench',{}).get('print_readability'),
            'declared_target_width_mm':receipt.get('workbench',{}).get('export',{}).get('target_width_mm'),
            'scientific_acceptance':False}


def _inspection_matches(current,inspection):
    target=current.get('declared_target_width_mm')
    if target is None:return True  # Preserve the historical review contract.
    return (isinstance(inspection,dict) and set(inspection)=={'scope','width_mm','artifacts'}
        and inspection['scope']=='individual_at_target_width'
        and type(inspection['width_mm']) in {int,float} and math.isfinite(inspection['width_mm'])
        and abs(inspection['width_mm']-target)<.01
        and isinstance(inspection['artifacts'],list) and bool(inspection['artifacts'])
        and all(isinstance(x,str) and x in ['png','pdf','svg'] for x in inspection['artifacts'])
        and len(inspection['artifacts'])==len(set(inspection['artifacts'])))


def record_visual(directory,decision,checks,notes,output,inspection=None):
    current=inspect_bundle(directory)
    if current['issues']:raise ValueError('Changed or incomplete exports cannot be visually accepted')
    if decision not in {'accepted','changes_requested'} or not isinstance(checks,dict) or set(checks)!=VISUAL_CHECKS:
        raise ValueError('Provide the exact visual checklist and explicit decision')
    if any(type(v) is not bool for v in checks.values()) or (decision=='accepted' and not all(checks.values())):
        raise ValueError('Acceptance requires all declared visual checks')
    if not isinstance(notes,str) or not notes.strip():raise ValueError('Record the actual inspection scope and notes')
    if decision=='accepted' and not _inspection_matches(current,inspection):
        raise ValueError('Target-size exports require an individual inspection scope, matching width and actual artifact types. A contact overview is insufficient.')
    record={**current,'schema_version':1,'decision':decision,'checks':checks,'notes':notes,
        'visual_acceptance':decision=='accepted','scientific_acceptance':False,
        'inspection':inspection,'reviewed_at_utc':datetime.now(timezone.utc).isoformat()}
    write_new(output,record)
    return record


def verify_visual(directory,record):
    current=inspect_bundle(directory)
    if (current['issues'] or record.get('bundle_sha256')!=current['bundle_sha256']
            or record.get('figure_id')!=current['figure_id']):
        return {**current,'visual_acceptance':False,'review_status':'STALE_REVIEW'}
    checks=record.get('checks',{})
    accepted=(record.get('decision')=='accepted' and set(checks)==VISUAL_CHECKS
        and all(v is True for v in checks.values()) and _inspection_matches(current,record.get('inspection')))
    return {**current,'visual_acceptance':accepted,'review_status':'VISUALLY_ACCEPTED' if accepted else 'CHANGES_REQUESTED'}
