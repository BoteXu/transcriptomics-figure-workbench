"""Compact existing reading volumes with byte-identical decoded operators."""
from pathlib import Path
import argparse,json,sys
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'skills/transcriptomics-figure-workbench/scripts'))
from figure_workbench.reading import _append_compressed
from figure_workbench.registry import digest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(exist_ok=False)
    index=json.loads((a.source/'reading-index.json').read_text(encoding='utf8'))
    for row in index['volumes']:
        with PdfReader(a.source/row['file']) as r:
            w=PdfWriter()
            for page in r.pages:_append_compressed(w,page)
            w.add_metadata({'/Title':'Frozen figure reading edition','/Author':'Figure Workbench Contributors','/Creator':'Figure Workbench'})
            w.compress_identical_objects()
            out=a.output/row['file']
            with out.open('xb') as f:w.write(f)
            w.close();row.update(sha256=digest(out),bytes=out.stat().st_size)
        print(json.dumps(row),flush=True)
    index['lossless_compression']='Decoded PDF drawing instruction streams preserved byte for byte'
    (a.output/'reading-index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf8')
