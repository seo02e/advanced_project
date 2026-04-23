interface FaqItem {
  question: string;
  answer: string;
  tag: string;
}

const FAQ_LIST: FaqItem[] = [
  {
    tag: "주거",
    question: "청년 월세 지원은 어떻게 신청하나요?",
    answer:
      "만 19~34세 무주택 청년이라면 월 최대 20만 원씩 최장 12개월간 월세를 지원받을 수 있어요. 복지로(bokjiro.go.kr) 또는 주민센터에서 신청 가능합니다.",
  },
  {
    tag: "취업",
    question: "청년 취업 장려금 대상이 되려면 어떤 조건인가요?",
    answer:
      "만 15~34세 구직자로, 중소·중견기업에 취업 후 6개월 이상 재직 시 최대 200만 원의 취업지원금을 지급받을 수 있어요. 고용24(work.go.kr)에서 신청하세요.",
  },
  {
    tag: "취업",
    question: "청년도약계좌는 누가 가입할 수 있나요?",
    answer:
      "만 19~34세이며 연 소득 7,500만 원 이하인 청년이라면 가입 가능해요. 매월 40~70만 원을 5년간 납입하면 정부 기여금과 비과세 혜택으로 최대 5,000만 원을 모을 수 있습니다.",
  },
];

const TAG_COLORS: Record<string, { bg: string; text: string }> = {
  주거: { bg: "#e0f2fe", text: "#0369a1" },
  취업: { bg: "#dcfce7", text: "#15803d" },
  금융: { bg: "#fef9c3", text: "#a16207" },
};

export default function FaqPanel() {
  return (
    <aside style={styles.panel}>
      {/* ── 배경 디자인 플레이스홀더 ── */}
      <div style={styles.bgPlaceholder} aria-hidden="true">
        {/* 추후 배경 이미지·그래픽 삽입 예정 */}
      </div>

      {/* ── 패널 콘텐츠 ── */}
      <div style={styles.content}>
        <div style={styles.header}>
          <span style={styles.headerIcon}>💡</span>
          <div>
            <div style={styles.headerTitle}>자주 묻는 질문</div>
            <div style={styles.headerSub}>청년들이 가장 많이 찾는 정책</div>
          </div>
        </div>

        <div style={styles.list}>
          {FAQ_LIST.map((item, i) => {
            const tagColor = TAG_COLORS[item.tag] ?? {
              bg: "#f1f5f9",
              text: "#475569",
            };
            return (
              <div key={i} style={styles.card}>
                {/* 번호 + 태그 */}
                <div style={styles.cardTop}>
                  <span style={styles.number}>0{i + 1}</span>
                  <span
                    style={{
                      ...styles.tag,
                      backgroundColor: tagColor.bg,
                      color: tagColor.text,
                    }}
                  >
                    {item.tag}
                  </span>
                </div>

                {/* 질문 */}
                <div style={styles.question}>
                  <span style={styles.qMark}>Q.</span>
                  {item.question}
                </div>

                {/* 구분선 */}
                <div style={styles.cardDivider} />

                {/* 답변 */}
                <div style={styles.answer}>
                  <span style={styles.aMark}>A.</span>
                  <span>{item.answer}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

const styles: Record<string, React.CSSProperties> = {
  panel: {
    position: "relative",
    height: "100%",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },

  /* 배경 영역 - 추후 디자인 삽입 예정 */
  bgPlaceholder: {
    position: "absolute",
    inset: 0,
    backgroundColor: "#1e293b",
    zIndex: 0,
    /* 여기에 backgroundImage, gradient 등 추후 삽입 */
  },

  /* 콘텐츠 (배경 위에 올라옴) */
  content: {
    position: "relative",
    zIndex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    padding: "24px 20px",
    height: "100%",
    overflowY: "auto",
    scrollbarWidth: "none" as React.CSSProperties["scrollbarWidth"],
  },

  /* 헤더 */
  header: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  headerIcon: {
    fontSize: "22px",
    marginTop: "2px",
  },
  headerTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#ffffff",
    letterSpacing: "-0.2px",
  },
  headerSub: {
    fontSize: "11px",
    color: "rgba(255,255,255,0.45)",
    marginTop: "2px",
    letterSpacing: "0.2px",
  },

  /* 카드 리스트 */
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },

  card: {
    backgroundColor: "rgba(255,255,255,0.07)",
    backdropFilter: "blur(8px)",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: "14px",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },

  cardTop: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  number: {
    fontSize: "11px",
    fontWeight: 700,
    color: "rgba(255,255,255,0.25)",
    letterSpacing: "1px",
  },
  tag: {
    fontSize: "10px",
    fontWeight: 700,
    padding: "2px 8px",
    borderRadius: "20px",
    letterSpacing: "0.3px",
  },

  /* 질문 */
  question: {
    fontSize: "12px",
    fontWeight: 600,
    color: "#ffffff",
    lineHeight: "1.55",
    display: "flex",
    gap: "5px",
  },
  qMark: {
    color: "#6baffc",
    fontWeight: 800,
    flexShrink: 0,
  },

  cardDivider: {
    height: "1px",
    backgroundColor: "rgba(255,255,255,0.08)",
  },

  /* 답변 */
  answer: {
    fontSize: "11px",
    color: "rgba(255,255,255,0.6)",
    lineHeight: "1.7",
    display: "flex",
    gap: "5px",
  },
  aMark: {
    color: "#93c5fd",
    fontWeight: 700,
    flexShrink: 0,
  },
};
