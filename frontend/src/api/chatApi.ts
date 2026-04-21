import { api } from "./axios";
// 공통 axios 인스턴스 가져오기
// baseURL, 쿠키 설정 등이 이미 포함된 상태

import type { ChatResponse } from "../types/chat";
// 채팅 api 응답 타입을 import
// Typescript에서 응답 데이터 구조를 명확히 하기 위해 사용
export const getChatHistory = async (): Promise<any> => {
  // 채팅 히스토리를 가져오는 함수
  // 현재 반환 타입이 any라서 타입 안정성이 없음
  const response = await api.get("/chat/history");
  //GET요청으로 채팅 기록을 서버에서 가져옴
  return response.data;
  // axios는 response 객체 안에 data가 실제 응답값이기 때문에
  // data만 꺼내서 반환
};

export const sendChatMessage = async (
  message: string,
  //사용자가 입력한 채팅 텍스트
): Promise<ChatResponse> => {
  // 사용자 메시지를 서버로 보내는 함수
  // 반환값은 ChatResponse 타입
  const response = await api.post("/chat/", { message });
  // POST 요청으로 메시지를 서버에 전달
  // body에 { message: "사용자입력값"} 형태로 전송됨
  return response.data;
  //서버에서 받은 응답 데이터 반환
};
