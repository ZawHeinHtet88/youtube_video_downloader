import { create } from "zustand";
import { VideoFormat, VideoInfo } from "../api/video";

export interface ActiveDownload {
  taskId: string;
  title: string;
  url: string;
  thumbnail: string | null;
  status: "downloading" | "completed" | "failed" | "cancelled";
  percent: number;
  filePath: string | null;
  formatId: string;
}

interface AppState {
  videoInfo: VideoInfo | null;
  videoUrl: string;
  selectedFormat: VideoFormat | null;
  activeDownloads: ActiveDownload[];

  setVideoInfo: (info: VideoInfo | null) => void;
  setVideoUrl: (url: string) => void;
  setSelectedFormat: (fmt: VideoFormat | null) => void;
  addDownload: (dl: ActiveDownload) => void;
  updateDownload: (taskId: string, updates: Partial<ActiveDownload>) => void;
  removeDownload: (taskId: string) => void;
}

export const useStore = create<AppState>((set) => ({
  videoInfo: null,
  videoUrl: "",
  selectedFormat: null,
  activeDownloads: [],

  setVideoInfo: (info) => set({ videoInfo: info }),
  setVideoUrl: (url) => set({ videoUrl: url }),
  setSelectedFormat: (fmt) => set({ selectedFormat: fmt }),

  addDownload: (dl) =>
    set((s) => ({ activeDownloads: [dl, ...s.activeDownloads] })),

  updateDownload: (taskId, updates) =>
    set((s) => ({
      activeDownloads: s.activeDownloads.map((d) =>
        d.taskId === taskId ? { ...d, ...updates } : d
      ),
    })),

  removeDownload: (taskId) =>
    set((s) => ({
      activeDownloads: s.activeDownloads.filter((d) => d.taskId !== taskId),
    })),
}));
