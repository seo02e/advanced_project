from fastapi import HTTPException
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService


# 채팅 관련 비즈니스 로직 담당
class ChatService:
    def __init__(self):
        self.repo = SessionRepository() #직접 redis에 접근해서 데이터 꺼내는 담당
        self.session_service = SessionService() # 세션 관련 함수

    # 사용자가 보낸 메시지 하나를 저장하는 핵심 함수
    def save_user_message(self, session_id: str, user_message: str) -> dict:
        # 세션 유효성 검사 + TTL 연장
        self.session_service.touch_session(session_id)

        # 1. 원문 메시지 저장
        message_data = {
            "role": "user",
            "raw_text": user_message
        }
        self.repo.append_message(session_id, message_data)

        # 2. 현재 state 업데이트
        current_state = self.repo.get_state(session_id)

        if not current_state:
            current_state = {
                "age": None,
                "region": None,
                "employment_status": None,
                "housing_status": None,
                "income_level": None,
                "interest_tags": [],
                "unknown_fields": [],
                "raw_text": ""
            }

        #raw_text를 파라미터로 정리
        current_state["raw_text"] = user_message
        self.repo.save_state(session_id, current_state)

        # 3. 전체 메시지 개수 반환
        messages = self.repo.get_messages(session_id)

        return {
            "session_id": session_id,
            "saved_message": message_data,
            "total_messages": len(messages)
        }

    def get_chat_history(self, session_id: str) -> list[dict]:
        self.session_service.touch_session(session_id)
        return self.repo.get_messages(session_id)