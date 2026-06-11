import React from "react";
import { View, FlatList, StyleSheet } from "react-native";
import { useStore } from "../../store/downloadStore";
import { DownloadCard } from "./DownloadCard";
import { EmptyState } from "../../shared/components/EmptyState";

export function DownloadsScreen() {
  const { activeDownloads } = useStore();

  return (
    <View style={styles.container}>
      <FlatList
        data={activeDownloads}
        keyExtractor={(item) => item.taskId}
        renderItem={({ item }) => <DownloadCard download={item} />}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <EmptyState message="No active downloads. Go paste a YouTube URL!" />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f23" },
  list: { padding: 16, flexGrow: 1 },
});
