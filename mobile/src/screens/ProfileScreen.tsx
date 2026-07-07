import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import { ActivityIndicator, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { api } from "@/api/client";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";
import type { CustomerProfile, RiskProfile } from "@/types";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

export function ProfileScreen() {
  const { session, logOut } = useSession();
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [risk, setRisk] = useState<RiskProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!session.customerId) return;
    try {
      const [profileRes, riskRes] = await Promise.all([
        api.getProfile(session.customerId),
        api.getRiskProfile(session.customerId),
      ]);
      setProfile(profileRes);
      setRisk(riskRes);
    } finally {
      setLoading(false);
    }
  }, [session.customerId]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

  if (loading || !profile) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.teal} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.avatarCircle}>
        <Text style={styles.avatarLetter}>{profile.name.charAt(0)}</Text>
      </View>
      <Text style={styles.name}>{profile.name}</Text>
      <Text style={styles.customerId}>{profile.customer_id}</Text>

      {risk ? (
        <View style={styles.riskCard}>
          <Text style={styles.riskLabel}>{risk.risk_label.toUpperCase()} INVESTOR</Text>
          <Text style={styles.riskConfidence}>{Math.round(risk.confidence * 100)}% model confidence</Text>
        </View>
      ) : null}

      <View style={styles.section}>
        <Row label="Age" value={String(profile.age)} />
        <Row label="Occupation" value={profile.occupation.replace("_", " ")} />
        <Row label="Dependents" value={String(profile.dependents)} />
        <Row label="Monthly income" value={`₹${profile.monthly_income.toLocaleString("en-IN")}`} />
        <Row label="Monthly savings" value={`₹${profile.monthly_savings.toLocaleString("en-IN")}`} />
        <Row label="Savings rate" value={`${Math.round(profile.savings_rate * 100)}%`} />
        <Row label="Current equity / debt mix" value={`${profile.equity_pct_current}% / ${profile.debt_pct_current}%`} />
        <Row label="SIP" value={profile.sip_active ? `₹${profile.sip_amount.toLocaleString("en-IN")}/mo` : "Not active"} />
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={logOut}>
        <Text style={styles.logoutText}>Log out</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 20, alignItems: "center", paddingBottom: 40 },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  avatarCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.orange,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 12,
  },
  avatarLetter: { color: colors.white, fontSize: 30, fontWeight: "700" },
  name: { fontSize: 20, fontWeight: "700", color: colors.dark, marginTop: 12 },
  customerId: { fontSize: 13, color: colors.gray, marginTop: 2 },
  riskCard: {
    backgroundColor: colors.teal,
    borderRadius: 16,
    paddingVertical: 14,
    paddingHorizontal: 24,
    alignItems: "center",
    marginTop: 20,
  },
  riskLabel: { color: colors.white, fontSize: 15, fontWeight: "700", letterSpacing: 0.5 },
  riskConfidence: { color: colors.orangeLight, fontSize: 12, marginTop: 4 },
  section: {
    width: "100%",
    backgroundColor: colors.white,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.lightGray,
    marginTop: 24,
    paddingHorizontal: 16,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.lightGray,
  },
  rowLabel: { fontSize: 14, color: colors.gray },
  rowValue: { fontSize: 14, color: colors.dark, fontWeight: "600", textTransform: "capitalize" },
  logoutButton: { marginTop: 28, paddingVertical: 12, paddingHorizontal: 24 },
  logoutText: { color: colors.danger, fontWeight: "700" },
});
