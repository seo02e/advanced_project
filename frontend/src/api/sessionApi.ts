import { api } from "./axios";
// 공통 axios 인스턴스 불러오기

import type {
  SessionCreateResponse,
  SessionInfoResponse,
} from "../types/session";
// 세션 관련 api / create, get

// 새로운 세션 생성하는 함수
export const createSession = async (): Promise<SessionCreateResponse> => {
  // 반환값: session_id, expires_in, message 등
  const response = await api.post("/session/");
  // POST /session 요청 → 서버에서 세션 생성
  // 이때 서버가 Set-Cookie로 session_id를 내려줌
  return response.data;
  // 실제 응답 데이터 반환
};

// 현재 사용자 세션 정보를 조회하는 함수
export const getMySession = async (): Promise<SessionInfoResponse> => {
  const response = await api.get("/session/me");
  // GET /session/me 요청
  // 브라우저가 쿠키(session_id)를 자동으로 포함해서 보냄 (withCredentials 덕분)
  return response.data;
  // session_id, created_at, last_accessed_at 등 반환
};

// 현재 세션을 삭제(로그아웃)하는 함수
export const deleteSession = async (): Promise<void> => {
  await api.delete("/session/");
  // DELETE /session 요청
  // 서버에서 해당 session_id를 제거 (Redis 등에서 삭제)
};
