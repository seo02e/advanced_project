import type { ChatMessage as ChatMessageType } from "../../types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        ...styles.row,
        justifyContent: isUser ? "flex-end" : "flex-start",
      }}
    >
      {/* AI 아바타 */}
      {!isUser && <div style={styles.avatar}>AI</div>}

      <div
        style={{
          ...styles.bubble,
          backgroundColor: isUser ? "#111827" : "#f1f5f9",
          color: isUser ? "#ffffff" : "#1e293b",
          borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
        }}
      >
        {message.raw_text}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  row: {
    display: "flex",
    alignItems: "flex-end",
    gap: "8px",
    marginBottom: "12px",
  },
  avatar: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    backgroundColor: "#6baffc",
    color: "#fff",
    fontSize: "10px",
    fontWeight: 700,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  bubble: {
    maxWidth: "68%",
    padding: "12px 16px",
    fontSize: "14px",
    lineHeight: "1.65",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    wordBreak: "break-word",
    whiteSpace: "pre-line",
  },
};
