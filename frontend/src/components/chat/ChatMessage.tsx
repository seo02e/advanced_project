import type { CSSProperties } from "react";
import type {
  AnswerBlocks,
  ChatMessage as ChatMessageType,
  Policy,
} from "../../types/chat";
import { getSourceDisplayLabel } from "../../utils/displayLabels";
import { dedupePolicies } from "../../utils/policyDedup";
import { formatStatusLabel, formatStatusText } from "../../utils/statusLabels";

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
        {isUser ? (
          <div>{message.raw_text}</div>
        ) : !hasAnswerBlocks ? (
          <div>{formatStatusText(message.raw_text)}</div>
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
    return <div>{formatStatusText(fallbackText)}</div>;
  }

  const recommended = dedupePolicies(answerBlocks.recommended);
  const needMoreInfo = (answerBlocks.need_more_info ?? []).map(formatStatusText);
  const policyPreviews = recommended.slice(0, 2).map(toPolicyPreview);
  const sources = collectSources(answerBlocks.sources, recommended);
  const summary = formatStatusText(answerBlocks.summary ?? fallbackText);
  const currentStatus = getCurrentStatus(recommended);
  const nextAction = answerBlocks.next_action
    ? formatNextActionText(answerBlocks.next_action)
    : undefined;

  return (
    <div style={styles.answerWrap}>
      {summary && (
        <section style={styles.section}>
          <div style={styles.sectionTitle}>✅ 현재 판단</div>
          <p style={styles.answerText}>{summary}</p>
        </section>
      )}

      <div style={styles.summaryBar}>
        <span style={styles.summaryPill}>후보 {recommended.length}건</span>
        <span style={styles.summaryPill}>추가 확인 {needMoreInfo.length}개</span>
        <span style={styles.summaryPill}>현재 상태: {currentStatus}</span>
      </div>

      <section style={styles.infoBox}>
        <div style={styles.sectionTitle}>📌 추천 정책 후보</div>
        <p style={styles.mutedText}>
          {recommended.length > 0
            ? `${recommended.length}개의 정책 후보를 찾았습니다. 상세 목록은 오른쪽 추천 정책 후보 패널에서 확인하세요.`
            : "아직 추천 정책 후보가 없습니다. 조건을 조금 더 알려주면 후보를 좁힐 수 있습니다."}
        </p>
        {policyPreviews.length > 0 && (
          <div style={styles.previewBox}>
            <div style={styles.previewTitle}>추천 정책 미리보기</div>
            <div style={styles.previewList}>
              {policyPreviews.map((preview, index) => (
                <div key={`${preview.name}-${index}`} style={styles.previewItem}>
                  <strong style={styles.previewName}>{preview.name}</strong>
                  {preview.reason && <span>: {preview.reason}</span>}
                </div>
              ))}
            </div>
          </div>
        )}
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

      {nextAction && (
        <section style={styles.nextActionBox}>
          <div style={styles.sectionTitle}>➡️ 다음 행동</div>
          <p style={styles.answerText}>{nextAction}</p>
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
      label: `${index}. ${getSourceDisplayLabel(url.hostname)}`,
    };
  } catch {
    return {
      label: `${index}. ${value.length > 72 ? `${value.slice(0, 69)}...` : value}`,
    };
  }
}

function toPolicyPreview(policy: Policy) {
  const name = policy.policy_name ?? policy.name ?? policy.title ?? "정책명 확인 필요";
  const rawReason = policy.short_reason ?? policy.recommend_reason ?? policy.reason ?? "";

  return {
    name,
    reason: truncateText(formatStatusText(rawReason), 64),
  };
}

function getCurrentStatus(policies: Policy[]) {
  const statuses = policies
    .map((policy) => policy.eligibility_status ?? policy.status)
    .filter(isString)
    .map(formatStatusLabel);

  if (statuses.includes("지원 가능성 높음")) {
    return "지원 가능성 높음";
  }

  if (statuses.includes("가능성 있음")) {
    return "가능성 있음";
  }

  if (statuses.includes("대상 아님")) {
    return "대상 아님";
  }

  return "확인 필요";
}

function truncateText(value: string, maxLength: number) {
  const normalized = value.replace(/\s+/g, " ").trim();
  return normalized.length > maxLength ? `${normalized.slice(0, maxLength - 3)}...` : normalized;
}

function formatNextActionText(value: string) {
  const formatted = formatStatusText(value);
  const genericMessage =
    "추가 확인 항목을 입력하면 지원 가능성 높음 / 가능성 있음 / 확인 필요 / 대상 아님 범위를 더 좁힐 수 있습니다.";

  return formatted.includes(genericMessage)
    ? formatted.replace(
        genericMessage,
        "나이, 지역, 소득수준을 알려주시면 각 정책의 가능성을 더 정확히 좁혀드릴 수 있습니다.",
      )
    : formatted;
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
  summaryBar: {
    display: "flex",
    flexWrap: "wrap",
    gap: "6px",
    padding: "10px 12px",
    borderRadius: "12px",
    backgroundColor: "#ffffff",
    border: "1px solid #dbeafe",
  },
  summaryPill: {
    padding: "4px 9px",
    borderRadius: "999px",
    backgroundColor: "#eff6ff",
    color: "#1d4ed8",
    fontSize: "12px",
    fontWeight: 700,
    lineHeight: 1.4,
  },
  infoBox: {
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "12px",
  },
  previewBox: {
    marginTop: "10px",
    paddingTop: "10px",
    borderTop: "1px solid #e2e8f0",
  },
  previewTitle: {
    fontSize: "12px",
    fontWeight: 800,
    color: "#475569",
    marginBottom: "6px",
  },
  previewList: {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
  },
  previewItem: {
    fontSize: "12px",
    lineHeight: "1.55",
    color: "#475569",
  },
  previewName: {
    color: "#1e293b",
    fontWeight: 800,
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
