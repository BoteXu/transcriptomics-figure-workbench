"""Package the checked public skill and overviews in a fresh directory."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/transcriptomics-figure-workbench'


def main(output):
    output.mkdir(parents=True,exist_ok=False)
    version=(ROOT/'VERSION').read_text().strip()
    assert version==(SKILL/'VERSION').read_text().strip()
    files={p.relative_to(SKILL).as_posix():p for p in SKILL.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert all(not p.is_symlink() for p in files.values())
    for name in ('LICENSE','requirements.txt','requirements-review.txt'):
        if name in files:assert files[name].read_bytes()==(ROOT/name).read_bytes(),'Conflicting package file: '+name
        else:files[name]=ROOT/name
    archive=output/f'transcriptomics-figure-workbench-v{version}.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,path in sorted(files.items()):z.write(path,'transcriptomics-figure-workbench/'+name)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(set(z.namelist()))==len(files)
        assert not z.testzip()
        for name,path in files.items():assert z.read('transcriptomics-figure-workbench/'+name)==path.read_bytes()
    assets=[archive]
    for source,name in [('visualization-overview.pdf','visualization-overview.pdf'),('source-archive-v021.pdf','all-previews.pdf'),('new-result-modes-v024.jpg','new-result-modes-v024.jpg')]:
        destination=output/name;shutil.copy2(ROOT/'examples/overview'/source,destination);assets.append(destination)
    (output/f'SHA256SUMS-v{version}.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in assets),encoding='utf8')
    print(json.dumps(dict(status='PUBLIC_RELEASE_ARCHIVE_VERIFIED',version=version,unique_archive_entries=len(files),assets=[dict(name=p.name,bytes=p.stat().st_size) for p in assets])))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();main(a.output)
