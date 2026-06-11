import { api } from "./client";

export interface VideoFormat {
  format_id: string;
  ext: string;
  resolution: string | null;
  fps: number | null;
  vcodec: string | null;
  acodec: string | null;
  filesize_approx: number | null;
  label: string;
}

export interface VideoInfo {
  title: string;
  thumbnail: string | null;
  duration: number | null;
  uploader: string | null;
  formats: VideoFormat[];
}

export async function fetchVideoInfo(url: string): Promise<VideoInfo> {
  const { data } = await api.post<VideoInfo>("/api/video/info", { url });
  return data;
}

export async function startDownload(
  url: string,
  formatId: string
): Promise<string> {
  const { data } = await api.post<{ task_id: string }>("/api/download", {
    url,
    format_id: formatId,
  });
  return data.task_id;
}

export function getFileUrl(taskId: string): string {
  return `${api.defaults.baseURL}/api/download/${taskId}/file`;
}

export function getProgressUrl(taskId: string): string {
  return `${api.defaults.baseURL}/api/download/${taskId}/progress`;
}
