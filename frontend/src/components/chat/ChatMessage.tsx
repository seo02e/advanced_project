import type { ChatMessage as ChatMessageType } from "../../types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const data = message.data;

  return (
    <div
      style={{
        ...styles.row,
        justifyContent: isUser ? "flex-end" : "flex-start",
      }}
    >
      {!isUser && <div style={styles.avatar}>AI</div>}

      <div
        style={{
          ...styles.bubble,
          backgroundColor: isUser ? "#111827" : "#f8fafc",
          color: isUser ? "#ffffff" : "#1e293b",
          borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
        }}
      >
        {isUser || !data ? (
          <div>{message.raw_text}</div>
        ) : (
          <AssistantAnswer message={message} />
        )}
      </div>
    </div>
  );
}

function AssistantAnswer({ message }: { message: ChatMessageType }) {
  const data = message.data ?? {};
  const answerText = data.answer_text ?? message.raw_text;
  const needMoreInfo: string[] = data.need_more_info ?? [];
  const citations: any[] = data.citations ?? [];

  return (
    <div style={styles.answerWrap}>
      <div>
        <div style={styles.sectionTitle}>✅ 현재 판단</div>
        <div style={styles.answerText}>{answerText}</div>
      </div>

      {needMoreInfo.length > 0 && (
        <div style={styles.infoBox}>
          <div style={styles.sectionTitle}>⚠️ 추가 확인 필요</div>
          <div style={styles.chipRow}>
            {needMoreInfo.map((item, index) => (
              <span key={index} style={styles.chip}>
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {citations.length > 0 && (
        <div style={styles.infoBox}>
          <div style={styles.sectionTitle}>📚 출처</div>
          <div style={styles.sourceList}>
            {citations.slice(0, 3).map((item, index) => (
              <div key={index} style={styles.sourceItem}>
                {typeof item === "string"
                  ? item
                  : (item.source_url ?? item.title)}
              </div>
            ))}
          </div>
        </div>
      )}
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
    maxWidth: "72%",
    padding: "14px 16px",
    fontSize: "14px",
    lineHeight: "1.65",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    wordBreak: "break-word",
    whiteSpace: "pre-line",
  },
  answerWrap: {
    display: "flex",
    flexDirection: "column",
    gap: "14px",
  },
  sectionTitle: {
    fontSize: "13px",
    fontWeight: 800,
    color: "#334155",
    marginBottom: "6px",
  },
  answerText: {
    fontSize: "14px",
    lineHeight: "1.75",
    color: "#1e293b",
  },
  infoBox: {
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "12px",
  },
  chipRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "6px",
  },
  chip: {
    padding: "4px 9px",
    borderRadius: "999px",
    backgroundColor: "#eff6ff",
    color: "#2563eb",
    fontSize: "12px",
    fontWeight: 600,
  },
  sourceList: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  sourceItem: {
    fontSize: "12px",
    color: "#475569",
    lineHeight: "1.5",
  },
};
