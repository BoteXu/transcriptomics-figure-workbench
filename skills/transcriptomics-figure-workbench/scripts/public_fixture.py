"""Render the exact public tables exported by public_fixture.R in Python."""
import sys
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from figure_core import plot_embedding, plot_dot, export_figure
from figure_extensions import plot_annotated_heatmap

def main(r_outputs, source, out):
    if out.exists(): raise FileExistsError('New output directory required')
    for name in ['public_embedding','public_dot','public_annotated_heatmap']:
        folder=r_outputs/name
        d=pd.read_csv(folder/(name+'.tsv'),sep='\t')
        old=json.loads((folder/(name+'.json')).read_text(encoding='utf-8'))
        keys=['source','palette','input_unit','experimental_unit','contrast','denominator','model','limits','filtering','uncertainty','interpretation_limit','synthetic']
        meta={k:old[k] for k in keys}; palette=meta['palette']
        if name=='public_embedding': fig=plot_embedding(d,palette)
        elif name=='public_dot': fig=plot_dot(d,'Mean stored RNA data across all cluster cells',value_semantics='mean_all',denominator_label='All cells in cluster')
        else: fig=plot_annotated_heatmap(d,'Mean stored RNA data',palette,{'T marker':'#8172B2','B marker':'#55A868','Myeloid marker':'#C99442','NK marker':'#B85C88'},scale_type='sequential',column_annotation_label='Cell type')
        fig.set_size_inches(10,6); fig.suptitle('PUBLIC PBMC EXAMPLE',weight='bold')
        fig.supxlabel('Renderer validation only; not project evidence',fontsize=8)
        export_figure(fig,d,out,name,meta,source_file=source,
                      expected_source_sha256='f2fecfcbc8a6360362ac45d2a68c9cd798e0ceb2e95768b2311000c71dc9ebda')
        plt.close(fig)
    print('PASS: 3 public figure bundles using exact R-exported rows; source SHA256 verified')

if __name__=='__main__': main(*map(Path,sys.argv[1:]))
