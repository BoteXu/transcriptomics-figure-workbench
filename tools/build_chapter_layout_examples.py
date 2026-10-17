"""Exercise every new chapter family with changed counts and a custom vertical layout."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
def main(source,out):
    import pandas as pd
    from figure_core import table_bytes
    out.mkdir(parents=True,exist_ok=False);records=[]
    for row in json.loads((source/'manifest.json').read_text())['records']:
        s=json.loads((source/row['spec']).read_text(encoding='utf8'));renderer=s['renderer']
        if renderer not in ['figure_chapter_views.plot_transcriptomic_chapter','figure_enrichment_story.plot_enrichment_story']:continue
        k=row['id'];folder=out/k;folder.mkdir();d=pd.read_csv(source/k/'example.tsv',sep='\t');s['parameters']['columns']=1
        # Expand complete declared grids/series rather than truncate a dense
        # example. Changes are fictional fixture construction, not inference.
        if renderer.endswith('plot_transcriptomic_chapter'):
            frames=[d]
            for p in s['parameters']['panels']:
                q=d[d.panel_id==p['id']].copy()
                if p['kind'] in ['matrix','bubble','interval','bars','stack']:
                    q['label']=q.label+' / B';frames.append(q)
                elif p['kind'] in ['points','embedding','vector']:
                    if 'label' in q:q['label']=q.label.fillna('Point')+' / B'
                    q['x']=q.x+.025;q['y']=q.y+.025;frames.append(q)
            d=pd.concat(frames,ignore_index=True)
            s['parameters']['scope_note']='Larger fictional display scope · custom one-column layout · no analysis'
        else:
            # Increase six pathways to twelve while preserving a complete
            # declared selected-gene membership grid and unchanged support.
            t=d[d.record_type.isin(['term','membership'])].copy();t['term']=t.term+' / B';d=pd.concat([d,t],ignore_index=True)
        raw=table_bytes(d);(folder/'example.tsv').write_bytes(raw);s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest());s['figure_id']+='_VerticalLarge';s['provenance']['source']='Fictional larger-count custom-layout fixture v0.9.1; not analysis';s['export'].update(target_width_mm=297)
        (folder/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8');records.append(dict(row,spec=k+'/example.spec.json'))
    (out/'manifest.json').write_text(json.dumps(dict(records=records,analysis_performed=False),indent=2)+'\n');print(json.dumps(dict(custom_layouts=len(records),all_new_chapter_grammars=True)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.fixtures,a.output)
