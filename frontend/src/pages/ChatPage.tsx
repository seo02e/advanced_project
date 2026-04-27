import { useState } from "react";
import ChatInput from "../components/chat/ChatInput";
import ChatWindow from "../components/chat/ChatWindow";
import PolicyPanel from "../components/chat/PolicyPanel";
import FaqPanel from "../components/chat/FaqPanel";
import { useChat } from "../hooks/useChat";
import { useSession } from "../hooks/useSession";

export default function ChatPage() {
  const [policyData, setPolicyData] = useState<any[]>([]); // ⭐ 추가

  const {
    sessionId,
    loading: sessionLoading,
    error: sessionError,
    resetSession,
  } = useSession();

  const {
    messages,
    input,
    setInput,
    sendMessage,
    sending,
    loadingHistory,
    error: chatError,
  } = useChat(!!sessionId, setPolicyData); // ⭐ 추가

  if (sessionLoading) {
    return (
      <div style={styles.loadingWrap}>
        <span style={styles.loadingText}>세션 불러오는 중...</span>
      </div>
    );
  }

  if (sessionError) {
    return (
      <div style={styles.loadingWrap}>
        <span style={{ color: "#e05" }}>{sessionError}</span>
      </div>
    );
  }

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.logoArea}>
            <span style={styles.logoIcon}>🏛</span>
            <div>
              <div style={styles.logoTitle}>AI 챗봇 서비스</div>
              <div style={styles.logoSub}>청년 지원 정책</div>
            </div>
          </div>
          <button onClick={resetSession} style={styles.newChatBtn}>
            + 새 대화
          </button>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.faqSection}>
          <FaqPanel />
        </div>

        <div style={styles.divider} />

        <section style={styles.chatSection}>
          {loadingHistory ? (
            <div style={styles.loadingInner}>대화 기록 불러오는 중...</div>
          ) : (
            <ChatWindow messages={messages} />
          )}

          {chatError && <div style={styles.errorBanner}>{chatError}</div>}

          <ChatInput
            input={input}
            setInput={setInput}
            onSend={sendMessage}
            disabled={sending}
          />
        </section>

        <div style={styles.divider} />

        {/* ⭐ 여기 핵심 수정 */}
        <aside style={styles.policySection}>
          <PolicyPanel policyData={policyData} />
        </aside>
      </main>
    </div>
  );
}

const HEADER_H = 64;

const styles: Record<string, React.CSSProperties> = {
  root: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    width: "100%",
    overflow: "hidden",
    backgroundColor: "#f0f4f8",
    fontFamily: "'Pretendard', 'Apple SD Gothic Neo', sans-serif",
    boxSizing: "border-box",
  },
  header: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    height: `${HEADER_H}px`,
    backgroundColor: "#111827",
    zIndex: 100,
    boxShadow: "0 2px 12px rgba(0,0,0,0.25)",
  },
  headerInner: {
    height: "100%",
    padding: "0 24px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  logoArea: { display: "flex", alignItems: "center", gap: "10px" },
  logoIcon: { fontSize: "22px" },
  logoTitle: {
    color: "#ffffff",
    fontSize: "15px",
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: "-0.3px",
  },
  logoSub: {
    color: "#6baffc",
    fontSize: "11px",
    fontWeight: 500,
    letterSpacing: "0.4px",
  },
  newChatBtn: {
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid rgba(255,255,255,0.15)",
    backgroundColor: "rgba(255,255,255,0.08)",
    color: "#ffffff",
    fontSize: "13px",
    fontWeight: 500,
    cursor: "pointer",
  },
  main: {
    display: "flex",
    flex: 1,
    marginTop: `${HEADER_H}px`,
    height: `calc(100vh - ${HEADER_H}px)`,
    overflow: "hidden",
  },
  faqSection: {
    flex: "0 0 20%",
    width: "20%",
    overflow: "hidden",
  },
  divider: {
    width: "1px",
    backgroundColor: "#d3d3e4",
    margin: "16px 0",
    flexShrink: 0,
  },
  chatSection: {
    flex: "0 0 50%",
    width: "50%",
    display: "flex",
    flexDirection: "column",
    padding: "20px",
    boxSizing: "border-box",
    overflow: "hidden",
  },
  policySection: {
    flex: "0 0 30%",
    width: "30%",
    padding: "20px 24px 20px 20px",
    boxSizing: "border-box",
    overflowY: "auto",
  },
  loadingWrap: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    width: "100%",
  },
  loadingText: { color: "#6b7280", fontSize: "15px" },
  loadingInner: { color: "#9ca3af", fontSize: "14px", padding: "20px 0" },
  errorBanner: {
    marginTop: "10px",
    padding: "10px 14px",
    borderRadius: "8px",
    backgroundColor: "#fee2e2",
    color: "#b91c1c",
    fontSize: "13px",
  },
};
