"""Small frozen fixtures; no random generation, fitting or scientific inference."""
import csv
import copy
import json
from pathlib import Path


def create_fixtures(directory,skill):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    theme=json.loads((skill/'references/project-theme-example.json').read_text(encoding='utf8'))
    theme['project_id']='synthetic-workbench-v030';theme['font_family']='DejaVu Sans'
    theme['group_slots']={'G1':0,'G2':6}
    meta={k:'SYNTHETIC DEMO frozen fixture; no scientific claim' for k in
          ['source','input_unit','experimental_unit','contrast','denominator','model','limits','filtering','uncertainty','interpretation_limit']}
    meta['synthetic']=True
    palette={'G1':'#506AAA','G2':'#E17692'}
    cases={
        'ma':('qc_de',[{'feature_id':'g1','effect':-1.2,'average':3,'status':'down'},
                       {'feature_id':'g2','effect':.1,'average':4,'status':'untested'},
                       {'feature_id':'g3','effect':.4,'average':5,'status':'other'},
                       {'feature_id':'g4','effect':1.4,'average':6,'status':'up'}],
              {'mode':'ma','contract':{'source_definition':'supplied synthetic results','independent_unit':'synthetic donor',
                 'denominator':'all four fixture features','effect_definition':'supplied log2 contrast','status_definition':'supplied upstream status',
                 'feature_selection':'all frozen fixture rows','average_definition':'supplied average log2 expression'}}),
        'rank':('rank_bump',[{'group':g,'stage':s,'rank':v} for g,values in [('G1',[1,2,1]),('G2',[2,1,2])] for s,v in zip(['S1','S2','S3'],values)],
                {'stage_order':['S1','S2','S3'],'title':'Supplied ranks'}),
        'paired':('paired',[{'subject_id':u,'condition':g,'value':v} for u,values in [('001',[1.,1.4]),('002',[1.5,1.2]),('003',[1.2,1.7])] for g,v in zip(['G1','G2'],values)],
                  {'palette':palette,'condition_order':['G1','G2'],'y_label':'Supplied measurement'}),
        'curve':('frozen_curve',[{'model':g,'x':x,'y':y} for g,ys in [('G1',[0,.6,.85,1]),('G2',[0,.4,.75,1])] for x,y in zip([0,.2,.6,1],ys)],
                 {'palette':palette,'curve_type':'ROC','labels':{'G1':'G1 · stored curve','G2':'G2 · stored curve'},'title':'Frozen ROC coordinates'}),
        'forest':('forest',[{'label':'Estimate A','group':'G1','estimate':.4,'lower':.1,'upper':.7},
                           {'label':'Estimate B','group':'G2','estimate':-.2,'lower':-.5,'upper':.1}],
                  {'palette':palette,'x_label':'Supplied difference','interval_label':'Supplied 95% CI','effect_scale':'difference','title':'Frozen effects'}),
        'matrix':('heatmap',[{'feature':f,'sample':s,'value':v} for f,vs in [('F1',[-1,.4]),('F2',[.7,-.3]),('F3',[0,1])] for s,v in zip(['G1','G2'],vs)],
                  {'value_label':'Supplied signed score','scale_type':'signed'}),
    }
    result={}
    for name,(renderer,records,params) in cases.items():
        table=directory/(name+'.tsv')
        with table.open('w',encoding='utf8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(records[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(records)
        spec={'schema_version':1,'figure_id':'WB_'+name,'renderer':renderer,'input':{'path':table.name},
              'theme':copy.deepcopy(theme),'parameters':params,'provenance':copy.deepcopy(meta),'appearance':{'preset':'paper'}}
        if name=='matrix':spec['export']={'raster_dpi':600,'tiff':True}
        result[name]=spec
        (directory/(name+'.spec.json')).write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
    return result
