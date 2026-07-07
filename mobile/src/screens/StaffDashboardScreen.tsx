import React, { useCallback, useState } from "react";
import { useFocusEffect } from "@react-navigation/native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { api } from "@/api/client";
import { useSession } from "@/context/SessionContext";
import { colors, engagementColor, scoreColor } from "@/theme/colors";
import type { StaffCustomerListItem } from "@/types";
import type { StaffStackParamList } from "@/navigation/RootNavigator";

type Props = NativeStackScreenProps<StaffStackParamList, "StaffDashboard">;

export function StaffDashboardScreen({ navigation }: Props) {
  const { session, logOut } = useSession();
  const [customers, setCustomers] = useState<StaffCustomerListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!session.staffToken) return;
    setError(null);
    try {
      setCustomers(await api.getStaffCustomers(session.staffToken));
    } catch (e) {
      setError("Couldn't load the customer book. Pull down to retry.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [session.staffToken]);

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
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hi {session.name ?? "there"}</Text>
          <Text style={styles.subGreeting}>Saarthi Staff Console · Outreach opportunities</Text>
        </View>
        <TouchableOpacity onPress={logOut}>
          <Text style={styles.logout}>Log out</Text>
        </TouchableOpacity>
      </View>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <FlatList
        data={customers}
        keyExtractor={(item) => item.customer_id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => {
              setRefreshing(true);
              load();
            }}
          />
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.row}
            onPress={() => navigation.navigate("StaffCustomerSummary", { customerId: item.customer_id, name: item.name })}
          >
            <View style={styles.rowLeft}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.meta}>{item.age} · {item.occupation.replace(/_/g, " ")}</Text>
            </View>
            <View style={styles.rowRight}>
              <Text style={[styles.topScore, { color: scoreColor(item.top_product_score) }]}>
                {item.top_product_label} {item.top_product_score}%
              </Text>
              <View style={[styles.badge, { backgroundColor: engagementColor(item.engagement_level) }]}>
                <Text style={styles.badgeText}>{item.engagement_level}</Text>
              </View>
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={styles.emptyText}>No customers found.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  centered: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: 20,
    paddingBottom: 8,
  },
  greeting: { fontSize: 22, fontWeight: "700", color: colors.dark },
  subGreeting: { fontSize: 13, color: colors.gray, marginTop: 2 },
  logout: { color: colors.danger, fontWeight: "700", marginTop: 4 },
  error: { color: colors.danger, marginHorizontal: 20, marginBottom: 8 },
  list: { paddingHorizontal: 20, paddingBottom: 40 },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.white,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.lightGray,
    padding: 14,
    marginBottom: 10,
  },
  rowLeft: { flexShrink: 1 },
  name: { fontSize: 15, fontWeight: "700", color: colors.dark },
  meta: { fontSize: 12, color: colors.gray, marginTop: 2, textTransform: "capitalize" },
  rowRight: { alignItems: "flex-end" },
  topScore: { fontSize: 13, fontWeight: "700" },
  badge: { borderRadius: 8, paddingHorizontal: 8, paddingVertical: 3, marginTop: 6 },
  badgeText: { color: colors.white, fontSize: 11, fontWeight: "700" },
  emptyText: { color: colors.gray, fontSize: 13, textAlign: "center", marginTop: 40 },
});
