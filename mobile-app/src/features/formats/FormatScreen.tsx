import React from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useStore } from "../../store/downloadStore";
import { useDownload } from "../../shared/hooks/useDownload";
import { formatBytes } from "../../shared/utils/format";
import { VideoFormat } from "../../api/video";
import { RootStackParamList } from "../../navigation/AppNavigator";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Format">;
};

export function FormatScreen({ navigation }: Props) {
  const { videoInfo, videoUrl, selectedFormat, setSelectedFormat } = useStore();
  const { start, monitorProgress } = useDownload();

  if (!videoInfo) {
    return (
      <View style={styles.container}>
        <Text style={styles.empty}>No video info. Go back and fetch a video.</Text>
      </View>
    );
  }

  const handleDownload = async (fmt: VideoFormat) => {
    setSelectedFormat(fmt);
    const taskId = await start(videoUrl, fmt.format_id, videoInfo.title, videoInfo.thumbnail);
    monitorProgress(taskId);
    navigation.navigate("Downloads");
  };

  const renderItem = ({ item }: { item: VideoFormat }) => (
    <TouchableOpacity style={styles.row} onPress={() => handleDownload(item)}>
      <View style={styles.rowLeft}>
        <Text style={styles.label}>{item.label}</Text>
        <Text style={styles.detail}>
          {item.ext.toUpperCase()}
          {item.fps ? ` - ${item.fps}fps` : ""}
          {item.filesize_approx ? ` - ${formatBytes(item.filesize_approx)}` : ""}
        </Text>
      </View>
      <Text style={styles.arrow}>></Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title} numberOfLines={1}>
        {videoInfo.title}
      </Text>
      <FlatList
        data={videoInfo.formats}
        keyExtractor={(item) => item.format_id}
        renderItem={renderItem}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f23" },
  title: { color: "#aaa", fontSize: 14, padding: 16, paddingBottom: 8 },
  list: { paddingHorizontal: 16 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#1e1e3a",
    padding: 16,
    borderRadius: 10,
  },
  rowLeft: { flex: 1 },
  label: { color: "#eee", fontSize: 15, fontWeight: "600" },
  detail: { color: "#888", fontSize: 13, marginTop: 2 },
  arrow: { color: "#6366f1", fontSize: 18, fontWeight: "700" },
  separator: { height: 8 },
  empty: { color: "#888", textAlign: "center", marginTop: 60, padding: 20 },
});
