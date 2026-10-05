"""Redraw registered saved auxiliary panels from the composition examples.

Uses shipped frozen tables and explicit fixed adapters. Component export files
remain independently accessible, while composition recipes control placement.
"""
from pathlib import Path
import argparse,copy,hashlib,json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from figure_core import export_figure,plot_dot
from figure_styles import plot_sample_distribution
from figure_extensions import plot_paired
from figure_publication import plot_feature_facets,plot_aligned_matrix,plot_raincloud,plot_publication_forest
from figure_network_extensions import plot_hex_density,plot_upset
from project_theme import read_theme,render_panel,apply_project_style,group_palette,validate_theme
from compose_catalog_examples import REGISTRY,safe_file

NUMERIC={'x','y','value','lower','upper','area','weight','sign','rank','fraction','estimate','row_count'}


def draw(name,data,spec,theme):
    kind=spec['kind']
    if kind=='reference_palette_plate':
        if len(spec['panel_specs'])!=1: raise ValueError('Single component panel required')
        fig=render_panel(data,spec['panel_specs'][0],theme)
        if name=='event_counts':
            for label in fig.axes[0].get_xticklabels(): label.set_rotation(45);label.set_ha('right')
            fig.axes[0].set_position([.15,.29,.61,.55])
        return fig
    if kind=='publication_stored_feature_facets':
        fig=plot_feature_facets(data,value_label=spec['value_label'],limits=spec['limits'],
                               ncols=3,point_size=spec['point_size'],continuous_colors=theme['continuous']['sequential'])
    elif kind=='publication_aligned_matrix':
        fig=plot_aligned_matrix(data,value_label=spec['value_label'],limits=spec['limits'],
             signed=spec['signed'],center=spec['center'],geometry=spec['geometry'],count_label=spec['count_label'],
             title='Stored marker means and recorded counts',continuous_colors=theme['continuous']['sequential'])
    elif kind=='publication_grouped_forest':
        fig=plot_publication_forest(data,group_palette(theme,list(data.group.unique())),
             x_label='Stored delta' if name=='delta_estimate' else 'Stored mean estimate',
             interval_label=spec['interval_label'],effect_scale=spec['effect_scale'],compact=False)
    elif kind=='publication_raincloud':
        fig=plot_raincloud(data,group_palette(theme,list(data.group.unique())),
                          y_label=spec['y_label'],unit_label=spec['unit_label'],density_min_n=spec['density_min_n'])
    elif kind=='sample_distribution':
        fig=plot_sample_distribution(data,group_palette(theme,list(data.group.unique())),y_label=spec['y_label'])
    elif kind=='paired':
        fig=plot_paired(data,group_palette(theme,spec['condition_order']),spec['condition_order'],spec['y_label'])
    elif kind=='hex_density':
        return plot_hex_density(data,theme,x_label='Same supplied X',y_label='Same supplied Y',
                                unit_label=spec['unit_label'],gridsize=spec['gridsize'],title='Same objects: XY occupancy counts')
    elif kind=='upset':
        return plot_upset(data,theme,set_columns=spec['set_columns'],unit_label=spec['unit_label'],title='Same known feature memberships')
    elif kind=='dot':
        fig=plot_dot(data,spec['value_label'],value_semantics=spec['value_semantics'],denominator_label=spec['denominator_label'])
        for ax in fig.axes:
            for artist in ax.collections:
                if artist.get_array() is not None:
                    artist.set_cmap(LinearSegmentedColormap.from_list('project_seq',theme['continuous']['sequential']));artist.set_clim(0,5)
        fig.set_size_inches(8.5,5.1);fig.set_layout_engine(None)
        fig.axes[0].set_position([.16,.24,.50,.58]);fig.axes[1].set_position([.70,.26,.023,.55])
        fig.axes[0].get_legend().set_bbox_to_anchor((.78,.87),transform=fig.transFigure)
    else:
        raise ValueError('Unsupported saved component contract')
    return apply_project_style(fig,theme)


def rebuild(gallery,output,ids,theme=None):
    gallery=Path(gallery).resolve();output=Path(output)
    registry=json.loads(REGISTRY.read_text(encoding='utf8'))
    components={c['id']:c for c in registry['supplemental_components']}
    if not ids or len(set(ids))!=len(ids) or set(ids)-set(components): raise ValueError('Unique registered component IDs required')
    if output.exists(): raise FileExistsError('Fresh component output directory required')
    if theme:validate_theme(theme)
    output.mkdir(parents=True);records=[]
    for name in ids:
        component=components[name];source=safe_file(gallery,component['prefix']+'.tsv');metadata=safe_file(gallery,component['metadata'])
        meta=json.loads(metadata.read_text(encoding='utf8'));spec=meta['figure_spec'];project=theme or spec['project_theme']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=meta['input_hash']:raise ValueError('Saved component input changed')
        if component.get('adapter'):
            from render_frozen_table import load_table,render,ADAPTERS
            style=json.loads(safe_file(gallery,component['style']).read_text(encoding='utf8'))
            adapter=component['adapter'];fn=ADAPTERS[adapter][0]
            if style.get('module')!=fn.__module__ or style.get('function')!=fn.__name__:raise ValueError('Component style/adapter mismatch')
            data=load_table(source,adapter,style['params']);fig,audit=render(adapter,data,style['params'],project)
        else:
            data=pd.read_csv(source,sep='\t',dtype=str,keep_default_na=False).replace('',np.nan)
            numeric=NUMERIC|set(spec.get('set_columns',[]))
            for column in numeric&set(data.columns):data[column]=pd.to_numeric(data[column],errors='raise')
            fig=draw(name,data,spec,project)
        context=copy.deepcopy(meta)
        for field in ('figure_spec','input_hash','input_hash_algorithm','input_hash_scope','output_sha256','source_file','source_file_sha256','schema_version','status','figure_id'):
            context.pop(field,None)
        context['palette']=project['palette_name']
        try:files=export_figure(fig,data,output,name,context,source_file=source,
                               expected_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        finally:plt.close(fig)
        records.append({'id':name,'files':[p.name for p in files],'rows':len(data)})
    (output/'component-manifest.json').write_text(json.dumps({'status':'RENDERED_UNREVIEWED','records':records},indent=2),encoding='utf8')
    return records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gallery',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--theme',type=Path)
    select=parser.add_mutually_exclusive_group(required=True);select.add_argument('--ids',nargs='+');select.add_argument('--all',action='store_true')
    args=parser.parse_args()
    ids=[c['id'] for c in json.loads(REGISTRY.read_text(encoding='utf8'))['supplemental_components']] if args.all else args.ids
    records=rebuild(args.gallery,args.output,ids,read_theme(args.theme) if args.theme else None)
    print(json.dumps({'status':'RENDERED_UNREVIEWED','components':len(records),'scientific_inference':False},indent=2))


if __name__=='__main__':main()
