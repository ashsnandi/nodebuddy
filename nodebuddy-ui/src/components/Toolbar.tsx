import { useHotkeys } from "react-hotkeys-hook";
import { useCanvas } from "../store";
import {
  toggleTag,
  transform,
  upsertNode,
  qc,
} from "../api";
import { useReactFlow, Node as RFNode } from "reactflow";
const { floor, setFloor } = useCanvas();



export default function Toolbar() {
  const rf = useReactFlow();
  const { gid } = useCanvas();

  // hot-key helpers
  const tag = (t: "hallway" | "elevator" | "full") => {
    const sel = rf.getNodes().find((n) => n.selected);
    if (!sel) return;
    toggleTag(gid, sel.id, t).then(() => qc.invalidateQueries(["graph", gid]));
  };
  useHotkeys("h", () => tag("hallway"));
  useHotkeys("e", () => tag("elevator"));
  useHotkeys("f", () => tag("full"));

  return (
    <div className="absolute left-2 top-2 z-10 flex gap-2">
         <button className="btn btn-xs" onClick={() => setFloor(floor - 1)}>
      ⬆ Floor
    </button>
    <button className="btn btn-xs" onClick={() => setFloor(floor + 1)}>
      ⬇ Floor
    </button>
      <label className="btn btn-xs">
        📁 Image
        <input
          type="file"
          hidden
          accept="image/*"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) =>
              useCanvas
                .getState()
                .setImage(
                  useCanvas.getState().floor,
                  { src: ev.target?.result as string, scale: 100 },
                );
            reader.readAsDataURL(file);
          }}
        />
      </label>
      <button
        className="btn btn-xs"
        onClick={() =>
          transform(gid, { type: "scale", factor: 1.2 }).then(() =>
            qc.invalidateQueries(["graph", gid])
          )}
      >
        + Scale
      </button>
      <button
        className="btn btn-xs"
        onClick={() =>
          transform(gid, { type: "scale", factor: 0.8 }).then(() =>
            qc.invalidateQueries(["graph", gid])
          )}
      >
        − Scale
      </button>
    </div>
  );
}
