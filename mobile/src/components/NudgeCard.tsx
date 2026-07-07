import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { severityColor } from "@/theme/colors";
import type { Nudge } from "@/types";

export function NudgeCard({ nudge }: { nudge: Nudge }) {
  const accent = severityColor(nudge.severity);
  return (
    <View style={[styles.card, { borderLeftColor: accent }]}>
      <Text style={styles.title}>{nudge.title}</Text>
      <Text style={styles.message}>{nudge.message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    borderLeftWidth: 5,
    borderWidth: 1,
    borderColor: "#E4E6E8",
    padding: 14,
    marginBottom: 10,
  },
  title: { fontSize: 14, fontWeight: "700", color: "#212529", marginBottom: 4 },
  message: { fontSize: 13, color: "#5A5A5A", lineHeight: 18 },
});
