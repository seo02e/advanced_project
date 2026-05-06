import type { CSSProperties } from "react";
import type { Policy } from "../../types/chat";
import { dedupePolicies } from "../../utils/policyDedup";
import { formatStatusLabel, formatStatusText } from "../../utils/statusLabels";

interface PolicyPanelProps {
  policyData: Policy[] | null;
}

export default function PolicyPanel({ policyData }: PolicyPanelProps) {
  const policies = dedupePolicies(policyData ?? []);
  const isEmpty = policies.length === 0;

  return (
    <div style={styles.panel}>
      <div style={styles.panelHeader}>
        <span style={styles.headerIcon}>📌</span>
        <span style={styles.headerTitle}>추천 정책 후보</span>
      </div>

      {isEmpty ? (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>📄</div>
          <p style={styles.emptyTitle}>아직 추천 정책이 없습니다</p>
          <p style={styles.emptyDesc}>
            질문을 입력하면 조건에 맞는 정책 후보가 이곳에 표시됩니다.
          </p>
        </div>
      ) : (
        <div style={styles.list}>
          {policies.map((item, index) => (
            <PolicyCard key={item.policy_id ?? `${getPolicyName(item)}-${index}`} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function PolicyCard({ item }: { item: Policy }) {
  const name = getPolicyName(item);
  const typeLabel = [item.support_type ?? item.policy_type, item.category ?? item.field]
    .filter(Boolean)
    .join(" / ");
  const rawStatus = item.eligibility_status ?? item.apply_status ?? item.status;
  const status = rawStatus ? formatStatusLabel(rawStatus) : undefined;
  const reason = item.recommend_reason ?? item.short_reason ?? item.reason;
  const missingInfo = [...(item.missing_requirements ?? []), ...(item.need_more_info ?? [])].map(
    formatStatusText,
  );
  const sourceLabel = getSourceLabel(item.source_layer);
  const url = item.source_url ?? item.url;

  return (
    <article style={styles.card}>
      <div style={styles.badgeRow}>
        {typeLabel && <span style={styles.badge}>{typeLabel}</span>}
        <span style={styles.sourceBadge}>{sourceLabel}</span>
      </div>

      <h3 style={styles.cardTitle}>{name}</h3>

      {item.summary && <p style={styles.cardDesc}>{formatStatusText(item.summary)}</p>}

      {status && (
        <div style={styles.infoRow}>
          <span style={styles.infoLabel}>상태</span>
          <span style={styles.infoValue}>{status}</span>
        </div>
      )}

      {reason && (
        <div style={styles.infoRow}>
          <span style={styles.infoLabel}>추천 이유</span>
          <span style={styles.infoValue}>{formatStatusText(reason)}</span>
        </div>
      )}

      {missingInfo.length > 0 && (
        <div style={styles.infoBlock}>
          <span style={styles.infoLabel}>추가 확인</span>
          <div style={styles.chipRow}>
            {missingInfo.map((value, index) => (
              <span key={`${value}-${index}`} style={styles.chip}>
                {value}
              </span>
            ))}
          </div>
        </div>
      )}

      {url && (
        <a href={url} target="_blank" rel="noreferrer" style={styles.linkBtn}>
          자세히 보기
        </a>
      )}
    </article>
  );
}

function getPolicyName(item: Policy) {
  return item.policy_name ?? item.title ?? item.name ?? "정책명 확인 필요";
}

function getSourceLabel(sourceLayer?: Policy["source_layer"]) {
  if (sourceLayer === "A") {
    return "공공 API";
  }

  if (sourceLayer === "B") {
    return "공고문 기반";
  }

  return "출처 확인 필요";
}

const styles: Record<string, CSSProperties> = {
  panel: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    gap: "0",
  },
  panelHeader: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "16px",
    paddingBottom: "12px",
    borderBottom: "2px solid #e2e8f0",
  },
  headerIcon: {
    fontSize: "18px",
  },
  headerTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#1e293b",
  },
  emptyState: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px 16px",
    gap: "10px",
    backgroundColor: "#ffffff",
    borderRadius: "16px",
    border: "1px dashed #cbd5e1",
  },
  emptyIcon: {
    fontSize: "32px",
    opacity: 0.5,
  },
  emptyTitle: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#64748b",
    margin: 0,
  },
  emptyDesc: {
    fontSize: "12px",
    color: "#94a3b8",
    textAlign: "center",
    lineHeight: "1.7",
    margin: 0,
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    overflowY: "auto",
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: "14px",
    padding: "16px",
    border: "1px solid #e2e8f0",
    boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  badgeRow: {
    display: "flex",
    gap: "6px",
    flexWrap: "wrap",
  },
  badge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "20px",
    backgroundColor: "#eff6ff",
    color: "#2563eb",
    fontSize: "11px",
    fontWeight: 600,
    width: "fit-content",
  },
  sourceBadge: {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "20px",
    backgroundColor: "#f8fafc",
    color: "#475569",
    fontSize: "11px",
    fontWeight: 600,
    width: "fit-content",
  },
  cardTitle: {
    fontSize: "14px",
    fontWeight: 800,
    color: "#1e293b",
    margin: 0,
    lineHeight: 1.45,
  },
  cardDesc: {
    fontSize: "12px",
    color: "#64748b",
    lineHeight: "1.65",
    margin: 0,
  },
  infoRow: {
    display: "grid",
    gridTemplateColumns: "72px 1fr",
    gap: "8px",
    fontSize: "12px",
  },
  infoBlock: {
    display: "grid",
    gridTemplateColumns: "72px 1fr",
    gap: "8px",
    fontSize: "12px",
  },
  infoLabel: {
    color: "#94a3b8",
    fontWeight: 700,
    flexShrink: 0,
  },
  infoValue: {
    color: "#475569",
    lineHeight: "1.55",
  },
  chipRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "6px",
  },
  chip: {
    padding: "3px 8px",
    borderRadius: "999px",
    backgroundColor: "#fff7ed",
    color: "#c2410c",
    fontSize: "11px",
    fontWeight: 600,
  },
  linkBtn: {
    display: "inline-block",
    width: "fit-content",
    marginTop: "2px",
    fontSize: "12px",
    fontWeight: 700,
    color: "#2563eb",
    textDecoration: "none",
  },
};
