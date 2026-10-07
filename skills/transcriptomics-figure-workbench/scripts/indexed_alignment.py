"""Shared index coordinates and rendered alignment checks for linked tracks."""
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox


def bind_index_axes(fig, main, track, dimension, keys, *, offset=0.):
    if dimension not in ('x','y') or not keys or len(keys)!=len(set(keys)):
        raise ValueError('Declare dimension and unique ordered index identities')
    bindings=getattr(fig,'_index_bindings',[])
    bindings.append(dict(main=main,track=track,dimension=dimension,keys=list(keys),offset=offset))
    fig._index_bindings=bindings
    track._indexed_locator=True
    original=track.get_position().bounds
    thickness=(original[3]*fig.get_figheight()) if dimension=='x' else (original[2]*fig.get_figwidth())
    distance=((original[1]-main.get_position().y1)*fig.get_figheight()) if dimension=='x' else ((original[0]-main.get_position().x0)*fig.get_figwidth())
    def locator(ax,renderer):
        b=main.get_position()
        if dimension=='x':return Bbox.from_bounds(b.x0,b.y1+distance/fig.get_figheight(),b.width,thickness/fig.get_figheight())
        return Bbox.from_bounds(b.x0+distance/fig.get_figwidth(),b.y0,thickness/fig.get_figwidth(),b.height)
    track.set_axes_locator(locator)
    if dimension=='x':track.set_xlim(*(np.asarray(main.get_xlim())+offset))
    else:track.set_ylim(*(np.asarray(main.get_ylim())+offset))
    return track


def audit_index_alignment(fig, tolerance_px=.75):
    fig.canvas.draw();issues=[];records=[]
    for binding in getattr(fig,'_index_bindings',[]):
        a,b=binding['main'],binding['track'];dim=binding['dimension'];offset=binding['offset']
        positions=np.arange(len(binding['keys']),dtype=float)
        points=np.column_stack([positions,np.zeros(len(positions))]) if dim=='x' else np.column_stack([np.zeros(len(positions)),positions])
        moved=points.copy();moved[:,0 if dim=='x' else 1]+=offset
        v=a.transData.transform(points)[:,0 if dim=='x' else 1]
        w=b.transData.transform(moved)[:,0 if dim=='x' else 1]
        error=float(np.max(np.abs(v-w)))
        records.append(dict(dimension=dim,keys=binding['keys'],max_center_error_px=error))
        if error>tolerance_px:issues.append(dict(kind='indexed_track_misalignment',dimension=dim,error_px=error))
    return dict(status='INDEX_GEOMETRY_CHECKS_ONLY',bindings=records,issues=issues)


def add_matrix_annotations(fig, main, rows, columns, *, row_annotations=None,
                           column_annotations=None, palettes=None):
    """ID-keyed categorical annotations; no positional zip or hidden reorder.

Each annotation is {track_name: {exact_ID: group}}. Repeated group runs are
labelled separately, so a noncontiguous group never spans unrelated cells.
"""
    palettes=palettes or {};receipt=[]
    if row_annotations:main.tick_params(axis='y',pad=8+12*len(row_annotations))
    for dimension,keys,annotations in [('y',rows,row_annotations),('x',columns,column_annotations)]:
        for index,(name,mapping) in enumerate((annotations or {}).items()):
            if set(mapping)!=set(keys) or name not in palettes:
                raise ValueError('Annotation keys and named palette must cover the exact displayed identities')
            values=[mapping[k] for k in keys];pal=palettes[name]
            if set(values)-set(pal):raise ValueError('Missing annotation category colour')
            b=main.get_position();fw,fh=fig.get_size_inches()
            if dimension=='x':
                track=fig.add_axes([b.x0,b.y1+(.12+index*.32)/fh,b.width,.24/fh])
                track.set_ylim(0,1)
            else:
                track=fig.add_axes([b.x0-(.16+index*.16)/fw,b.y0,.09/fw,b.height])
                track.set_xlim(0,1)
            bind_index_axes(fig,main,track,dimension,keys)
            for i,g in enumerate(values):
                track.add_patch(Rectangle((i-.5,0) if dimension=='x' else (0,i-.5),1,1,fc=pal[g],ec='white',lw=.25))
            if dimension=='x':
                start=0
                for stop in range(1,len(keys)+1):
                    if stop==len(keys) or values[stop]!=values[start]:
                        text=track.text((start+stop-1)/2,.5,str(values[start]),ha='center',va='center',fontsize=8,
                                        bbox=dict(fc='white',ec='none',alpha=.7,pad=.15))
                        text.set_gid('annotation_group_label');start=stop
                track.text(-.08,.5,name,transform=track.transAxes,ha='right',va='center',fontsize=8)
            else:track.text(.5,1.02,name,transform=track.transAxes,ha='center',va='bottom',rotation=90,fontsize=8)
            track.axis('off');receipt.append(dict(name=name,dimension=dimension,keys=list(keys),groups=values,palette=pal))
    fig._omics_spec['matrix_annotations']=receipt
    return fig
