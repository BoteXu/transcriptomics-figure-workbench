"""Conserved path geometry, independent of plotting and page orientation.

Rows describe the same cohort/path across stages. Pairwise associations or
overlapping memberships do not satisfy this input contract.
"""
import math
import numpy as np
from figure_core import checked


def layout_paths(data, stage_columns, *, stage_orders=None, path_order=None,
                 gap_fraction=.045, path_field='path_id', weight_field='weight'):
    stages=list(stage_columns)
    if (len(stages)<2 or len(stages)!=len(set(stages)) or
            any(not isinstance(c,str) or not c.strip() for c in stages) or
            len(set(stages+[path_field,weight_field]))!=len(stages)+2):
        raise ValueError('Declare at least two distinct stage columns and separate ID/weight fields')
    if not np.isfinite(gap_fraction) or gap_fraction<0:
        raise ValueError('gap_fraction must be finite and nonnegative')
    d=checked(data,[path_field,weight_field]+stages,[weight_field])
    for col in [path_field]+stages:
        if any(not isinstance(v,str) or not v.strip() for v in d[col]):
            raise ValueError('Path and category IDs must be nonempty strings; preserve their exact spelling')
    if d[path_field].duplicated().any() or (d[weight_field]<0).any():
        raise ValueError('Unique path IDs and nonnegative weights required')
    try: total=math.fsum(d[weight_field])
    except OverflowError as e: raise ValueError('Total weight exceeds finite numeric range') from e
    if not math.isfinite(total) or total<=0:
        raise ValueError('At least one positive finite path weight is required')
    if stage_orders is not None and set(stage_orders)!=set(stages):
        raise ValueError('stage_orders must cover every stage exactly')
    orders={}
    for col in stages:
        observed=list(d[col].unique())
        order=list(stage_orders[col]) if stage_orders is not None else observed
        if len(order)!=len(set(order)) or set(order)!=set(observed):
            raise ValueError('Each stage order must contain every category exactly once')
        orders[col]=order
    records=d.to_dict('records')
    if path_order is not None:
        path_order=list(path_order)
        if len(path_order)!=len(set(path_order)) or set(path_order)!=set(d[path_field]):
            raise ValueError('path_order must contain every path ID exactly once')
        ranks={v:i for i,v in enumerate(path_order)}
        records.sort(key=lambda r:ranks[r[path_field]])
    else:
        ranks={c:{v:i for i,v in enumerate(orders[c])} for c in stages}
        records.sort(key=lambda r:tuple(ranks[c][r[c]] for c in stages)+(r[path_field],))
    gap=total*gap_fraction; nodes=[]; slots={}; extents=[]
    for j,col in enumerate(stages):
        cursor=0.
        for group in orders[col]:
            members=[r for r in records if r[col]==group]
            weight=math.fsum(r[weight_field] for r in members)
            start=cursor; boundaries=[start]
            for r in members:
                end=start+float(r[weight_field])
                if r[weight_field]>0 and end<=start:
                    raise ValueError('Weight precision cannot represent a positive band; rescale weights explicitly')
                slots[(r[path_field],j)]=(start,end)
                boundaries.append(end);start=end
            if not math.isclose(start-cursor,weight,rel_tol=1e-12,abs_tol=total*1e-14):
                raise ValueError('Accumulated geometry does not conserve node weight')
            nodes.append(dict(stage=col,stage_index=j,category=group,lo=cursor,hi=start,
                              weight=weight,path_ids=[r[path_field] for r in members]))
            cursor=start+gap
        extents.append(cursor-gap)
    segments=[]
    for r in records:
        for j in range(len(stages)-1):
            a,b=slots[(r[path_field],j)],slots[(r[path_field],j+1)]
            segments.append(dict(path_id=r[path_field],stage_index=j,source=r[stages[j]],
                                 target=r[stages[j+1]],weight=float(r[weight_field]),
                                 source_interval=list(a),target_interval=list(b)))
    return dict(total=total,gap=gap,extent=max(extents),stages=stages,stage_orders=orders,
                path_order=[r[path_field] for r in records],nodes=nodes,segments=segments,
                zero_paths=[r[path_field] for r in records if r[weight_field]==0],
                path_field=path_field,weight_field=weight_field)
