import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";

type FloorImg = { src: string; scale: number };
interface CanvasState {
  gid: string;
  floor: number;
  images: Record<number, FloorImg>;
  setImage: (floor: number, img: FloorImg) => void;
  setFloor: (f: number) => void;
}
export const useCanvas = create<CanvasState>()(
  subscribeWithSelector((set) => ({
    gid: "",
    floor: 0,
    images: {},
    setImage: (floor, img) =>
      set((s) => ({ images: { ...s.images, [floor]: img } })),
    setFloor: (f) => set({ floor: f }),
  })),
);
