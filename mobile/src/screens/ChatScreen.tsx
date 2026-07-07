import React, { useRef, useState } from "react";
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { api } from "@/api/client";
import { AvatarBubble } from "@/components/AvatarBubble";
import { UserBubble } from "@/components/UserBubble";
import { useSession } from "@/context/SessionContext";
import { colors } from "@/theme/colors";
import type { ChatMessage } from "@/types";

let nextId = 0;
const genId = () => `${Date.now()}-${nextId++}`;

export function ChatScreen() {
  const { session } = useSession();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: genId(),
      role: "avatar",
      content: `Hi ${session.name ?? ""}! Ask me about your goals, risk profile, portfolio, or wealth health score.`,
      source: "fallback",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const listRef = useRef<FlatList<ChatMessage>>(null);

  const send = async () => {
    const text = input.trim();
    if (!text || !session.customerId || sending) return;

    const userMessage: ChatMessage = { id: genId(), role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const res = await api.sendChatMessage(session.customerId, text);
      setMessages((prev) => [
        ...prev,
        { id: genId(), role: "avatar", content: res.reply, source: res.source },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: genId(),
          role: "avatar",
          content: "I couldn't reach the wealth service just now -- please try again in a moment.",
          source: "fallback",
        },
      ]);
    } finally {
      setSending(false);
      setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
        renderItem={({ item }) =>
          item.role === "user" ? (
            <UserBubble text={item.content} />
          ) : (
            <AvatarBubble text={item.content} tag={item.source === "llm" ? "Saarthi (AI)" : "Saarthi"} />
          )
        }
      />

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Ask Saarthi about your wealth..."
          onSubmitEditing={send}
          returnKeyType="send"
        />
        <TouchableOpacity style={styles.sendButton} onPress={send} disabled={sending}>
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  list: { padding: 16 },
  inputRow: {
    flexDirection: "row",
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: colors.lightGray,
    backgroundColor: colors.white,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.lightGray,
    borderRadius: 22,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    marginRight: 8,
  },
  sendButton: {
    backgroundColor: colors.orange,
    borderRadius: 22,
    paddingHorizontal: 18,
    justifyContent: "center",
  },
  sendText: { color: colors.white, fontWeight: "700" },
});
