"""Risk-focused v2 checks. Only a new output directory may be used."""
import sys
import json
import hashlib
import warnings
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from figure_core import *
from figure_extensions import *

def main(out):
    if out.exists(): raise FileExistsError('New test directory required')
    out.mkdir(parents=True)
    meta=dict(source='Synthetic regression fixture',palette='Declared in figure_spec',input_unit='test rows',experimental_unit='test subjects',contrast='DEMO',denominator='eligible test rows',model='none',limits='none',filtering='none',uncertainty='supplied test bounds',interpretation_limit='software validation only',synthetic=True)
    f=pd.DataFrame(dict(label=['a','b'],estimate=[1.4,.7],lower=[1.1,.5],upper=[1.8,.9]))
    total=0
    def reject(fn, types=(ValueError,FileExistsError,TypeError)):
        nonlocal total
        try: fn()
        except types: total+=1; return
        raise AssertionError('Expected rejection')
    fig=plot_forest(f,'HR','Synthetic interval',effect_scale='ratio')
    assert fig.axes[0].get_xscale()=='log' and list(fig.axes[0].lines[0].get_xdata())==[1,1]
    reject(lambda:plot_forest(f,'HR','bounds'))
    bad=f.copy(); bad.loc[0,'lower']=0
    reject(lambda:plot_forest(bad,'HR','bounds',effect_scale='ratio'))
    reject(lambda:plot_forest(f,'HR','bounds',effect_scale='unknown'))
    reject(lambda:export_figure(fig,f,out,'bad_hash',dict(meta,input_hash='invented')))
    reject(lambda:export_figure(fig,f,out,'empty_source',dict(meta,source=' ')))
    reject(lambda:export_figure(fig,f.iloc[::-1],out,'mismatched_rows',meta))
    altered=f.copy(); altered.loc[0,'estimate']=1.5
    reject(lambda:export_figure(fig,altered,out,'mismatched_values',meta))
    source=Path(__file__).resolve(); sha=hashlib.sha256(source.read_bytes()).hexdigest()
    reject(lambda:export_figure(fig,f,out,'source_mismatch',meta,source_file=source,expected_source_sha256='0'*64))
    reject(lambda:export_figure(fig,f,out,'source_missing',meta,expected_source_sha256=sha))
    # Failure after image and table writes must not publish any part of the bundle.
    reject(lambda:export_figure(fig,f,out,'retryable',dict(meta,unserializable=object())))
    assert not (out/'retryable').exists() and not list(out.glob('.retryable*'))
    files=export_figure(fig,f,out,'retryable',meta,source_file=source,expected_source_sha256=sha)
    record=json.loads(files[4].read_text(encoding='utf-8'))
    assert record['source_file_sha256']==sha and record['input_hash']==hashlib.sha256(files[3].read_bytes()).hexdigest()
    before={p.name:p.read_bytes() for p in files}
    reject(lambda:export_figure(fig,f,out,'retryable',meta))
    assert all(p.read_bytes()==before[p.name] for p in files)
    lock=out/'.reserved.lock'; lock.write_text('another writer',encoding='utf-8')
    reject(lambda:export_figure(fig,f,out,'reserved',meta))
    assert lock.read_text()=='another writer'; lock.unlink()
    pairs=pd.DataFrame(dict(subject_id=['a','a','b'],condition=['A','B','A'],value=[1,2,3]))
    reject(lambda:plot_paired(pairs,{'A':'blue','B':'red'},['A','B'],'value'))
    e=pd.DataFrame(dict(feature=['a'],contrast=['b'],estimate=[1.],lower=[.5],upper=[1.5],padj=[0.]))
    reject(lambda:plot_effect_matrix(e,'effect',effect_scale='difference'))
    h=pd.DataFrame(dict(feature=['g','g'],sample=['s','s'],value=[1,2],sample_group=['A','B'],feature_block=['X','X']))
    reject(lambda:plot_annotated_heatmap(h,'value',{'A':'blue','B':'red'},{'X':'green'},scale_type='signed'))
    scores=pd.DataFrame(dict(feature=['x'],score_a=[.5],score_b=[.7],delta=[.3],lower_delta=[.2],upper_delta=[.4]))
    reject(lambda:plot_score_comparison(scores,'AUC',['A','B']))
    dots=pd.DataFrame(dict(feature=['g'],group=['c'],fraction=[.5],value=[1.]))
    reject(lambda:plot_dot(dots,'value',value_semantics='unknown',denominator_label='cells'))
    reject(lambda:plot_dot(dots,'value',value_semantics='mean_all',denominator_label=''))
    # Font validation rejects a silent missing-glyph fallback.
    font_manager.findfont('Microsoft YaHei',fallback_to_default=False)
    with plt.rc_context({'font.family':'Microsoft YaHei'}), warnings.catch_warnings():
        warnings.filterwarnings('error',message='Glyph .* missing from font')
        zh=pd.DataFrame(dict(sample_id=['动物甲','动物乙'],group=['对照组','处理组'],value=[1.,2.]))
        image=plot_samples(zh,{'对照组':'#35618F','处理组':'#B84E35'},'表达量（演示）')
        export_figure(image,zh,out/'中文路径','unicode',meta)
    plt.close('all')
    print(f'PASS: {total} rejection cases; ratio reference; input/source hashes; failed-export retry; existing-output preservation; Unicode path/font')

if __name__=='__main__': main(Path(sys.argv[1]))
