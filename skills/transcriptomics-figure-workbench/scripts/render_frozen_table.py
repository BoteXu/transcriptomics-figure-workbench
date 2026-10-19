"""Render one reviewed result table with a fixed adapter and project theme.

Only named local renderers are callable. No model fitting, analysis, installation
or external service occurs. Identifier strings and declared numeric fields stay
separate; mixed-record tables may contain empty fields in other record types.
"""
from pathlib import Path
from collections.abc import Mapping
import argparse, inspect, json
from figure_workbench.registry import read_registry, resolve, load_callable


class LazyAdapters(Mapping):
    """Compatible tuple access; load only the selected renderer module."""
    def __init__(self):
        self.definitions = read_registry()['aliases']
    def __iter__(self):
        return iter(self.definitions)
    def __len__(self):
        return len(self.definitions)
    def __contains__(self, key):
        return key in self.definitions
    def __getitem__(self, key):
        row = self.definitions[key]
        return load_callable(key), ' '.join(row['numeric_columns']), row['theme_mode']


ADAPTERS = LazyAdapters()


def load_table(path,adapter,params,numeric_columns=()):
    import pandas as pd
    import numpy as np
    data=pd.read_csv(path,sep='\t',dtype=str,keep_default_na=False).replace('',np.nan)
    numeric=list(ADAPTERS.definitions[adapter]['numeric_columns'] if adapter in ADAPTERS else resolve(adapter)['numeric_columns'])+list(numeric_columns)
    if adapter in {'two_set_overlap','upset'}:numeric+=list(params.get('set_columns',[]))
    if adapter=='ternary':numeric+=list(params.get('components',[]))
    # Matrix renderers may rename their axes/value field or accept an explicit
    # wide value-column list.  Parse only declared numeric channels; identifier
    # columns remain strings (including leading-zero IDs).
    for key in ('value_field','value_column','row_count_field','effect_field','estimate_field','lower_field','upper_field','padj_field','weight_field','fraction_field'):
        value=params.get(key)
        if isinstance(value,str):numeric.append(value)
    if isinstance(params.get('value_columns'),(list,tuple)):numeric.extend(params['value_columns'])
    for c in set(numeric)&set(data.columns):
        values=pd.to_numeric(data[c],errors='raise')
        # Restore the nearest binary float represented by a frozen decimal.
        # The fast numeric parser can truncate the last few bits of a 17-digit
        # TSV coordinate on a second read. Keep integer IDs/types separate.
        if values.dtype.kind=='f':values=data[c].map(float)
        data[c]=values
    return data


def render(adapter,data,params,theme,*,layout=None):
    import matplotlib.pyplot as plt
    from project_theme import validate_theme, render_with_theme
    from panel_layout_audit import audit_panel_layout
    row=resolve(adapter)
    validate_theme(theme);fn=load_callable(adapter);mode=row['theme_mode'];params=dict(params);page_layout=params.pop('page_layout',None)
    accepted=set(inspect.signature(fn).parameters)-{'data','theme'}
    from figure_workbench.responsive import validate_layout,apply_native_layout
    layout=validate_layout(layout);native=dict(layout)
    if 'axis_groups' not in native and row['module'] in {'figure_chapter_views','figure_enrichment_story','figure_wgcna_views','figure_lineage_views','figure_coexpression_evidence','figure_analysis_evidence','figure_three_dimensional'}:
        for key in ['columns','rows']:
            if key in native:
                if key not in accepted:raise ValueError('This chapter supports columns; rows follow the complete content')
                if key in params and params[key] not in ['auto',None,native[key]]:raise ValueError('Conflicting chapter layout settings')
                params[key]=native.pop(key)
    elif 'axis_groups' not in native and 'ncols' in accepted:
        if row['module']=='figure_gsea' and params.get('mode','classic')!='facets' and any(k in native for k in ['columns','rows']):raise ValueError('Use GSEA facets for requested rows/columns')
        for key,arg in [('columns','ncols'),('rows','nrows'),('panel_width_inches','panel_width'),('panel_height_inches','panel_height')]:
            if key in native:
                if arg not in accepted:raise ValueError('Renderer does not support '+arg)
                if arg in params and params[arg]!=native[key]:raise ValueError('Conflicting layout and renderer facet settings')
                params[arg]=native.pop(key)
    elif 'axis_groups' not in native and row['module'] in {'figure_package_styles','figure_refined_views'} and params.get('view') in {'gsea','gsea_strip'}:
        if params.get('view')=='gsea' and params['options'].get('mode','classic')!='facets' and any(k in native for k in ['columns','rows']):raise ValueError('Use GSEA facets for requested rows/columns')
        params['options']=dict(params['options'])
        for key,arg in [('columns','ncols'),('rows','nrows'),('panel_width_inches','panel_width'),('panel_height_inches','panel_height')]:
            if key in native:params['options'][arg]=native.pop(key)
    if set(params)-accepted:raise ValueError('Unknown drawing parameters: '+str(sorted(set(params)-accepted)))
    before=set(plt.get_fignums())
    try:
        if mode=='wrapper':fig=render_with_theme(fn,data,params,theme)
        else:fig=fn(data,theme,**params)
    except Exception:
        for number in set(plt.get_fignums())-before:plt.close(number)
        raise
    if adapter in ['xy_points','embedding','frozen_dynamics','composition','grouped_estimates']:
        fig.set_layout_engine(None);ax=fig.axes[0];ax.set_position([.12,.30,.60,.50] if adapter=='frozen_dynamics' else [.12,.20,.60,.62]);legend=ax.get_legend()
        if legend:legend.set_bbox_to_anchor((1.07,1));legend.set_loc('upper left')
    if fig._suptitle is not None and fig._suptitle.get_text().startswith('SYNTHETIC DEMO'):fig._suptitle.set_text('')
    fig._omics_spec['demo_label_style']='compact'
    if native:
        try:fig=apply_native_layout(fig,native)
        except Exception:plt.close(fig);raise
    if layout:
        fig._omics_spec['requested_layout']=layout
        fig._omics_spec['visual_review_after_layout']='REQUIRED'
    if page_layout:
        from figure_layout import apply_page_layout
        fig=apply_page_layout(fig,page_layout)
    audit=audit_panel_layout(fig)
    if audit['issues']:plt.close(fig);raise ValueError('Guide layout requires repair: '+str(audit['issues']))
    return fig,audit


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('adapter',choices=sorted(ADAPTERS));p.add_argument('--input',required=True,type=Path)
    p.add_argument('--style',required=True,type=Path);p.add_argument('--meta',required=True,type=Path)
    p.add_argument('--theme',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--id',required=True)
    a=p.parse_args()
    import figure_core as core
    import matplotlib.pyplot as plt
    style=json.loads(a.style.read_text(encoding='utf8'));params=style.get('params',style)
    # Gallery style records identify their callable; a mismatch must not silently replay.
    fn=ADAPTERS[a.adapter][0]
    for field,value in [('module',fn.__module__),('function',fn.__name__)]:
        if field in style and style[field]!=value:raise ValueError('Style does not match selected adapter')
    theme=json.loads(a.theme.read_text(encoding='utf8'));meta=json.loads(a.meta.read_text(encoding='utf8'))
    # A saved gallery receipt can supply context only after its original table is verified.
    # Newly minted export hashes/settings must describe this render, never a copied receipt.
    if 'input_hash' in meta and meta['input_hash']!=core.file_sha256(a.input):
        raise ValueError('Saved metadata does not match supplied source table')
    for field in ['input_hash','input_hash_algorithm','input_hash_scope','output_sha256','figure_spec','source_file','source_file_sha256','schema_version','status','figure_id']:
        meta.pop(field,None)
    meta['palette']=theme['palette_name']
    data=load_table(a.input,a.adapter,params);fig,audit=render(a.adapter,data,params,theme)
    meta['layout_audit']=audit
    try:files=core.export_figure(fig,data,a.output,a.id,meta,source_file=a.input,expected_source_sha256=core.file_sha256(a.input))
    finally:plt.close(fig)
    print(json.dumps({'renderer':a.adapter,'rows':len(data),'files':[str(x) for x in files],'manual_export_review_required':True},ensure_ascii=True))


if __name__=='__main__':main()
