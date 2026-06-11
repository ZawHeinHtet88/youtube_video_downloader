import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useVideoInfo } from "../../shared/hooks/useVideoInfo";
import { VideoCard } from "../../shared/components/VideoCard";
import { useStore } from "../../store/downloadStore";
import { RootStackParamList } from "../../navigation/AppNavigator";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Home">;
};

export function HomeScreen({ navigation }: Props) {
  const [url, setUrl] = useState("");
  const { info, loading, error, load } = useVideoInfo();
  const { setVideoInfo, setVideoUrl } = useStore();

  const handleFetch = () => {
    const trimmed = url.trim();
    if (!trimmed) {
      Alert.alert("Error", "Please enter a YouTube URL");
      return;
    }
    load(trimmed);
  };

  const handleNext = () => {
    if (info) {
      setVideoInfo(info);
      setVideoUrl(url.trim());
      navigation.navigate("Format");
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Text style={styles.label}>Paste YouTube URL</Text>
      <TextInput
        style={styles.input}
        placeholder="https://youtube.com/watch?v=..."
        placeholderTextColor="#555"
        value={url}
        onChangeText={setUrl}
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleFetch}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Fetch Video</Text>
        )}
      </TouchableOpacity>

      {error && <Text style={styles.error}>{error}</Text>}

      {info && (
        <View style={styles.preview}>
          <VideoCard
            title={info.title}
            thumbnail={info.thumbnail}
            duration={info.duration}
            uploader={info.uploader}
          />
          <Text style={styles.formatCount}>
            {info.formats.length} formats available
          </Text>

          <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
            <Text style={styles.buttonText}>Select Quality</Text>
          </TouchableOpacity>
        </View>
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, paddingTop: 60 },
  label: { color: "#eee", fontSize: 16, marginBottom: 8 },
  input: {
    backgroundColor: "#1e1e3a",
    color: "#eee",
    padding: 14,
    borderRadius: 10,
    fontSize: 15,
    borderWidth: 1,
    borderColor: "#333",
  },
  button: {
    backgroundColor: "#6366f1",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 12,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  error: { color: "#f87171", marginTop: 12, textAlign: "center" },
  preview: { marginTop: 20 },
  formatCount: { color: "#888", fontSize: 13, marginBottom: 12, textAlign: "center" },
  nextButton: {
    backgroundColor: "#22c55e",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
});
