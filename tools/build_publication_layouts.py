"""Bounded synthetic layout probes for the existing publication templates."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))


def build(source,out):
    import pandas as pd
    from figure_workbench.contracts import make_plan
    from figure_workbench.pipeline import render_plan
    out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf8'));by={r['id']:r for r in manifest['records']};records=[]
    for key,base in [('QC_4','BulkQC'),('QC_24','BulkQC'),('Composition_2col','DonorComposition'),('Features_2col','MarkerFeatures'),('Effects_12','GeneEffects'),('Expression_1col','GeneExpression')]:
        row=by[base];s=json.loads((source/row['assets']['spec']).read_text(encoding='utf8'))
        if s['provenance']['synthetic'] is not True:raise ValueError('Only declared fictional fixtures may be duplicated for layout testing')
        d=pd.read_csv(source/row['assets']['tsv'],sep='\t',float_precision='round_trip');params=s['parameters'];s['figure_id']=key
        if key.startswith('QC_'):
            if key=='QC_4':
                keep=[v for g,q in d.groupby('group',sort=False) for v in q['sample'].unique()[:2]];d=d[d['sample'].isin(keep)].copy()
                params['cloud_shapes']={m:{k:v for k,v in shapes.items() if k in keep} for m,shapes in params['cloud_shapes'].items()}
            else:
                extra=d.copy();extra['sample']+='_b';d=pd.concat([d,extra],ignore_index=True)
                for m,shapes in params['cloud_shapes'].items():shapes.update({k+'_b':copy.deepcopy(v) for k,v in list(shapes.items())})
            params['title']='Synthetic layout check · '+str(d['sample'].nunique())+' samples'
        elif key=='Composition_2col':params.update(ncols=2,nrows=3)
        elif key=='Features_2col':params.update(ncols=2,nrows=3);s['export']['target_width_mm']=240
        elif key=='Effects_12':
            parts=[]
            for i in range(3):
                q=d.copy();q['label']+=f'_{i+1}';parts.append(q)
            d=pd.concat(parts,ignore_index=True);params['title']='Synthetic layout check · twelve supplied effects'
        elif key=='Expression_1col':params.update(columns=1,rows=4);s['export']['target_width_mm']=180
        s['provenance']['source']+='; synthetic count or explicit layout probe; duplicated values are layout fixtures only'
        folder=out/key;folder.mkdir();table=folder/'input.tsv';d.to_csv(table,sep='\t',index=False,na_rep='')
        s['input']['path']='input.tsv';s['input']['sha256']=hashlib.sha256(table.read_bytes()).hexdigest();p=folder/'figure.spec.json';p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        result=render_plan(make_plan(s,folder),folder/'rendered')
        records.append(dict(id=key,source=base,spec=p.relative_to(out).as_posix(),result=result))
        (out/'manifest.json').write_text(json.dumps(dict(records=records,synthetic_only=True,analysis_performed=False,visual_acceptance=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print('LAYOUT_DRAWN '+key,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.source,a.output)
