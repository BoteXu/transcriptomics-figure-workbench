"""Regression checks for observed row, header and guide collisions; not beauty."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))

def main(base):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from figure_workbench.pipeline import project_appearance
    from render_frozen_table import load_table,render
    manifest=json.loads((base/'manifest.json').read_text(encoding='utf8'));count=0
    for row in manifest['records']:
        p=base/(row.get('spec') or row['assets']['spec']);s=json.loads(p.read_text(encoding='utf8'))
        d=load_table(p.parent/s['input']['path'],s['renderer'],s['parameters'],s['input']['numeric_columns'])
        theme=project_appearance(s);f,_=render(s['renderer'],d,s['parameters'],theme)
        # Export adds provenance space. Inspect that real final geometry as well
        # as the renderer; axes-owned headings must follow the moved axes.
        from figure_layout import add_software_bands,optimize_guide_layout
        add_software_bands(f,s['figure_id'],theme['font_family']);optimize_guide_layout(f)
        f.canvas.draw();r=f.canvas.get_renderer()
        if s['renderer'].startswith('figure_enrichment_story'):
            a,b=f.axes[:2]
            if f._omics_spec['linked_term_rows']:
                for y in range(len(f._omics_spec['term_order'])):
                    assert abs(a.transData.transform((0,y))[1]-b.transData.transform((0,y))[1])<.01
                assert not any(x.get_visible() for x in b.get_yticklabels())
            assert sum(not p.get_fill() for p in b.patches)==int(d.loc[d.record_type=='membership','member'].sum())
            keys=[ax.get_tightbbox(r) for ax in f.axes[2:]]
            for ax in [a,b]:
                title_box=ax._left_title.get_window_extent(r)
                assert all(not title_box.overlaps(key) for key in keys),row['id']+' panel title overlaps colour key'
                assert all(not title_box.overlaps(t.get_window_extent(r)) for t in f.texts[:2]),row['id']+' caption overlaps panel title'
            for legend in f.legends:
                assert all(not legend.get_window_extent(r).overlaps(key) for key in keys),row['id']+' legend overlaps colour key'
            for i,l in enumerate(f.legends):
                assert all(not l.get_window_extent(r).overlaps(x.get_window_extent(r)) for x in f.legends[i+1:])
        else:
            if row['id'] in ['CellTypes','Evidence_12Markers_autoColumns']:
                wider=copy.deepcopy(s['parameters']);wider['panel_width']=wider.get('panel_width',3.25)*1.2
                large,_=render(s['renderer'],d,wider,theme)
                assert large.get_figwidth()>f.get_figwidth()*1.19,row['id']+' ignored panel width'
                plt.close(large)
            headings=[t for ax in f.axes for t in ax.texts if getattr(t,'_panel_heading',False)]
            assert all(t.get_fontsize()==theme['design']['title_pt'] for t in headings)
            assert f.texts[0].get_fontsize()==theme['design']['title_pt']+2
            headers=[t.get_window_extent(r) for t in f.texts[:2]]
            assert all(not a.overlaps(t.get_window_extent(r)) for a in headers for t in headings),row['id']+' header collision'
            assert not f.legends[0].get_window_extent(r).overlaps(f.axes[-1].get_tightbbox(r))
            if f._omics_spec['composition']=='evidence':
                assert abs(headings[0].get_transform().transform(headings[0].get_position())[1]-headings[1].get_transform().transform(headings[1].get_position())[1])<.01
                assert max(f.axes[i].get_position().y1 for i in range(2,len(f.axes)-1))<min(ax.get_position().y0 for ax in f.axes[:2])
                tick_boxes=[x.get_window_extent(r) for x in f.axes[1].get_xticklabels()]
                assert all(not x.overlaps(t.get_window_extent(r)) for x in tick_boxes for t in headings[2:]),row['id']+' marker tick overlaps map heading'
        plt.close(f);count+=1
    print(json.dumps(dict(status='EDITORIAL_RUNTIME_PASS',figures=count,
        checks=['exact shared term rows','one label lane for aligned panels','explicit absent/member cells',
        'non-overlapping colour and size keys','context before marker maps','theme-based heading typography'],aesthetic_approval=False)))

if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else SKILL/'assets/editorial-gallery')
