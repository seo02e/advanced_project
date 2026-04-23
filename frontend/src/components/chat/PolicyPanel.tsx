interface PolicyItem {
  title: string;
  category?: string;
  description?: string;
  eligibility?: string;
  benefit?: string;
  period?: string;
  link?: string;
}

interface PolicyPanelProps {
  policyData: PolicyItem[] | null;
}

export default function PolicyPanel({ policyData }: PolicyPanelProps) {
  const isEmpty = !policyData || policyData.length === 0;

  return (
    <div style={styles.panel}>
      {/* 패널 헤더 */}
      <div style={styles.panelHeader}>
        <span style={styles.headerIcon}>📋</span>
        <span style={styles.headerTitle}>관련 정책 정보</span>
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
          {policyData.map((item, i) => (
            <div key={i} style={styles.card}>
              {item.category && (
                <span style={styles.badge}>{item.category}</span>
              )}
              <h3 style={styles.cardTitle}>{item.title}</h3>

              {item.description && (
                <p style={styles.cardDesc}>{item.description}</p>
              )}

              {item.eligibility && (
                <div style={styles.infoRow}>
                  <span style={styles.infoLabel}>신청 대상</span>
                  <span style={styles.infoValue}>{item.eligibility}</span>
                </div>
              )}
              {item.benefit && (
                <div style={styles.infoRow}>
                  <span style={styles.infoLabel}>지원 내용</span>
                  <span style={styles.infoValue}>{item.benefit}</span>
                </div>
              )}
              {item.period && (
                <div style={styles.infoRow}>
                  <span style={styles.infoLabel}>신청 기간</span>
                  <span style={styles.infoValue}>{item.period}</span>
                </div>
              )}

              {item.link && (
                <a href={item.link} target="_blank" rel="noreferrer" style={styles.linkBtn}>
                  자세히 보기 →
                </a>
              )}
            </div>
          ))}
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

  /* 헤더 */
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

  /* 빈 상태 */
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

  /* 정책 카드 리스트 */
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
