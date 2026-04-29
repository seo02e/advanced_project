from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService
from app.ai_modules.D_retrieval.rag_pipeline import answer_question


def infer_interest_from_text(text: str) -> str | None:
    housing_words = ["월세", "주거", "무주택", "전세", "임대", "자취", "집"]
    employment_words = ["취업", "구직", "일자리", "면접", "자격증", "어학"]

    if any(word in text for word in housing_words):
        return "housing"

    if any(word in text for word in employment_words):
        return "employment"

    return None

class ChatService:
    def __init__(self):
        self.repo = SessionRepository()
        self.session_service = SessionService()

    def save_user_message(self, session_id: str, user_message: str) -> dict:
        self.session_service.touch_session(session_id)

        # 1. 기존 누적 상태 가져오기
        previous_state = self.repo.get_state(session_id) or {}

        # 2. 최근 대화 가져오기
        all_messages = self.repo.get_messages(session_id)

        recent_user_messages = [
            msg.get("raw_text", "")
            for msg in all_messages
            if msg.get("role") == "user"
        ][-5:]

        # 3. 사용자 메시지 저장
        user_data = {
            "role": "user",
            "raw_text": user_message,
            "data": None,
        }
        self.repo.append_message(session_id, user_data)

        # 4. 멀티턴용 질문 만들기
        multiturn_question = f"""
[이미 확인된 사용자 조건]
{previous_state}

[최근 사용자 발화]
{recent_user_messages}

[현재 질문]
{user_message}

주의:
- 이미 확인된 사용자 조건은 유지하세요.
- 현재 질문에서 명확히 정정한 값만 변경하세요.
- assistant의 이전 답변 내용은 사용자 조건으로 간주하지 마세요.
"""

        # 5. answer_question 호출
        answer = answer_question(multiturn_question)

        # 6. profile_state 저장
        profile = (
            answer.get("profile_used")
            or answer.get("debug", {}).get("profile_used")
            or previous_state
        )

        interest = infer_interest_from_text(user_message)

        if interest:
            profile["primary_interest"] = interest
            profile["interest_tags"] = [interest]
        elif previous_state.get("primary_interest") and not profile.get("primary_interest"):
            profile["primary_interest"] = previous_state.get("primary_interest")
            profile["interest_tags"] = previous_state.get("interest_tags", [])
        
        profile["raw_text"] = user_message
        
        profile.pop("profile_llm_enhancement", None)
        profile.pop("reason_flags", None)
        profile.pop("need_more_info", None)
        profile.pop("result_status", None)
        
        
        self.repo.save_state(session_id, profile)

        # 7. assistant 메시지 저장
        assistant_text = answer.get("answer_text")

        assistant_data = {
            "role": "assistant",
            "raw_text": assistant_text,
            "data": answer,
        }
        self.repo.append_message(session_id, assistant_data)

        return {
            "session_id": session_id,
            "saved_message": user_data,
            "assistant_message": assistant_data,
            "profile": profile,
            "answer": answer,
            "total_messages": len(self.repo.get_messages(session_id)),
        }
    def get_chat_history(self, session_id: str) -> list[dict]:
        self.session_service.touch_session(session_id)
        return self.repo.get_messages(session_id)