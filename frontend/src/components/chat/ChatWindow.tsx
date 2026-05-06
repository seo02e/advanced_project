import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import ChatMessage from "./ChatMessage";

interface ChatWindowProps {
  messages: ChatMessageType[];
  onSelectExample: (question: string) => void;
  onFillInput: (draftText: string) => void;
}

const EXAMPLE_QUESTIONS = [
  "서울 27세 무주택 구직자인데 월세 지원 가능해?",
  "정규직인데 이직 준비 중이야. 취업 지원 대상이 되나?",
  "신청 마감 안 된 정책만 보고 싶어. 서울 거주 26세야",
];

export default function ChatWindow({
  messages,
  onSelectExample,
  onFillInput,
}: ChatWindowProps) {
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
            나이·지역·상황을 입력하면 가능한 청년정책 후보를 찾아드립니다.
          </p>
          <div style={styles.exampleRow}>
            {EXAMPLE_QUESTIONS.map((question) => (
              <button
                key={question}
                type="button"
                onClick={() => onSelectExample(question)}
                style={styles.exampleChip}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
      {safeMessages.map((message, index) => (
        <ChatMessage
          key={`${message.role}-${index}`}
          message={message}
          onFillInput={onFillInput}
        />
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
    padding: "24px",
    textAlign: "center",
  },
  emptyIcon: {
    fontSize: "36px",
    opacity: 0.45,
  },
  emptyText: {
    fontSize: "14px",
    color: "#6b7280",
    margin: 0,
    lineHeight: "1.65",
    maxWidth: "420px",
  },
  exampleRow: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: "8px",
    maxWidth: "560px",
    marginTop: "4px",
  },
  exampleChip: {
    border: "1px solid #dbeafe",
    borderRadius: "999px",
    backgroundColor: "#eff6ff",
    color: "#1d4ed8",
    padding: "7px 11px",
    fontSize: "12px",
    fontWeight: 700,
    fontFamily: "inherit",
    cursor: "pointer",
    lineHeight: "1.4",
    transition: "background-color 0.2s, border-color 0.2s",
  },
};
