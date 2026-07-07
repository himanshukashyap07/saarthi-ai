import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/theme/colors";
import type { Goal } from "@/types";

function formatINR(n: number): string {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  return `₹${n.toLocaleString("en-IN")}`;
}

export function GoalCard({ goal }: { goal: Goal }) {
  const barColor = goal.on_track ? colors.teal : colors.orange;
  return (
    <View style={styles.card}>
      <View style={styles.headerRow}>
        <Text style={styles.name}>{goal.name}</Text>
        <Text style={[styles.badge, { color: barColor }]}>
          {goal.on_track ? "On track" : "Needs attention"}
        </Text>
      </View>
      <Text style={styles.sub}>
        {formatINR(goal.current_amount)} of {formatINR(goal.target_amount)} target
      </Text>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${Math.min(goal.funded_pct, 100)}%`, backgroundColor: barColor }]} />
      </View>
      <Text style={[styles.pct, { color: barColor }]}>{goal.funded_pct}% funded</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 16,
    marginBottom: 14,
  },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  name: { fontSize: 17, fontWeight: "700", color: colors.dark },
  badge: { fontSize: 12, fontWeight: "700" },
  sub: { fontSize: 13, color: colors.gray, marginTop: 4 },
  track: { height: 10, borderRadius: 5, backgroundColor: colors.lightGray, marginTop: 12, overflow: "hidden" },
  fill: { height: "100%", borderRadius: 5 },
  pct: { fontSize: 13, fontWeight: "600", marginTop: 6 },
});
