import React, { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { api, ApiError } from "@/api/client";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";

const DEMO_STAFF_ID = "STAFF001";
const DEMO_STAFF_PASSWORD = "saarthi-demo";

export function StaffLoginScreen({ onSwitchToCustomer }: { onSwitchToCustomer: () => void }) {
  const { logInAsStaff } = useSession();
  const [staffId, setStaffId] = useState(DEMO_STAFF_ID);
  const [password, setPassword] = useState(DEMO_STAFF_PASSWORD);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.staffLogin(staffId.trim(), password);
      logInAsStaff(res.token, res.name, res.branch);
    } catch (e) {
      const message = e instanceof ApiError ? e.message : "Could not reach the Saarthi backend. Is it running?";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <StatusBar style="light" />
      <View style={styles.hero}>
        <View style={styles.avatarCircle}>
          <Text style={styles.avatarLetter}>B</Text>
        </View>
        <Text style={styles.title}>Saarthi for Bank Staff</Text>
        <Text style={styles.subtitle}>Aggregated customer insights &amp; sales leads</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Staff ID</Text>
        <TextInput
          style={styles.input}
          value={staffId}
          onChangeText={setStaffId}
          autoCapitalize="characters"
          autoCorrect={false}
          placeholder={DEMO_STAFF_ID}
        />

        <Text style={[styles.label, { marginTop: 16 }]}>Password</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
        />

        <Text style={styles.hint}>
          Seeded demo login: {DEMO_STAFF_ID} / {DEMO_STAFF_PASSWORD}. Staff only ever
          see aggregated scores below -- never a customer's raw chat with Saarthi.
        </Text>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
          {loading ? <ActivityIndicator color={colors.white} /> : <Text style={styles.buttonText}>Continue</Text>}
        </TouchableOpacity>

        <TouchableOpacity style={styles.staffLink} onPress={onSwitchToCustomer}>
          <Text style={styles.staffLinkText}>Back to customer login</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.tealDark },
  hero: { alignItems: "center", marginTop: 96, marginBottom: 40 },
  avatarCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: colors.orange,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  avatarLetter: { color: colors.white, fontSize: 40, fontWeight: "700" },
  title: { color: colors.white, fontSize: 26, fontWeight: "700", textAlign: "center", paddingHorizontal: 24 },
  subtitle: { color: colors.orangeLight, fontSize: 14, marginTop: 6, textAlign: "center", paddingHorizontal: 24 },
  form: {
    flex: 1,
    backgroundColor: colors.white,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    padding: 24,
  },
  label: { fontSize: 13, color: colors.gray, marginBottom: 8, fontWeight: "600" },
  input: {
    borderWidth: 1,
    borderColor: colors.lightGray,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.dark,
  },
  hint: { fontSize: 12, color: colors.gray, marginTop: 14, lineHeight: 17 },
  error: { fontSize: 13, color: colors.danger, marginTop: 14 },
  button: {
    backgroundColor: colors.teal,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 24,
  },
  buttonText: { color: colors.white, fontSize: 16, fontWeight: "700" },
  staffLink: { alignItems: "center", marginTop: 18 },
  staffLinkText: { color: colors.teal, fontSize: 13, fontWeight: "600" },
});
