import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/theme/colors";

export function UserBubble({ text }: { text: string }) {
  return (
    <View style={styles.row}>
      <View style={styles.bubble}>
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", justifyContent: "flex-end", marginVertical: 6, paddingLeft: 48 },
  bubble: {
    backgroundColor: colors.orange,
    borderRadius: 18,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  text: { fontSize: 15, color: colors.white, lineHeight: 21 },
});
