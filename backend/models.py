# backend/models.py
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class Node(BaseModel):
    id: str
    x: float
    y: float
    floor: int = 0
    tags: Dict[str, bool] = Field(
        default_factory=lambda: {"hallway": False, "elevator": False, "full": False}
    )

class Edge(BaseModel):
    u: str
    v: str

class Graph(BaseModel):
    nodes_dict: Dict[str, Node] = Field(default_factory=dict)  # fast lookup
    edges: List[Edge] = Field(default_factory=list)

class GraphID(BaseModel):
    graph_id: str

# ---------- aux requests ----------
class Transform(BaseModel):
    type: Literal["translate", "rotate", "scale"]
    ids: Optional[List[str]] = None          # None → whole graph
    dx: Optional[float] = None
    dy: Optional[float] = None
    angle: Optional[float] = None
    factor: Optional[float] = None

class ElevatorAlign(BaseModel):
    threshold: float = 100.0

class ImportRequest(BaseModel):
    json_text: str
