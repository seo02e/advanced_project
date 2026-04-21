import { useEffect, useState } from "react";
import { createSession, deleteSession, getMySession } from "../api/sessionApi";

export function useSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const initSession = async () => {
    try {
      setLoading(true);
      setError(null);

      try {
        const session = await getMySession();
        setSessionId(session.session_id);
      } catch {
        const newSession = await createSession();
        setSessionId(newSession.session_id);
      }
    } catch {
      setError("세션을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const resetSession = async () => {
    try {
      await deleteSession();
      setSessionId(null);
      await initSession();
    } catch {
      setError("세션 초기화에 실패했습니다.");
    }
  };

  useEffect(() => {
    initSession();
  }, []);

  return {
    sessionId,
    loading,
    error,
    resetSession,
  };
}
