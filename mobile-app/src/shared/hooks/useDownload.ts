import { useRef } from "react";
import { useStore } from "../../store/downloadStore";
import * as FileSystem from "expo-file-system";
import * as MediaLibrary from "expo-media-library";

let downloadCounter = 0;

export function useDownload() {
  const { addDownload, updateDownload, removeDownload } = useStore();
  const resumableRef = useRef<FileSystem.DownloadResumable | null>(null);

  const start = async (
    url: string,
    title: string,
    thumbnail: string | null,
    formatId: string,
    ext: string
  ) => {
    downloadCounter++;
    const taskId = `dl_${Date.now()}_${downloadCounter}`;
    const safeName = title.replace(/[<>:"/\\|?*]/g, "_").substring(0, 100);
    const filename = `${safeName}.${ext}`;
    const fileUri = FileSystem.documentDirectory + filename;

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

    const resumable = FileSystem.createDownloadResumable(
      url,
      fileUri,
      {},
      (downloadProgress) => {
        const { totalBytesWritten, totalBytesExpectedToWrite } = downloadProgress;
        const percent = totalBytesExpectedToWrite > 0
          ? (totalBytesWritten / totalBytesExpectedToWrite) * 100
          : 0;

        updateDownload(taskId, {
          percent,
          speed: null,
          eta: null,
        });
      }
    );

    resumableRef.current = resumable;

    try {
      const result = await resumable.downloadAsync();
      if (result) {
        await saveToMediaLibrary(result.uri, title);
        updateDownload(taskId, {
          filePath: result.uri,
          status: "completed",
          percent: 100,
        });
      }
    } catch (e: any) {
      if (e?.message === "Download cancelled") {
        updateDownload(taskId, { status: "cancelled" });
      } else {
        updateDownload(taskId, { status: "failed", percent: 0 });
      }
    }

    return taskId;
  };

  const cancel = async () => {
    if (resumableRef.current) {
      await resumableRef.current.cancelAsync();
      resumableRef.current = null;
    }
  };

  return { start, cancel };
}

async function saveToMediaLibrary(uri: string, title: string) {
  try {
    const { status } = await MediaLibrary.requestPermissionsAsync();
    if (status === "granted") {
      await MediaLibrary.createAssetAsync(uri);
    }
  } catch {
    // Silently fail - file still saved in app's document directory
  }
}
