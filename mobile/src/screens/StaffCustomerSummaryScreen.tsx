import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "@/api/client";
import { OpportunityScoreCard } from "@/components/OpportunityScoreCard";
import { useSession } from "@/context/SessionContext";
import { colors, engagementColor } from "@/theme/colors";
import type { StaffCustomerSummary } from "@/types";
import type { StaffStackParamList } from "@/navigation/RootNavigator";

type Props = NativeStackScreenProps<StaffStackParamList, "StaffCustomerSummary">;

export function StaffCustomerSummaryScreen({ route }: Props) {
  const { customerId, name } = route.params;
  const { session } = useSession();
  const [summary, setSummary] = useState<StaffCustomerSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!session.staffToken) return;
    setError(null);
    try {
      setSummary(await api.getStaffCustomerSummary(session.staffToken, customerId));
    } catch (e) {
      setError("Couldn't load this customer's summary.");
    } finally {
      setLoading(false);
    }
  }, [session.staffToken, customerId]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  if (loading || !summary) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.teal} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.name}>{summary.name ?? name}</Text>
      <Text style={styles.meta}>{summary.age} · {summary.occupation.replace(/_/g, " ")} · {summary.customer_id}</Text>

      <View style={styles.engagementCard}>
        <Text style={styles.engagementLabel}>Engagement</Text>
        <View style={styles.engagementRow}>
          <View style={[styles.engagementDot, { backgroundColor: engagementColor(summary.engagement.level) }]} />
          <Text style={styles.engagementValue}>{summary.engagement.level}</Text>
        </View>
        <Text style={styles.engagementSub}>
          {summary.engagement.total_interactions} interaction(s) with Saarthi
          {summary.engagement.days_since_last_active !== null
            ? ` · last active ${summary.engagement.days_since_last_active}d ago`
            : ""}
        </Text>
      </View>

      <Text style={styles.sectionTitle}>Sales opportunities</Text>
      <Text style={styles.topOpportunity}>{summary.top_opportunity}</Text>
      {summary.opportunities.map((o) => (
        <OpportunityScoreCard key={o.product} opportunity={o} />
      ))}

      <View style={styles.privacyBanner}>
        <Text style={styles.privacyText}>🔒 {summary.chat_access_note}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 20, paddingBottom: 40 },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  name: { fontSize: 22, fontWeight: "700", color: colors.dark },
  meta: { fontSize: 13, color: colors.gray, marginTop: 4, textTransform: "capitalize" },
  engagementCard: {
    backgroundColor: colors.tealDark,
    borderRadius: 16,
    padding: 16,
    marginTop: 16,
  },
  engagementLabel: { color: colors.orangeLight, fontSize: 12, fontWeight: "700", textTransform: "uppercase" },
  engagementRow: { flexDirection: "row", alignItems: "center", marginTop: 6 },
  engagementDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  engagementValue: { color: colors.white, fontSize: 20, fontWeight: "700" },
  engagementSub: { color: colors.orangeLight, fontSize: 12, marginTop: 6 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.dark, marginTop: 24, marginBottom: 4 },
  topOpportunity: { fontSize: 13, color: colors.gray, marginBottom: 12, lineHeight: 18 },
  privacyBanner: {
    backgroundColor: colors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 14,
    marginTop: 16,
  },
  privacyText: { fontSize: 12, color: colors.gray, lineHeight: 18 },
});
