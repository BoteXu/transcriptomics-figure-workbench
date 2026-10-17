"""An existing private profile must never be replaced by a public stub."""
import sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from sync_public_skill import sync
def main():
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/'public';target=Path(tmp)/'installed'
        for root in [source,target]:(root/'references').mkdir(parents=True)
        (source/'references/lps-profile.md').write_text('public placeholder')
        (target/'references/lps-profile.md').write_text('private custom settings')
        (source/'script.py').write_text('new public source')
        (target/'custom.md').write_text('keep customized file')
        (source/'custom.md').write_text('public example')
        r=sync(source,target,False,['custom.md']);assert r['preserved_files']==2 and not (target/'script.py').exists()
        r=sync(source,target,True,['custom.md']);assert (target/'references/lps-profile.md').read_text()=='private custom settings'
        assert (target/'custom.md').read_text()=='keep customized file' and (target/'script.py').read_text()=='new public source'
    print('PRIVATE_PROFILE_UPDATE_PROTECTION_PASS')
if __name__=='__main__':main()
