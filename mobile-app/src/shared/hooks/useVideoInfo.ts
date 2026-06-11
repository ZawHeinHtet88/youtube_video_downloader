import { useState, useCallback } from "react";
import { fetchVideoInfo, VideoInfo } from "../../api/video";

export function useVideoInfo() {
  const [info, setInfo] = useState<VideoInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (url: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchVideoInfo(url);
      setInfo(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || "Failed to fetch video info");
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setInfo(null);
    setError(null);
  }, []);

  return { info, loading, error, load, reset };
}
