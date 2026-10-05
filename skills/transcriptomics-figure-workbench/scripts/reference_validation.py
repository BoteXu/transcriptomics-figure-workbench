"""Risk-based input, semantics and export checks using synthetic fixtures."""
from pathlib import Path
import json,sys,hashlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import figure_reference as render
import figure_process_dashboard as process
from reference_fixture import reference_fixtures
from figure_core import export_figure,table_bytes,file_sha256
from figure_reference_palettes import category_map,get_palette

def main(out):
    out=Path(out)
    if out.exists(): raise FileExistsError('Fresh validation directory required')
    out.mkdir(parents=True); examples=reference_fixtures(); results=[]
    def rejected(label,fn):
        try: fn()
        except (ValueError,FileExistsError,TypeError,KeyError) as e: results.append(dict(test=label,status='REJECTED_AS_EXPECTED',exception=type(e).__name__))
        else: raise AssertionError('Unsafe input accepted: '+label)
        finally: plt.close('all')
    def case(id,label,change):
        e=examples[id]; d=e['data'].copy(); params=e['params'].copy(); change(d,params)
        mod=render if hasattr(render,e['function']) else process
        rejected(label,lambda:getattr(mod,e['function'])(d,**params))
    def setfirst(d,kind,column,value): d.loc[d[d.record_type==kind].index[0],column]=value
    case('R01','Negative secondary area',lambda d,p:setfirst(d,'profile','area',-1))
    case('R01','Primary value outside declared radius',lambda d,p:setfirst(d,'profile','value',9000))
    case('R03','Negative evidence magnitude',lambda d,p:setfirst(d,'effect','evidence',-1))
    case('R04','Non-integer recorded counts',lambda d,p:setfirst(d,'count','value',2.5))
    case('R04','Detection fraction above one',lambda d,p:setfirst(d,'marker','fraction',1.1))
    case('R05','Correlation above one',lambda d,p:setfirst(d,'correlation','r',1.1))
    case('R06','Self edge',lambda d,p:setfirst(d,'edge','b',d[d.record_type=='edge'].a.iloc[0]))
    case('R07','p outside probability range',lambda d,p:setfirst(d,'mantel','p',1.1))
    case('R07','Undeclared p convention',lambda d,p:p.update(p_type='unknown'))
    case('R08','Nonfinite coordinate',lambda d,p:setfirst(d,'point','x',np.inf))
    case('R09','Mismatched trial score',lambda d,p:setfirst(d,'trial','score',.999))
    case('R10','Feature color outside declared display scale',lambda d,p:setfirst(d,'contribution','feature_value',-1))
    case('R11','Contribution share not summing to one',lambda d,p:setfirst(d,'share','value',.99))
    case('R12','Invalid box order',lambda d,p:setfirst(d,'box','q1',9000))
    case('R13','Reversed fit interval',lambda d,p:setfirst(d,'fit','lower',9000))
    case('R14','Nonpositive logarithmic bound',lambda d,p:setfirst(d,'gradient','lower',0))
    case('R15','Missing matrix cell',lambda d,p:d.drop(d[d.record_type=='matrix'].index[0],inplace=True))
    case('R16','Interval excluding estimate',lambda d,p:setfirst(d,'summary','upper',-9))
    case('R17','Duplicated unit',lambda d,p:setfirst(d,'observation','unit_id',d[d.record_type=='observation'].unit_id.iloc[1]))
    case('R18','Nonpositive ellipse width',lambda d,p:setfirst(d,'ellipse','width',0))
    case('R20','Missing faceted grid cell',lambda d,p:d.drop(d.index[0],inplace=True))
    case('R21','Invalid adjusted p',lambda d,p:setfirst(d,'effect','padj',-1))
    case('R22','Noninteger counts',lambda d,p:setfirst(d,'count','value',.3))
    case('R23','Missing surface cell',lambda d,p:d.drop(d.index[0],inplace=True))
    case('R24','Unknown line style',lambda d,p:setfirst(d,'edge','line_style','invented'))
    case('R24','Unknown surface landmark',lambda d,p:setfirst(d,'landmark','surface_id','Missing'))
    rejected('Wrong palette semantics',lambda:get_palette('card_01',semantic='diverging'))
    rejected('Category colors never cycle',lambda:category_map('card_01',list('ABCDEFG')))
    rejected('Duplicate categories',lambda:category_map('card_01',['A','A']))
    assert hashlib.sha256(table_bytes(examples['R01']['data'])).hexdigest()==hashlib.sha256(table_bytes(examples['R02']['data'])).hexdigest()
    assert table_bytes(examples['R18']['data'])==table_bytes(examples['R19']['data'])
    results.extend([dict(test='R01/R02 same frozen data',status='PASS'),dict(test='R18/R19 same frozen data',status='PASS')])
    e=examples['R23']; data=e['data']; fig=render.plot_surface_grid(data,**e['params']); source=out/'input.tsv'; source.write_bytes(table_bytes(data))
    meta=dict(source='Synthetic test fixture',palette='surface_terrain',input_unit='frozen grid rows',experimental_unit='synthetic',contrast='demo',denominator='complete grid',model='none',limits='declared',filtering='none',uncertainty='none',interpretation_limit='software only',synthetic=True)
    files=export_figure(fig,data,out/'bundles','VALID',meta,source_file=source,expected_source_sha256=file_sha256(source))
    rejected('Refuse overwrite existing output',lambda:export_figure(fig,data,out/'bundles','VALID',meta))
    changed=data.copy(); changed.loc[0,'z']+=1
    rejected('Changed table after plot',lambda:export_figure(fig,changed,out/'bundles','TAMPER',meta))
    rejected('Caller forged input hash',lambda:export_figure(fig,data,out/'bundles','FORGED',dict(meta,input_hash='forged')))
    (out/'receipt.json').write_text(json.dumps(dict(status='SOFTWARE_CHECKS_PASS',checks=results,render_acceptance='separate visual review; no scientific validation'),indent=2),encoding='utf8')
    print(len(results),'risk checks passed')

if __name__=='__main__': main(sys.argv[1])
