"""Selected-renderer execution. Import scientific drawing dependencies only here."""
import copy
import json
from pathlib import Path
import tempfile
from .contracts import PRESETS, check_plan, hash_value, validate_spec
from .registry import digest
from . import __version__


def project_appearance(spec):
    theme=copy.deepcopy(spec['theme'])
    appearance=spec.get('appearance',{})
    theme.setdefault('design',{}).update(PRESETS[appearance.get('preset','paper')])
    for key in ['label_pt','tick_pt','title_pt','note_pt']:
        if key in appearance:theme['design'][key]=appearance[key]
    for key in ['font_family','line_width']:
        if key in appearance:theme[key]=appearance[key]
    return theme


def render_plan(plan,output):
    check_plan(plan)
    spec=plan['spec']; theme=project_appearance(spec)
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    destination=output/spec['figure_id']
    if destination.exists():raise FileExistsError('Existing figure exports are preserved')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from project_theme import validate_theme
    from render_frozen_table import load_table,render
    from figure_core import export_figure
    from figure_design import geometry_signature
    validate_theme(theme)
    data=load_table(plan['input_path'],spec['renderer'],spec['parameters'],spec['input'].get('numeric_columns',[]))
    fig,audit=render(spec['renderer'],data,spec['parameters'],theme)
    meta=copy.deepcopy(spec['provenance']);meta['palette']=theme['palette_name']
    meta['layout_audit']=audit
    settings={'raster_dpi':300,'tiff':False,**spec.get('export',{})}
    from .quality import print_readability
    try:
        readability=print_readability(fig,settings)
        if settings.get('readability_policy')=='block' and readability['state']!='MEASUREMENT_PASS':
            raise ValueError('PRINT_SIZE_HOLD: essential text is too small at the declared width; reflow or simplify panels, or choose a larger target. No final bundle was written.')
    except Exception:
        plt.close(fig)
        raise
    meta['workbench']={'version':__version__,'spec':copy.deepcopy(spec),'spec_sha256':plan['spec_sha256'],
        'input_sha256':plan['input_sha256'],'source_identity':plan['source_identity'],
        'renderer':plan['renderer'],'quantitative_geometry_sha256':geometry_signature(fig),
        'appearance_sha256':hash_value(theme),'export':settings,'print_readability':readability,'visual_acceptance':False,'scientific_acceptance':False}
    lock=output/('.'+spec['figure_id']+'.lock')
    guard=None
    try:
        if fig.get_figwidth()*fig.get_figheight()*settings['raster_dpi']**2>40_000_000:
            raise ValueError('Raster exceeds 40 million pixels; choose a smaller preview or approved server render')
        guard=lock.open('x',encoding='utf8')
        with tempfile.TemporaryDirectory(prefix='.'+spec['figure_id']+'-workbench-',dir=output) as temporary:
            files=export_figure(fig,data,temporary,spec['figure_id'],meta,source_file=plan['input_path'],
                                expected_source_sha256=plan['input_sha256'])
            bundle=Path(temporary)/spec['figure_id'];png=bundle/(spec['figure_id']+'.png')
            if settings['raster_dpi']!=300:fig.savefig(png,dpi=settings['raster_dpi'],facecolor='white')
            if settings['tiff']:
                tiff=bundle/(spec['figure_id']+'.tiff');fig.savefig(tiff,dpi=settings['raster_dpi'],facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
                files.append(tiff)
            receipt_path=bundle/(spec['figure_id']+'.json')
            receipt=json.loads(receipt_path.read_text(encoding='utf8'))
            receipt['output_sha256'][png.name]=digest(png)
            if settings['tiff']:receipt['output_sha256'][tiff.name]=digest(tiff)
            receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
            if destination.exists():raise FileExistsError('Destination appeared; existing exports preserved')
            bundle.rename(destination)
            files=[destination/p.name for p in files]
    finally:
        plt.close(fig)
        if guard is not None:guard.close();lock.unlink(missing_ok=True)
    return {'status':'RENDERED_UNREVIEWED','renderer':plan['renderer'],'rows':len(data),
            'files':[str(p) for p in files],'print_readability':readability,'inference_performed':False,'visual_review_required':True}


def restyle_spec(spec,appearance,figure_id):
    result=copy.deepcopy(spec)
    result['appearance']=copy.deepcopy(appearance)
    result['figure_id']=figure_id
    validate_spec(result)
    return result
