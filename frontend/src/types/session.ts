export interface SessionCreateResponse {
  session_id: string;
  // 새로 생성된 세션의 고유 ID
  expires_in?: number;
  // 세션이 유지되는 시간 (초 단위, TTL)
  message?: string;
  // 세션 생성 관련 안내 메시지
}
// 새 세션을 만들때

export interface SessionInfoResponse {
  session_id: string;
  // 현재 세션 ID
  created_at?: string;
  // 세션 생성 시간
  last_accessed_at?: string;
  // 마지막으로 이 세션이 사용된 시간
}
// 기존 세션 조회할때
