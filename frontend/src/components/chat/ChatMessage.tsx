import type { ChatMessage as ChatMessageType } from "../../types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "12px",
      }}
    >
      <div
        style={{
          maxWidth: "65%",
          padding: "14px 18px",
          borderRadius: "20px",
          backgroundColor: isUser ? "#6baffc" : "#e5e7eb",
          color: isUser ? "#ffffff" : "#111827",
          fontSize: "14px",
          lineHeight: "1.6",
          boxShadow: "0 2px 6px rgba(0, 0, 0, 0.16)",
        }}
      >
        {message.raw_text}
      </div>
    </div>
  );
}
