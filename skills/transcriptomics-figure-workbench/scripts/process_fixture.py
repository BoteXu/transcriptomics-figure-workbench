"""Synthetic schematic geometry; no protein coordinates or design algorithm."""
import numpy as np
import pandas as pd

def process_fixture():
    rows=[]; rng=np.random.default_rng(24)
    def r(kind,**kw): rows.append(dict(record_type=kind,**kw))
    colors=dict(Module='#9FC7D0',Accent='#BD94B8',Object='#789AB6',Backdrop='#D1D3DE',Highlight='#C71872',Paper='#FFFFFF',Stage1='#C71872',Stage2='#BD94B8',Stage3='#789AB6',Stage4='#D1D3DE')
    def node(id,x,y,w,h,text,group='Paper'): r('node',node_id=id,x=x,y=y,width=w,height=h,text=text,group=group)
    node('container',20,51,22,40,'','Backdrop'); node('module_a',27,71,12,14,'Module A','Object'); node('module_b',23,57,12,13,'Module B','Module'); node('combine',24,52,15,3,'Combined inputs','Accent')
    node('expand',17,26,77,14,'','Backdrop')
    for i,text in enumerate(['Recorded values','Provided weights','Selected records']): node(f'label{i}',19+i*24,23,19,3,text)
    for x,text in [(1,'Input A'),(1,'Input B'),(44,'Joint view'),(67,'Local view'),(85,'Retained view')]:
        y=90 if text!='Input B' else 53
        node(text,x,y,14 if x<85 else 13,4,text)
    def glyph(id,cx,cy,scale,shape,group):
        if shape=='outline':
            theta=np.linspace(0,2*np.pi,140); radius=1+.12*np.sin(9*theta)+.08*np.cos(15*theta)
            xx=cx+scale*radius*np.cos(theta); yy=cy+scale*.9*radius*np.sin(theta)
        else:
            theta=np.linspace(0,7*np.pi,140); xx=cx+scale*.62*np.sin(theta)+np.linspace(-scale*.6,scale*.6,len(theta)); yy=cy+np.linspace(-scale,scale,len(theta))+.5*np.cos(theta)
        for i,(x,y) in enumerate(zip(xx,yy)): r('path',object_id=id,order=i,x=x,y=y,group=group,shape=shape)
    glyph('input1',8,79,6,'ribbon','Accent'); glyph('input2',8,64,5,'outline','Object')
    for i,cx in enumerate([51,73,92]):
        glyph(f'target{i}',cx,69,7 if i!=1 else 4.5,'outline','Object'); glyph(f'ribbon{i}',cx-1,79,6,'ribbon','Accent')
        glyph(f'highlight{i}',cx+1,75,1.6,'ribbon','Highlight')
    for i,cx in enumerate([7,22,37,52,67]):
        glyph(f'candidate_target{i}',cx,18,3.6,'outline','Object'); glyph(f'candidate_ribbon{i}',cx,22,3.2,'ribbon','Accent'); node(f'candidate_label{i}',cx-5,11,10,2.5,f'Object {i+1}')
    for i,(x0,y0,x1,y1,style) in enumerate([(15,79,26,79,'solid'),(14,64,22,64,'dashed'),(39,78,46,78,'solid'),(57,78,65,78,'dashed'),(79,78,85,78,'solid'),(32,72,30,69,'dotted'),(39,73,39,54,'dotted'),(42,54,57,40,'solid')]): r('edge',edge_id=f'E{i}',x0=x0,y0=y0,x1=x1,y1=y1,line_style=style)
    for m in range(3):
        for row in range(5):
            for col in range(13): r('matrix',matrix_id=m,row=row,column=col,value=float(rng.uniform(.05,.9)))
    for i,s in enumerate(['Surface A','Surface B','Combined surface']):
        centers=[(-.6,.4),(.6,-.4)]
        for y in np.linspace(-2,2,31):
            for x in np.linspace(-2,2,31):
                value=sum((1.4 if (k==i or i==2) else .65)*np.exp(-((x-c[0])**2+(y-c[1])**2)/(.12 if i==2 else .19)) for k,c in enumerate(centers))
                r('surface',surface_id=s,x=float(x),y=float(y),z=float(value))
        for k,(x,y) in enumerate(centers):
            z=sum((1.4 if (j==i or i==2) else .65)*np.exp(-((x-c[0])**2+(y-c[1])**2)/(.12 if i==2 else .19)) for j,c in enumerate(centers))
            r('landmark',surface_id=s,landmark=f'L{k}',x=x,y=y,z=z,group='Module' if k==0 else 'Highlight')
    for bg,n in [('Group A',4),('Group B',2)]:
        for i in range(n):
            for j,stage in enumerate(['Stage1','Stage2','Stage3','Stage4']): r('count',bar_group=bg,category=f'C{i+1}',stage=stage,value=float(rng.integers(2,24)))
    return dict(data=pd.DataFrame(rows),function='plot_process_dashboard',params=dict(palette=colors,surface_order=['Surface A','Surface B','Combined surface'],bar_group_order=['Group A','Group B'],stage_order=['Stage1','Stage2','Stage3','Stage4'],geometry_label='Illustrative geometry only; replace with rendered PDB/mmCIF panels for real structures',count_label='Recorded count'))
