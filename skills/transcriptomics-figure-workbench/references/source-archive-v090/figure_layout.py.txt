"""Page orientation independent of scientific axes and panel arrangement.

Canvas expansion preserves the physical plotting area, font size, aspect and
all guides. Separate exported panels can be reflowed using compose_panels.
"""
import numpy as np
from matplotlib.transforms import Affine2D, Bbox
from figure_design import geometry_signature


def _expand_canvas(fig,sizes,shift_inches):
    old=np.asarray(fig.get_size_inches(),float);sizes=np.asarray(sizes,float)
    scale=old/sizes;shift=np.asarray(shift_inches,float)/sizes
    bounds=[(a,list(a.get_position().bounds)) for a in fig.axes]
    texts=[(t,np.asarray(t.get_position(),float)) for t in fig.texts if t.get_transform()==fig.transFigure]
    from matplotlib.legend import Legend
    legends=[(l,l.get_bbox_to_anchor().transformed(fig.transFigure.inverted())) for l in fig.findobj(Legend)
             if l in fig.legends or getattr(l,'_page_fixed_anchor',False)]
    fig.set_layout_engine(None);fig.set_size_inches(*sizes)
    for ax,b in bounds:
        if not getattr(ax,'_indexed_locator',False):ax.set_axes_locator(None)
        ax.set_position([shift[0]+b[0]*scale[0],shift[1]+b[1]*scale[1],b[2]*scale[0],b[3]*scale[1]])
    for t,p in texts:t.set_position(p*scale+shift)
    for legend,b in legends:
        legend.set_bbox_to_anchor(Bbox.from_bounds(shift[0]+b.x0*scale[0],shift[1]+b.y0*scale[1],b.width*scale[0],b.height*scale[1]),transform=fig.transFigure)
    remap=Affine2D().scale(*scale).translate(*shift)+fig.transFigure
    for patch in fig.patches:patch.set_transform(remap)


def optimize_guide_layout(fig):
    """Move legends out of all data regions and grow for real text extents.

    Does not shrink fonts, truncate labels, change quantitative arrays or infer
    a shared legend. Every supplied guide keeps its original order and title.
    """
    from matplotlib.legend import Legend
    fig.canvas.draw();before=geometry_signature(fig);renderer=fig.canvas.get_renderer()
    # Preserve caller rotation and all labels. Expand the physical canvas
    # instead of shrinking fonts or selecting a fixed subset of ticks.
    tick_scale=np.ones(2)
    for ax in fig.axes:
        if not ax.axison or hasattr(ax,'_colorbar'):continue
        for dim,labels in enumerate((ax.get_xticklabels(),ax.get_yticklabels())):
            boxes=[t.get_window_extent(renderer) for t in labels if t.get_visible() and t.get_text()]
            boxes.sort(key=lambda b:(b.x0+b.x1) if dim==0 else (b.y0+b.y1))
            for a,b in zip(boxes,boxes[1:]):
                ca=(a.x0+a.x1)/2 if dim==0 else (a.y0+a.y1)/2
                cb=(b.x0+b.x1)/2 if dim==0 else (b.y0+b.y1)/2
                span=(a.width+b.width)/2 if dim==0 else (a.height+b.height)/2
                if cb-ca>1:tick_scale[dim]=max(tick_scale[dim],(span+3)/(cb-ca))
    if np.max(tick_scale)>1.005:
        fig.set_size_inches(*(np.asarray(fig.get_size_inches())*tick_scale))
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
    # Measure neighbouring complete axes, including their tick/title lanes.
    # Native axes positions are retained; enlarge their physical separation.
    # Overlapping axes (insets and intentional overlays) are never guessed apart.
    adjacent_scale=np.ones(2)
    for _ in range(4):
        renderer=fig.canvas.get_renderer();scale=np.ones(2)
        axes=[a for a in fig.axes if a.axison]
        for i,a in enumerate(axes):
            ab=a.bbox;at=a.get_tightbbox(renderer,bbox_extra_artists=[])
            if at is None:continue
            for b in axes[i+1:]:
                bb=b.bbox;bt=b.get_tightbbox(renderer,bbox_extra_artists=[])
                if bt is None:continue
                if min(ab.y1,bb.y1)-max(ab.y0,bb.y0)>.5*min(ab.height,bb.height):
                    left,right,lt,rt=(ab,bb,at,bt) if ab.x0<bb.x0 else (bb,ab,bt,at)
                    gap=right.x0-left.x1
                    if gap>2:scale[0]=max(scale[0],(max(0,lt.x1-left.x1)+max(0,right.x0-rt.x0)+5)/gap)
                if min(ab.x1,bb.x1)-max(ab.x0,bb.x0)>.5*min(ab.width,bb.width):
                    bottom,top,bt0,tt=(ab,bb,at,bt) if ab.y0<bb.y0 else (bb,ab,bt,at)
                    gap=top.y0-bottom.y1
                    if gap>2:scale[1]=max(scale[1],(max(0,bt0.y1-bottom.y1)+max(0,top.y0-tt.y0)+5)/gap)
        scale=np.minimum(scale,1.8)
        if max(scale)<=1.01:break
        from figure_workbench.responsive import canvas_budget
        fig.set_size_inches(*canvas_budget(*(np.asarray(fig.get_size_inches())*scale)))
        adjacent_scale*=scale;fig.canvas.draw()
    data_axes=[a for a in fig.axes if a.axison and not hasattr(a,'_colorbar')]
    legends=[l for l in fig.findobj(Legend) if l.get_visible()]
    moved=[]
    for legend in legends:
        box=legend.get_window_extent(renderer)
        if any(min(box.x1,a.bbox.x1)-max(box.x0,a.bbox.x0)>2 and min(box.y1,a.bbox.y1)-max(box.y0,a.bbox.y0)>2 for a in data_axes):
            moved.append((legend,box.width/fig.dpi,box.height/fig.dpi))
    if moved:
        old=np.asarray(fig.get_size_inches(),float);lane=max(w for _,w,_ in moved)+.35
        needed=sum(h+.18 for _,_,h in moved)+.3
        sizes=[old[0]+lane,max(old[1],needed)]
        _expand_canvas(fig,sizes,[0,0]);y=sizes[1]-.15
        for legend,w,h in moved:
            legend.set_bbox_to_anchor(((old[0]+.10)/sizes[0],y/sizes[1]),transform=fig.transFigure)
            legend._page_fixed_anchor=True
            legend.set_loc('upper left');legend.borderaxespad=0;y-=h+.18
    # Captions need their own physical lane after typography changes. Scaling
    # the entire page preserves an existing caption/x-label collision, so move
    # only colliding low figure-level notes into a newly reserved bottom lane.
    fig.canvas.draw();renderer=fig.canvas.get_renderer();notes=[]
    excluded=set(getattr(fig,'_software_band_artists',[]))
    axes_boxes=[a.get_tightbbox(renderer,bbox_extra_artists=[]) for a in fig.axes if a.axison]
    for t in fig.texts:
        if t in excluded or getattr(t,'_panel_heading',False) or not t.get_visible() or not t.get_text().strip() or t.get_transform()!=fig.transFigure or t.get_position()[1]>=.25:continue
        tb=t.get_window_extent(renderer)
        if any(b is not None and min(tb.x1,b.x1)>max(tb.x0,b.x0) and min(tb.y1,b.y1)+4>max(tb.y0,b.y0) for b in axes_boxes):
            notes.append((t,tb.height/fig.dpi))
    if notes:
        old=np.asarray(fig.get_size_inches(),float);lane=sum(h+.10 for _,h in notes)+.14
        _expand_canvas(fig,old+[0,lane],[0,lane]);cursor=.10
        for t,h in reversed(notes):
            t.set_y(cursor/fig.get_figheight());t.set_verticalalignment('bottom');cursor+=h+.10
    fig.canvas.draw();box=fig.get_tightbbox(fig.canvas.get_renderer());sizes=np.asarray(fig.get_size_inches(),float)
    if box is not None:
        left=max(0,.12-box.x0);bottom=max(0,.12-box.y0)
        right=max(0,box.x1+.12-sizes[0]);top=max(0,box.y1+.12-sizes[1])
        if max(left,bottom,right,top)>.005:_expand_canvas(fig,sizes+[left+right,bottom+top],[left,bottom])
    fig.canvas.draw()
    if before!=geometry_signature(fig):raise RuntimeError('Guide optimization changed quantitative geometry')
    fig._omics_spec['guide_layout']=dict(strategy='Measured adjacent axes and separate outer lanes; canvas grows instead of hiding guides',legends_relocated=len(moved),captions_relocated=len(notes),tick_canvas_scale=list(tick_scale),adjacent_canvas_scale=list(adjacent_scale),geometry_sha256=before)
    return fig


def add_software_bands(fig, figure_id, font_family='sans-serif'):
    """Dedicated synthetic provenance bands; never replace a scientific title."""
    if hasattr(fig,'_software_band_artists'):
        fig._software_band_artists[0].set_text('SYNTHETIC DEMO | '+figure_id)
        return fig
    fig.canvas.draw();old=np.asarray(fig.get_size_inches(),float)
    _expand_canvas(fig,old+[0,.50],[0,.25])
    header=fig.text(.02,1-.04/fig.get_figheight(),'SYNTHETIC DEMO | '+figure_id,fontsize=8,
             va='top',color='#66727D',fontfamily=font_family)
    footer=fig.text(.02,.04/fig.get_figheight(),'Software test fixture; not biological evidence',fontsize=7,
             va='bottom',color='#66727D',fontfamily=font_family)
    fig._software_band_artists=[header,footer]
    return fig


def apply_page_layout(fig, orientation='landscape', *, aspect=1.414, padding_inches=.15):
    if orientation not in ('landscape','portrait'):
        raise ValueError("page_layout must be 'landscape' or 'portrait'")
    if not np.isfinite(aspect) or aspect<=1 or not np.isfinite(padding_inches) or padding_inches<0:
        raise ValueError('Use finite aspect > 1 and nonnegative page padding')
    if not hasattr(fig,'_omics_spec'):
        raise ValueError('A stamped renderer figure is required')
    fig.canvas.draw();before=geometry_signature(fig)
    old=np.asarray(fig.get_size_inches(),float)
    sizes=old+2*padding_inches
    if orientation=='landscape':sizes[0]=max(sizes[0],sizes[1]*aspect)
    else:sizes[1]=max(sizes[1],sizes[0]*aspect)
    scale=old/sizes;shift=(1-scale)/2
    _expand_canvas(fig,sizes,(sizes-old)/2)
    fig.canvas.draw()
    if geometry_signature(fig)!=before:
        raise RuntimeError('Page arrangement changed scientific geometry')
    fig._omics_spec['page_layout']=dict(orientation=orientation,strategy='canvas expansion; original physical plot and guide sizes retained',
                                      size_inches=list(sizes),geometry_sha256=before)
    return fig
