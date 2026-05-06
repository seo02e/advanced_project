from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService
from app.ai_modules.D_retrieval.rag_pipeline import answer_question
from app.ai_modules.C_profile.profile_parser_final import (
    build_need_more_info,
    build_reason_flags,
    build_unknown_fields,
    load_rules,
    parse_profile,
)


def infer_interest_from_text(text: str) -> str | None:
    housing_words = ["월세", "주거", "무주택", "전세", "임대", "자취", "집"]
    employment_words = ["취업", "구직", "일자리", "면접", "자격증", "어학"]

    if any(word in text for word in housing_words):
        return "housing"

    if any(word in text for word in employment_words):
        return "employment"

    return None


def has_correction_signal(text: str) -> bool:
    correction_words = ["아니고", "아니라", "사실", "정정", "실은", "무직이 아니라", "구직자가 아니라"]
    return any(word in text for word in correction_words)


def is_known_value(value) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return value.strip() not in ["", "unknown", "none", "null"]

    if isinstance(value, list):
        return len(value) > 0

    return True


def has_explicit_income_in_text(text: str) -> bool:
    income_markers = [
        "소득", "월소득", "수입", "월급", "연봉", "연소득", "중위소득",
        "무소득", "벌이", "저소득", "고소득", "수급자", "차상위"
    ]
    return bool(text) and any(marker in text for marker in income_markers)


def has_valid_income_state(profile: dict) -> bool:
    if not isinstance(profile, dict):
        return False

    if profile.get("income_provided") is True:
        return True

    if profile.get("monthly_income") is not None:
        return True

    return has_explicit_income_in_text(str(profile.get("raw_text", "")))


def merge_profile_state(previous_state: dict, current_profile: dict, user_message: str) -> dict:
    profile = dict(previous_state or {})
    current = dict(current_profile or {})

    scalar_fields = [
        "age",
        "region",
        "employment_status",
        "housing_status",
        "primary_interest",
    ]

    for field in scalar_fields:
        value = current.get(field)
        if is_known_value(value):
            profile[field] = value

    if current.get("income_provided") is True or current.get("monthly_income") is not None:
        profile["income_level"] = current.get("income_level", "unknown")
        profile["monthly_income"] = current.get("monthly_income")
        profile["income_provided"] = True
    elif not has_valid_income_state(previous_state):
        profile["income_level"] = "unknown"
        profile["monthly_income"] = None
        profile["income_provided"] = False

    if is_known_value(current.get("interest_tags")):
        profile["interest_tags"] = current.get("interest_tags", [])
    elif not isinstance(profile.get("interest_tags"), list):
        profile["interest_tags"] = []

    previous_flags = previous_state.get("condition_flags", {}) if isinstance(previous_state, dict) else {}
    current_flags = current.get("condition_flags", {}) if isinstance(current.get("condition_flags"), dict) else {}
    condition_flags = dict(previous_flags if isinstance(previous_flags, dict) else {})

    for key, value in current_flags.items():
        if is_known_value(value):
            condition_flags[key] = value

    profile["condition_flags"] = condition_flags
    profile["raw_text"] = user_message

    if has_correction_signal(user_message) and current.get("employment_status") == "employed":
        profile["employment_status"] = "employed"
        profile["correction_notice"] = "재직 중 상태로 반영했습니다."
        condition_flags["employment_detail"] = "employed"
    else:
        profile.pop("correction_notice", None)

    if "employment" in current.get("interest_tags", []):
        profile["primary_interest"] = "employment"
    elif "housing" in current.get("interest_tags", []):
        profile["primary_interest"] = "housing"

    profile.setdefault("schema_version", current.get("schema_version", "c_profile_v1"))
    profile.setdefault("age", None)
    profile.setdefault("region", "unknown")
    profile.setdefault("employment_status", "unknown")
    profile.setdefault("housing_status", "unknown")
    profile.setdefault("income_level", "unknown")
    profile.setdefault("monthly_income", None)
    profile.setdefault("income_provided", False)

    rules = load_rules()
    profile["unknown_fields"] = build_unknown_fields(profile)
    profile["reason_flags"] = build_reason_flags(profile)
    profile["need_more_info"] = build_need_more_info(profile["unknown_fields"], rules)
    profile["result_status"] = "확인 필요" if profile["unknown_fields"] else "profile_ready"

    return profile

class ChatService:
    def __init__(self):
        self.repo = SessionRepository()
        self.session_service = SessionService()

    def save_user_message(self, session_id: str, user_message: str) -> dict:
        self.session_service.touch_session(session_id)

        # 1. 기존 누적 상태 가져오기
        previous_state = self.repo.get_state(session_id) or {}

        # 2. 사용자 메시지 저장
        user_data = {
            "role": "user",
            "raw_text": user_message,
            "data": None,
        }
        self.repo.append_message(session_id, user_data)

        # 3. 현재 발화만 파싱한 뒤 기존 profile_state와 명시값 중심으로 병합
        current_profile = parse_profile(user_message)
        profile_for_answer = merge_profile_state(previous_state, current_profile, user_message)

        # 4. answer_question 호출
        answer = answer_question(user_message, profile=profile_for_answer)

        # 5. profile_state 저장
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

        # 6. assistant 메시지 저장
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
