import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import ChatMessage from "./ChatMessage";

interface ChatWindowProps {
  messages: ChatMessageType[];
}

export default function ChatWindow({ messages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const safeMessages = Array.isArray(messages) ? messages : [];

  return (
    <div style={styles.window}>
      {safeMessages.length === 0 && (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>💬</div>
          <p style={styles.emptyText}>
            청년 지원 정책에 대해 무엇이든 물어보세요.
          </p>
        </div>
      )}
      {safeMessages.map((message, index) => (
        <ChatMessage key={`${message.role}-${index}`} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  window: {
    flex: 1,
    overflowY: "auto",
    padding: "20px",
    borderRadius: "16px",
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    boxShadow: "0 1px 6px rgba(0,0,0,0.06)",
    /* 스크롤바 */
    scrollbarWidth: "thin",
  } as React.CSSProperties,
  empty: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    gap: "12px",
    opacity: 0.4,
  },
  emptyIcon: {
    fontSize: "36px",
  },
  emptyText: {
    fontSize: "14px",
    color: "#6b7280",
    margin: 0,
  },
};
