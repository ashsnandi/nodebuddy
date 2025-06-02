# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from . import store, models, geometry, tags, elevator, import_export

app = FastAPI(title="Hospital Graph API", version="0.1.0")

# --- CORS so the React dev-server (localhost:5173) can call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. CRUD -------------------------------------------------------------
@app.post("/graph", response_model=models.GraphID)
def create_graph() -> models.GraphID:
    return {"graph_id": store.new_graph()}

@app.get("/graph/{gid}", response_model=models.Graph)
def get_graph(gid: str):
    g = store.get(gid)
    if g is None:
        raise HTTPException(404, "graph not found")
    return g

@app.put("/graph/{gid}/node")
def upsert_node(gid: str, node: models.Node):
    store.upsert_node(gid, node)
    return {"ok": True}

@app.delete("/graph/{gid}/node/{nid}")
def delete_node(gid: str, nid: str):
    store.delete_node(gid, nid)
    return {"ok": True}

@app.post("/graph/{gid}/edge")
def add_edge(gid: str, edge: models.Edge):
    store.add_edge(gid, edge)
    return {"ok": True}

@app.delete("/graph/{gid}/edge")
def del_edge(gid: str, edge: models.Edge):
    store.delete_edge(gid, edge)
    return {"ok": True}

# 2. Tags / modes (replicates hot-keys e,h,f in e.py) -----------------
@app.patch("/graph/{gid}/node/{nid}/tag/{tag_name}")
def toggle_tag(gid: str, nid: str, tag_name: tags.TagName):
    tags.toggle(gid, nid, tag_name)
    return {"ok": True}

# 3. Geometry tools (dx/dy, rotate, scale) ---------------------------
@app.post("/graph/{gid}/transform")
def transform(gid: str, op: models.Transform):
    geometry.apply(gid, op)
    return {"ok": True}

# 4. Elevator auto-align (from elevator.py) --------------------------
@app.post("/graph/{gid}/elevators/align")
def align_elevators(gid: str, req: models.ElevatorAlign):
    elevator.align(gid, req.threshold)
    return {"ok": True}

# 5. Import / export --------------------------------------------------
@app.post("/graph/import", response_model=models.GraphID)
def import_graph(req: models.ImportRequest):
    gid = import_export.from_json(req.json_text)
    return {"graph_id": gid}

@app.get("/graph/{gid}/export")
def export_graph(gid: str):
    return import_export.to_json(gid)

# 6. Live-edit WebSocket ---------------------------------------------
@app.websocket("/ws/{gid}")
async def ws(gid: str, ws: WebSocket):
    await ws.accept()
    # basic pub/sub so every change is echoed to all clients
    store.subscribe(gid, ws)
    try:
        while True:
            msg = await ws.receive_json()
            store.apply_ws(gid, msg)   # same messages React will send
    except WebSocketDisconnect:
        store.unsubscribe(gid, ws)
