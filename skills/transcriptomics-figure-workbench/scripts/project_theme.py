"""Central project appearance; changes visuals only, never analysis values.

Project identity-to-colour mappings are explicit and stable across figure subsets.
"""
from pathlib import Path
import json,copy,hashlib
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from figure_reference_palettes import load_palettes,palette_scope,resolve_card_name
from figure_design import DesignSpec,apply_design

def create_theme(project_id,palette_name,group_slots,*,font_family='Arial',roles=None):
    palette_name=resolve_card_name(palette_name)
    card=load_palettes()[palette_name]
    if card['semantic']!='categorical': raise ValueError('Project base card must be categorical; set continuous roles separately')
    colors=card['colors']; slots=dict(group_slots)
    if not project_id or not slots or any(type(v) is not int or v<0 or v>=len(colors) for v in slots.values()): raise ValueError('Explicit valid category slots required; no cycling')
    derived_roles={'primary':colors[0],'negative':colors[0],'positive':colors[-1],'accent':colors[-1],'neutral':'#A8ADB3','significant':colors[-1],'border':'#526272'}
    if roles: derived_roles.update(roles)
    return dict(schema_version=1,project_id=project_id,palette_name=palette_name,palette_colors=list(colors),group_slots=slots,roles=derived_roles,continuous={'sequential':['#F7F9FC',colors[0]],'diverging':[colors[0],'#F7F7F7',colors[-1]]},continuous_provenance='Explicit original semantic extensions from selected base card; not an author-provided scale',font_family=font_family,design=dict(label_pt=10,tick_pt=9,title_pt=11,note_pt=8,spine_width=.7,spine_mode='keep',grid='keep'),line_width=1.4,point_edge_width=.4,preview_only=True)

def validate_theme(theme):
    required={'schema_version','project_id','palette_name','palette_colors','group_slots','roles','continuous','font_family','design','line_width','point_edge_width','preview_only'}
    if not required<=set(theme) or theme['schema_version']!=1: raise ValueError('Incomplete project theme')
    card=load_palettes()[theme['palette_name']]
    if card['semantic']!='categorical' or card['colors']!=theme['palette_colors']: raise ValueError('Palette changed; rebuild and review project theme')
    if not isinstance(theme['font_family'],str) or not theme['font_family']: raise ValueError('Font must be explicit')
    for slot in theme['group_slots'].values():
        if type(slot) is not int or not 0<=slot<len(card['colors']): raise ValueError('Category slot outside card capacity')
    for name in ('sequential','diverging'):
        if len(theme['continuous'][name])<2: raise ValueError('Incomplete continuous scale')
        for c in theme['continuous'][name]: to_rgba(c)
        if name in theme.get('continuous_cards',{}):
            continuous_card=load_palettes()[theme['continuous_cards'][name]]
            if continuous_card['semantic']!=name or continuous_card['colors']!=theme['continuous'][name]: raise ValueError('Continuous card changed or has incompatible semantics')
    for c in theme['roles'].values(): to_rgba(c)
    DesignSpec(font_family=theme['font_family'],**theme['design']).validate()
    if theme['line_width']<=0 or theme['point_edge_width']<0: raise ValueError('Invalid line/point appearance')
    return theme

def read_theme(path): return validate_theme(json.loads(Path(path).read_text(encoding='utf8')))

def group_palette(theme,groups):
    validate_theme(theme); groups=list(groups)
    if len(groups)!=len(set(groups)) or set(groups)-set(theme['group_slots']): raise ValueError('Unregistered or duplicated project identities; never guess by row order')
    return {g:theme['palette_colors'][theme['group_slots'][g]] for g in groups}

def bind_panel(theme,spec,data):
    theme=validate_theme(theme); spec=copy.deepcopy(spec); typ=spec['type']
    if 'group' in data:
        groups=list(data.group.dropna().unique())
        categorical=data.record_type.isin(['point','line','bar','share','box','density','radar','schematic'])
        needed=list(data.loc[categorical,'group'].dropna().unique())
        if typ=='volcano': spec['group_palette']={'Positive':theme['roles']['positive'],'Negative':theme['roles']['negative'],'Other':theme['roles']['neutral']}
        elif typ not in ('flow_gate',) and not spec.get('continuous_color'): spec['group_palette']=group_palette(theme,needed)
    if typ in ('matrix','clustered_matrix','bubble_matrix','world_map','regional_map','map_flows'):
        lo,hi=spec['color_limits']; semantic='diverging' if lo<0<hi else 'sequential'; spec['continuous_colors']=theme['continuous'][semantic]; spec['map_colors']=theme['continuous'][semantic]
    if typ=='flow_gate' or spec.get('continuous_color'): spec['continuous_colors']=theme['continuous']['sequential']
    spec.pop('bounds',None)
    return spec

def render_panel(data,spec,theme,*,size=(6.7,5.1),page_layout=None):
    from figure_palette_applications import plot_palette_panel
    theme=validate_theme(theme); bound=bind_panel(theme,spec,data)
    with palette_scope(theme),plt.rc_context({'font.family':theme['font_family']}):
        fig=plot_palette_panel(data,palette_name=theme['palette_name'],panel_spec=bound,size=size,font_family=theme['font_family'])
        fig=apply_project_style(fig,theme)
    if page_layout:
        from figure_layout import apply_page_layout
        fig=apply_page_layout(fig,page_layout)
    return fig

def apply_project_style(fig,theme):
    theme=validate_theme(theme); fig=apply_design(fig,DesignSpec(font_family=theme['font_family'],**theme['design']))
    # Set only foreground line widths; no point area, data coordinate or limits change.
    for ax in fig.axes:
        for text in ax.texts: text.set_fontsize(theme['design']['note_pt'])
        for line in ax.lines:
            if line.get_linestyle() not in ('None','none',''): line.set_linewidth(theme['line_width'])
    from matplotlib.legend import Legend
    for legend in fig.findobj(Legend):
        for text in legend.get_texts(): text.set_fontsize(theme['design']['tick_pt'])
        legend.get_title().set_fontsize(theme['design']['label_pt'])
    canonical=json.dumps(theme,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
    fig._omics_spec['project_theme']=copy.deepcopy(theme); fig._omics_spec['project_theme_sha256']=hashlib.sha256(canonical).hexdigest()
    from figure_layout import optimize_guide_layout
    fig=optimize_guide_layout(fig)
    return fig

def render_with_theme(renderer,data,params,theme):
    """Shared entry for stamped table renderers with explicit palette parameters.

    Legacy renderers without semantic colour adapters receive typography only;
    record this limit rather than guess artist/group meaning from pixels.
    """
    import inspect
    theme=validate_theme(theme); settings=copy.deepcopy(params); signature=inspect.signature(renderer)
    for field in ('palette','stack_palette','group_palette'):
        if field in settings:
            if not isinstance(settings[field],dict): raise ValueError('Explicit named category map required')
            settings[field]=group_palette(theme,list(settings[field]))
    for field,role in [('node_color','primary'),('up_color','positive'),('down_color','negative')]:
        if field in signature.parameters: settings[field]=theme['roles'][role]
    if 'continuous_colors' in signature.parameters:
        scale_parameter=signature.parameters.get('scale_type')
        default_scale=scale_parameter.default if scale_parameter else None
        signed=settings.get('signed',False) or settings.get('scale_type',default_scale)=='signed' or settings.get('value_semantics') in ('scaled','signed_effect')
        settings['continuous_colors']=theme['continuous']['diverging' if signed else 'sequential']
    if isinstance(settings.get('block_palette'),dict) and set(settings['block_palette'])<=set(theme['group_slots']):
        settings['block_palette']=group_palette(theme,list(settings['block_palette']))
    if isinstance(settings.get('annotation_palettes'),dict):
        for name,palette in settings['annotation_palettes'].items():
            if set(palette)<=set(theme['group_slots']):settings['annotation_palettes'][name]=group_palette(theme,list(palette))
    if 'font_family' in signature.parameters: settings['font_family']=theme['font_family']
    with palette_scope(theme),plt.rc_context({'font.family':theme['font_family']}): fig=renderer(data,**settings); fig=apply_project_style(fig,theme)
    fig._omics_spec['theme_adapter']=renderer.__module__+'.'+renderer.__name__
    fig._omics_spec['colour_scope']='Explicit category arguments and semantic reference adapters; unsupported legacy internal colours require a reviewed adapter'
    return fig
