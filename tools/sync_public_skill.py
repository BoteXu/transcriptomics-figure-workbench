"""Copy a selected public payload, preserving existing private profile paths.

This is a scoped file synchronizer, not an automatic custom-code merge or a
transactional package manager. Preview the paths before --apply. Additional
customized public filenames must be explicitly protected by the caller.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
DEFAULT_PROTECTED=('references/lps-profile.md','private/','profiles/','.env','SKILL.local.md')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sync(source,target,apply=False,protect=()):
    source=source.resolve();target=target.resolve()
    if source==target or source in target.parents or target in source.parents:
        raise ValueError('Select separate source and installation roots')
    rules=list(DEFAULT_PROTECTED)+list(protect)
    for x in rules:
        if Path(x).is_absolute() or '..' in Path(x).parts:raise ValueError('Protected names must stay relative to the selected root')
    selected=[];preserved=[]
    for p in sorted(source.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(source).as_posix();dest=target/rel
        if p.is_symlink() or dest.is_symlink() or (target not in dest.resolve().parents):raise ValueError('Symlinks or escaping paths are not a public payload')
        if dest.is_file() and any(rel==r.rstrip('/') or (r.endswith('/') and rel.startswith(r)) for r in rules):
            preserved.append((dest,sha(dest)));continue
        selected.append((p,dest,rel))
    if apply:
        for p,dest,rel in selected:
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            if sha(p)!=sha(dest):raise ValueError('Installed public bytes do not match: '+rel)
        if any(sha(p)!=digest for p,digest in preserved):raise ValueError('Protected profile changed')
    return dict(state='PUBLIC_PAYLOAD_SYNCED' if apply else 'PUBLIC_PAYLOAD_PREVIEW',public_files=len(selected),preserved_files=len(preserved),
        protected_paths=rules,custom_code_merge=False,private_contents_disclosed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--target',required=True,type=Path);p.add_argument('--apply',action='store_true');p.add_argument('--protect',action='append',default=[]);a=p.parse_args();print(json.dumps(sync(a.source,a.target,a.apply,a.protect)))
