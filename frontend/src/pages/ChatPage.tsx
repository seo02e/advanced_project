import ChatInput from "../components/chat/ChatInput";
import ChatWindow from "../components/chat/ChatWindow";
import { useChat } from "../hooks/useChat";
import { useSession } from "../hooks/useSession";

export default function ChatPage() {
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
  } = useChat(!!sessionId);

  if (sessionLoading) {
    return <div style={{ padding: "20px" }}>세션 불러오는 중...</div>;
  }

  if (sessionError) {
    return <div style={{ padding: "20px" }}>{sessionError}</div>;
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "40px 20px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
        }}
      >
        <h1>AI 챗봇 서비스 - 청년 지원 정책</h1>
        <button
          onClick={resetSession}
          style={{
            padding: "10px 14px",
            borderRadius: "10px",
            border: "none",
            backgroundColor: "#111827",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          새 대화
        </button>
      </div>

      {loadingHistory ? (
        <div>대화 기록 불러오는 중...</div>
      ) : (
        <ChatWindow messages={messages} />
      )}

      {chatError && (
        <div style={{ marginTop: "12px", color: "crimson" }}>{chatError}</div>
      )}

      <ChatInput
        input={input}
        setInput={setInput}
        onSend={sendMessage}
        disabled={sending}
      />
    </div>
  );
}
