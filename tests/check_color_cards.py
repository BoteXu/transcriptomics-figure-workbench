"""Verify card semantics and font-only replacement without changing colour roles."""
from pathlib import Path
import copy,json,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/transcriptomics-figure-workbench/scripts'
sys.path.insert(0,str(SCRIPTS))
from figure_reference_palettes import load_color_cards,get_palette,resolve_card_name
from project_theme import create_theme,validate_theme,group_palette

def main():
    cards=load_color_cards()
    assert list(cards)==[f'C{i:02d}' for i in range(1,16)]
    assert sum(c['semantic']=='categorical' for c in cards.values())==13
    for id_,card in cards.items():
        resolved=get_palette(resolve_card_name(id_),semantic=card['semantic'])
        assert resolved['colors']==card['colors']
        if card['semantic']=='categorical':
            theme=create_theme('card-check',id_,{'A':0},font_family='DejaVu Sans')
            assert group_palette(theme,['A'])=={'A':card['colors'][0]}
        else:
            try:create_theme('invalid-card',id_,{'A':0},font_family='DejaVu Sans')
            except ValueError:pass
            else:raise AssertionError('Continuous card accepted as unordered category base')
    with tempfile.TemporaryDirectory(prefix='figure-card-check-') as directory:
        directory=Path(directory);source=directory/'base.json';selected=directory/'selected.json';font_only=directory/'font.json'
        theme=create_theme('continuous-check','C06',{'A':0},font_family='DejaVu Sans')
        source.write_text(json.dumps(theme),encoding='utf8')
        command=[sys.executable,str(SCRIPTS/'set_project_theme.py'),'--from-theme',str(source),'--sequential-card','C14','--diverging-card','C15','--output',str(selected)]
        subprocess.run(command,check=True,capture_output=True,text=True)
        first=validate_theme(json.loads(selected.read_text(encoding='utf8')))
        assert first['continuous']['sequential']==cards['C14']['colors'] and first['continuous']['diverging']==cards['C15']['colors']
        subprocess.run([sys.executable,str(SCRIPTS/'set_project_theme.py'),'--from-theme',str(selected),'--font','DejaVu Serif','--output',str(font_only)],check=True,capture_output=True,text=True)
        second=validate_theme(json.loads(font_only.read_text(encoding='utf8')))
        assert first['group_slots']==second['group_slots'] and first['roles']==second['roles']
        assert first['continuous']==second['continuous'] and second['font_family']=='DejaVu Serif'
    print(json.dumps({'status':'COLOR_CARD_CONTRACTS_PASS','cards':15,'categorical':13,'sequential':1,'diverging':1,'font_only_continuous_preservation':True},indent=2))

if __name__=='__main__':main()
