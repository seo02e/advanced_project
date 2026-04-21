import type { KeyboardEvent } from "react";

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
}

export default function ChatInput({
  input,
  setInput,
  onSend,
  disabled,
}: ChatInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div
      style={{
        display: "flex",
        gap: "8px",
        marginTop: "12px",
      }}
    >
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="메시지를 입력하세요"
        rows={2}
        disabled={disabled}
        style={{
          flex: 1,
          resize: "none",
          padding: "12px",
          borderRadius: "12px",
          border: "1px solid #d3d3e4",
        }}
      />
      <button
        onClick={onSend}
        disabled={disabled || !input.trim()}
        style={{
          padding: "0 18px",
          borderRadius: "12px",
          border: "none",
          cursor: "pointer",
          backgroundColor: "#111827",
          color: "#ffffff",
        }}
      >
        전송
      </button>
    </div>
  );
}
