"""Package only committed source and de-identified reviewed public examples."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(destination):
 from check_scientific_release import main as check
 check();out=Path(destination);out.mkdir(exist_ok=False,parents=True)
 if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT).strip():raise ValueError('Commit the reviewed source before packaging')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assets=[]
 for path,prefix,name in [('skills/scientific-visualization/','scientific-visualization','scientific-visualization-v2.2.0.zip'),('examples/scientific-v220/','scientific-examples','scientific-visualization-examples-v2.2.0.zip')]:
  names=[n for n in subprocess.check_output(['git','ls-files','-z','--',path],cwd=ROOT).decode('utf8').split('\0') if n]
  assert names and all(n.startswith(path) for n in names)
  target=out/name
  with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for n in sorted(names):z.write(ROOT/n,prefix+'/'+n[len(path):])
  with zipfile.ZipFile(target) as z:
   assert not z.testzip()
   for n in names:assert hashlib.sha256(z.read(prefix+'/'+n[len(path):])).hexdigest()==sha(ROOT/n)
  assets.append({'file':name,'sha256':sha(target),'bytes':target.stat().st_size,'members':len(names)})
 receipt={'schema':'public-scientific-release/1','version':'2.2.0','commit':commit,'repository':'https://github.com/BoteXu/transcriptomics-figure-workbench','assets':assets,'legacy_engine_version':'0.14.0','legacy_sources_preserved':True,'native_engine_runs':0,'server_runtime':'NOT_RUN_THIS_UPGRADE','scientific_acceptance':'NOT_ESTABLISHED'}
 p=out/'SCIENTIFIC_RELEASE_SOURCE.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (out/'SHA256SUMS-v2.2.0.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in assets)+sha(p)+'  '+p.name+'\n',encoding='utf8')
 print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('destination');build(parser.parse_args().destination)
