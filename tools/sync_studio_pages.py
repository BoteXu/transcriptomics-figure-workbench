"""Synchronize cached public Studio metadata; preserve every embedded example and SVG."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/transcriptomics-figure-workbench'
sys.path.insert(0,str(SKILL/'scripts'))
from figure_workbench.registry import read_registry


def sync(check=False):
    count=0
    for path in [SKILL/'assets/figure-studio.html',ROOT/'examples/studio/index.html']:
        text=path.read_text('utf8')
        opening=text.index('>',text.index('studio-data'))+1;end=text.index('</script>',opening)
        data=json.loads(text[opening:end]);data['registry']=read_registry()
        encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
        updated=text[:opening]+encoded+text[end:]
        version=(SKILL/'VERSION').read_text('utf8').strip()
        updated=re.sub(r'科研绘图工作台 · \d+\.\d+\.\d+','科研绘图工作台 · '+version,updated)
        prefix=Path(os.path.relpath(SKILL/'assets/connected-examples',path.parent)).as_posix()
        link='<a class="button secondary" href="'+prefix+'/index.html">同对象联动检查 · 冻结结果交接</a>'
        if link not in updated:updated=updated.replace('</header>',link+'</header>',1)
        if check and updated!=text:raise ValueError('Cached public Studio is stale; run tools/sync_studio_pages.py')
        if not check and updated!=text:path.write_bytes(updated.encode('utf8'))
        count+=1
    return {'state':'STUDIO_CACHE_CURRENT' if check else 'STUDIO_CACHE_SYNCHRONIZED','pages':count,'existing_examples_preserved':True}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();print(json.dumps(sync(a.check)))
