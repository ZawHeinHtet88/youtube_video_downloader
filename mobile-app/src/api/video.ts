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
  url: string;
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

export interface CookieStatus {
  has_cookies: boolean;
  size_bytes: number;
}

export async function getCookieStatus(): Promise<CookieStatus> {
  const { data } = await api.get<CookieStatus>("/api/cookies");
  return data;
}

export async function uploadCookies(cookieText: string): Promise<CookieStatus> {
  const { data } = await api.post<CookieStatus>("/api/cookies", {
    cookies: cookieText,
  });
  return data;
}
