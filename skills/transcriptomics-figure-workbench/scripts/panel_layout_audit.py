"""Check reserved guide lanes on the standalone panel route.

Bounding boxes detect occlusion/clipping, not perceptual or scientific validity.
Call after appearance replacement and again inspect the actual exported page.
"""
from matplotlib.legend import Legend

def audit_panel_layout(fig):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer(); issues=[]
    axes=[a for a in fig.axes if a.axison and not hasattr(a,'_colorbar')]
    for i,legend in enumerate(fig.findobj(Legend)):
        if not legend.get_visible(): continue
        box=legend.get_window_extent(renderer)
        if box.x0<fig.bbox.x0-1 or box.y0<fig.bbox.y0-1 or box.x1>fig.bbox.x1+1 or box.y1>fig.bbox.y1+1:
            issues.append({'kind':'legend_outside_canvas','legend':i})
        for j,ax in enumerate(axes):
            ab=ax.get_window_extent(renderer)
            # Small antialias/tick contact is allowed, but guides must not cover data.
            width=min(box.x1,ab.x1)-max(box.x0,ab.x0)
            height=min(box.y1,ab.y1)-max(box.y0,ab.y0)
            if width>2 and height>2: issues.append({'kind':'legend_over_data_region','legend':i,'axis':j})
    return {'status':'LAYOUT_CHECKS_ONLY','issues':issues,'manual_export_review_required':True,
            'scope':'Legend/canvas and legend/data-region bounding boxes only; titles, labels, contrast and colorbars still need inspection'}

