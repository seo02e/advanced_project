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
    <div style={styles.wrap}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="메시지를 입력하세요  (Shift+Enter로 줄바꿈)"
        rows={2}
        disabled={disabled}
        style={styles.textarea}
      />
      <button
        onClick={onSend}
        disabled={disabled || !input.trim()}
        style={{
          ...styles.sendBtn,
          opacity: disabled || !input.trim() ? 0.45 : 1,
          cursor: disabled || !input.trim() ? "not-allowed" : "pointer",
        }}
      >
        {disabled ? (
          <span style={styles.spinner} />
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        )}
      </button>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    display: "flex",
    alignItems: "flex-end",
    gap: "10px",
    marginTop: "14px",
    padding: "12px 14px",
    borderRadius: "16px",
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    boxShadow: "0 1px 6px rgba(0,0,0,0.06)",
  },
  textarea: {
    flex: 1,
    resize: "none",
    border: "none",
    outline: "none",
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#1e293b",
    backgroundColor: "transparent",
    fontFamily: "inherit",
    padding: "2px 0",
  },
  sendBtn: {
    width: "40px",
    height: "40px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#111827",
    color: "#ffffff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    transition: "opacity 0.2s",
  },
  spinner: {
    display: "inline-block",
    width: "14px",
    height: "14px",
    border: "2px solid rgba(255,255,255,0.3)",
    borderTop: "2px solid #fff",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
  } as React.CSSProperties,
};
