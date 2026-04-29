# profile_llm_enhancer.py
# Youth-Sync C Layer - Profile LLM Enhancer
# 목적:
# 1) 기존 rule-based profile을 기준으로 한다.
# 2) LLM은 unknown/애매한 값만 보완한다.
# 3) top-level schema는 최대한 유지한다.
# 4) 새 feature는 condition_flags 안에 넣는다.
# 5) 근거 없는 값은 추정하지 않는다.

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional


DEFAULT_PROFILE_LLM_MODEL = "gpt-5.4-mini"

ENV_ENABLE_PROFILE_LLM_API = "ENABLE_PROFILE_LLM_API"
ENV_PROFILE_LLM_MODEL = "PROFILE_LLM_MODEL"


ALLOWED_PRIMARY_INTEREST = ["housing", "employment", "startup", "life", "unknown"]
ALLOWED_EMPLOYMENT_DETAIL = [
    "sme_employee",
    "employed",
    "job_seeking",
    "unemployed",
    "resigned_this_year",
    "student",
    "unknown",
]
ALLOWED_POLICY_INTENT_STRENGTH = ["direct", "indirect", "unclear"]
ALLOWED_HOME_OWNERSHIP_STATUS = ["homeless", "homeowner", "unknown"]


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def should_use_profile_llm_api() -> bool:
    return os.getenv(ENV_ENABLE_PROFILE_LLM_API, "").strip() == "1"


def get_profile_llm_model() -> str:
    return (
        clean_value(os.getenv(ENV_PROFILE_LLM_MODEL, ""))
        or clean_value(os.getenv("OPENAI_MODEL", ""))
        or DEFAULT_PROFILE_LLM_MODEL
    )


def ensure_profile_shape(profile: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(profile)

    out.setdefault("age", None)
    out.setdefault("region", "unknown")
    out.setdefault("employment_status", "unknown")
    out.setdefault("housing_status", "unknown")
    out.setdefault("income_level", "unknown")
    out.setdefault("interest_tags", [])
    out.setdefault("unknown_fields", [])
    out.setdefault("condition_flags", {})
    out.setdefault("raw_text", "")

    if out["interest_tags"] is None:
        out["interest_tags"] = []

    if out["unknown_fields"] is None:
        out["unknown_fields"] = []

    if out["condition_flags"] is None:
        out["condition_flags"] = {}

    return out


def build_profile_enhancer_instructions() -> str:
    return """
너는 Youth-Sync 청년정책 추천 서비스의 사용자 프로필 보완기다.

역할:
- 사용자의 자연어 질문과 rule-based profile을 보고, 정책 추천에 필요한 보조 feature를 보완한다.
- 기존 rule-based profile을 대체하지 않는다.
- 명확한 근거가 없는 값은 절대 추정하지 않는다.

반드시 지켜야 할 원칙:
1. age, region, employment_status, housing_status, income_level 같은 top-level 값은 명확한 오류가 아닌 이상 바꾸지 않는다.
2. 문장에 없는 지역, 소득, 자산, 세대주 여부, 무주택 여부를 만들지 않는다.
3. 새 정보는 주로 condition_flags 안에 넣는다.
4. "자취"는 renting 신호일 수 있지만 homeless 확정 근거는 아니다.
5. "월세가 부담"은 rent_burden_signal=true 근거가 될 수 있다.
6. "올해 퇴사"는 employment_detail=resigned_this_year 근거가 될 수 있다.
7. "중소기업 재직"은 employment_detail=sme_employee 근거가 될 수 있다.
8. "청년 정책 대상이 되나"처럼 분야가 불명확하면 primary_interest=unknown 또는 unclear로 둔다.
9. 최종 자격 eligible 여부를 판단하지 않는다. 자격 판단은 D 레이어가 한다.
10. 출력은 JSON만 한다. 설명 문장, markdown, 코드블록을 붙이지 않는다.

반환 JSON schema:
{
  "condition_flags_patch": {
    "primary_interest": "housing/employment/startup/life/unknown",
    "specific_region": "문장에 시군구가 있으면 값, 없으면 unknown",
    "employment_detail": "sme_employee/employed/job_seeking/unemployed/resigned_this_year/student/unknown",
    "rent_burden_signal": true/false,
    "home_ownership_status": "homeless/homeowner/unknown",
    "policy_intent_strength": "direct/indirect/unclear"
  },
  "interest_tags_patch": ["housing", "employment", "startup", "life"],
  "unknown_fields_patch": ["필요하지만 모르는 항목"],
  "changed_fields": ["변경 또는 보완한 필드 경로"],
  "evidence": {
    "필드명": "근거가 된 사용자 문구"
  },
  "confidence": 0.0부터 1.0,
  "notes": ["주의사항"]
}
""".strip()


def build_profile_enhancer_prompt(raw_text: str, profile: Dict[str, Any]) -> str:
    payload = {
        "raw_text": raw_text,
        "rule_based_profile": profile,
        "allowed_values": {
            "primary_interest": ALLOWED_PRIMARY_INTEREST,
            "employment_detail": ALLOWED_EMPLOYMENT_DETAIL,
            "policy_intent_strength": ALLOWED_POLICY_INTENT_STRENGTH,
            "home_ownership_status": ALLOWED_HOME_OWNERSHIP_STATUS,
        },
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    cleaned = clean_value(text)

    if not cleaned:
        return None

    # 혹시 모델이 코드블록을 붙이면 제거한다.
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json\n", "", 1).replace("JSON\n", "", 1).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    return parsed


def normalize_condition_flags_patch(patch: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    primary_interest = clean_value(patch.get("primary_interest", "unknown"))
    if primary_interest in ALLOWED_PRIMARY_INTEREST:
        out["primary_interest"] = primary_interest

    specific_region = clean_value(patch.get("specific_region", "unknown"))
    out["specific_region"] = specific_region or "unknown"

    employment_detail = clean_value(patch.get("employment_detail", "unknown"))
    if employment_detail in ALLOWED_EMPLOYMENT_DETAIL:
        out["employment_detail"] = employment_detail

    rent_burden_signal = patch.get("rent_burden_signal", False)
    out["rent_burden_signal"] = bool(rent_burden_signal)

    home_ownership_status = clean_value(patch.get("home_ownership_status", "unknown"))
    if home_ownership_status in ALLOWED_HOME_OWNERSHIP_STATUS:
        out["home_ownership_status"] = home_ownership_status

    policy_intent_strength = clean_value(patch.get("policy_intent_strength", "unclear"))
    if policy_intent_strength in ALLOWED_POLICY_INTENT_STRENGTH:
        out["policy_intent_strength"] = policy_intent_strength

    return out


def normalize_interest_tags_patch(tags: Any) -> List[str]:
    if not isinstance(tags, list):
        return []

    allowed = {"housing", "employment", "startup", "life"}
    normalized: List[str] = []

    for tag in tags:
        value = clean_value(tag)
        if value in allowed and value not in normalized:
            normalized.append(value)

    return normalized


def normalize_unknown_fields_patch(fields: Any) -> List[str]:
    if not isinstance(fields, list):
        return []

    normalized: List[str] = []

    for field in fields:
        value = clean_value(field)
        if value and value not in normalized:
            normalized.append(value)

    return normalized


def apply_llm_patch(profile: Dict[str, Any], llm_patch: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    enhanced = ensure_profile_shape(profile)

    condition_flags = enhanced.get("condition_flags", {})
    condition_flags_patch = normalize_condition_flags_patch(
        llm_patch.get("condition_flags_patch", {}) or {}
    )

    # condition_flags 확장
    for key, value in condition_flags_patch.items():
        existing = condition_flags.get(key)

        # 이미 명확한 값이 있으면 덮어쓰지 않는다.
        if existing not in [None, "", "unknown"]:
            continue

        condition_flags[key] = value

    enhanced["condition_flags"] = condition_flags

    # interest_tags 보완
    current_tags = list(enhanced.get("interest_tags", []) or [])
    patch_tags = normalize_interest_tags_patch(llm_patch.get("interest_tags_patch", []))

    for tag in patch_tags:
        if tag not in current_tags:
            current_tags.append(tag)

    enhanced["interest_tags"] = current_tags

    # unknown_fields 보완
    current_unknown = list(enhanced.get("unknown_fields", []) or [])
    patch_unknown = normalize_unknown_fields_patch(llm_patch.get("unknown_fields_patch", []))

    for field in patch_unknown:
        if field not in current_unknown:
            current_unknown.append(field)

    enhanced["unknown_fields"] = current_unknown

    enhanced["profile_llm_enhancement"] = {
        "status": "enhanced_openai_responses_api",
        "model": model_name,
        "changed_fields": llm_patch.get("changed_fields", []),
        "evidence": llm_patch.get("evidence", {}),
        "confidence": llm_patch.get("confidence", None),
        "notes": llm_patch.get("notes", []),
        "raw_patch": llm_patch,
    }

    return enhanced


def fallback_profile(profile: Dict[str, Any], status: str, message: str = "") -> Dict[str, Any]:
    enhanced = ensure_profile_shape(profile)

    enhanced["profile_llm_enhancement"] = {
        "status": status,
        "model": "",
        "changed_fields": [],
        "evidence": {},
        "confidence": None,
        "notes": [message] if message else [],
        "raw_patch": {},
    }

    return enhanced


def enhance_profile_with_llm(raw_text: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    rule-based profile을 받아 LLM으로 보조 feature를 보완한다.
    ENABLE_PROFILE_LLM_API=1일 때만 실제 API 호출.
    꺼져 있거나 실패하면 기존 profile을 그대로 반환하되 status만 기록한다.
    """
    base_profile = ensure_profile_shape(profile)

    if not should_use_profile_llm_api():
        return fallback_profile(
            base_profile,
            status="skipped_disabled_enable_profile_llm_api_not_1",
        )

    if not clean_value(os.getenv("OPENAI_API_KEY", "")):
        return fallback_profile(
            base_profile,
            status="skipped_missing_openai_api_key",
        )

    try:
        from openai import OpenAI
    except Exception as e:
        return fallback_profile(
            base_profile,
            status=f"skipped_openai_import_error_{type(e).__name__}",
            message=str(e),
        )

    model_name = get_profile_llm_model()

    try:
        client = OpenAI()

        response = client.responses.create(
            model=model_name,
            instructions=build_profile_enhancer_instructions(),
            input=build_profile_enhancer_prompt(raw_text, base_profile),
        )

        output_text = clean_value(getattr(response, "output_text", ""))
        parsed = parse_json_safely(output_text)

        if parsed is None:
            return fallback_profile(
                base_profile,
                status="fallback_invalid_json_from_profile_llm",
                message=output_text[:500],
            )

        return apply_llm_patch(
            profile=base_profile,
            llm_patch=parsed,
            model_name=model_name,
        )

    except Exception as e:
        return fallback_profile(
            base_profile,
            status=f"fallback_profile_llm_api_error_{type(e).__name__}",
            message=str(e),
        )


if __name__ == "__main__":
    sample_raw_text = "올해 퇴사한 28세 자취생인데 월세가 부담돼"

    sample_profile = {
        "age": 28,
        "region": "unknown",
        "employment_status": "unemployed",
        "housing_status": "renting",
        "income_level": "unknown",
        "interest_tags": ["housing"],
        "unknown_fields": ["region", "income_level"],
        "condition_flags": {
            "household_head_status": "unknown"
        },
        "raw_text": sample_raw_text,
    }

    result = enhance_profile_with_llm(sample_raw_text, sample_profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))