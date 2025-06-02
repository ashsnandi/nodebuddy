"""
tags.py – hallway / elevator / full toggles (e/h/f)

Mirrors the hot-key logic in editor.py & plan.py 
"""

from typing import Literal
from . import store

TagName = Literal["hallway", "elevator", "full"]


def toggle(gid: str, nid: str, tag_name: TagName) -> None:
    g = store.get(gid)
    if g is None or nid not in g.nodes_dict:
        return
    node = g.nodes_dict[nid]
    cur = node.tags.get(tag_name, False)
    node.tags[tag_name] = not cur
    store.broadcast(gid)
