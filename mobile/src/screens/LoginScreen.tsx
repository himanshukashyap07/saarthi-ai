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

const DEMO_CUSTOMER_ID = "SAARTHI100000";

export function LoginScreen({ onSwitchToStaff }: { onSwitchToStaff: () => void }) {
  const { logIn } = useSession();
  const [customerId, setCustomerId] = useState(DEMO_CUSTOMER_ID);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(customerId.trim());
      logIn(res.customer_id, res.name);
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
          <Text style={styles.avatarLetter}>N</Text>
        </View>
        <Text style={styles.title}>Saarthi</Text>
        <Text style={styles.subtitle}>Your AI wealth avatar, by IDBI Bank</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Customer ID</Text>
        <TextInput
          style={styles.input}
          value={customerId}
          onChangeText={setCustomerId}
          autoCapitalize="characters"
          autoCorrect={false}
          placeholder={DEMO_CUSTOMER_ID}
        />
        <Text style={styles.hint}>
          Seeded demo customer: {DEMO_CUSTOMER_ID}. This is a mock login for the
          prototype -- a real rollout sits behind IDBI's existing app authentication.
        </Text>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
          {loading ? <ActivityIndicator color={colors.white} /> : <Text style={styles.buttonText}>Continue</Text>}
        </TouchableOpacity>

        <TouchableOpacity style={styles.staffLink} onPress={onSwitchToStaff}>
          <Text style={styles.staffLinkText}>Sign in as bank staff instead</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.teal },
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
  title: { color: colors.white, fontSize: 32, fontWeight: "700" },
  subtitle: { color: colors.orangeLight, fontSize: 15, marginTop: 6 },
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
  hint: { fontSize: 12, color: colors.gray, marginTop: 10, lineHeight: 17 },
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
