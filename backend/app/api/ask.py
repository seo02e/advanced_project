from fastapi import APIRouter
from pydantic import BaseModel

from app.ai_modules.C_profile.profile_parser_final import parse_profile
from app.ai_modules.D_retrieval.rag_pipeline import generate_answer

router = APIRouter(prefix="/api", tags=["ask"])


class AskRequest(BaseModel):
    raw_text: str


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


@router.post("/ask")
def ask(request: AskRequest):
    profile = parse_profile(request.raw_text)
    answer = generate_answer(profile)

    answer["display_text"] = build_display_text(answer)

    return answer