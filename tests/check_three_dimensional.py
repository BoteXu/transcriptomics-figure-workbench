"""Independent display invariants for XYZ, ray compositing and stored frames."""
import copy,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(S/'scripts'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from figure_three_dimensional import composite_volume,_volume,_trajectory,plot_scatter3d,plot_molecular_trajectory
from project_theme import create_theme


def reject(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('Malformed drawing input accepted')


def main():
    axes=[np.array([0.,1.])]*3;knots=np.array([0.,1.]);colors=np.array([[1.,0.,0.],[0.,0.,1.]]);opacity=np.array([.5,.5])
    grid=np.zeros((2,2,2));grid[:,:,1]=1
    front=composite_volume(grid,axes,knots,colors,opacity,'z+',1)
    back=composite_volume(grid,axes,knots,colors,opacity,'z-',1)
    # Two layers: front red/blue alpha=.5, plus .25 white background.
    np.testing.assert_allclose(front,np.broadcast_to([.75,.25,.5],(2,2,3)))
    np.testing.assert_allclose(back,np.broadcast_to([.5,.25,.75],(2,2,3)))
    np.testing.assert_allclose(composite_volume(grid,axes,knots,colors,np.zeros(2),'z+',1),1)
    homogeneous=np.zeros((2,2,2));spaced=[np.array([0.,2.])]*3
    np.testing.assert_allclose(composite_volume(homogeneous,spaced,knots,colors,opacity,'z+',1),np.broadcast_to([1.,.0625,.0625],(2,2,3)))
    voxels=pd.DataFrame([dict(x=i,y=j,z=k,value=.25) for i in range(2) for j in range(2) for k in range(2)])
    transfer=[dict(value=0,color='#FFFFFF',opacity=0),dict(value=1,color='#008080',opacity=.6)]
    reject(lambda:_volume(voxels.iloc[:-1],[0,1],transfer));reject(lambda:_volume(pd.concat([voxels,voxels.iloc[:1]]),[0,1],transfer))
    reject(lambda:_volume(voxels,[0,.1],transfer));reject(lambda:composite_volume(grid,axes,knots,colors,opacity,'diagonal',1))
    theme=create_theme('synthetic-3d-regression','package_editorial',{'A':0,'B':1},font_family='DejaVu Sans')
    points=pd.DataFrame(dict(object_id=['1','2','3'],group=['A','B','A'],x=[1.,2.,3.],y=[4.,5.,6.],z=[7.,8.,9.]))
    original=points.copy(deep=True)
    fig=plot_scatter3d(points,theme,axis_labels=['X','Y','Z'],coordinate_unit='mm',coordinate_definition='Supplied coordinates',views=[(20,-45)],include_projections=True,columns=1)
    xyz=fig.axes[0].collections[0]._offsets3d
    np.testing.assert_allclose(xyz[2],[7.,9.]);pd.testing.assert_frame_equal(points,original)
    assert len(fig.axes)==4 and fig._responsive_facets['columns']==1;plt.close(fig)
    reject(lambda:plot_scatter3d(pd.concat([points,points.iloc[:1]]),theme,axis_labels=['X','Y','Z'],coordinate_unit='mm',coordinate_definition='Supplied coordinates'))
    atoms=pd.DataFrame([dict(record_type='atom',frame_id=f'F{f}',time=float(f),atom_id=str(a),element='C',chain='A',x=float(a),y=float(f),z=0.) for f in range(3) for a in range(2)])
    frames=['F0','F1','F2'];_,coordinates,times,bonds=_trajectory(atoms,frames)
    np.testing.assert_allclose(coordinates[:,0,1],[0,1,2]);np.testing.assert_allclose(times,[0,1,2]);assert bonds==[]
    reject(lambda:_trajectory(atoms.iloc[:-1],frames));reject(lambda:_trajectory(atoms,list(reversed(frames))))
    bad=atoms.copy();bad.loc[bad.frame_id=='F1','element']='N';reject(lambda:_trajectory(bad,frames))
    from PIL import Image
    fig=plot_molecular_trajectory(atoms,theme,frame_order=frames,coordinate_unit='Å',time_unit='ps',topology_definition='No explicit bonds',coordinate_definition='Stored fixture',periodic_boundary_handling='Nonperiodic fixture',columns=1)
    with tempfile.TemporaryDirectory() as tmp:
        paths=fig._workbench_animation_writer(tmp,'frames',synthetic=True)
        with Image.open(Path(tmp)/'frames.gif') as im:assert im.n_frames==3
        meta=json.loads((Path(tmp)/'frames.animation.json').read_text());assert meta['times']==[0,1,2] and not meta['coordinates_refit']
        html=(Path(tmp)/'frames.html').read_text();assert 'id="frame"' in html and 'connect-src' in html
    plt.close(fig)
    # Exercise the real export hook and bind animation hashes, rather than
    # treating a standalone writer call as pipeline acceptance.
    from figure_workbench.contracts import make_plan
    from figure_workbench.pipeline import render_plan
    import hashlib
    sample=S/'assets/method-upgrade-gallery/D03_Trajectory_Small'
    spec=json.loads((sample/'example.spec.json').read_text(encoding='utf8'))
    with tempfile.TemporaryDirectory() as tmp:
        receipt=render_plan(make_plan(spec,sample),tmp)
        bundle=Path(tmp)/spec['figure_id'];record=json.loads((bundle/(spec['figure_id']+'.json')).read_text(encoding='utf8'))
        assert len(record['workbench']['animation_exports'])==3
        for name in record['workbench']['animation_exports']:
            assert record['output_sha256'][name]==hashlib.sha256((bundle/name).read_bytes()).hexdigest()
        with Image.open(bundle/(spec['figure_id']+'.gif')) as im:assert im.n_frames==6
        assert receipt['inference_performed'] is False
    print('THREE_DIMENSIONAL_COORDINATES_COMPOSITING_AND_PLAYBACK_PASS')


if __name__=='__main__':main()
