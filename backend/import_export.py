"""
import_export.py – simple Graph ⇆ JSON helpers
"""

from __future__ import annotations
import json, uuid
from . import store, models


def to_json(gid: str) -> str:
    g = store.get(gid)
    if g is None:
        raise ValueError(f"graph {gid!r} not found")
    # convert nodes_dict → list for export
    out = models.Graph(
        nodes_dict=g.nodes_dict,
        edges=g.edges
    ).model_dump()
    out["nodes"] = list(out.pop("nodes_dict").values())
    return json.dumps(out, indent=2)


def from_json(json_text: str) -> str:
    data = json.loads(json_text)
    gid = str(uuid.uuid4())
    g = models.Graph()
    for n in data.get("nodes", []):
        node = models.Node(**n)
        g.nodes_dict[node.id] = node
    for u, v in data.get("edges", []):
        g.edges.append(models.Edge(u=u, v=v))
    # register
    store._GRAPHS[gid] = g       # pylint: disable=protected-access
    store._SUBS[gid] = set()     # pylint: disable=protected-access
    return gid
