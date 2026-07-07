import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { api } from "@/api/client";
import { NudgeCard } from "@/components/NudgeCard";
import { StatCard } from "@/components/StatCard";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";
import type { Nudge, WealthSummary } from "@/types";

function formatINR(n: number): string {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)}Cr`;
  if (n >= 100000) return `₹${(n / 100000).toFixed(1)}L`;
  return `₹${n.toLocaleString("en-IN")}`;
}

export function HomeScreen() {
  const { session } = useSession();
  const [summary, setSummary] = useState<WealthSummary | null>(null);
  const [nudges, setNudges] = useState<Nudge[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!session.customerId) return;
    setError(null);
    try {
      const [summaryRes, nudgesRes] = await Promise.all([
        api.getWealthSummary(session.customerId),
        api.getNudges(session.customerId),
      ]);
      setSummary(summaryRes);
      setNudges(nudgesRes);
    } catch (e) {
      setError("Couldn't load your wealth summary. Pull down to retry.");
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
      <Text style={styles.greeting}>Hi {session.name ?? "there"}</Text>
      <Text style={styles.subGreeting}>Saarthi · your wealth avatar</Text>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {summary ? (
        <>
          <View style={styles.scoreCard}>
            <Text style={styles.scoreLabel}>Wealth Health Score</Text>
            <Text style={styles.scoreValue}>{summary.wealth_health_score}/100</Text>
            <View style={styles.breakdownRow}>
              {Object.entries(summary.health_score_breakdown).map(([key, value]) => (
                <View key={key} style={styles.breakdownItem}>
                  <Text style={styles.breakdownValue}>{value}</Text>
                  <Text style={styles.breakdownLabel}>{key.replace("_", " ")}</Text>
                </View>
              ))}
            </View>
          </View>

          <View style={styles.statRow}>
            <StatCard label="Portfolio" value={formatINR(summary.portfolio_value)} sub={`Saving ${formatINR(summary.monthly_savings)}/mo`} />
            <View style={{ width: 12 }} />
            <StatCard
              label="SIP Health"
              value={summary.sip_status}
              accent={summary.sip_status === "Healthy" ? colors.teal : colors.orange}
            />
          </View>
        </>
      ) : null}

      <Text style={styles.sectionTitle}>Nudges from Saarthi</Text>
      {nudges.length === 0 ? (
        <Text style={styles.emptyText}>No nudges right now -- you're on track.</Text>
      ) : (
        nudges.map((n, i) => <NudgeCard key={`${n.type}-${i}`} nudge={n} />)
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 20, paddingBottom: 40 },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  greeting: { fontSize: 26, fontWeight: "700", color: colors.dark },
  subGreeting: { fontSize: 14, color: colors.gray, marginBottom: 20 },
  error: { color: colors.danger, marginBottom: 12 },
  scoreCard: {
    backgroundColor: colors.teal,
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
  },
  scoreLabel: { color: colors.orangeLight, fontSize: 13, fontWeight: "600" },
  scoreValue: { color: colors.white, fontSize: 36, fontWeight: "700", marginTop: 4 },
  breakdownRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 16 },
  breakdownItem: { alignItems: "center", flex: 1 },
  breakdownValue: { color: colors.white, fontSize: 16, fontWeight: "700" },
  breakdownLabel: { color: colors.orangeLight, fontSize: 10, marginTop: 2, textTransform: "capitalize", textAlign: "center" },
  statRow: { flexDirection: "row", marginBottom: 24 },
  sectionTitle: { fontSize: 17, fontWeight: "700", color: colors.dark, marginBottom: 10 },
  emptyText: { color: colors.gray, fontSize: 13 },
});
