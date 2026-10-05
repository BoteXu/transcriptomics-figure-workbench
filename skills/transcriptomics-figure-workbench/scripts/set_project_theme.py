"""Create or replace a project style in a fresh JSON file, keeping identity slots."""
from pathlib import Path
import argparse,json
from project_theme import create_theme,read_theme,validate_theme

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--from-theme',type=Path); p.add_argument('--project'); p.add_argument('--card'); p.add_argument('--groups',type=Path); p.add_argument('--font'); p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.from_theme:
        old=read_theme(a.from_theme); theme=create_theme(a.project or old['project_id'],a.card or old['palette_name'],old['group_slots'],font_family=a.font or old['font_family']); theme['design']=old['design']; theme['line_width']=old['line_width']; theme['point_edge_width']=old['point_edge_width']; theme['preview_only']=old['preview_only']
    else:
        if not a.project or not a.card or not a.groups or not a.font: p.error('New project needs --project --card --groups --font')
        theme=create_theme(a.project,a.card,json.loads(a.groups.read_text(encoding='utf8')),font_family=a.font); theme['preview_only']=False
    validate_theme(theme); a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf8') as f: json.dump(theme,f,ensure_ascii=False,indent=2)
    print('Saved one project theme; rerender the project manifest into a fresh output directory')

if __name__=='__main__': main()
