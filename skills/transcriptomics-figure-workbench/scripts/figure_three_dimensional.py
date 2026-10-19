"""Frozen-coordinate 3D displays, direct volume compositing and trajectory playback.

These are drawing operations, never embedding estimation, segmentation, bond
inference, molecular dynamics, trajectory alignment or periodic re-imaging.
"""
import base64
import io
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from figure_core import checked, stamp
from project_theme import group_palette
from figure_workbench.responsive import grid_shape, canvas_budget, facet_slots


def _words(*values):
    if any(not isinstance(s,str) or not s.strip() for s in values):
        raise ValueError('Explicit coordinate, unit and source definitions are required')


def _page(count, columns, rows, width, panel_height, title):
    nr,nc=grid_shape(count,columns,rows)
    height=nr*panel_height+1.0
    fig=plt.figure(figsize=canvas_budget(width or nc*4.0+.5,height),facecolor='white')
    # Keep top/bottom whitespace bounded in physical inches on long reading
    # pages; percentage-only margins otherwise grow with every requested row.
    slots=facet_slots(fig,count,nr,nc,left=.11,right=.95,
                      bottom=min(.7,.10*height)/height,
                      top=1-min(1.8,.17*height)/height,wspace=.42,hspace=.48)
    fig.suptitle(title,fontsize=13,weight='normal',y=.98)
    fig._responsive_facets=dict(rows=nr,columns=nc,panels=count)
    return fig,slots


def _three_axis(ax, limits, labels, view):
    from matplotlib.ticker import MaxNLocator
    ax.set_proj_type('ortho');ax.view_init(*view)
    for lim,func,label in zip(limits,[ax.set_xlim,ax.set_ylim,ax.set_zlim],labels):func(lim)
    ax.set(xlabel=textwrap.fill(labels[0],18),ylabel=textwrap.fill(labels[1],18),zlabel='')
    # mplot3d's automatic z-label projects outside its axes, where it can collide
    # with an adjacent panel or be cropped in a keyframe grid. Reserve an inside
    # caption above the box instead; the numerical z ticks remain on the axis.
    ax.text2D(.97,.88,textwrap.fill(labels[2],18),transform=ax.transAxes,
              ha='right',va='top',fontsize=9,color='#405B69')
    ax.set_box_aspect([b-a for a,b in limits]);ax.tick_params(labelsize=8,pad=1)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:
        axis.set_major_locator(MaxNLocator(3));axis.label.set_fontsize(9);axis.labelpad=5
        axis.pane.set_facecolor('#F6F8FA');axis.pane.set_edgecolor('#DCE4E8')
        axis._axinfo['grid'].update(color='#DDE5E9',linewidth=.55)
    ax._explicit_guide_layout=True


def _limits(xyz):
    low=xyz.min(axis=0);high=xyz.max(axis=0);span=np.maximum(high-low,1e-8)
    return list(zip(low-.08*span,high+.08*span))


def plot_scatter3d(data,theme,*,axis_labels,coordinate_unit,coordinate_definition,
                   views=((23,-58),),include_projections=True,columns='auto',rows=None,
                   width=None,panel_height=3.8,title='Stored three-dimensional coordinates'):
    """Actual 3D points and aligned orthographic companions, with no fitting."""
    d=checked(data,['object_id','group','x','y','z'],['x','y','z'])
    if d.object_id.duplicated().any():raise ValueError('Unique object IDs required')
    if len(axis_labels)!=3:raise ValueError('Three axis labels required')
    _words(coordinate_unit,coordinate_definition,*axis_labels)
    if not views or len(views)>8 or any(len(v)!=2 or not np.isfinite(v).all() for v in views):raise ValueError('Supply 1–8 explicit elevation/azimuth views')
    if type(include_projections) is not bool:raise ValueError('include_projections must be boolean')
    groups=list(pd.unique(d.group));pal=group_palette(theme,groups);lim=_limits(d[['x','y','z']].to_numpy(float))
    labels=[f'{label} ({coordinate_unit})' for label in axis_labels]
    fig,slots=_page(len(views)+(3 if include_projections else 0),columns,rows,width,panel_height,title)
    for i,view in enumerate(views):
        ax=fig.add_subplot(slots[i],projection='3d');_three_axis(ax,lim,labels,view)
        for group in groups:
            q=d[d.group==group];ax.scatter(q.x,q.y,q.z,s=18,c=pal[group],edgecolors='white',linewidths=.25,alpha=.85,depthshade=False)
        ax.set_title(f'3D · elevation {view[0]:g}° / azimuth {view[1]:g}°',fontsize=10,pad=10)
    if include_projections:
        for i,(a,b) in enumerate([(0,1),(0,2),(1,2)]):
            ax=fig.add_subplot(slots[len(views)+i]);ax._explicit_guide_layout=True
            for group in groups:
                q=d[d.group==group];ax.scatter(q[['x','y','z'][a]],q[['x','y','z'][b]],s=15,color=pal[group],alpha=.72,edgecolors='white',linewidths=.25)
            ax.set(xlim=lim[a],ylim=lim[b],xlabel=labels[a],ylabel=labels[b],title=f'{axis_labels[a]} / {axis_labels[b]} projection')
            ax.spines[['top','right']].set_visible(False);ax.set_aspect('auto');ax.grid(color='#E9EEF1',lw=.5)
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color=pal[g],label=f'{g}  ·  n={int((d.group==g).sum())}') for g in groups],
               loc='upper center',bbox_to_anchor=(.5,1-min(.6,.06*fig.get_figheight())/fig.get_figheight()),ncol=min(len(groups),max(1,int(fig.get_figwidth()/3.4))),frameon=False,fontsize=9)
    return stamp(fig,data,'scatter3d',axis_labels=axis_labels,coordinate_unit=coordinate_unit,
                 coordinate_definition=coordinate_definition,views=views,include_projections=include_projections,
                 columns=columns,rows=rows,width=width,panel_height=panel_height,title=title,
                 stored_coordinates_unchanged=True,object_count=len(d),inference='none')


def _volume(data,limits,transfer):
    d=checked(data,['x','y','z','value'],['x','y','z','value'])
    if d.duplicated(['x','y','z']).any():raise ValueError('Unique physical voxel centres required')
    axes=[np.sort(d[c].unique()) for c in ['x','y','z']]
    if any(len(a)<2 or not np.allclose(np.diff(a),np.diff(a)[0],rtol=1e-7,atol=1e-10) for a in axes):raise ValueError('A complete uniform physical voxel grid is required')
    if len(d)!=np.prod([len(a) for a in axes]) or len(d)>2_000_000:raise ValueError('Complete bounded voxel grid required; missing is never zero')
    if len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1] or d.value.min()<limits[0] or d.value.max()>limits[1]:raise ValueError('Value limits must include every supplied voxel')
    if len(transfer)<2 or set(transfer[0])!={'value','color','opacity'}:raise ValueError('Explicit value/color/opacity transfer knots required')
    knots=np.array([p['value'] for p in transfer],float);alpha=np.array([p['opacity'] for p in transfer],float)
    if not np.isfinite(knots).all() or not np.isfinite(alpha).all() or (np.diff(knots)<=0).any() or (alpha<0).any() or (alpha>1).any() or knots[0]>limits[0] or knots[-1]<limits[1]:raise ValueError('Ordered transfer function must cover limits, with opacity in [0,1]')
    colors=np.array([to_rgb(p['color']) for p in transfer])
    grid=d.set_index(['x','y','z']).reindex(pd.MultiIndex.from_product(axes,names=['x','y','z'])).value.to_numpy().reshape(*map(len,axes))
    return grid,axes,knots,colors,alpha


def composite_volume(grid,axes,knots,colors,opacity,view,unit_distance):
    """Orthographic front-to-back alpha compositing, with physical step correction."""
    if view not in [a+s for a in 'xyz' for s in '+-']:raise ValueError('Volume view must be x+/x-/y+/y-/z+/z-')
    if not np.isfinite(unit_distance) or unit_distance<=0:raise ValueError('Positive opacity reference distance required')
    axis='xyz'.index(view[0]);layers=np.moveaxis(grid,axis,0)
    if view[1]=='-':layers=layers[::-1]
    rgb=np.zeros(layers.shape[1:]+(3,));transmittance=np.ones(layers.shape[1:])
    step=abs(axes[axis][1]-axes[axis][0]);factor=step/unit_distance
    for layer in layers:
        a=1-np.power(1-np.interp(layer,knots,opacity),factor)
        color=np.stack([np.interp(layer,knots,colors[:,i]) for i in range(3)],axis=-1)
        rgb+=(transmittance*a)[...,None]*color;transmittance*=1-a
    return rgb+transmittance[...,None]  # White background; no max-intensity projection.


def plot_volume_rendering(data,theme,*,coordinate_unit,value_label,value_limits,transfer,
                          opacity_unit_distance,volume_definition,views=('z+','x+','y+'),
                          slice_axes=(),columns='auto',rows=None,width=None,panel_height=3.6,
                          title='Direct volume rendering · supplied voxel field'):
    """True direct volume compositing, declared transfer function and optional slices."""
    _words(coordinate_unit,value_label,volume_definition)
    grid,axes,knots,colors,opacity=_volume(data,value_limits,transfer)
    if not views or len(views)>6 or len(set(views))!=len(views):raise ValueError('Explicit unique volume views required')
    if len(set(slice_axes))!=len(slice_axes) or set(slice_axes)-set('xyz'):raise ValueError('Choose unique x/y/z central slices')
    fig,slots=_page(len(views)+len(slice_axes)+1,columns,rows,width,panel_height,title)
    def plane(ax,image,axis,caption):
        remaining=[i for i in range(3) if i!=axis];a,b=remaining
        edges=[(v[0]-(v[1]-v[0])/2,v[-1]+(v[1]-v[0])/2) for v in axes]
        ax.imshow(np.swapaxes(image,0,1),origin='lower',extent=(*edges[a],*edges[b]),interpolation='bilinear',aspect='equal')
        ax.set(xlabel=f'{"XYZ"[a]} ({coordinate_unit})',ylabel=f'{"XYZ"[b]} ({coordinate_unit})',title=caption)
        ax.spines[['top','right']].set_visible(False);ax._explicit_guide_layout=True
    for i,view in enumerate(views):
        ax=fig.add_subplot(slots[i]);image=composite_volume(grid,axes,knots,colors,opacity,view,opacity_unit_distance)
        plane(ax,image,'xyz'.index(view[0]),f'Volume · looking along {view}')
    cmap=LinearSegmentedColormap.from_list('declared_volume',list(zip((knots-knots[0])/(knots[-1]-knots[0]),colors)))
    for j,axis_name in enumerate(slice_axes):
        axis='xyz'.index(axis_name);mid=len(axes[axis])//2;values=np.take(grid,mid,axis=axis)
        plane(fig.add_subplot(slots[len(views)+j]),cmap(Normalize(*value_limits)(values)),axis,f'Slice · {axis_name}={axes[axis][mid]:.3g} {coordinate_unit}')
    ax=fig.add_subplot(slots[-1]);ax._explicit_guide_layout=True
    for lo,hi,c in zip(knots[:-1],knots[1:],colors[:-1]):ax.axvspan(lo,hi,color=c,alpha=.11,lw=0)
    ax.plot(knots,opacity,color='#456B80',lw=1.8,marker='o',ms=5)
    ax.set(xlabel=value_label,ylabel='Opacity per reference distance',ylim=(-.03,1.03),xlim=value_limits,title='Declared transfer function')
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E6ECEF',lw=.5)
    ax.text(.02,.94,f'Reference distance: {opacity_unit_distance:g} {coordinate_unit}\nFront-to-back compositing · uniform voxels',transform=ax.transAxes,va='top',fontsize=8)
    return stamp(fig,data,'volume_rendering',coordinate_unit=coordinate_unit,value_label=value_label,value_limits=value_limits,
                 transfer=transfer,opacity_unit_distance=opacity_unit_distance,volume_definition=volume_definition,
                 views=views,slice_axes=slice_axes,columns=columns,rows=rows,width=width,panel_height=panel_height,title=title,
                 voxel_shape=list(grid.shape),projection='orthographic direct volume compositing',inference='none')


def _trajectory(data,frame_order):
    if 'record_type' not in data or set(data.record_type)-{'atom','bond'}:raise ValueError('Use explicit atom/bond records')
    atoms=checked(data[data.record_type=='atom'],['frame_id','time','atom_id','element','chain','x','y','z'],['time','x','y','z'])
    if atoms.duplicated(['frame_id','atom_id']).any():raise ValueError('An atom occurs twice in a frame')
    frames=list(frame_order)
    if not 2<=len(frames)<=240 or len(set(frames))!=len(frames) or set(frames)!=set(atoms.frame_id):raise ValueError('Declare every supplied frame exactly once (2–240)')
    first=atoms[atoms.frame_id==frames[0]].set_index('atom_id');ids=list(first.index)
    if not ids or len(ids)>20000:raise ValueError('Choose a bounded, explicitly selected atom set')
    times=[];coordinates=[]
    for frame in frames:
        part=atoms[atoms.frame_id==frame].set_index('atom_id')
        if set(part.index)!=set(ids) or part.time.nunique()!=1:raise ValueError('Every frame must contain the same atoms and one time')
        part=part.loc[ids]
        if not part[['element','chain']].equals(first[['element','chain']]):raise ValueError('Atom identity changed across frames')
        times.append(float(part.time.iloc[0]));coordinates.append(part[['x','y','z']].to_numpy(float))
    if (np.diff(times)<=0).any():raise ValueError('Frame order must have strictly increasing supplied times')
    bonds=data[data.record_type=='bond'];pairs=[]
    if len(bonds):
        checked(bonds,['source_id','target_id'])
        if bonds.duplicated(['source_id','target_id']).any():raise ValueError('Duplicate bonds')
        seen=set()
        for a,b in zip(bonds.source_id,bonds.target_id):
            if a not in ids or b not in ids or a==b or frozenset([a,b]) in seen:raise ValueError('Invalid or repeated explicit bond')
            seen.add(frozenset([a,b]));pairs.append((ids.index(a),ids.index(b)))
    return first,np.array(coordinates),np.array(times),pairs


def plot_molecular_trajectory(data,theme,*,frame_order,coordinate_unit,time_unit,topology_definition,
                              coordinate_definition,periodic_boundary_handling,key_frames=None,
                              view=(22,-60),columns='auto',rows=None,width=None,panel_height=3.2,
                              animation_fps=10,title='Molecular trajectory · stored coordinates'):
    """Static keyframes plus actual GIF and offline frame-by-frame HTML playback."""
    _words(coordinate_unit,time_unit,topology_definition,coordinate_definition,periodic_boundary_handling)
    if type(animation_fps) is not int or not 1<=animation_fps<=30:raise ValueError('Playback rate must be an integer 1–30 fps')
    if len(view)!=2 or not np.isfinite(view).all():raise ValueError('Explicit finite camera elevation/azimuth required')
    atoms,xyz,times,bonds=_trajectory(data,frame_order)
    selected=list(key_frames) if key_frames is not None else list(dict.fromkeys([frame_order[0],frame_order[len(frame_order)//2],frame_order[-1]]))
    if not selected or len(set(selected))!=len(selected) or set(selected)-set(frame_order):raise ValueError('Keyframes must refer to actual supplied frames')
    pal={'C':'#668B9E','N':'#5279BC','O':'#D77966','S':'#C4A449','H':'#C4D0D5','P':'#A486B5'}
    if set(atoms.element)-set(pal):raise ValueError('Unsupported element; supply supported explicit element identities')
    lim=_limits(xyz.reshape(-1,3));labels=[f'{c} ({coordinate_unit})' for c in 'XYZ']
    def draw(ax,idx):
        from mpl_toolkits.mplot3d.art3d import Line3DCollection
        _three_axis(ax,lim,labels,view);q=xyz[idx]
        if bonds:ax.add_collection3d(Line3DCollection(np.array([[q[a],q[b]] for a,b in bonds]),colors='#9AACB4',linewidths=1.6,alpha=.78))
        for element in pd.unique(atoms.element):
            keep=atoms.element.to_numpy()==element;ax.scatter(*q[keep].T,s=32 if element!='H' else 15,c=pal[element],edgecolors='white',linewidths=.4,depthshade=False,zorder=3)
        ax.set_title(f'{frame_order[idx]} · {times[idx]:g} {time_unit}',fontsize=10,pad=8)
    fig,slots=_page(len(selected),columns,rows,width,panel_height,title)
    for slot,frame in zip(slots,selected):draw(fig.add_subplot(slot,projection='3d'),frame_order.index(frame))
    fig.legend(handles=[Line2D([],[],marker='o',ls='',color=pal[e],label=e) for e in pd.unique(atoms.element)],loc='upper center',bbox_to_anchor=(.5,1-min(.6,.06*fig.get_figheight())/fig.get_figheight()),ncol=6,frameon=False,fontsize=9)
    def write_animation(directory,figure_id,synthetic=False):
        from PIL import Image
        out=Path(directory);images=[];encoded=[]
        af=plt.figure(figsize=(6.0,5.1),facecolor='white');ax=af.add_subplot(111,projection='3d');af.subplots_adjust(left=.02,right=.92,bottom=.08,top=.90)
        af.legend(handles=[Line2D([],[],marker='o',ls='',color=pal[e],label=e) for e in pd.unique(atoms.element)],
                  loc='upper left',bbox_to_anchor=(.025,.985),ncol=3,frameon=False,fontsize=8,
                  handletextpad=.3,columnspacing=.9)
        try:
            for idx in range(len(frame_order)):
                ax.clear();draw(ax,idx)
                label=af.text(.03,.02,'Synthetic coordinates · no molecular dynamics run' if synthetic else 'Stored coordinates · fixed camera and scale',fontsize=8,color='#667C85')
                af.canvas.draw();rgba=np.asarray(af.canvas.buffer_rgba());im=Image.fromarray(rgba.copy()).convert('RGB');im.thumbnail((660,560));images.append(im)
                stream=io.BytesIO();im.save(stream,format='PNG');encoded.append('data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode());label.remove()
            gif=out/(figure_id+'.gif');images[0].save(gif,save_all=True,append_images=images[1:],duration=round(1000/animation_fps),loop=0,disposal=2)
            payload=json.dumps(dict(frames=encoded,times=times.tolist(),ids=list(frame_order),time_unit=time_unit,fps=animation_fps)).replace('<','\\u003c')
            html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'"><title>Stored molecular trajectory</title><style>body{font:16px system-ui;color:#294550;background:#f1f5f5;margin:24px}main{max-width:850px;background:white;padding:24px;margin:auto;border-radius:12px}img{display:block;width:min(100%,660px);margin:auto}input{width:100%}button{padding:8px 18px;background:white;border:1px solid #90b5b2;border-radius:6px}small{display:block;margin-top:20px;color:#687c85}</style><main><h1>Stored molecular trajectory</h1><img id="art" alt="Stored atom coordinates"><p id="time"></p><input id="frame" aria-label="Frame" type="range" min="0" step="1"><button id="play">Play</button><small>No fitting, MD simulation, alignment or inferred bonds. Camera and axes stay fixed. Playback fps is a display speed; labelled times are supplied physical times.</small></main><script>const D=PAYLOAD;const a=document.getElementById('art'),s=document.getElementById('frame'),t=document.getElementById('time');let timer; s.max=D.frames.length-1;function draw(){const i=Number(s.value);a.src=D.frames[i];t.textContent=D.ids[i]+' · '+D.times[i]+' '+D.time_unit}s.value=0;s.oninput=draw;document.getElementById('play').onclick=function(){if(timer){clearInterval(timer);timer=null;this.textContent='Play'}else{this.textContent='Pause';timer=setInterval(()=>{s.value=(Number(s.value)+1)%D.frames.length;draw()},1000/D.fps)}};draw();</script></html>'''.replace('PAYLOAD',payload)
            page=out/(figure_id+'.html');page.write_text(html,encoding='utf8')
            receipt=out/(figure_id+'.animation.json');receipt.write_text(json.dumps(dict(frame_ids=list(frame_order),times=times.tolist(),coordinate_unit=coordinate_unit,time_unit=time_unit,atom_count=len(atoms),explicit_bonds=len(bonds),view=list(view),playback_fps=animation_fps,coordinates_refit=False,periodic_boundary_handling=periodic_boundary_handling,scientific_acceptance=False),indent=2)+'\n',encoding='utf8')
            return [gif,page,receipt]
        finally:
            plt.close(af)
            for im in images:im.close()
    fig._workbench_animation_writer=write_animation
    return stamp(fig,data,'molecular_trajectory',frame_order=frame_order,coordinate_unit=coordinate_unit,time_unit=time_unit,
                 topology_definition=topology_definition,coordinate_definition=coordinate_definition,periodic_boundary_handling=periodic_boundary_handling,
                 key_frames=selected,view=view,columns=columns,rows=rows,width=width,panel_height=panel_height,
                 animation_fps=animation_fps,title=title,atom_count=len(atoms),frame_count=len(frame_order),inference='none')
