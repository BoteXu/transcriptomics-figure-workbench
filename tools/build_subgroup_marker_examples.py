# -*- coding: utf-8 -*-
"""Small fictional drawing fixtures, never marker inference or analysis."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))

def build(source,out):
    import numpy as np
    import pandas as pd
    from figure_core import table_bytes
    base=json.loads((source/'CellTypes/CellTypes.spec.json').read_text(encoding='utf8'))
    atlas=pd.read_csv(source/'CellTypes/CellTypes.tsv',sep='\t')
    emb=atlas[atlas.record_type=='embedding'].copy()
    dots=atlas[atlas.record_type=='marker_dot'].copy()
    groups=list(emb.group.unique());out.mkdir(parents=True,exist_ok=False);rows=[]
    # Expression channels are explicit fictional fixtures, deliberately varying
    # in within-population support and off-population signal. No labels are
    # discovered from this expression and no statistical tests are computed.
    for j,group in enumerate(groups):
        selected=list(dots[dots.feature_group==group].feature.unique())
        features=[];summaries=[]
        for k,gene in enumerate(selected):
            idx=np.arange(len(emb));target=(emb.group==group).to_numpy()
            vals=np.where(target,2.1+.38*k+.95*(np.sin(idx*.41+k)+1)/2,
                          .03+.12*(np.sin(idx*.27+k)+1)/2)
            vals=np.where((idx+k*3)%(7+k)==0,0,vals)
            vals=np.where((~target)&((idx+k)%4<3),0,vals)
            features.append(pd.DataFrame(dict(record_type='feature_map',object_id=emb.object_id,
                feature=gene,x=emb.x,y=emb.y,value=vals)))
            for comparison in groups:
                values=vals[(emb.group==comparison).to_numpy()]
                summaries.append(dict(record_type='marker_dot',feature=gene,group=comparison,
                    feature_group=group,value=float(values.mean()),fraction=float(np.mean(values>0))))
        table=pd.concat([emb,pd.DataFrame(summaries),*features],ignore_index=True)
        key='Subgroup_'+str(j+1).zfill(2);folder=out/key;folder.mkdir()
        s=copy.deepcopy(base);s.update(figure_id=key,renderer='figure_annotation_views.plot_annotation_evidence')
        s['parameters'].update(mode='subgroup',title=group+' · marker evidence',focus_group=group,
            marker_order=selected,ncols='auto',group_order=groups,expression_label='log1p normalized expression')
        s['appearance'].update(label_pt=10,tick_pt=9.5,title_pt=11,note_pt=10)
        s['export'].update(target_width_mm=240,raster_dpi=300)
        raw=table_bytes(table);(folder/'example.tsv').write_bytes(raw)
        s['input'].update(path='example.tsv',sha256=hashlib.sha256(raw).hexdigest(),
            numeric_columns=[c for c in table if pd.api.types.is_numeric_dtype(table[c])])
        s['provenance'].update(source='Fictional per-subgroup marker display fixture v0.9.1',
            interpretation_limit='Illustrative cell-level expression and separately supplied summary means/fractions; not validated markers, inference or donor-level evidence')
        (folder/'example.spec.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        rows.append(dict(id=key,spec=key+'/example.spec.json',assay='single_cell',chapters=['single_cell.annotation','single_cell.subcluster'],focus_group=group,markers=selected))
    # The same first subgroup is also drawn with 2 and 8 markers and explicit
    # one/two-column requests. These are layout variants, not new plot types.
    original=out/'Subgroup_01';s0=json.loads((original/'example.spec.json').read_text(encoding='utf8'))
    t0=pd.read_csv(original/'example.tsv',sep='\t')
    for number,cols in [(2,1),(4,2),(8,3)]:
        k='Layout_'+str(number).zfill(2)+'Markers_'+str(cols)+'Columns';p=out/k;p.mkdir()
        s=copy.deepcopy(s0);t=t0.copy();selected=list(s['parameters']['marker_order'])
        if number==2:
            selected=selected[:2];t=t[(t.record_type=='embedding')|t.feature.isin(selected)].copy()
        elif number==8:
            parts=[t]
            for gene in selected:
                q=t[t.feature==gene].copy();q['feature']=gene+'_demoB';parts.append(q)
            t=pd.concat(parts,ignore_index=True);selected += [g+'_demoB' for g in selected]
        raw=table_bytes(t);(p/'example.tsv').write_bytes(raw)
        s['input']['sha256']=hashlib.sha256(raw).hexdigest();s['parameters'].update(marker_order=selected,ncols=cols)
        s['figure_id']=k;s['export']['target_width_mm']=260 if number==8 else 240 if cols>1 else 110
        (p/'example.spec.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        rows.append(dict(id=k,spec=k+'/example.spec.json',assay='single_cell',chapters=['single_cell.annotation'],focus_group=groups[0],markers=selected))
    (out/'manifest.json').write_text(json.dumps(dict(records=rows,analysis_performed=False),indent=2)+'\n')
    print('SUBGROUP_MARKER_INPUTS '+str(len(rows)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();build(a.source,a.output)
