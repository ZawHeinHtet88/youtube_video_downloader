import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { getCookieStatus, uploadCookies } from "../../api/video";
import { RootStackParamList } from "../../navigation/AppNavigator";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Settings">;
};

export function SettingsScreen({ navigation }: Props) {
  const [cookieText, setCookieText] = useState("");
  const [hasCookies, setHasCookies] = useState(false);
  const [cookieSize, setCookieSize] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const status = await getCookieStatus();
      setHasCookies(status.has_cookies);
      setCookieSize(status.size_bytes);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    const text = cookieText.trim();
    if (!text) {
      Alert.alert("Error", "Paste your cookies text first");
      return;
    }
    if (!text.startsWith("# Netscape")) {
      Alert.alert("Error", "Invalid format. Must start with '# Netscape HTTP Cookie File'");
      return;
    }

    setSaving(true);
    try {
      const status = await uploadCookies(text);
      setHasCookies(status.has_cookies);
      setCookieSize(status.size_bytes);
      setCookieText("");
      Alert.alert("Success", "Cookies saved! YouTube downloads should work now.");
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e.message || "Failed to save cookies";
      Alert.alert("Error", msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.statusCard}>
          <Text style={styles.statusLabel}>YouTube Cookies</Text>
          <Text style={[styles.statusValue, { color: hasCookies ? "#4ade80" : "#f87171" }]}>
            {loading ? "Checking..." : hasCookies ? `Active (${(cookieSize / 1024).toFixed(1)} KB)` : "Not configured"}
          </Text>
          <Text style={styles.statusHint}>
            {hasCookies
              ? "Cookies are set. Try fetching a video."
              : "Paste browser cookies to bypass YouTube bot detection."}
          </Text>
        </View>

        <Text style={styles.label}>How to get cookies:</Text>
        <Text style={styles.steps}>1. Install "Get cookies.txt LOCALLY" extension</Text>
        <Text style={styles.steps}>2. Go to youtube.com (make sure you're logged in)</Text>
        <Text style={styles.steps}>3. Click extension icon {"->"} Export</Text>
        <Text style={styles.steps}>4. Copy ALL the text below</Text>

        <Text style={[styles.label, { marginTop: 16 }]}>Paste cookies here:</Text>
        <TextInput
          style={styles.input}
          placeholder="# Netscape HTTP Cookie File\n.youtube.com TRUE / ..."
          placeholderTextColor="#555"
          value={cookieText}
          onChangeText={setCookieText}
          multiline
          autoCapitalize="none"
          autoCorrect={false}
          textAlignVertical="top"
        />

        <TouchableOpacity
          style={[styles.button, saving && styles.buttonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.buttonText}>
            {saving ? "Saving..." : "Save Cookies"}
          </Text>
        </TouchableOpacity>

        {hasCookies && (
          <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
            <Text style={styles.backButtonText}>Back to Home</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f23" },
  scroll: { padding: 20, paddingTop: 60 },
  statusCard: {
    backgroundColor: "#1e1e3a",
    padding: 16,
    borderRadius: 10,
    marginBottom: 20,
  },
  statusLabel: { color: "#eee", fontSize: 16, fontWeight: "600" },
  statusValue: { fontSize: 14, marginTop: 4 },
  statusHint: { color: "#888", fontSize: 12, marginTop: 4 },
  label: { color: "#eee", fontSize: 14, marginBottom: 8 },
  steps: { color: "#888", fontSize: 13, lineHeight: 20 },
  input: {
    backgroundColor: "#1e1e3a",
    color: "#eee",
    padding: 14,
    borderRadius: 10,
    fontSize: 13,
    borderWidth: 1,
    borderColor: "#333",
    height: 200,
    fontFamily: "monospace",
    marginBottom: 12,
  },
  button: {
    backgroundColor: "#6366f1",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  backButton: {
    padding: 14,
    alignItems: "center",
    marginTop: 12,
  },
  backButtonText: { color: "#6366f1", fontSize: 14 },
});
