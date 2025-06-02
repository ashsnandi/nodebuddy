import { useCanvas } from "../store";

export default function ImageLayer() {
  const { floor, images } = useCanvas();
  const img = images[floor];
  if (!img) return null;
  return (
    <img
      src={img.src}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: `${img.scale * 100}%`,
        pointerEvents: "none",
        userSelect: "none",
        transformOrigin: "top left",
      }}
    />
  );
}
