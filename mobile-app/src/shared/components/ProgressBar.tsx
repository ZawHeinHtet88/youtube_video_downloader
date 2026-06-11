import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface Props {
  percent: number;
  height?: number;
  color?: string;
  showLabel?: boolean;
}

export function ProgressBar({
  percent,
  height = 8,
  color = "#4ade80",
  showLabel = true,
}: Props) {
  const clamped = Math.max(0, Math.min(100, percent));

  return (
    <View style={styles.container}>
      <View style={[styles.track, { height }]}>
        <View
          style={[
            styles.fill,
            { width: `${clamped}%`, backgroundColor: color, height },
          ]}
        />
      </View>
      {showLabel && (
        <Text style={styles.label}>{clamped.toFixed(1)}%</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { width: "100%" },
  track: {
    width: "100%",
    backgroundColor: "#333",
    borderRadius: 4,
    overflow: "hidden",
  },
  fill: { borderRadius: 4 },
  label: { color: "#aaa", fontSize: 12, marginTop: 2, textAlign: "right" },
});
