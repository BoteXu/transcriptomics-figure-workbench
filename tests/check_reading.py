"""Small bounded PDF execution, coverage, path binding and stale-plan checks."""
from pathlib import Path
import copy,json,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.reading import make_reading_plan,export_reading,_positions

def refused(call):
    try:call()
    except (ValueError,TypeError,KeyError,FileNotFoundError):return
    raise AssertionError('Unbound reading plan accepted')

def main():
    for length,cap in [(20,500),(501,500),(5000,500),(920,650)]:
        xs=_positions(length,cap);assert xs[0]==0 and xs[-1]+cap>=length-.01
        assert all(b-a<=cap for a,b in zip(xs,xs[1:]))
    full=json.loads((ROOT/'examples/review-v060/review-index.json').read_text())
    with tempfile.TemporaryDirectory(prefix='figure-reading-test-') as tmp:
        tmp=Path(tmp);index=tmp/'index.json';selected=[r for r in full['records'] if r['id'] in ['REF04','T19']]
        assert len(selected)==2;data=dict(records=selected);index.write_text(json.dumps(data))
        plan=make_reading_plan(index,ROOT,volume_size=1)
        for mutate in [lambda p:p.update(width_mm=True),lambda p:p.update(minimum_text_pt=float('nan')),lambda p:p.update(volume_size=0)]:
            p=copy.deepcopy(plan);mutate(p);refused(lambda:export_reading(p,tmp/'bad'))
        bad=copy.deepcopy(data);bad['records'][0]['assets']['pdf']='../outside.pdf';index.write_text(json.dumps(bad));refused(lambda:make_reading_plan(index,ROOT))
        index.write_text(json.dumps(data));plan=make_reading_plan(index,ROOT,volume_size=1);result=export_reading(plan,tmp/'pdfs')
        from pypdf import PdfReader
        assert result['figures']==2 and result['full_region_coverage'] and not result['visual_acceptance']
        for volume in result['volumes']:
            with PdfReader(tmp/'pdfs'/volume['file']) as reader:
                assert len(reader.pages)==volume['pages']
                for page in reader.pages:assert page.get_contents().get_data()
        for row in result['records']:
            assert row['detail_body_minimum_pt']>=7.5-1e-6
            assert row['xs'][-1]+178*72/25.4>=row['width_pt']*row['scale']-.01
        index.write_text(json.dumps(data)+' ');refused(lambda:export_reading(plan,tmp/'stale'))
    print(json.dumps(dict(status='READING_RUNTIME_PASS',figures=2,path_and_stale_rejection=True,uniform_coverage=True,decoded_streams=True,scientific_acceptance=False,visual_acceptance=False)))
if __name__=='__main__':main()
