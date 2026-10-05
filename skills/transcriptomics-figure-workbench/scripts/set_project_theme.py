"""Create or replace a project style in a fresh JSON file, keeping identity slots."""
from pathlib import Path
import argparse,json,copy
from project_theme import create_theme,read_theme,validate_theme
from figure_reference_palettes import load_color_cards,get_palette,resolve_card_name

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--from-theme',type=Path); p.add_argument('--project'); p.add_argument('--card'); p.add_argument('--groups',type=Path); p.add_argument('--font'); p.add_argument('--sequential-card'); p.add_argument('--diverging-card'); p.add_argument('--list-cards',action='store_true'); p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.list_cards:
        print(json.dumps({id_:dict(registry_name=c['registry_name'],semantic=c['semantic'],colors=c['colors']) for id_,c in load_color_cards().items()},ensure_ascii=False,indent=2)); return
    if not a.output: p.error('--output is required when creating a theme')
    if a.from_theme:
        old=read_theme(a.from_theme); theme=create_theme(a.project or old['project_id'],a.card or old['palette_name'],old['group_slots'],font_family=a.font or old['font_family']); theme['design']=old['design']; theme['line_width']=old['line_width']; theme['point_edge_width']=old['point_edge_width']; theme['preview_only']=old['preview_only']
        if theme['palette_name']==old['palette_name']:
            for field in ('roles','continuous','continuous_cards','continuous_provenance'):
                if field in old: theme[field]=copy.deepcopy(old[field])
    else:
        if not a.project or not a.card or not a.groups or not a.font: p.error('New project needs --project --card --groups --font')
        theme=create_theme(a.project,a.card,json.loads(a.groups.read_text(encoding='utf8')),font_family=a.font); theme['preview_only']=False
    for semantic,name in [('sequential',a.sequential_card),('diverging',a.diverging_card)]:
        if name:
            registry_name=resolve_card_name(name); card=get_palette(registry_name,semantic=semantic)
            theme['continuous'][semantic]=list(card['colors'])
            theme.setdefault('continuous_cards',{})[semantic]=registry_name
    if theme.get('continuous_cards'):
        theme['continuous_provenance']='Explicit continuous cards: '+json.dumps(theme['continuous_cards'],sort_keys=True)+'; unspecified roles retain the derived base-card scale'
    validate_theme(theme); a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf8') as f: json.dump(theme,f,ensure_ascii=False,indent=2)
    print('Saved one project theme; rerender the project manifest into a fresh output directory')

if __name__=='__main__': main()
