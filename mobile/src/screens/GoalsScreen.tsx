import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { ActivityIndicator, RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "@/api/client";
import { GoalCard } from "@/components/GoalCard";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";
import type { Goal, Recommendation } from "@/types";

export function GoalsScreen() {
  const { session } = useSession();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!session.customerId) return;
    try {
      const [goalsRes, recRes] = await Promise.all([
        api.getGoals(session.customerId),
        api.getRecommendations(session.customerId),
      ]);
      setGoals(goalsRes);
      setRecommendation(recRes);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [session.customerId]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.teal} />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => {
            setRefreshing(true);
            load();
          }}
        />
      }
    >
      <Text style={styles.title}>Your Goals</Text>
      <Text style={styles.subtitle}>{goals.length} active</Text>

      {goals.map((g) => (
        <GoalCard key={g.id} goal={g} />
      ))}

      {recommendation ? (
        <View style={styles.recCard}>
          <Text style={styles.recTitle}>Recommended allocation ({recommendation.risk_label})</Text>
          <Text style={styles.recSplit}>
            {recommendation.recommended_equity_pct}% Equity / {recommendation.recommended_debt_pct}% Debt
          </Text>
          <Text style={styles.recRationale}>{recommendation.rationale}</Text>

          {recommendation.goal_suggestions
            .filter((s) => s.suggested_topup > 0)
            .map((s) => (
              <Text key={s.goal_id} style={styles.topupText}>
                • Increase '{s.goal_name}' contribution by ₹{s.suggested_topup.toLocaleString("en-IN")}/mo to stay on
                track at an assumed {s.assumed_annual_return_pct}% p.a. return.
              </Text>
            ))}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 20, paddingBottom: 40 },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  title: { fontSize: 26, fontWeight: "700", color: colors.dark },
  subtitle: { fontSize: 14, color: colors.gray, marginBottom: 20 },
  recCard: {
    backgroundColor: colors.white,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 16,
    marginTop: 8,
  },
  recTitle: { fontSize: 15, fontWeight: "700", color: colors.tealDark, textTransform: "capitalize" },
  recSplit: { fontSize: 20, fontWeight: "700", color: colors.dark, marginTop: 6 },
  recRationale: { fontSize: 13, color: colors.gray, marginTop: 8, lineHeight: 18 },
  topupText: { fontSize: 13, color: colors.dark, marginTop: 10, lineHeight: 18 },
});
