import { useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { getChatHistory, sendChatMessage } from "../api/chatApi";
import type { ChatData, ChatMessage, Policy } from "../types/chat";
import { dedupePolicies } from "../utils/policyDedup";

export function useChat(
  enabled: boolean,
  setPolicyData?: Dispatch<SetStateAction<Policy[]>>,
) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [sending, setSending] = useState<boolean>(false);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      setError(null);

      const history: unknown = await getChatHistory();
      const nextMessages = normalizeHistory(history);

      setMessages(nextMessages);
      const lastAssistant = [...nextMessages]
        .reverse()
        .find((message) => message.role === "assistant");

      if (lastAssistant?.data) {
        setPolicyData?.(selectPolicyPanelData(lastAssistant.data));
      }
    } catch {
      setMessages([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const sendMessage = async () => {
    const trimmedMessage = input.trim();

    if (!trimmedMessage || sending) return;

    const userMessage: ChatMessage = {
      role: "user",
      raw_text: trimmedMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);
    setError(null);

    try {
      const response = await sendChatMessage(trimmedMessage);
      const assistantMessage = response.assistant_message;

      if (assistantMessage) {
        setMessages((prev) => [...prev, assistantMessage]);
      }

      const data = (assistantMessage?.data ?? response.answer ?? {}) as ChatData;
      setPolicyData?.(selectPolicyPanelData(data));
    } catch (err) {
      console.error(err);
      setError("메시지 전송에 실패했습니다.");
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    if (enabled) {
      loadHistory();
    }
  }, [enabled]);

  return {
    messages,
    input,
    setInput,
    sendMessage,
    sending,
    loadingHistory,
    error,
  };
}

function normalizeHistory(history: unknown): ChatMessage[] {
  if (Array.isArray(history)) {
    return history as ChatMessage[];
  }

  if (
    history &&
    typeof history === "object" &&
    "messages" in history &&
    Array.isArray(history.messages)
  ) {
    return history.messages as ChatMessage[];
  }

  return [];
}

function selectPolicyPanelData(data: ChatData): Policy[] {
  if (hasItems(data.answer_blocks?.recommended)) {
    return dedupePolicies(data.answer_blocks.recommended);
  }

  if (hasItems(data.recommended_policies)) {
    return dedupePolicies(data.recommended_policies);
  }

  if (hasItems(data.retrieved_chunks)) {
    return dedupePolicies(data.retrieved_chunks);
  }

  return [];
}

function hasItems<T>(value: T[] | undefined): value is T[] {
  return Array.isArray(value) && value.length > 0;
}
