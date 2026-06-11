import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { ActiveDownload } from "../../store/downloadStore";
import { ProgressBar } from "../../shared/components/ProgressBar";
import { formatSpeed, formatETA } from "../../shared/utils/format";

interface Props {
  download: ActiveDownload;
}

const STATUS_COLORS: Record<string, string> = {
  downloading: "#4ade80",
  merging: "#facc15",
  completed: "#22d3ee",
  failed: "#f87171",
  cancelled: "#a78bfa",
};

export function DownloadCard({ download }: Props) {
  const color = STATUS_COLORS[download.status] || "#888";

  return (
    <View style={styles.card}>
      {download.thumbnail && (
        <Image source={{ uri: download.thumbnail }} style={styles.thumb} />
      )}
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={2}>
          {download.title}
        </Text>

        <ProgressBar percent={download.percent} color={color} height={6} />

        <View style={styles.meta}>
          <Text style={[styles.status, { color }]}>{download.status}</Text>
          {download.speed != null && (
            <Text style={styles.speed}>{formatSpeed(download.speed)}</Text>
          )}
          {download.eta != null && (
            <Text style={styles.eta}>ETA {formatETA(download.eta)}</Text>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    backgroundColor: "#1e1e3a",
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
  },
  thumb: { width: 80, height: 60, borderRadius: 6, backgroundColor: "#333" },
  content: { flex: 1, marginLeft: 12 },
  title: { color: "#eee", fontSize: 14, fontWeight: "500", marginBottom: 6 },
  meta: { flexDirection: "row", marginTop: 4, gap: 10 },
  status: { fontSize: 12, fontWeight: "600" },
  speed: { color: "#888", fontSize: 12 },
  eta: { color: "#888", fontSize: 12 },
});
