import type { CSSProperties } from "react";
import type {
  AnswerBlocks,
  ChatMessage as ChatMessageType,
  Policy,
} from "../../types/chat";
import { dedupePolicies } from "../../utils/policyDedup";

interface ChatMessageProps {
  message: ChatMessageType;
}

interface SourceLink {
  label: string;
  href?: string;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const hasAnswerBlocks = Boolean(message.data?.answer_blocks);

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
          maxWidth: isUser ? "72%" : "82%",
          backgroundColor: isUser ? "#111827" : "#f8fafc",
          color: isUser ? "#ffffff" : "#1e293b",
          borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
          whiteSpace: isUser || !hasAnswerBlocks ? "pre-line" : "normal",
        }}
      >
        {isUser || !hasAnswerBlocks ? (
          <div>{message.raw_text}</div>
        ) : (
          <AssistantAnswer
            answerBlocks={message.data?.answer_blocks}
            fallbackText={message.data?.answer_text ?? message.raw_text}
          />
        )}
      </div>
    </div>
  );
}

function AssistantAnswer({
  answerBlocks,
  fallbackText,
}: {
  answerBlocks?: AnswerBlocks;
  fallbackText: string;
}) {
  if (!answerBlocks) {
    return <div>{fallbackText}</div>;
  }

  const recommended = dedupePolicies(answerBlocks.recommended);
  const needMoreInfo = answerBlocks.need_more_info ?? [];
  const sources = collectSources(answerBlocks.sources, recommended);
  const summary = answerBlocks.summary ?? fallbackText;

  return (
    <div style={styles.answerWrap}>
      {summary && (
        <section style={styles.section}>
          <div style={styles.sectionTitle}>✅ 현재 판단</div>
          <p style={styles.answerText}>{summary}</p>
        </section>
      )}

      <section style={styles.infoBox}>
        <div style={styles.sectionTitle}>📌 추천 정책 후보</div>
        <p style={styles.mutedText}>
          {recommended.length > 0
            ? `${recommended.length}개의 정책 후보를 찾았습니다. 상세 목록은 오른쪽 추천 정책 후보 패널에서 확인하세요.`
            : "아직 추천 정책 후보가 없습니다. 조건을 조금 더 알려주면 후보를 좁힐 수 있습니다."}
        </p>
      </section>

      {needMoreInfo.length > 0 && (
        <section style={styles.infoBox}>
          <div style={styles.sectionTitle}>⚠️ 추가 확인 필요</div>
          <div style={styles.chipRow}>
            {needMoreInfo.map((item, index) => (
              <span key={`${item}-${index}`} style={styles.chip}>
                {item}
              </span>
            ))}
          </div>
        </section>
      )}

      {sources.length > 0 && (
        <section style={styles.infoBox}>
          <div style={styles.sectionTitle}>📚 참고한 대표 출처</div>
          <div style={styles.sourceList}>
            {sources.map((source, index) =>
              source.href ? (
                <a
                  key={`${source.href}-${index}`}
                  href={source.href}
                  target="_blank"
                  rel="noreferrer"
                  style={styles.sourceLink}
                >
                  {source.label}
                </a>
              ) : (
                <span key={`${source.label}-${index}`} style={styles.sourceItem}>
                  {source.label}
                </span>
              ),
            )}
          </div>
        </section>
      )}

      {answerBlocks.next_action && (
        <section style={styles.nextActionBox}>
          <div style={styles.sectionTitle}>➡️ 다음 행동</div>
          <p style={styles.answerText}>{answerBlocks.next_action}</p>
        </section>
      )}
    </div>
  );
}

function collectSources(sources: string[] = [], policies: Policy[] = []): SourceLink[] {
  const seen = new Set<string>();
  const values = [
    ...sources,
    ...policies.map((policy) => policy.source_url ?? policy.url).filter(isString),
  ];

  return values.reduce<SourceLink[]>((acc, value) => {
    const normalized = value.trim();
    if (!normalized || seen.has(normalized) || acc.length >= 3) {
      return acc;
    }

    seen.add(normalized);
    acc.push(toSourceLink(normalized, acc.length + 1));
    return acc;
  }, []);
}

function toSourceLink(value: string, index: number): SourceLink {
  try {
    const url = new URL(value);
    return {
      href: value,
      label: `${index}. ${url.hostname.replace(/^www\./, "")}`,
    };
  } catch {
    return {
      label: `${index}. ${value.length > 72 ? `${value.slice(0, 69)}...` : value}`,
    };
  }
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

const styles: Record<string, CSSProperties> = {
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
    padding: "14px 16px",
    fontSize: "14px",
    lineHeight: "1.65",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    wordBreak: "break-word",
  },
  answerWrap: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  section: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  sectionTitle: {
    fontSize: "13px",
    fontWeight: 800,
    color: "#334155",
    marginBottom: "2px",
  },
  answerText: {
    fontSize: "14px",
    lineHeight: "1.75",
    color: "#1e293b",
    margin: 0,
  },
  mutedText: {
    fontSize: "13px",
    lineHeight: "1.65",
    color: "#475569",
    margin: 0,
  },
  infoBox: {
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "12px",
  },
  nextActionBox: {
    backgroundColor: "#f0f9ff",
    border: "1px solid #bae6fd",
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
  sourceLink: {
    fontSize: "12px",
    color: "#2563eb",
    lineHeight: "1.5",
    textDecoration: "none",
    overflowWrap: "anywhere",
  },
};
