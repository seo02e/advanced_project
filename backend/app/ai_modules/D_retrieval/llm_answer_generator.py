# llm_answer_generator.py
# Youth-Sync D Layer - LLM Answer Generator
# 목적:
# 1) answer_blocks / recommended_policies / retrieved_chunks를 바탕으로 LLM 응답 생성
# 2) OPENAI_API_KEY가 없거나 ENABLE_LLM_API=1이 아니면 기존 template answer_text 유지
# 3) LLM이 없는 값을 추정하지 않도록 prompt에 제한 조건 명시

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


DEFAULT_LLM_MODEL_NAME = "gpt-5.5"

ENV_ENABLE_LLM_API = "ENABLE_LLM_API"
ENV_OPENAI_MODEL = "OPENAI_MODEL"


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def compact_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    eligibility_result = policy.get("eligibility_result", {})

    return {
        "policy_name": clean_value(policy.get("policy_name", "")),
        "source_layer": clean_value(policy.get("source_layer", "")),
        "support_type": clean_value(policy.get("support_type", "")),
        "apply_status": clean_value(policy.get("apply_status", "")),
        "eligibility_status": clean_value(policy.get("eligibility_status", "")),
        "short_reason": clean_value(policy.get("short_reason", "")),
        "missing_requirements": policy.get("missing_requirements", []),
        "eligibility_reasons": eligibility_result.get("eligibility_reasons", []),
        "source_url": clean_value(policy.get("source_url", "")),
    }


def compact_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "policy_name": clean_value(chunk.get("policy_name", "")),
        "section_title": clean_value(chunk.get("section_title", "")),
        "chunk_text": clean_value(chunk.get("chunk_text", ""))[:500],
        "source_url": clean_value(chunk.get("source_url", "")),
        "retrieval_method": clean_value(chunk.get("retrieval_method", "")),
        "bm25_score": chunk.get("bm25_score"),
        "bm25_norm_score": chunk.get("bm25_norm_score"),
        "dense_score": chunk.get("dense_score"),
        "hybrid_score": chunk.get("hybrid_score"),
        "dense_status": clean_value(chunk.get("dense_status", "")),
        "dense_model_name": clean_value(chunk.get("dense_model_name", "")),
    }


def build_llm_context(answer: Dict[str, Any]) -> Dict[str, Any]:
    profile = answer.get("profile_used", {})
    policies = answer.get("recommended_policies", [])
    chunks = answer.get("retrieved_chunks", [])
    answer_blocks = answer.get("answer_blocks", {})

    return {
        "user_question": clean_value(profile.get("raw_text", "")),
        "profile_used": {
            "age": profile.get("age"),
            "region": clean_value(profile.get("region", "")),
            "employment_status": clean_value(profile.get("employment_status", "")),
            "housing_status": clean_value(profile.get("housing_status", "")),
            "income_level": clean_value(profile.get("income_level", "")),
            "interest_tags": profile.get("interest_tags", []),
            "unknown_fields": profile.get("unknown_fields", []),
            "need_more_info": profile.get("need_more_info", []),
            "condition_flags": profile.get("condition_flags", {}),
        },
        "result_status": clean_value(answer.get("result_status", "")),
        "need_more_info": answer.get("need_more_info", []),
        "recommended_policies": [compact_policy(policy) for policy in policies[:5]],
        "retrieved_chunks": [compact_chunk(chunk) for chunk in chunks[:5]],
        "answer_blocks": answer_blocks,
        "next_action": clean_value(answer.get("next_action", "")),
        "caution_notes": answer.get("caution_notes", []),
    }


def build_instructions() -> str:
    return """
너는 Youth-Sync 청년정책 추천 서비스의 응답 생성기다.

반드시 지켜야 할 원칙:
1. 제공된 JSON context 안의 정보만 사용한다.
2. 없는 정보는 추정하지 않는다.
3. 최종 자격을 단정하지 않는다.
4. eligibility_status가 "확인 필요"이면 반드시 추가 확인 필요 항목을 말한다.
5. eligibility_status가 "maybe"여도 최종 확정처럼 말하지 않는다.
6. 정책 추천 이유는 profile_used, eligibility_reasons, retrieved_chunks 근거에 맞춰 설명한다.
7. 출처 URL이 있으면 정책별로 표시한다.
8. Dense/BM25 점수는 사용자가 이해하기 쉽게 "근거 문서 검색 결과" 정도로만 설명한다.
9. 한국어로 답한다.
10. 답변은 너무 길지 않게, 실제 서비스 화면에 들어갈 수 있는 형태로 작성한다.

출력 형식:
- 첫 문단: 전체 요약
- [추천 정책 후보]
- [추가 확인 필요 정보]
- [근거 및 출처]
- [다음 행동]
""".strip()


def build_user_prompt(context: Dict[str, Any]) -> str:
    return f"""
아래 JSON context를 바탕으로 사용자에게 보여줄 최종 응답문을 작성해줘.

JSON context:
{json.dumps(context, ensure_ascii=False, indent=2)}
""".strip()


def should_use_llm_api() -> bool:
    return os.getenv(ENV_ENABLE_LLM_API, "").strip() == "1"


def get_model_name() -> str:
    return clean_value(os.getenv(ENV_OPENAI_MODEL, "")) or DEFAULT_LLM_MODEL_NAME


def generate_llm_answer(answer: Dict[str, Any]) -> Dict[str, Any]:
    """
    반환:
    {
      "answer_text": "...",
      "llm_generation_status": "...",
      "llm_model_name": "...",
      "llm_context": {...}
    }
    """
    fallback_text = clean_value(answer.get("answer_text", ""))
    context = build_llm_context(answer)

    if not should_use_llm_api():
        return {
            "answer_text": fallback_text,
            "llm_generation_status": "skipped_disabled_enable_llm_api_not_1",
            "llm_model_name": "",
            "llm_context": context,
        }

    if not clean_value(os.getenv("OPENAI_API_KEY", "")):
        return {
            "answer_text": fallback_text,
            "llm_generation_status": "skipped_missing_openai_api_key",
            "llm_model_name": "",
            "llm_context": context,
        }

    try:
        from openai import OpenAI
    except Exception as e:
        return {
            "answer_text": fallback_text,
            "llm_generation_status": f"skipped_openai_import_error_{type(e).__name__}",
            "llm_model_name": "",
            "llm_context": context,
        }

    model_name = get_model_name()

    try:
        client = OpenAI()

        response = client.responses.create(
            model=model_name,
            instructions=build_instructions(),
            input=build_user_prompt(context),
        )

        generated_text = clean_value(getattr(response, "output_text", ""))

        if not generated_text:
            return {
                "answer_text": fallback_text,
                "llm_generation_status": "fallback_empty_llm_output",
                "llm_model_name": model_name,
                "llm_context": context,
            }

        return {
            "answer_text": generated_text,
            "llm_generation_status": "generated_openai_responses_api",
            "llm_model_name": model_name,
            "llm_context": context,
        }

    except Exception as e:
        return {
            "answer_text": fallback_text,
            "llm_generation_status": f"fallback_llm_api_error_{type(e).__name__}",
            "llm_model_name": model_name,
            "llm_context": context,
        }