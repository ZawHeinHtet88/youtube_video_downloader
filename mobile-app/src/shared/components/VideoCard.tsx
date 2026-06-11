import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { formatDuration } from "../utils/format";

interface Props {
  title: string;
  thumbnail: string | null;
  duration: number | null;
  uploader: string | null;
}

export function VideoCard({ title, thumbnail, duration, uploader }: Props) {
  return (
    <View style={styles.card}>
      {thumbnail && (
        <View style={styles.thumbnailWrap}>
          <Image source={{ uri: thumbnail }} style={styles.thumbnail} />
          {duration != null && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{formatDuration(duration)}</Text>
            </View>
          )}
        </View>
      )}
      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={2}>
          {title}
        </Text>
        {uploader && (
          <Text style={styles.uploader} numberOfLines={1}>
            {uploader}
          </Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { marginBottom: 12 },
  thumbnailWrap: { position: "relative" },
  thumbnail: { width: "100%", aspectRatio: 16 / 9, backgroundColor: "#222" },
  badge: {
    position: "absolute",
    bottom: 8,
    right: 8,
    backgroundColor: "rgba(0,0,0,0.8)",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeText: { color: "#fff", fontSize: 12 },
  info: { marginTop: 8 },
  title: { color: "#eee", fontSize: 16, fontWeight: "600" },
  uploader: { color: "#888", fontSize: 13, marginTop: 2 },
});
