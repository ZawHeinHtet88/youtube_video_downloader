import AsyncStorage from "@react-native-async-storage/async-storage";

export interface DownloadRecord {
  id: string;
  title: string;
  taskId: string;
  url: string;
  filePath: string;
  completedAt: number;
}

const STORAGE_KEY = "download_history";

export async function getHistory(): Promise<DownloadRecord[]> {
  const raw = await AsyncStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function addHistory(record: DownloadRecord): Promise<void> {
  const history = await getHistory();
  history.unshift(record);
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, 100)));
}

export async function clearHistory(): Promise<void> {
  await AsyncStorage.removeItem(STORAGE_KEY);
}
