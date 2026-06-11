import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface Props {
  icon?: string;
  message: string;
}

export function EmptyState({ icon = "Nothing here yet", message }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>{icon}</Text>
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 32 },
  icon: { fontSize: 48, marginBottom: 16 },
  message: { color: "#888", fontSize: 15, textAlign: "center", lineHeight: 22 },
});
