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
    <div
      style={{
        height: "70vh",
        overflowY: "auto",
        padding: "20px",
        borderRadius: "20px",
        backgroundColor: "#f8fafc",
        border: "1px solid #d3d3e4",
      }}
    >
      {safeMessages.map((message, index) => (
        <ChatMessage key={`${message.role}-${index}`} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
