"""
geometry.py – pure numeric transforms (translate / rotate / scale)

Derived from the transform-sliders in combiner.py :contentReference[oaicite:0]{index=0}
"""

from __future__ import annotations
import math
from typing import Iterable
from . import store
from .models import Transform, Node


def _centroid(nodes: Iterable[Node]) -> tuple[float, float]:
    xs, ys = zip(*[(n.x, n.y) for n in nodes])
    return sum(xs) / len(xs), sum(ys) / len(ys)


def apply(gid: str, op: Transform) -> None:
    g = store.get(gid)
    if g is None:
        raise ValueError(f"Graph {gid!r} not found")

    nodes = (
        [g.nodes_dict[nid] for nid in op.ids if nid in g.nodes_dict]
        if op.ids else
        list(g.nodes_dict.values())
    )
    if not nodes:
        return

    if op.type == "translate":
        dx, dy = (op.dx or 0.0), (op.dy or 0.0)
        for n in nodes:
            n.x += dx
            n.y += dy

    elif op.type == "scale":
        factor = op.factor or 1.0
        cx, cy = _centroid(nodes)
        for n in nodes:
            n.x = cx + (n.x - cx) * factor
            n.y = cy + (n.y - cy) * factor

    elif op.type == "rotate":
        angle_rad = math.radians(op.angle or 0.0)
        cos_t, sin_t = math.cos(angle_rad), math.sin(angle_rad)
        cx, cy = _centroid(nodes)
        for n in nodes:
            ox, oy = n.x - cx, n.y - cy
            n.x = cx + ox * cos_t - oy * sin_t
            n.y = cy + ox * sin_t + oy * cos_t

    else:
        raise ValueError(f"Unknown transform type {op.type!r}")

    store.broadcast(gid)
