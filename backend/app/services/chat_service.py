from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService
from app.ai_modules.D_retrieval.rag_pipeline import answer_question

def build_display_text(answer: dict) -> str:
    policies = answer.get("recommended_policies", [])
    chunks = answer.get("retrieved_chunks", [])
    need_more_info = answer.get("need_more_info", [])

    policy_lines = "\n".join(
        f"- {p.get('policy_name', '')}" for p in policies
    ) or "- 현재 조건에 맞는 정책 후보 없음"

    chunk_lines = "\n".join(
        f"- {c.get('policy_name', '')} / {c.get('section_title', '')}" for c in chunks
    ) or "- 관련 근거 없음"

    need_lines = "\n".join(
        f"- {item}" for item in need_more_info
    ) or "- 없음"

    return f"""📌 판정 상태
{answer.get("result_status", "확인 필요")}

📊 온통청년 기반 정책 후보
{policy_lines}

📚 LH 기반 정책/공고 근거
{chunk_lines}

⚠️ 추가 확인 필요
{need_lines}
"""


class ChatService:
    def __init__(self):
        self.repo = SessionRepository()
        self.session_service = SessionService()

    def save_user_message(self, session_id: str, user_message: str) -> dict:
        self.session_service.touch_session(session_id)

        user_data = {
            "role": "user",
            "raw_text": user_message,
            "data": None,
        }
        self.repo.append_message(session_id, user_data)

        answer = answer_question(user_message)

        profile = answer.get("profile_used", {})
        self.repo.save_state(session_id, profile)

        

        assistant_data = {
            "role": "assistant",
            "raw_text": answer.get("answer_text", ""),
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