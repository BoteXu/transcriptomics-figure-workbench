"""Community-informed display comparisons from the same existing synthetic sources."""
from pathlib import Path
import argparse,copy,csv,json,sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench';sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.contracts import make_plan
from figure_workbench.pipeline import render_plan
from figure_workbench.registry import digest
from project_theme import create_theme

def read(p):
    with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def build(output):
    output.mkdir(exist_ok=False,parents=True);inputs=output/'inputs';inputs.mkdir();cases=[]
    for k,key in [('REF01','PKG01'),('REF02','PKG03')]:
        spec=json.loads((ROOT/'examples/package-v040/inputs'/(key+'.spec.json')).read_text(encoding='utf8'));o=spec['parameters']['options'];source=ROOT/'examples/package-v040'/key/(key+'.tsv')
        options={f:o[f] for f in ['curve_order','ranked_universe','metric_label','contrast','gene_set_version']};options['title']='Enrichment in compact aligned tracks'
        options['line_encoding']='rank_metric' if key=='PKG01' else 'pathway'
        cases.append((k,'gsea_strip',read(source),options,source,'complete selected GSEA export'))
    source=ROOT/'examples/gallery/figures/R14/R14.tsv';rows=read(source);selected=[r for r in rows if r['record_type']=='loss'];curves=[dict(series=r['series'],x=r['epoch'],estimate=r['value'],lower=r['lower'],upper=r['upper']) for r in selected]
    cases.append(('REF03','ribbon',curves,dict(series_order=list(dict.fromkeys(r['series'] for r in curves)),interval_definition='Illustrative supplied display bands; probability meaning unspecified',x_label='Epoch',y_label='Loss',title='Training curves with supplied interval bands',subtitle='Same loss rows as R14 / no model training'),source,'all 240 loss rows; other dashboard record types excluded explicitly'))
    source=ROOT/'examples/gallery/figures/P22/P22.tsv';rows=read(source)
    cases.append(('REF04','score_shift',rows,dict(feature_order=[r['feature'] for r in rows],label_a='Score A',label_b='Score B',score_label='Supplied score',difference_label='B minus A',interval_definition='Supplied difference bounds; no new inference',title='Score comparison and change uncertainty',subtitle='Same features, scores and difference intervals as P22'),source,'all rows'))
    source=ROOT/'examples/gallery/figures/R07/R07.tsv';rows=read(source);names=list(dict.fromkeys([r['a'] for r in rows if r['record_type']=='correlation']+[r['b'] for r in rows if r['record_type']=='correlation']))
    cases.append(('REF05','association',rows,dict(variable_order=names,specimen_order=list(dict.fromkeys(r['specimen'] for r in rows if r['record_type']=='mantel')),correlation_label='Pairwise r',title='Associations without crossing edges',subtitle='Same pairwise and Mantel summaries as R07 / distinct measures'),source,'all 91 pairwise and 56 Mantel summaries'))
    records=[];template=json.loads((ROOT/'examples/design-v050/inputs/VIS02.spec.json').read_text(encoding='utf8'))
    for key,view,rows,options,source,selection in cases:
        p=inputs/(key+'.tsv');columns=list(dict.fromkeys(k for r in rows for k in r))
        with p.open('x',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=columns,delimiter='\t');w.writeheader();w.writerows(rows)
        spec=copy.deepcopy(template);spec.update(figure_id=key,renderer='refined',input=dict(path=p.name,sha256=digest(p)));spec['parameters']=dict(view=view,options=options,contract=copy.deepcopy(template['parameters']['contract']))
        categories=list(dict.fromkeys(r[k] for r in rows for k in ['pathway','series'] if r.get(k)))
        if view=='score_shift':categories=[options['label_a'],options['label_b']]
        if not categories:categories=['Supplied associations']
        spec['theme']=create_theme('synthetic-refined-'+key,'package_editorial',{g:i for i,g in enumerate(categories)},font_family='DejaVu Sans');spec['theme']['continuous']['diverging']=['#327D9F','#F7F7F4','#D8795B']
        spec['provenance']['source']='Frozen public synthetic source: '+source.relative_to(ROOT).as_posix();spec['provenance']['filtering']=selection;spec['export']=dict(target_width_mm=178,minimum_text_pt=7.5,readability_policy='block')
        unit,denominator,value,uncertainty={
            'gsea_strip':('Synthetic ranked identifiers and selected pathways; not independent biological subjects','Complete supplied ranked universe and exact supplied pathway hit sets','Running ES, NES, adjusted probability, leading-edge flags and ranked metric supplied separately','No interval supplied; adjusted probabilities are existing display inputs'),
            'ribbon':('Synthetic stored curve; epochs are repeated positions, not independent experiments','All loss positions within both selected stored curves','Supplied epoch, estimate and interval endpoints','Illustrative supplied bounds; probability meaning unspecified; not estimated here'),
            'score_shift':('Synthetic feature identity; connecting scores does not establish paired subjects','All six supplied feature comparisons','Scores A/B and supplied B-minus-A effect with its separate bounds','Existing difference bounds only; no intervals inferred for raw scores'),
            'association':('Synthetic variable-pair and set/variable summary; not biological subjects','All supplied pairwise and Mantel summaries; missing diagonal not assumed to be a measured zero','Pairwise r and Mantel r retain distinct guides; raw p-values remain available in the exact table','No interval supplied; no correlation or p-value calculation')
        }[view]
        spec['parameters']['contract'].update(source_definition=spec['provenance']['source'],independent_unit=unit,denominator=denominator,value_definition=value,uncertainty_definition=uncertainty)
        spec['provenance'].update(input_unit=unit,experimental_unit=unit,denominator=denominator,uncertainty=uncertainty,model='Frozen synthetic display channels; no model fitting or native package execution',limits=value)
        write(inputs/(key+'.spec.json'),spec);render_plan(make_plan(spec,inputs),output)
        receipt=output/key/(key+'.json');meta=json.loads(receipt.read_text(encoding='utf8'));meta['source_file']='inputs/'+p.name;write(receipt,meta)
        records.append(dict(id=key,view=view,source=source.relative_to(ROOT).as_posix(),source_sha256=digest(source),input_sha256=digest(p),png_sha256=digest(output/key/(key+'.png')),selection=selection,status='RENDERED_UNREVIEWED'))
        write(output/'manifest.json',dict(records=records,scientific_acceptance=False));print(key+' rendered',flush=True)
    html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Community design comparisons</title><style>body{font:16px/1.6 system-ui;max-width:1050px;padding:24px;margin:auto;color:#243449;background:#edf1f3}article{margin:24px 0;padding:30px;background:white;border-radius:10px}img{max-width:100%;display:block}a{color:#218c8d}</style><h1>Community design comparisons</h1><p>Independently implemented frozen-result examples; no upstream packages, inference or smoothing.</p>'
    for r in records:
        k=r['id'];html+='<article id="'+k+'"><h2>'+k+' | '+r['view']+'</h2><img src="'+k+'/'+k+'.png" alt="'+r['view']+'"><p>'+r['selection']+'</p><p>'+' · '.join('<a href="'+k+'/'+k+'.'+e+'">'+e.upper()+'</a>' for e in ['svg','pdf','tsv','json'])+' · <a href="inputs/'+k+'.spec.json">SPEC</a></p></article>'
    (output/'index.html').write_text(html,encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);build(p.parse_args().output)
