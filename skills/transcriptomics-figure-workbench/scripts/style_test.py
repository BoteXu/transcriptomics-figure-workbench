"""Synthetic software fixtures for optional styles, not biological findings.

Usage: python style_test.py NEW_OUTPUT_DIRECTORY
R counterpart reads the generated _input directory for matching fixtures.
"""
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_core import export_figure, plot_volcano, plot_samples, plot_composition, file_sha256
from figure_styles import (plot_volcano_editorial, plot_volcano_marginal, plot_enrichment_lollipop,
                           plot_composition_panels, plot_sample_distribution)

def main(out):
    out.mkdir(parents=True, exist_ok=False); inputs=out/'_input'; inputs.mkdir()
    rng=np.random.default_rng(260926)
    volcano=pd.DataFrame({'gene':[f'Gene{i:03d}' for i in range(360)],
                         'log2FC':rng.normal(0,1.25,360),'padj':10**(-rng.uniform(.02,4.5,360))})
    focal=['Gene003','Gene018','Gene045','Gene067','Gene120','Gene200']
    for i,(fc,padj) in zip([3,18,45,67,120,200],[(-2.6,1e-5),(-1.9,2e-4),(-2.9,8e-4),(2.5,2e-5),(1.8,5e-4),(3.1,8e-5)]):
        volcano.loc[i,['log2FC','padj']]=[fc,padj]
    samples=pd.DataFrame({'sample_id':[f'S{i:02d}' for i in range(20)],
                          'group':['Control']*10+['Condition']*10,
                          'value':np.r_[rng.normal(3.7,.65,10),rng.normal(4.5,.85,10)]})
    types=['T cells','B cells','Monocytes','NK cells','Dendritic cells','Other cells']
    rows=[]
    for i in range(12):
        counts=rng.multinomial(800+i*40, [.36,.18,.21,.14,.06,.05] if i<6 else [.28,.16,.28,.18,.05,.05])
        rows.extend({'sample':f'D{i:02d}','group':'Control' if i<6 else 'Condition',
                     'celltype':ct,'count':int(n)} for ct,n in zip(types,counts))
    composition=pd.DataFrame(rows)
    terms=['Inflammatory response','Extracellular matrix organization','Oxidative phosphorylation',
           'Interferon response','Fatty acid metabolism','Leukocyte migration','Angiogenesis','Calcium signaling']
    enrichment=pd.DataFrame({'term':terms,'score':[.22,.18,.17,.15,.14,.12,.10,.08],
                             'padj':[.0002,.001,.003,.009,.014,.032,.09,.18],
                             'count':[44,36,34,30,28,24,20,16]})
    nes=enrichment.copy(); nes['score']=[2.2,1.8,-1.9,1.5,-1.6,1.2,.9,-.8]
    tables={'volcano':volcano,'samples':samples,'composition':composition,'enrichment':enrichment,'nes':nes}
    for name,tab in tables.items(): tab.to_csv(inputs/(name+'.tsv'),sep='\t',index=False)
    pal={'Control':'#35618F','Condition':'#B84E35'}
    cellpal=dict(zip(types,['#35618F','#67A9A2','#B84E35','#C9A64B','#857AA8','#AAB4BD']))
    meta=dict(source='Deterministic synthetic style_test.py fixtures, seed 260926',
              palette='Explicit renderer maps in figure_spec',input_unit='synthetic reviewed-table schema',
              experimental_unit='synthetic sample IDs; no experimental evidence',contrast='synthetic demonstration only',
              denominator='all supplied rows per declared sample; enrichment 200 query genes for ratio fixture',
              model='none; frozen illustrative numbers',limits='all supplied values displayed',
              filtering='no automatic selection; six named volcano labels only',uncertainty='no CI; distribution rectangle is Q1-Q3',
              interpretation_limit='Software and layout test only; no biological or clinical claim',synthetic=True)
    jobs=[('a_volcano_basic',volcano,lambda:plot_volcano(volcano)),
          ('b_volcano_editorial',volcano,lambda:plot_volcano_editorial(volcano,labels=focal)),
          ('b2_volcano_marginal',volcano,lambda:plot_volcano_marginal(volcano,labels=focal)),
          ('c_samples_basic',samples,lambda:plot_samples(samples,pal,'Illustrative log2 CPM')),
          ('d_sample_distribution',samples,lambda:plot_sample_distribution(samples,pal,'Illustrative log2 CPM')),
          ('e_composition_basic',composition,lambda:plot_composition(composition,cellpal)),
          ('f_composition_panels',composition,lambda:plot_composition_panels(composition,pal,unit_label='synthetic sample',y_max=.5)),
          ('g_enrichment_ratio',enrichment,lambda:plot_enrichment_lollipop(enrichment,score_type='GeneRatio',denominator_label='ORA example | 200 query genes; fixed supplied terms',count_label='Overlap genes')),
          ('h_enrichment_NES',nes,lambda:plot_enrichment_lollipop(nes,score_type='NES',denominator_label='GSEA example | supplied ranking and sets',count_label='Leading-edge genes'))]
    for name,tab,fun in jobs:
        fig=fun(); paths=export_figure(fig,tab,out,name,meta); plt.close(fig)
        assert len(paths)==6
        rec=json.loads((out/name/(name+'.json')).read_text())
        assert all(file_sha256(out/name/file)==sha for file,sha in rec['output_sha256'].items())
    # Observable invariants, not just labels: original x/y and proportions survive.
    fig=plot_volcano_editorial(volcano,labels=focal)
    plotted=np.concatenate([c.get_offsets() for c in fig.axes[0].collections[:3]])
    expected=np.c_[volcano.log2FC,-np.log10(volcano.padj)]
    assert np.allclose(plotted[np.lexsort(plotted.T)],expected[np.lexsort(expected.T)])
    circle_paths=[c.get_paths()[0] for c in fig.axes[0].collections[:3]]
    assert all(np.array_equal(p.vertices,circle_paths[0].vertices) for p in circle_paths[1:])
    plt.close(fig)
    fig=plot_volcano_marginal(volcano,labels=focal)
    main=fig._omics_axes['main']
    plotted=np.concatenate([c.get_offsets() for c in main.collections[:3]])
    assert np.allclose(plotted[np.lexsort(plotted.T)],expected[np.lexsort(expected.T)])
    assert fig._omics_spec['point_count']==len(volcano)
    assert sum(fig._omics_spec['status_counts'].values())==len(volcano)
    assert len(fig._omics_axes['top_histogram'].patches)>0
    assert len(fig._omics_axes['right_histogram'].patches)>0
    plt.close(fig)
    fig=plot_composition_panels(composition,pal,unit_label='synthetic sample')
    for ax,ct in zip(fig.axes,types):
        actual=np.concatenate([c.get_offsets()[:,1] for c in ax.collections])
        z=composition[composition.celltype==ct]
        totals=composition.groupby('sample')['count'].sum()
        assert np.allclose(actual,z['count'].to_numpy()/totals.loc[z['sample']].to_numpy())
    plt.close(fig)
    small=samples.iloc[:3]; fig=plot_sample_distribution(small,pal,'value')
    assert len(fig.axes[0].patches)==0; plt.close(fig)
    negatives=[lambda:plot_volcano_editorial(volcano,labels=['missing']),
               lambda:plot_volcano_editorial(volcano,labels=[focal[0]]*2),
               lambda:plot_volcano_editorial(volcano.assign(padj=0)),
               lambda:plot_volcano_editorial(volcano,fc=0),
               lambda:plot_enrichment_lollipop(enrichment,score_type='unknown',denominator_label='x',count_label='n'),
               lambda:plot_enrichment_lollipop(enrichment.assign(score=2),score_type='GeneRatio',denominator_label='x',count_label='n'),
               lambda:plot_enrichment_lollipop(enrichment.assign(count=.5),score_type='NES',denominator_label='x',count_label='n'),
               lambda:plot_enrichment_lollipop(enrichment,score_type='NES',denominator_label='',count_label='n'),
               lambda:plot_composition_panels(composition.iloc[1:],pal,unit_label='sample'),
               lambda:plot_composition_panels(composition.assign(count=0),pal,unit_label='sample'),
               lambda:plot_composition_panels(composition,pal,unit_label='sample',y_max=.1),
               lambda:plot_composition_panels(composition.assign(group=['Control']+['Condition']*(len(composition)-1)),pal,unit_label='sample'),
               lambda:plot_sample_distribution(pd.concat([samples,samples.iloc[:1]]),pal,'value'),
               lambda:plot_sample_distribution(samples,{'Control':'#35618F'},'value')]
    for fun in negatives:
        try: fun()
        except (ValueError, KeyError): pass
        else: raise AssertionError('Invalid input was accepted')
    print('PASS: 9 style/baseline bundles; 14 rejected inputs; exact volcano coordinates and composition fractions; small-n no-IQR; SHA256 verified')

if __name__=='__main__': main(Path(sys.argv[1]))
