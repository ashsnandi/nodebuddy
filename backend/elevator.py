"""
elevator.py – align clusters of elevator nodes onto a common (avg-x, avg-y)

Ported from refactor_elevators_gui.py :contentReference[oaicite:2]{index=2}
"""

from collections import deque
import math
from . import store


def _euclidean(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def _cluster_elevators(nodes, threshold):
    elevs = [n for n in nodes if n.tags.get("elevator")]
    clusters: list[list] = []
    for n in elevs:
        placed = False
        for c in clusters:
            if _euclidean(n, c[0]) <= threshold:
                c.append(n)
                placed = True
                break
        if not placed:
            clusters.append([n])
    return clusters


def _build_adj(edges):
    adj = {}
    for e in edges:
        adj.setdefault(e.u, []).append(e.v)
        adj.setdefault(e.v, []).append(e.u)
    return adj


def _bfs(start, adj):
    seen = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj.get(u, []):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return seen


def align(gid: str, threshold: float = 300.0) -> None:
    g = store.get(gid)
    if g is None:
        return

    nodes = list(g.nodes_dict.values())
    clusters = _cluster_elevators(nodes, threshold)
    if not clusters:
        return

    adj = _build_adj(g.edges)

    for cluster in clusters:
        # Average position within the cluster
        cx = sum(n.x for n in cluster) / len(cluster)
        cy = sum(n.y for n in cluster) / len(cluster)

        for n in cluster:
            dx, dy = cx - n.x, cy - n.y
            # Move the whole connected component together
            for nid in _bfs(n.id, adj):
                comp_node = g.nodes_dict[nid]
                comp_node.x += dx
                comp_node.y += dy

    store.broadcast(gid)
