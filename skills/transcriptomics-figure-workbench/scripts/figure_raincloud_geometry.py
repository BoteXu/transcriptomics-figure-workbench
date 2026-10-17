"""Render explicitly supplied cloud geometry beside every raw observation.

No density estimation occurs during drawing. Small-n shapes require the same
explicit provenance as larger clouds and never replace the observation dots.
"""
import numpy as np


def draw_supplied_raincloud(ax,x,values,color,cloud,point_size=20):
    v=np.asarray(values,float)
    if v.ndim!=1 or len(v)<2 or not np.isfinite(v).all():
        raise ValueError('Rainclouds require at least two finite observations')
    if not isinstance(cloud,dict) or set(cloud)!={'grid','width','n','definition'}:
        raise ValueError('Supply frozen cloud grid, width, observation count and density definition')
    grid=np.asarray(cloud['grid'],float);width=np.asarray(cloud['width'],float)
    if (grid.ndim!=1 or width.shape!=grid.shape or not 8<=len(grid)<=1024
        or not np.isfinite(grid).all() or not np.isfinite(width).all()
        or np.any(np.diff(grid)<=0) or np.any(width<0) or width.max()<=0
        or type(cloud['n']) is not int or cloud['n']!=len(v)
        or not isinstance(cloud['definition'],str) or not cloud['definition'].strip()
        or not np.isclose(grid.min(),v.min(),rtol=0,atol=1e-9)
        or not np.isclose(grid.max(),v.max(),rtol=0,atol=1e-9)):
        raise ValueError('Cloud geometry must match its declared observation scope and observed range')
    ax.fill_betweenx(grid,x-.38*width/width.max(),x,color=color,alpha=.26,edgecolor=color,lw=.8,zorder=1)
    ax.plot(x-.38*width/width.max(),grid,c=color,lw=.85,alpha=.8,zorder=2)
    offset=.21+((np.arange(len(v))*.61803398875)%1-.5)*.15
    ax.scatter(x+offset,v,c=color,s=point_size,alpha=.78 if len(v)<30 else .35,ec='white' if len(v)<30 else 'none',lw=.45,zorder=3,rasterized=True)
    ax.boxplot([v],positions=[x+.065],widths=.085,manage_ticks=False,patch_artist=True,showfliers=False,
        boxprops=dict(fc='white',ec=color,lw=.9),medianprops=dict(color=color,lw=1.5),
        whiskerprops=dict(color=color,lw=.8),capprops=dict(color=color,lw=.8))
