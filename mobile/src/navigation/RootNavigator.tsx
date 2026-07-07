import React, { useState } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Text } from "react-native";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";
import { LoginScreen } from "@/screens/LoginScreen";
import { StaffLoginScreen } from "@/screens/StaffLoginScreen";
import { HomeScreen } from "@/screens/HomeScreen";
import { GoalsScreen } from "@/screens/GoalsScreen";
import { ChatScreen } from "@/screens/ChatScreen";
import { ProfileScreen } from "@/screens/ProfileScreen";
import { StaffDashboardScreen } from "@/screens/StaffDashboardScreen";
import { StaffCustomerSummaryScreen } from "@/screens/StaffCustomerSummaryScreen";

const Tab = createBottomTabNavigator();
const StaffStack = createNativeStackNavigator<StaffStackParamList>();

export type StaffStackParamList = {
  StaffDashboard: undefined;
  StaffCustomerSummary: { customerId: string; name: string };
};

const TAB_ICONS: Record<string, string> = {
  Home: "H",
  Goals: "G",
  Talk: "T",
  Profile: "P",
};

function TabIcon({ route, color }: { route: string; color: string }) {
  return <Text style={{ fontSize: 14, fontWeight: "700", color }}>{TAB_ICONS[route] ?? "•"}</Text>;
}

function AppTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.teal,
        tabBarInactiveTintColor: colors.gray,
        tabBarIcon: ({ color }) => <TabIcon route={route.name} color={color} />,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Goals" component={GoalsScreen} />
      <Tab.Screen name="Talk" component={ChatScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

function StaffApp() {
  return (
    <StaffStack.Navigator screenOptions={{ headerTintColor: colors.dark, headerStyle: { backgroundColor: colors.white } }}>
      <StaffStack.Screen name="StaffDashboard" component={StaffDashboardScreen} options={{ headerShown: false }} />
      <StaffStack.Screen
        name="StaffCustomerSummary"
        component={StaffCustomerSummaryScreen}
        options={({ route }) => ({ title: route.params.name })}
      />
    </StaffStack.Navigator>
  );
}

function AuthGate() {
  const [mode, setMode] = useState<"customer" | "staff">("customer");
  return mode === "customer" ? (
    <LoginScreen onSwitchToStaff={() => setMode("staff")} />
  ) : (
    <StaffLoginScreen onSwitchToCustomer={() => setMode("customer")} />
  );
}

export function RootNavigator() {
  const { session } = useSession();

  return (
    <NavigationContainer>
      {session.role === "customer" ? <AppTabs /> : session.role === "staff" ? <StaffApp /> : <AuthGate />}
    </NavigationContainer>
  );
}
