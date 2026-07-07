import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/theme/colors";

export function AvatarBubble({ text, tag }: { text: string; tag?: string }) {
  return (
    <View style={styles.row}>
      <View style={styles.avatar}>
        <Text style={styles.avatarLetter}>N</Text>
      </View>
      <View style={styles.bubble}>
        {tag ? <Text style={styles.tag}>{tag}</Text> : null}
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", alignItems: "flex-end", marginVertical: 6, paddingRight: 48 },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.orange,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
  },
  avatarLetter: { color: colors.white, fontWeight: "700" },
  bubble: {
    backgroundColor: colors.lightGray,
    borderRadius: 18,
    paddingHorizontal: 16,
    paddingVertical: 10,
    flexShrink: 1,
  },
  tag: { fontSize: 11, color: colors.gray, marginBottom: 2 },
  text: { fontSize: 15, color: colors.dark, lineHeight: 21 },
});
