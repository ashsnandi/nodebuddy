import { useEffect } from "react";
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
} from "reactflow";
import type { Node, Edge, Connection, } from "reactflow";
import "reactflow/dist/style.css";
import { QueryClientProvider, useQuery } from "@tanstack/react-query";
import {
  createGraph,
  fetchGraph,
  upsertNode,
  addEdge as apiAddEdge,
  qc,
} from "./api";
import Toolbar from "./components/Toolbar";
import ImageLayer from "./components/ImageLayer";
import { useCanvas } from "./store";

function FlowCanvas() {
  const { gid, floor } = useCanvas();
  const { data } = useQuery({
    queryKey: ["graph", gid],
    queryFn: () => fetchGraph(gid),
    refetchInterval: 1000, // WS later
  });

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  /** refresh if server data changes */
  useEffect(() => {
    if (!data) return;
    setNodes(
      Object.values<any>(data.nodes_dict)
        .filter((n) => n.floor === floor)
        .map((n) => ({
          id: n.id,
          position: { x: n.x, y: n.y },
          data: { label: n.id },
          style: {
            border: n.tags.elevator
              ? "3px solid royalblue"
              : n.tags.hallway
              ? "2px solid darkgray"
              : "1px solid salmon",
            background: "#fff",
          },
        })),
    );
    setEdges(
      data.edges.map((e: any) => ({
        id: `${e.u}-${e.v}`,
        source: e.u,
        target: e.v,
        animated: true,
      })),
    );
  }, [data, floor]);

  /** commit position on drag-stop */
  const onNodeDragStop = (_: any, node: Node) => {
    upsertNode(gid, {
      id: node.id,
      x: node.position.x,
      y: node.position.y,
      floor,
    }).then(() => qc.invalidateQueries(["graph", gid]));
  };

  /** new edge */
  const onConnect = (c: Connection) => {
    apiAddEdge(gid, c.source!, c.target!).then(() => {
      setEdges((eds) => addEdge(c, eds));
      qc.invalidateQueries(["graph", gid]);
    });
  };

  /** double-click canvas → create node */
  const handlePane = (evt: React.MouseEvent) => {
    const { top, left } = (evt.target as HTMLElement).getBoundingClientRect();
    const pos = {
      x: evt.clientX - left,
      y: evt.clientY - top,
    };
    const id = crypto.randomUUID().slice(0, 6);
    upsertNode(gid, { id, ...pos, floor }).then(() =>
      qc.invalidateQueries(["graph", gid])
    );
  };

  return (
    <div className="rf-wrapper-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeDragStop={onNodeDragStop}
        onConnect={onConnect}
	onPaneClick={(e) => {
			 if (e.detail === 2) handlePane(e);
			 }}
        proOptions={{ hideAttribution: true }}
        fitView
      >
        <ImageLayer />
      </ReactFlow>
    </div>
  );
}

export default function App() {
  const setGid = useCanvas((s) => s);
  useEffect(() => {
    createGraph().then((gid) => useCanvas.setState({ gid }));
  }, []);

  return (
    <QueryClientProvider client={qc}>
      <ReactFlowProvider>
	<Toolbar />
        <FlowCanvas />
      </ReactFlowProvider>
    </QueryClientProvider>
  );
}
