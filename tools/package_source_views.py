"""Make portable frozen-input specs and installed previews of reviewed examples.

This copies and describes exports. It never records or grants visual approval.
"""
import argparse,csv,hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
IDENTITIES=set('group sample sample_id cell_id unit_id object_id feature feature_id label category series condition record_type kind panel layer node_id source target term term_id term_label gene gene_id pathway chromosome chain signal variant_id transcript_id state stage surface_id track track_id edge_id family segment decision spec_id event set_id'.split())
def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def specs():
    from figure_workbench.contracts import make_plan
    for group in ['single','volume/small','volume/medium','volume/large']:
        base=ROOT/'examples/source-v093'/group
        for r in load(base/'manifest.json')['records']:
            if 'adapter' not in r:continue
            key=r['id'];dest=base/key;request=load(dest/'request.json');table=dest/(key+'.tsv')
            with table.open(encoding='utf8',newline='') as f:
                reader=csv.DictReader(f,delimiter='\t');rows=list(reader);columns=reader.fieldnames
            numeric=[]
            for c in columns:
                identity=c in IDENTITIES or c.endswith('_id')
                if (c in ['label','label_id'] and request['base_form']=='slice') or (c=='matrix_id' and request['adapter']=='figure_process_dashboard.plot_process_dashboard'):identity=False
                vals=[row[c] for row in rows if row[c]]
                if identity or not vals:continue
                try:
                    for value in vals:float(value)
                except ValueError:continue
                numeric.append(c)
            meta=dict(source=request.get('fixture_definition','Existing public frozen software fixture'),input_unit='Synthetic display record',
                experimental_unit='None inferred; records are not independent biomedical samples',contrast='Fictional declared display contrast only',
                denominator='Exact supplied example table; see volume preparation receipt for selected identities',
                model='No scientific model fitted by this drawing example',limits='Synthetic display verification only; no biological or clinical validity',
                filtering='Explicit software fixture preparation before drawing; plotted table frozen and hashed',
                uncertainty='Supplied illustrative channels only; no interval estimation',interpretation_limit='Review new data and intended physical size again',synthetic=True)
            spec=dict(schema_version=1,figure_id=key,renderer=request['adapter'],
                input=dict(path=table.name,sha256=sha(table),numeric_columns=numeric,max_rows=100000,max_bytes=20*1024**2),
                parameters=request['parameters'],theme=request['theme'],provenance=meta,
                export=dict(raster_dpi=300,readability_policy='warn'))
            if r.get('requested_layout'):spec['layout']=r['requested_layout']
            make_plan(spec,dest) # actual contracts and exact input hash; no fitting/import
            write(dest/'example.spec.json',spec)
    print('Portable specs validated for all 355 native single/volume examples')

def review_index():
    import copy
    base=ROOT/'examples/source-v093';records=[]
    for scope,count in [('single',96),('volume/small',87),('volume/medium',87),('volume/large',87),('layout',48)]:
        doc=load(base/scope/'review-ledger.json');assert doc['state']=='SCREEN_REVIEWED' and len(doc['records'])==count
        manifest={r['id']:r for r in load(base/scope/'manifest.json')['records']}
        for r in doc['records']:
            r=copy.deepcopy(r);item=manifest[r['id']]
            assert r['png_sha256']==sha(base/scope/item['png'])
            r.update(scope=scope,png=scope+'/'+item['png'],svg=scope+'/'+item['file'],
                svg_sha256=sha(base/scope/item['file']),pdf_sha256=sha((base/scope/item['file']).with_suffix('.pdf')))
            records.append(r)
    write(base/'review-ledger.json',dict(version='0.9.3',state='SCREEN_REVIEWED',records=records,
        aesthetic_publication_approval=False,independent_second_review=False,calibrated_paper_proof=False,
        separately_rasterized_pdf_views=['single/gsea','single/reference-aligned-tracks','layout/Layout07_custom'],
        scope='405 individually viewed final PNG exports. Three representative PDFs separately rasterized and viewed. Current exported examples only; not all historical images or all possible inputs.',
        scientific_acceptance=False))
    print('Aggregated existing exact-image screen records: 405')

def install(output):
    from PIL import Image
    output.mkdir(parents=True,exist_ok=False);records=[]
    base=ROOT/'examples/source-v093/single'
    for r in load(base/'manifest.json')['records']:
        key=r['id'];dest=output/key;dest.mkdir();files={}
        for extension in ['svg','png','pdf','tsv']:
            src=base/key/(key+'.'+extension)
            if src.is_file():shutil.copyfile(src,dest/src.name);files[extension]=key+'/'+src.name
        for name in ['example.spec.json','request.json','reference.json']:
            src=base/key/name
            if src.is_file():shutil.copyfile(src,dest/name);files[name]=key+'/'+name
        with Image.open(base/r['png']) as im:
            im.thumbnail((1450,1350));im.convert('RGB').save(dest/'preview.jpg',quality=94)
        files['preview']=key+'/preview.jpg'
        records.append(dict(id=key,form=r['form'],assets=files,sha256={k:sha(output/v) for k,v in files.items()},scientific_acceptance=False))
    shutil.copyfile(base/'index.html',output/'index.html')
    shutil.copyfile(base/'review-ledger.json',output/'review-ledger.json')
    # Installed catalogue links to the local portable spec, not repository paths.
    text=(output/'index.html').read_text(encoding='utf8')
    text=text.replace('>Request</a>','>Original request</a>')
    for r in records:
        key=r['id']
        if 'example.spec.json' in r['assets']:
            anchor=f'<h2>{key}</h2>'
            text=text.replace(anchor,anchor+f'<p><a href="{key}/example.spec.json">Portable runnable spec</a></p>')
    (output/'index.html').write_text(text,encoding='utf8')
    write(output/'manifest.json',dict(version='0.9.3',records=records,scope='96 exact final singles; previews resized for navigation only',scientific_acceptance=False))
    print('Packaged 96 complete current example views and portable inputs')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['specs','install','review-index']);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.action=='specs':specs()
    elif a.action=='review-index':review_index()
    else:install(a.output)
