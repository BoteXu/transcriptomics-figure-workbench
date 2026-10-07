"""Original renderers discovered from Biomni result types, not analysis engines.

Consume frozen heights, contacts, trees and registered pixels. Never perform
motif discovery, phylogeny estimation, segmentation or image registration.
"""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Affine2D
from matplotlib.patches import PathPatch, Polygon, Patch
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize, ListedColormap
from figure_core import checked
from figure_method_extensions import _new, _axis, _finish, _cmap, _unique
from project_theme import group_palette


def _declared(*values):
    if any(not isinstance(v,str) or not v.strip() for v in values):
        raise ValueError('Nonempty definitions and units are required')


def _limits(limits):
    if len(limits)!=2 or not np.isfinite(limits).all() or limits[0]>=limits[1]:
        raise ValueError('Two finite ordered scale limits required')
    return limits


def _order(values,order):
    if not order or len(order)!=len(set(order)) or set(order)!=set(values):
        raise ValueError('Provide each displayed ID exactly once in its order')
    return list(order)


def plot_sequence_logo(data,theme,*,position_order,alphabet,symbol_slots,height_definition,
                       height_unit,position_label='Supplied position',title=''):
    d=checked(data,['position_id','symbol','height'],['height']);_unique(d,['position_id','symbol'])
    order=_order(d.position_id,position_order);letters=_order(d.symbol,alphabet)
    if any(not isinstance(s,str) or len(s)!=1 or s.isspace() for s in letters):
        raise ValueError('Logo symbols must be single visible characters')
    if set(symbol_slots)!=set(letters) or (d.height<0).any():raise ValueError('Nonnegative heights and complete symbol color slots required')
    if len(d)!=len(order)*len(letters):raise ValueError('Include explicit zero heights for absent symbols at every position')
    _declared(height_definition,height_unit,position_label)
    pal=group_palette(theme,list(dict.fromkeys(symbol_slots.values())))
    fig=_new(theme,(max(7,2+len(order)*.42),4.4));ax=_axis(fig,[.10,.23,.72,.62])
    font=FontProperties(family=theme['font_family'],weight='bold');totals=[]
    paths={s:TextPath((0,0),s,size=1,prop=font) for s in letters}
    for j,pos in enumerate(order):
        q=d[d.position_id==pos].set_index('symbol');bottom=0
        for symbol in sorted(letters,key=lambda s:(q.loc[s,'height'],letters.index(s))):
            height=float(q.loc[symbol,'height'])
            if height==0:continue
            path=paths[symbol];box=path.get_extents()
            transform=Affine2D().translate(-box.x0,-box.y0).scale(.82/box.width,height/box.height).translate(j-.41,bottom)
            patch=PathPatch(path,transform=transform+ax.transData,color=pal[symbol_slots[symbol]],lw=0)
            patch.set_gid('logo:'+str(pos)+':'+symbol);ax.add_patch(patch);bottom+=height
        totals.append(bottom)
    if max(totals)<=0:raise ValueError('At least one positive symbol height is required')
    ax.set(xlim=(-.6,len(order)-.4),ylim=(0,max(totals)*1.08),xticks=range(len(order)),
           xticklabels=order,xlabel=position_label,ylabel=height_unit,title=title)
    if any(len(str(x))>5 for x in order):ax.tick_params(axis='x',labelrotation=35)
    fig.legend(handles=[Patch(color=pal[symbol_slots[s]],label=s) for s in letters],loc='upper left',bbox_to_anchor=(.85,.85),frameon=False,title='Symbol')
    fig.text(.10,.055,textwrap.fill(height_definition,100),fontsize=8)
    return _finish(fig,data,theme,'sequence_logo',position_order=order,alphabet=letters,symbol_slots=symbol_slots,
                   height_definition=height_definition,height_unit=height_unit,position_label=position_label,title=title,
                   inference='none; individual glyph height equals supplied height')


def plot_contact_tracks(data,theme,*,bin_order,track_order,region_definition,coordinate_unit,
                        value_definition,value_limits,track_unit,title=''):
    if 'record_type' not in data or set(data.record_type)-{'bin','contact','signal'}:raise ValueError('Use bin/contact/signal records')
    bins=checked(data[data.record_type=='bin'],['bin_id','start','end'],['start','end']);_unique(bins,['bin_id'])
    order=_order(bins.bin_id,bin_order);bins=bins.set_index('bin_id').loc[order]
    if (bins.end<=bins.start).any() or not np.allclose(bins.end.to_numpy()[:-1],bins.start.to_numpy()[1:],rtol=0,atol=1e-8):
        raise ValueError('Ordered bins must have positive contiguous physical intervals')
    q=data[data.record_type=='contact'].copy();checked(q,['bin_i','bin_j']);_unique(q,['bin_i','bin_j'])
    rank={b:i for i,b in enumerate(order)}
    if set(zip(q.bin_i,q.bin_j))!={(a,b) for i,a in enumerate(order) for b in order[i:]}:
        raise ValueError('Supply every upper-triangle pair; unknown measurements must have an explicit missing value')
    values=pd.to_numeric(q.value,errors='raise');known=values.notna()
    if not np.isfinite(values[known]).all() or (values[known]<0).any():raise ValueError('Contact display quantity must be finite and nonnegative or explicitly missing')
    lo,hi=_limits(value_limits)
    if lo<0 or ((values[known]<lo)|(values[known]>hi)).any():raise ValueError('Contact limits must include all known values')
    _declared(region_definition,coordinate_unit,value_definition,track_unit)
    signals=data[data.record_type=='signal']
    tracks=[] if signals.empty else _order(signals.track,track_order)
    if signals.empty and track_order:raise ValueError('Track order supplied without signal records')
    if tracks:
        signals=checked(signals,['track','bin_id','value'],['value']);_unique(signals,['track','bin_id'])
        if set(zip(signals.track,signals.bin_id))!={(t,b) for t in tracks for b in order}:raise ValueError('Every track must use exactly the contact bins')
    width=max(8,len(order)*.3+3);fig=_new(theme,(width,5+len(tracks)*1.15))
    total=len(tracks)+3.5;bottom=.12;available=.68;main_h=available*3.5/total
    ax=_axis(fig,[.12,bottom,.68,main_h]);start=float(bins.start.iloc[0]);end=float(bins.end.iloc[-1])
    patches=[]
    for row in q.itertuples():
        a=bins.loc[row.bin_i];b=bins.loc[row.bin_j]
        corners=[(a.start,b.start),(a.end,b.start),(a.end,b.end),(a.start,b.end)] if row.bin_i!=row.bin_j else [(a.start,a.start),(a.start,a.end),(a.end,a.end)]
        patches.append(Polygon([((u+v)/2,(v-u)/2) for u,v in corners]))
    collection=PatchCollection(patches,cmap=_cmap(theme,False),norm=Normalize(lo,hi),edgecolor='white',linewidth=.3)
    collection.cmap.set_bad(theme['roles']['neutral']);collection.set_array(np.ma.masked_invalid(values.to_numpy(float)));ax.add_collection(collection)
    ax.set(xlim=(start,end),ylim=(0,(end-start)/2),xlabel=coordinate_unit,ylabel='Pair separation / 2 ('+coordinate_unit+')')
    cax=fig.add_axes([.84,bottom,.022,main_h]);fig.colorbar(collection,cax=cax,label=value_definition)
    edges=np.r_[bins.start.to_numpy(),bins.end.iloc[-1]]
    for i,t in enumerate(tracks):
        track=_axis(fig,[.12,bottom+main_h+(i+.22)*available/total,.68,.68*available/total]);track.sharex(ax)
        v=signals[signals.track==t].set_index('bin_id').loc[order,'value'].to_numpy()
        track.stairs(v,edges,color=theme['roles']['primary'],fill=True,alpha=.7)
        track.tick_params(labelbottom=False);track.set_ylabel(t,fontsize=9,rotation=0,ha='right',va='center')
        track.text(1.02,.5,track_unit,transform=track.transAxes,fontsize=8,va='center')
    fig.text(.12,.91,title,weight='bold',fontsize=11);fig.text(.12,.035,textwrap.fill(region_definition+'; missing contacts are masked, not zero.',110),fontsize=8)
    return _finish(fig,data,theme,'contact_tracks',bin_order=order,track_order=tracks,region_definition=region_definition,
                   coordinate_unit=coordinate_unit,value_definition=value_definition,value_limits=value_limits,track_unit=track_unit,title=title,
                   coordinate_map='x=(u+v)/2; y=(v-u)/2; physical bin intervals retained',missing='neutral mask; explicit zero remains zero')


def plot_branch_tree(data,theme,*,root_id,leaf_order,branch_unit,tree_definition,title=''):
    d=checked(data,['node_id','branch_length','label'],['branch_length']);_unique(d,['node_id'])
    if 'parent_id' not in d or root_id not in set(d.node_id) or (d.branch_length<0).any():raise ValueError('Explicit root, parent IDs and nonnegative branches required')
    _declared(branch_unit,tree_definition);d=d.set_index('node_id');children={n:[] for n in d.index}
    if pd.notna(d.loc[root_id,'parent_id']) and d.loc[root_id,'parent_id']!='':raise ValueError('Root has no parent')
    if d.loc[root_id,'branch_length']!=0:raise ValueError('Root branch length must be zero')
    for n,row in d.iterrows():
        if n==root_id:continue
        if row.parent_id not in d.index or row.parent_id==n:raise ValueError('Unknown parent or self-cycle')
        children[row.parent_id].append(n)
    leaves=_order([n for n in d.index if not children[n]],leaf_order);ranks={n:i for i,n in enumerate(leaves)}
    seen=set();active=set();x={root_id:0};y={};desc={}
    def visit(n):
        if n in active:raise ValueError('Tree contains a cycle')
        active.add(n);seen.add(n)
        for c in children[n]:x[c]=x[n]+float(d.loc[c,'branch_length']);visit(c)
        desc[n]=[r for c in children[n] for r in desc[c]] if children[n] else [ranks[n]]
        if max(desc[n])-min(desc[n])+1!=len(desc[n]):raise ValueError('Leaf order must keep each clade contiguous')
        y[n]=(min(desc[n])+max(desc[n]))/2;active.remove(n)
    visit(root_id)
    if seen!=set(d.index):raise ValueError('Tree is disconnected or cyclic')
    fig=_new(theme,(8,max(4,1.8+len(leaves)*.31)));ax=_axis(fig,[.12,.19,.60,.65]);color=theme['palette_colors'][0]
    for n in d.index:
        if children[n]:ax.plot([x[n],x[n]],[min(y[c] for c in children[n]),max(y[c] for c in children[n])],c=color,lw=1.2)
        if n!=root_id:
            line,=ax.plot([x[d.loc[n,'parent_id']],x[n]],[y[n],y[n]],c=color,lw=1.2);line.set_gid('branch:'+n)
    span=max(x.values())
    if not np.isfinite(span) or span<=0:raise ValueError('Tree needs positive finite total branch span')
    ax.set(xlim=(0,span*1.03),ylim=(len(leaves)-.4,-.6),xlabel=branch_unit,yticks=[],title=title)
    ax.spines[['left','top','right']].set_visible(False)
    for n in leaves:ax.text(1.02,y[n],d.loc[n,'label'],transform=ax.get_yaxis_transform(),va='center',fontsize=9)
    fig.text(.12,.06,textwrap.fill(tree_definition,95),fontsize=8)
    return _finish(fig,data,theme,'branch_tree',root_id=root_id,leaf_order=leaves,branch_unit=branch_unit,tree_definition=tree_definition,title=title,
                   inference='none; x is supplied cumulative branch length, not clustering height')


def _pixel_grid(data,columns,view=None):
    d=data if view is None else data[data.view==view]
    d=checked(d,['u','v',*columns],['u','v',*columns]);_unique(d,['u','v'])
    u=np.sort(d.u.unique());v=np.sort(d.v.unique())
    if len(u)<2 or len(v)<2 or len(d)!=len(u)*len(v):raise ValueError('Complete rectangular pixel grid with at least 2 pixels per axis required')
    if not np.allclose(np.diff(u),u[1]-u[0]) or not np.allclose(np.diff(v),v[1]-v[0]):raise ValueError('Pixel coordinates must use regular physical spacing')
    extent=[u[0]-(u[1]-u[0])/2,u[-1]+(u[1]-u[0])/2,v[0]-(v[1]-v[0])/2,v[-1]+(v[1]-v[0])/2]
    arrays={c:d.pivot(index='v',columns='u',values=c).reindex(index=v,columns=u).to_numpy() for c in columns}
    return arrays,extent


def plot_slice_overlay(data,theme,*,view_order,axis_labels,label_slots,intensity_limits,
                       registration_definition,orientation_definition,arrangement='horizontal',title=''):
    checked(data,['view']);views=_order(data.view,view_order)
    if set(axis_labels)!=set(views) or any(len(x)!=2 for x in axis_labels.values()):raise ValueError('Provide physical u/v axis labels for every slice')
    if arrangement not in ('horizontal','vertical'):raise ValueError('Unknown panel arrangement')
    _declared(registration_definition,orientation_definition);lo,hi=_limits(intensity_limits)
    labels=sorted(set(data.label));pal=group_palette(theme,list(dict.fromkeys(label_slots.values())))
    if labels[0]<0 or any(x%1!=0 for x in labels) or set(label_slots)!=set(str(int(x)) for x in labels if x>0):raise ValueError('Label 0 is background; every positive integer label needs a color slot')
    fig=_new(theme,((4.4*len(views)+1.5,5.1) if arrangement=='horizontal' else (6,3.5*len(views)+1.4)))
    for i,view in enumerate(views):
        arrays,extent=_pixel_grid(data,['intensity','label'],view)
        if ((arrays['intensity']<lo)|(arrays['intensity']>hi)).any():raise ValueError('Intensity limits must include all supplied pixels')
        bounds=[.075+i*.78/len(views),.20,.60/len(views),.62] if arrangement=='horizontal' else [.14,.17+(len(views)-i-1)*.69/len(views),.62,.60/len(views)]
        ax=_axis(fig,bounds);ax.imshow(arrays['intensity'],cmap='gray',vmin=lo,vmax=hi,origin='lower',extent=extent,interpolation='nearest')
        for label in labels:
            if label==0:continue
            mask=np.ma.masked_where(arrays['label']!=label,arrays['label'])
            ax.imshow(mask,cmap=ListedColormap([pal[label_slots[str(int(label))]]]),alpha=.5,origin='lower',extent=extent,interpolation='nearest')
        ax.set(title=view,xlabel=axis_labels[view][0],ylabel=axis_labels[view][1]);ax.set_aspect('equal')
    fig.legend(handles=[Patch(color=pal[s],label='Label '+l) for l,s in label_slots.items()],loc='upper left',bbox_to_anchor=(.88,.82),frameon=False)
    fig.text(.075,.95,title,fontsize=11,weight='bold');fig.text(.075,.045,textwrap.fill(orientation_definition,105),fontsize=8)
    return _finish(fig,data,theme,'slice_overlay',view_order=views,axis_labels=axis_labels,label_slots=label_slots,intensity_limits=intensity_limits,
                   registration_definition=registration_definition,orientation_definition=orientation_definition,arrangement=arrangement,title=title,
                   inference='none; frozen registered slice labels, not generated segmentations')


def plot_registration_check(data,theme,*,intensity_limits,difference_limits,tile_pixels,
                            coordinate_labels,registration_definition,arrangement='horizontal',title=''):
    arrays,extent=_pixel_grid(data,['fixed','registered']);lo,hi=_limits(intensity_limits);dl,dh=_limits(difference_limits)
    if len(coordinate_labels)!=2 or type(tile_pixels) is not int or tile_pixels<1:raise ValueError('Two coordinate labels and a positive integer checker tile size required')
    if arrangement not in ('horizontal','vertical'):raise ValueError('Unknown panel arrangement')
    if dl>=0 or dh<=0 or any(((a<lo)|(a>hi)).any() for a in arrays.values()):raise ValueError('Signed difference scale and complete common intensity limits required')
    _declared(registration_definition);delta=arrays['registered']-arrays['fixed']
    if ((delta<dl)|(delta>dh)).any():raise ValueError('Difference scale must include every displayed subtraction')
    yy,xx=np.indices(delta.shape);checker=np.where((xx//tile_pixels+yy//tile_pixels)%2,arrays['fixed'],arrays['registered'])
    figures=[('Fixed',arrays['fixed']),('Registered',arrays['registered']),('Checkerboard',checker),('Registered - fixed',delta)]
    fig=_new(theme,(15.5,5) if arrangement=='horizontal' else (6,14))
    for i,(label,values) in enumerate(figures):
        b=[.06+i*.205,.23,.172,.60] if arrangement=='horizontal' else [.14,.13+(3-i)*.195,.56,.16]
        ax=_axis(fig,b);im=ax.imshow(values,origin='lower',extent=extent,interpolation='nearest',cmap=_cmap(theme,True) if i==3 else 'gray',vmin=dl if i==3 else lo,vmax=dh if i==3 else hi)
        ax.set(title=label,xlabel=coordinate_labels[0],ylabel=coordinate_labels[1]);ax.set_aspect('equal')
        if i==3:
            cax=fig.add_axes([.91,.23,.012,.6] if arrangement=='horizontal' else [.78,.13,.028,.16]);fig.colorbar(im,cax=cax,label='Pixel intensity difference')
    fig.text(.06,.95,title,fontsize=11,weight='bold');fig.text(.06,.045,'Checkerboard alternates supplied images; subtraction uses identical pixel coordinates and declared intensity scale.',fontsize=8)
    return _finish(fig,data,theme,'registration_check',intensity_limits=intensity_limits,difference_limits=difference_limits,tile_pixels=tile_pixels,
                   coordinate_labels=coordinate_labels,registration_definition=registration_definition,arrangement=arrangement,title=title,
                   difference_definition='registered minus fixed at identical frozen physical pixel coordinates; no normalization',inference='none; no registration or performance metric estimation')
