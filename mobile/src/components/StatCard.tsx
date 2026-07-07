import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/theme/colors";

export function StatCard({
  label,
  value,
  sub,
  accent = colors.teal,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <View style={[styles.card, { borderLeftColor: accent }]}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
      {sub ? <Text style={[styles.sub, { color: accent }]}>{sub}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: colors.white,
    borderRadius: 16,
    borderLeftWidth: 5,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 14,
  },
  label: { fontSize: 12, color: colors.gray, textTransform: "uppercase", letterSpacing: 0.5 },
  value: { fontSize: 22, fontWeight: "700", color: colors.dark, marginTop: 4 },
  sub: { fontSize: 12, marginTop: 4, fontWeight: "600" },
});
