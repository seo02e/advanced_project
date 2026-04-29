import { useEffect, useState } from "react";
import { getChatHistory, sendChatMessage } from "../api/chatApi";
import type { ChatMessage } from "../types/chat";

export function useChat(
  enabled: boolean,
  setPolicyData?: React.Dispatch<React.SetStateAction<any[]>>,
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

      const history: any = await getChatHistory();

      if (Array.isArray(history)) {
        setMessages(history as ChatMessage[]);
      } else if (history && Array.isArray(history.messages)) {
        setMessages(history.messages);
      } else {
        setMessages([]);
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
      const response: any = await sendChatMessage(trimmedMessage);

      if (response.assistant_message) {
        setMessages((prev) => [...prev, response.assistant_message]);
      }

      const data = response.assistant_message?.data ?? response.answer ?? {};

      const policyPanelData =
        data.answer_blocks?.recommended?.length > 0
          ? data.answer_blocks.recommended
          : data.recommended_policies?.length > 0
            ? data.recommended_policies
            : [];

      setPolicyData?.(policyPanelData);
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
