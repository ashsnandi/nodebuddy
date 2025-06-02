// src/api.ts
import { QueryClient } from "@tanstack/react-query";

const url = (path: string) => `http://localhost:8000${path}`;
export const qc = new QueryClient();

export async function createGraph() {
  const r = await fetch(url("/graph"), { method: "POST" });
  return (await r.json()).graph_id as string;
}
export async function fetchGraph(gid: string) {
  const r = await fetch(url(`/graph/${gid}`));
  return r.json();
}
export async function upsertNode(gid: string, node: any) {
  await fetch(url(`/graph/${gid}/node`), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(node),
  });
}
export async function addEdge(gid: string, u: string, v: string) {
  await fetch(url(`/graph/${gid}/edge`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ u, v }),
  });
}
export async function toggleTag(
  gid: string,
  nid: string,
  tag: "hallway" | "elevator" | "full",
) {
  await fetch(url(`/graph/${gid}/node/${nid}/tag/${tag}`), {
    method: "PATCH",
  });
}
export async function transform(gid: string, payload: any) {
  await fetch(url(`/graph/${gid}/transform`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
