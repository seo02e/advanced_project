interface PolicyItem {
  policy_id?: string;
  policy_name?: string;
  source_layer?: "A" | "B" | string;
  short_reason?: string;
  recommend_reason?: string;
  support_type?: string;
  eligibility_status?: string;
  missing_requirements?: string[];
  apply_status?: string;
  source_url?: string;
  summary?: string;
}

interface PolicyPanelProps {
  policyData: PolicyItem[] | null;
}

export default function PolicyPanel({ policyData }: PolicyPanelProps) {
  const isEmpty = !policyData || policyData.length === 0;

  return (
    <div style={styles.panel}>
      <div style={styles.panelHeader}>
        <span style={styles.headerIcon}>📋</span>
        <span style={styles.headerTitle}>추천 정책 후보</span>
      </div>

      {isEmpty ? (
        <div style={styles.emptyState}>
          <div style={styles.emptyIcon}>🔍</div>
          <p style={styles.emptyTitle}>조회된 정책이 없습니다</p>
          <p style={styles.emptyDesc}>
            챗봇에게 궁금한 청년 지원 정책을 질문하면
            <br />
            관련 정책이 여기에 표시됩니다.
          </p>
        </div>
      ) : (
        <div style={styles.list}>
          {policyData.map((item, i) => {
            const reason = item.recommend_reason ?? item.short_reason;

            const sourceLabel =
              item.source_layer === "A"
                ? "온통청년 API 기반 정책"
                : item.source_layer === "B"
                  ? "LH 공고문 기반 정책"
                  : "출처 확인 필요";

            return (
              <div key={item.policy_id ?? i} style={styles.card}>
                <div style={styles.badgeRow}>
                  {item.support_type && (
                    <span style={styles.badge}>{item.support_type}</span>
                  )}
                  <span style={styles.sourceBadge}>{sourceLabel}</span>
                </div>

                <h3 style={styles.cardTitle}>{item.policy_name}</h3>

                {item.summary && <p style={styles.cardDesc}>{item.summary}</p>}

                {reason && (
                  <div style={styles.infoRow}>
                    <span style={styles.infoLabel}>추천 이유</span>
                    <span style={styles.infoValue}>{reason}</span>
                  </div>
                )}

                {item.eligibility_status && (
                  <div style={styles.infoRow}>
                    <span style={styles.infoLabel}>자격</span>
                    <span style={styles.infoValue}>
                      {item.eligibility_status}
                    </span>
                  </div>
                )}

                {item.missing_requirements &&
                  item.missing_requirements.length > 0 && (
                    <div style={styles.infoRow}>
                      <span style={styles.infoLabel}>부족 조건</span>
                      <span style={styles.infoValue}>
                        {item.missing_requirements.join(", ")}
                      </span>
                    </div>
                  )}

                {item.apply_status && (
                  <div style={styles.infoRow}>
                    <span style={styles.infoLabel}>상태</span>
                    <span style={styles.infoValue}>{item.apply_status}</span>
                  </div>
                )}

                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer"
                    style={styles.linkBtn}
                  >
                    자세히 보기 →
                  </a>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
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
    letterSpacing: "-0.2px",
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
    opacity: 0.4,
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
    gap: "8px",
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
    color: "#3b82f6",
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
    fontSize: "13px",
    fontWeight: 700,
    color: "#1e293b",
    margin: 0,
    lineHeight: 1.4,
  },
  cardDesc: {
    fontSize: "12px",
    color: "#64748b",
    lineHeight: "1.65",
    margin: 0,
  },
  infoRow: {
    display: "flex",
    gap: "8px",
    fontSize: "12px",
  },
  infoLabel: {
    color: "#94a3b8",
    fontWeight: 600,
    flexShrink: 0,
    width: "60px",
  },
  infoValue: {
    color: "#475569",
    lineHeight: "1.5",
  },
  linkBtn: {
    display: "inline-block",
    marginTop: "4px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#6baffc",
    textDecoration: "none",
  },
};
