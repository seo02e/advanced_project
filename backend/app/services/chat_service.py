from fastapi import HTTPException
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService
# -----------------
from app.ai_modules.C_profile.profile_parser_final import parse_profile
from app.ai_modules.D_retrieval.rag_pipeline import generate_answer
# -----------------
# 채팅 관련 비즈니스 로직 담당
class ChatService:
    def __init__(self):
        self.repo = SessionRepository() #직접 redis에 접근해서 데이터 꺼내는 담당
        self.session_service = SessionService() # 세션 관련 함수

    # 사용자가 보낸 메시지 하나를 저장하는 핵심 함수
    def save_user_message(self, session_id: str, user_message: str) -> dict:
        # 세션 유효성 검사 + TTL 연장
        self.session_service.touch_session(session_id)

        # 1. 유저 메시지 저장
        user_data = {
            "role": "user",
            "raw_text": user_message
        }
        self.repo.append_message(session_id, user_data)

        # 2. C 모듈: 사용자 질문 -> profile 생성
        profile = parse_profile(user_message)

        # 3. state에 profile 저장
        self.repo.save_state(session_id, profile)

        # 4. D 모듈: profile -> answer JSON 생성
        answer = generate_answer(profile)

        # 5. 프론트에 보여줄 assistant 메시지 구성
        assistant_text = answer.get("why_recommended", "")

        assistant_data = {
            "role": "assistant",
            "raw_text": assistant_text,
            "data": answer
        }
        self.repo.append_message(session_id, assistant_data)

        # 6. 프론트 반환
        return {
            "session_id": session_id,
            "saved_message": user_data,
            "assistant_message": assistant_data,
            "profile": profile,
            "answer": answer,
            "total_messages": len(self.repo.get_messages(session_id))
        }



    def get_chat_history(self, session_id: str) -> list[dict]:
        self.session_service.touch_session(session_id)
        return self.repo.get_messages(session_id)
    
    