# backend/store.py
from typing import Dict, List, Set
from fastapi import WebSocket
from .models import Graph, Node, Edge
import uuid, asyncio, json

_GRAPHS: Dict[str, Graph] = {}
_SUBS: Dict[str, Set[WebSocket]] = {}

# ---------- helpers ----------
def new_graph() -> str:
    gid = str(uuid.uuid4())
    _GRAPHS[gid] = Graph()
    _SUBS[gid]   = set()
    return gid

def get(gid: str) -> Graph | None: return _GRAPHS.get(gid)

def broadcast(gid: str):
    if gid not in _SUBS: return
    payload = json.dumps(_GRAPHS[gid].model_dump())
    for ws in list(_SUBS[gid]):
        asyncio.create_task(ws.send_text(payload))

# ---------- CRUD --------------
def upsert_node(gid: str, node: Node):
    g = _GRAPHS[gid]
    g.nodes_dict[node.id] = node
    broadcast(gid)

def delete_node(gid: str, nid: str):
    g = _GRAPHS[gid]
    g.nodes_dict.pop(nid, None)
    g.edges = [e for e in g.edges if e.u != nid and e.v != nid]
    broadcast(gid)

def add_edge(gid: str, edge: Edge):
    _GRAPHS[gid].edges.append(edge)
    broadcast(gid)

def delete_edge(gid: str, edge: Edge):
    g = _GRAPHS[gid]
    g.edges = [e for e in g.edges if not (e.u == edge.u and e.v == edge.v)]
    broadcast(gid)

# ---------- WS -----------------
def subscribe(gid: str, ws: WebSocket):
    _SUBS[gid].add(ws)
    asyncio.create_task(ws.send_json(_GRAPHS[gid].model_dump()))

def unsubscribe(gid: str, ws: WebSocket):
    _SUBS[gid].discard(ws)

def apply_ws(gid: str, msg: dict):
    """Called by main.ws(); msg already contains type + payload."""
    # e.g. {"type":"move","ids":[...],"dx":12,"dy":5}
    # do minimal routing here, or just call the same helpers
    ...
