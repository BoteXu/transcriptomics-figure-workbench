"""Original, opt-in appearance controls for stamped Matplotlib figures.

No fitting, aggregation, dependency installation or foreign script execution.
Layout checks are advisory; actual exports still need visual inspection.
"""
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib
import json
import math
import textwrap
import numpy as np
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.text import Text


@dataclass
class DesignSpec:
    width_mm: float | None = None
    height_mm: float | None = None
    font_family: str | None = None
    label_pt: float = 10
    tick_pt: float = 9
    title_pt: float = 11
    note_pt: float = 8
    spine_width: float = 0.7
    spine_mode: str = 'keep'
    grid: str = 'keep'
    x_tick_rotation: float | None = None
    axis_bounds: dict = field(default_factory=dict)
    figure_text_positions: dict = field(default_factory=dict)
    figure_text_wraps: dict = field(default_factory=dict)
    legend_zone: list | None = None
    legend_columns: int = 1
    legend_title_width: int | None = None

    def validate(self):
        for key in ('width_mm','height_mm','label_pt','tick_pt','title_pt','note_pt','spine_width'):
            value=getattr(self,key)
            if value is not None and (not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0):
                raise ValueError('Positive finite dimension required: '+key)
        if self.spine_mode not in ('keep','minimal','boxed') or self.grid not in ('keep','none','x','y','both'):
            raise ValueError('Unknown spine/grid mode')
        if self.x_tick_rotation is not None and (not math.isfinite(self.x_tick_rotation) or abs(self.x_tick_rotation)>90):
            raise ValueError('Rotation must be within -90..90')
        if type(self.legend_columns) is not int or self.legend_columns<1:
            raise ValueError('legend_columns must be a positive integer')
        for bounds in list(self.axis_bounds.values())+([self.legend_zone] if self.legend_zone is not None else []):
            if len(bounds)!=4 or any(not math.isfinite(x) for x in bounds): raise ValueError('Bounds need four finite fractions')
            x,y,w,h=bounds
            if min(x,y)<0 or min(w,h)<=0 or x+w>1 or y+h>1: raise ValueError('Bounds outside canvas')
        for pos in self.figure_text_positions.values():
            if len(pos)!=2 or any(not math.isfinite(x) or x<0 or x>1 for x in pos): raise ValueError('Text position outside canvas')
        for width in list(self.figure_text_wraps.values())+([self.legend_title_width] if self.legend_title_width is not None else []):
            if type(width) is not int or width<5: raise ValueError('Text wrap width must be an integer >=5')
        return self

    @classmethod
    def read(cls,path):
        # Dataclass rejects unknown keys; no eval, imports or executable config.
        return cls(**json.loads(Path(path).read_text(encoding='utf-8'))).validate()

    def write(self,path):
        self.validate()
        with Path(path).open('x',encoding='utf-8') as handle:
            json.dump(asdict(self),handle,ensure_ascii=False,indent=2)


def resolve_font(preferred,text=''):
    """Choose an already installed font covering supplied characters. Never install."""
    candidates=[preferred,'Microsoft YaHei','Noto Sans CJK SC','SimHei','DejaVu Sans']
    required={ord(c) for c in text if not c.isspace()}
    for name in dict.fromkeys(x for x in candidates if x):
        try:
            path=font_manager.findfont(name,fallback_to_default=False)
        except ValueError:
            continue
        if required.issubset(FT2Font(path).get_charmap()): return name
    raise ValueError('No installed font covers the supplied text; select a font or shorten/translate labels')


def geometry_signature(fig):
    """Quantitative artist geometry/arrays/scales; appearance and canvas position excluded."""
    digest=hashlib.sha256()
    def add(value):
        a=np.ma.asarray(value)
        digest.update(str((a.shape,str(a.dtype))).encode())
        digest.update(np.asarray(a.filled(np.nan) if np.issubdtype(a.dtype,np.floating) else a).tobytes())
        digest.update(np.ma.getmaskarray(a).tobytes())
    for ax in fig.axes:
        if getattr(ax,'_figure_legend_zone',False): continue
        digest.update(str((ax.get_xscale(),ax.get_yscale())).encode())
        add(ax.get_xlim());add(ax.get_ylim())
        for line in ax.lines: add(line.get_xydata())
        for collection in ax.collections:
            add(collection.get_offsets())
            if collection.get_array() is not None: add(collection.get_array())
            if hasattr(collection,'get_segments'):
                for seg in collection.get_segments(): add(seg)
            for path in collection.get_paths(): add(path.vertices)
            digest.update(str(collection.get_clim()).encode())
        for im in ax.images:
            add(im.get_array());add(im.get_extent());digest.update(str(im.get_clim()).encode())
        for patch in ax.patches:
            add(patch.get_path().vertices)
            add(patch.get_patch_transform().get_matrix())
    return digest.hexdigest()


def named_layout(fig,panels):
    """Create explicitly named panels using fractions, including optional blank legend regions."""
    DesignSpec(axis_bounds=panels).validate()
    if fig.axes: raise ValueError('Named layout requires an empty figure')
    axes={}
    for name,bounds in panels.items():
        ax=fig.add_axes(bounds,label=name)
        ax.set_gid(name);axes[name]=ax
    return axes


def apply_design(fig,spec):
    """Restyle in place; retain exact input stamp and quantitative geometry signature."""
    if not hasattr(fig,'_omics_input_sha256'): raise ValueError('A reviewed/stamped renderer figure is required')
    if not isinstance(spec,DesignSpec): raise TypeError('Expected DesignSpec')
    spec.validate();fig.canvas.draw();before=geometry_signature(fig)
    axes=list(fig.axes)
    lookup={str(i):ax for i,ax in enumerate(axes)}
    for ax in axes:
        if ax.get_gid(): lookup[ax.get_gid()]=ax
    if set(spec.axis_bounds)-set(lookup): raise ValueError('Unknown axis name/index')
    if (set(spec.figure_text_positions)|set(spec.figure_text_wraps))-{t.get_text() for t in fig.texts}: raise ValueError('Unknown figure-level text')
    if spec.legend_zone is not None and any(getattr(a,'_figure_legend_zone',False) for a in axes):
        raise ValueError('Legend zone already exists; render afresh before restyling')
    font=None
    if spec.font_family:
        font=resolve_font(spec.font_family,''.join(t.get_text() for t in fig.findobj(Text)))
    if spec.axis_bounds or spec.legend_zone is not None:
        fig.set_layout_engine(None)
    fig.set_size_inches((spec.width_mm/25.4 if spec.width_mm else fig.get_figwidth()),
                        (spec.height_mm/25.4 if spec.height_mm else fig.get_figheight()))
    for text in fig.findobj(Text):
        if font: text.set_fontfamily(font)
    for text in fig.texts:
        original_text=text.get_text()
        text.set_fontsize(spec.title_pt if str(text.get_weight()) in ('bold','heavy','800','900') else spec.note_pt)
        if original_text in spec.figure_text_positions: text.set_position(spec.figure_text_positions[original_text])
        if original_text in spec.figure_text_wraps: text.set_text(textwrap.fill(original_text,spec.figure_text_wraps[original_text]))
    legends=[]
    for ax in axes:
        ax.xaxis.label.set_fontsize(spec.label_pt);ax.yaxis.label.set_fontsize(spec.label_pt)
        for title in (ax.title,ax._left_title,ax._right_title): title.set_fontsize(spec.title_pt)
        ax.tick_params(labelsize=spec.tick_pt)
        for spine in ax.spines.values(): spine.set_linewidth(spec.spine_width)
        if spec.spine_mode!='keep':
            for key,spine in ax.spines.items(): spine.set_visible(spec.spine_mode=='boxed' or key in ('left','bottom'))
        if spec.grid!='keep':
            ax.grid(False,which='both',axis='both')
            if spec.grid!='none': ax.grid(True,axis=spec.grid,color='#DCE1E4',linewidth=.45)
        if spec.x_tick_rotation is not None and not hasattr(ax,'_colorbar'):
            for tick in ax.get_xticklabels():
                tick.set_rotation(spec.x_tick_rotation)
                tick.set_ha('right' if spec.x_tick_rotation else 'center')
        legend=ax.get_legend()
        if legend:
            for t in legend.get_texts(): t.set_fontsize(spec.tick_pt)
            legend.get_title().set_fontsize(spec.label_pt)
            if spec.legend_title_width: legend.get_title().set_text(textwrap.fill(legend.get_title().get_text(),spec.legend_title_width))
            legends.append(legend)
    for key,bounds in spec.axis_bounds.items(): lookup[key].set_position(bounds)
    if spec.legend_zone is not None:
        # Preserve each legend's title and order, including size/color semantic guides.
        legends+=list(fig.legends)
        if not legends: raise ValueError('No existing legends to relocate')
        zone=fig.add_axes(spec.legend_zone,label='legend_zone');zone._figure_legend_zone=True
        zone.set_axis_off()
        for i,legend in enumerate(legends):
            handles=list(legend.legend_handles);labels=[t.get_text() for t in legend.get_texts()]
            title=legend.get_title().get_text();legend.remove()
            new=zone.legend(handles,labels,title=title,loc='upper left',bbox_to_anchor=(0,1-i/len(legends)),
                            ncols=spec.legend_columns,frameon=False,fontsize=spec.tick_pt,title_fontsize=spec.label_pt)
            if font:
                for t in new.get_texts()+[new.get_title()]: t.set_fontfamily(font)
            zone.add_artist(new)
    fig.canvas.draw();after=geometry_signature(fig)
    if before!=after: raise RuntimeError('Restyling changed quantitative artist geometry; discard figure and render afresh')
    fig._omics_spec['design']=dict(asdict(spec),resolved_font=font,geometry_sha256=after)
    return fig


def design_for(fig):
    """Conservative first-pass appearance profile; inspect exports and override for real labels.

    Preserves palette, limits, coordinates, order, semantic legends and point areas.
    Original renderer calls remain valid; this profile is the recommended new-work entry.
    """
    if not hasattr(fig,'_omics_spec'): raise ValueError('A stamped renderer figure is required')
    kind=fig._omics_spec['kind']
    spec=DesignSpec(width_mm=max(180,fig.get_figwidth()*25.4),
                    height_mm=max(115,fig.get_figheight()*25.4),font_family='DejaVu Sans')
    # Use all text for installed-font resolution; CJK fallback happens in apply_design.
    matrix_kinds={'heatmap','dot','effect_matrix','annotated_heatmap','publication_aligned_matrix',
                  'polished_matrix','association_matrix'}
    if kind in matrix_kinds:
        spec.width_mm=max(200,spec.width_mm);spec.x_tick_rotation=30
    if kind=='dot':
        spec.axis_bounds={'0':[.18,.22,.34,.62],'1':[.60,.22,.025,.62]}
        spec.legend_zone=[.76,.26,.23,.5]
        spec.legend_title_width=22
    if kind=='polished_matrix' and fig._omics_spec.get('layout')=='transpose':
        spec.width_mm=max(230,spec.width_mm);spec.x_tick_rotation=60
    if kind=='recorded_evidence':
        spec.height_mm=165 if fig._omics_spec['layout']=='split' else 135
        spec.legend_zone=[.25,.81,.74,.065];spec.legend_columns=3
        for i,ax in enumerate(fig.axes):
            bounds=list(ax.get_position().bounds)
            bounds[1:4:2]=[.53,.18] if fig._omics_spec['layout']=='split' and i==0 else [.20,.19] if fig._omics_spec['layout']=='split' else [.28,.42]
            spec.axis_bounds[str(i)]=bounds
        for text in fig.texts:
            content=text.get_text();x=text.get_position()[0]
            if content=='Recorded evidence':spec.figure_text_positions[content]=[x,.93]
            elif content.startswith('A counts:'):spec.figure_text_positions[content]=[x,.77]
            elif content.startswith('N/A ='):spec.figure_text_positions[content]=[x,.065]
    if kind=='availability_counts':
        spec.height_mm=135;spec.axis_bounds={'0':[.27,.28,.68,.48]}
        spec.legend_zone=[.25,.80,.72,.065];spec.legend_columns=2
        for text in fig.texts:
            content=text.get_text();x=text.get_position()[0]
            if content=='Record availability':spec.figure_text_positions[content]=[x,.93]
            elif content.startswith('Availability,'):
                spec.figure_text_positions[content]=[x,.06];spec.figure_text_wraps[content]=80
    return spec.validate()


def audit_layout(fig,min_font_pt=7):
    """Advisory rendered-bbox/font checks. Not a scientific or aesthetic approval."""
    fig.canvas.draw();renderer=fig.canvas.get_renderer();canvas=fig.bbox;issues=[]
    def visible(t): return t.get_visible() and bool(t.get_text().strip())
    def overlap(a,b):
        x=min(a.x1,b.x1)-max(a.x0,b.x0);y=min(a.y1,b.y1)-max(a.y0,b.y0)
        return x>1 and y>1
    off_view=set()
    for ax in fig.axes:
        for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
            lo,hi=sorted(limits)
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not ax.axison or not lo<=tick.get_loc()<=hi:
                    off_view.update((id(tick.label1),id(tick.label2)))
            if not ax.axison:off_view.add(id(axis.label))
    texts={id(t):t for t in fig.findobj(Text)}
    for ident,t in texts.items():
        if ident in off_view: continue
        if not visible(t): continue
        b=t.get_window_extent(renderer)
        if b.x0<canvas.x0-1 or b.y0<canvas.y0-1 or b.x1>canvas.x1+1 or b.y1>canvas.y1+1:
            issues.append({'kind':'text_outside_canvas','text':t.get_text()})
        if t.get_fontsize()<min_font_pt: issues.append({'kind':'small_font','text':t.get_text(),'pt':t.get_fontsize()})
        path=font_manager.findfont(t.get_fontproperties());glyphs=FT2Font(path).get_charmap()
        missing=sorted({c for c in t.get_text() if not c.isspace() and ord(c) not in glyphs})
        if missing: issues.append({'kind':'missing_glyph','text':t.get_text(),'characters':missing})
    for i,ax in enumerate(fig.axes):
        if not ax.axison: continue
        for axis,ticks in [('x',ax.get_xticklabels()),('y',ax.get_yticklabels())]:
            ticks=[t for t in ticks if visible(t)]
            for a,b in zip(ticks,ticks[1:]):
                if overlap(a.get_window_extent(renderer),b.get_window_extent(renderer)):
                    issues.append({'kind':'tick_overlap','axis':i,'dimension':axis,'text':[a.get_text(),b.get_text()]})
    candidates=list(fig.texts)
    for ax in fig.axes:
        candidates.extend((ax.title,ax._left_title,ax._right_title))
        if ax.axison:candidates.extend((ax.xaxis.label,ax.yaxis.label))
    headings=list({id(t):t for t in candidates if visible(t)}.values())
    for i,a in enumerate(headings):
        for b in headings[i+1:]:
            if overlap(a.get_window_extent(renderer),b.get_window_extent(renderer)):
                issues.append({'kind':'heading_overlap','text':[a.get_text(),b.get_text()]})
    return {'status':'LAYOUT_CHECKS_ONLY','issues':issues,'manual_review_required':True,
            'limits':'Cannot establish data correctness, legend occlusion, perceptual quality or exported-file acceptance'}
