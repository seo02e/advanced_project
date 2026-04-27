export type Role = "user" | "assistant";
// Role은 메시지의 주체를 나타내는 타입.
// "user" -> 사용자가 보낸 메시지
// "assistant" -> ai가 응답한 메시지
// 문자열을 검증하는 부분

export interface ChatMessage {
  role: "user" | "assistant";
  raw_text: string;
  data?: any;
}
// 하나의 채팅 메시지를 나타내는 데이터 구조
// role -> 누가 보낸 메시지인지 (user|assistant)
// raw_text -> 실제 메시지 내용 (텍스트)
// 예:
// { role: "user", raw_text: "안녕" }
// { role: "assistant", raw_text: "안녕하세요!" }

export interface ChatResponse {
  session_id: string;
  //현재 대화 세션 ID
  // (어떤 사용자/대화인지 구분하기 위한 값)

  saved_message?: ChatMessage;
  //사용자가 보낸 메시지 (?옵션)

  assistant_message?: ChatMessage;
  //AI가 생성한 응답 메시지 (?옵션)

  total_messages: number;
  //현재 세션에 저장된 전체 메시지 개수
}
// 서버에서 채팅 요청 후 응답으로 내려주는 데이터 구조
// ? (optional)이 붙은 이유: 상황에 따라 값이 없을 수도 있기 때문
