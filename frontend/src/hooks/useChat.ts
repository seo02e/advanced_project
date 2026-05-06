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
      const assistantMessage = normalizeMessage(response?.assistant_message);

      if (assistantMessage) {
        setMessages((prev) => [...prev, assistantMessage]);
      }

      const data = normalizeChatData(assistantMessage?.data ?? response?.answer);
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
    return history.map(normalizeMessage).filter((message): message is ChatMessage => Boolean(message));
  }

  if (
    history &&
    typeof history === "object" &&
    "messages" in history &&
    Array.isArray(history.messages)
  ) {
    return history.messages
      .map(normalizeMessage)
      .filter((message): message is ChatMessage => Boolean(message));
  }

  return [];
}

function normalizeMessage(message: unknown): ChatMessage | null {
  if (!message || typeof message !== "object") {
    return null;
  }

  const candidate = message as Partial<ChatMessage>;
  const role = candidate.role === "user" ? "user" : "assistant";
  const rawText = typeof candidate.raw_text === "string" ? candidate.raw_text : "";

  return {
    role,
    raw_text: rawText,
    data: normalizeChatData(candidate.data),
  };
}

function normalizeChatData(data: unknown): ChatData {
  return data && typeof data === "object" ? (data as ChatData) : {};
}

function selectPolicyPanelData(data: ChatData): Policy[] {
  const answerBlocks =
    data.answer_blocks && typeof data.answer_blocks === "object" ? data.answer_blocks : undefined;

  if (hasItems(answerBlocks?.recommended)) {
    return dedupePolicies(answerBlocks.recommended);
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
