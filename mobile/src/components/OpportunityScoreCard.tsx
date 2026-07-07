import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors, scoreColor } from "@/theme/colors";
import type { OpportunityScore } from "@/types";

export function OpportunityScoreCard({ opportunity }: { opportunity: OpportunityScore }) {
  const accent = scoreColor(opportunity.score);
  return (
    <View style={[styles.card, { borderLeftColor: accent }]}>
      <View style={styles.headerRow}>
        <Text style={styles.label}>{opportunity.label}</Text>
        <Text style={[styles.score, { color: accent }]}>{opportunity.score}%</Text>
      </View>
      <View style={styles.barTrack}>
        <View style={[styles.barFill, { width: `${opportunity.score}%`, backgroundColor: accent }]} />
      </View>
      <Text style={styles.rationale}>{opportunity.rationale}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: 14,
    borderLeftWidth: 5,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 14,
    marginBottom: 10,
  },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  label: { fontSize: 15, fontWeight: "700", color: colors.dark },
  score: { fontSize: 18, fontWeight: "700" },
  barTrack: { height: 6, borderRadius: 3, backgroundColor: colors.lightGray, marginTop: 8, overflow: "hidden" },
  barFill: { height: "100%", borderRadius: 3 },
  rationale: { fontSize: 12, color: colors.gray, marginTop: 8, lineHeight: 17 },
});
