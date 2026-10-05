"""Reference-inspired semantic palettes. Screenshot colors are approximate.

No claim is made that an inaccessible WeChat article was read or that these
palettes are validated for color-vision deficiency. Project palettes take priority.
"""
import json
from contextvars import ContextVar
from contextlib import contextmanager
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap, to_rgba

REGISTRY_PATH = Path(__file__).parent.parent/'references'/'reference-palettes.json'
_PROJECT_CONTEXT=ContextVar('figure_project_context',default=None)

@contextmanager
def palette_scope(project):
    token=_PROJECT_CONTEXT.set(project)
    try: yield
    finally: _PROJECT_CONTEXT.reset(token)

def semantic_color(role,fallback):
    project=_PROJECT_CONTEXT.get()
    return project['roles'].get(role,fallback) if project else fallback

def load_palettes():
    return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))['palettes']

def load_color_cards():
    """Return the 15 registered cards; ordinary reference colours stay separate."""
    registry=json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    cards={f'C{i:02d}':dict(registry['palettes'][f'card_{i:02d}'],registry_name=f'card_{i:02d}') for i in range(1,8)}
    cards.update({card['id']:dict(card) for card in registry['additional_cards']})
    return cards

def resolve_card_name(name):
    cards=load_color_cards()
    return cards[name]['registry_name'] if name in cards else name

def get_palette(name, *, semantic=None):
    p=load_palettes()[name]
    if semantic is not None and p['semantic']!=semantic:
        raise ValueError(f'{name} has {p["semantic"]} semantics; requested {semantic}')
    for c in p['colors']: to_rgba(c)
    project=_PROJECT_CONTEXT.get()
    if project and p['semantic'] in ('sequential','diverging'):
        p=dict(p,colors=project['continuous'][p['semantic']],provenance='project_theme_semantic_mapping',project_id=project['project_id'])
    return p.copy()

def reference_cmap(name, *, semantic='diverging'):
    p=get_palette(name,semantic=semantic)
    if semantic not in ('diverging','sequential'): raise ValueError('Continuous palette required')
    return LinearSegmentedColormap.from_list(name,p['colors'])

def category_map(name, categories):
    p=get_palette(name,semantic='categorical'); cats=list(categories)
    if len(cats)>len(p['colors']): raise ValueError('Too many categories; supply a project palette or facet')
    if len(set(cats))!=len(cats): raise ValueError('Duplicate category')
    return dict(zip(cats,p['colors']))
