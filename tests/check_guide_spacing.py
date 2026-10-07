"""Regression for dense labels and displaced explanatory text, with data intact."""
from pathlib import Path
import sys,inspect,json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'skills/transcriptomics-figure-workbench/scripts';sys.path.insert(0,str(S))
from reference_fixture import reference_fixtures
from process_fixture import process_fixture
import figure_reference as reference
from figure_process_dashboard import plot_process_dashboard
from figure_polish import plot_availability_counts
from figure_layout import optimize_guide_layout
from figure_design import geometry_signature,audit_layout


def main():
    fixtures=reference_fixtures();cases=[]
    for id_ in ('R14','R15','R16'):
        c=fixtures[id_];cases.append((id_,getattr(reference,c['function']),c['data'],c['params']))
    c=process_fixture();cases.append(('R24',plot_process_dashboard,c['data'],c['params']))
    g=ROOT/'examples/gallery';m=json.loads((g/'metadata/P32.json').read_text(encoding='utf8'))
    accepted=set(inspect.signature(plot_availability_counts).parameters)-{'data'}
    cases.append(('P32',plot_availability_counts,pd.read_csv(g/'figures/P32/P32.tsv',sep='\t'),{k:v for k,v in m['figure_spec'].items() if k in accepted}))
    for id_,fn,data,params in cases:
        original=data.copy(deep=True);f=fn(data,**params);f.canvas.draw();signature=geometry_signature(f)
        f=optimize_guide_layout(f);pd.testing.assert_frame_equal(data,original)
        assert geometry_signature(f)==signature,id_+' guide changed quantity'
        issues=[q for q in audit_layout(f)['issues'] if q['kind'] in ('heading_overlap','tick_overlap')]
        assert not issues,(id_,issues)
        size=f.get_size_inches().copy();optimize_guide_layout(f)
        assert np.allclose(f.get_size_inches(),size,atol=.01),id_+' guide optimization keeps growing'
        plt.close(f)
    print(json.dumps(dict(status='GUIDE_SPACING_PASS',cases=len(cases),all_labels_retained=True,quantitative_geometry_preserved=True)))

if __name__=='__main__':main()
