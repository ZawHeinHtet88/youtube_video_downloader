import { useEffect, useRef, useState } from "react";
import { startDownload, getProgressUrl, getFileUrl } from "../../api/video";
import { useStore } from "../../store/downloadStore";
import * as FileSystem from "expo-file-system";

export function useDownload() {
  const { addDownload, updateDownload } = useStore();
  const [progressUrl, setProgressUrl] = useState<string | null>(null);
  const eventSourceRef = useRef<any>(null);

  const start = async (url: string, formatId: string, title: string, thumbnail: string | null) => {
    const taskId = await startDownload(url, formatId);

    addDownload({
      taskId,
      title,
      url,
      thumbnail,
      status: "downloading",
      percent: 0,
      speed: null,
      eta: null,
      filePath: null,
      formatId,
    });

    return taskId;
  };

  const monitorProgress = (taskId: string) => {
    const url = getProgressUrl(taskId);

    const poll = async () => {
      try {
        const res = await fetch(url);
        const reader = res.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader!.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = JSON.parse(line.slice(6));
              updateDownload(taskId, {
                status: data.status,
                percent: data.percent || 0,
                speed: data.speed,
                eta: data.eta,
                filePath: data.filename || null,
              });

              if (data.status === "completed") {
                downloadToDevice(taskId, data.filename);
              }
              if (["completed", "failed", "cancelled"].includes(data.status)) {
                return;
              }
            }
          }
        }
      } catch (e) {
        updateDownload(taskId, { status: "failed", percent: 0 });
      }
    };

    poll();
  };

  const downloadToDevice = async (taskId: string, serverPath: string) => {
    try {
      const fileUrl = getFileUrl(taskId);
      const filename = serverPath.split(/[/\\]/).pop() || "video.mp4";
      const localUri = FileSystem.documentDirectory + filename;

      const { uri } = await FileSystem.downloadAsync(fileUrl, localUri);
      updateDownload(taskId, { filePath: uri, status: "completed", percent: 100 });
    } catch (e) {
      updateDownload(taskId, { status: "failed" });
    }
  };

  return { start, monitorProgress };
}
