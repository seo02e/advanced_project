# profile_parser_final.py
# Youth-Sync C Layer
# 역할: 사용자 자연어 질문을 D/A가 사용할 수 있는 profile JSON으로 변환한다.
# 원칙: 모르는 값은 추정하지 않고 unknown 또는 unknown_fields로 남긴다.

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


RULE_PATH = Path(__file__).with_name("eligibility_rules_final.json")


DEFAULT_RULES: Dict[str, Any] = {
    "schema_version": "c_profile_v1",
    "allowed_values": {
        "region": ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종", "전국", "unknown"],
        "employment_status": ["job_seeking", "employed", "unemployed", "student", "unknown"],
        "housing_status": ["homeless", "renting", "living_with_parents", "homeowner", "unknown"],
        "income_level": ["low", "middle", "high", "unknown"],
        "interest_tags": ["housing", "employment"]
    },
    "interest_to_category": {
        "housing": "주거",
        "employment": "취업"
    },
    "unknown_field_labels": {
        "age": "나이",
        "region": "지역",
        "employment_status": "취업상태",
        "housing_status": "주거상태",
        "income_level": "소득수준",
        "household_head_status": "세대주 여부"
    }
}


REGION_KEYWORDS = {
    "서울": ["서울", "서울시", "서울특별시"],
    "경기": ["경기", "경기도"],
    "인천": ["인천", "인천시", "인천광역시"],
    "부산": ["부산", "부산시", "부산광역시"],
    "대구": ["대구", "대구시", "대구광역시"],
    "광주": ["광주", "광주시", "광주광역시"],
    "대전": ["대전", "대전시", "대전광역시"],
    "울산": ["울산", "울산시", "울산광역시"],
    "세종": ["세종", "세종시", "세종특별자치시"],
    "전국": ["전국", "어디든", "지역 상관없", "전지역"]
}


EMPLOYMENT_KEYWORDS = {
    "job_seeking": ["취준", "취업 준비", "취업준비", "구직", "일자리 찾", "미취업", "취준생", "구직자"],
    "employed": ["재직", "직장인", "회사 다니", "근무 중", "근무중", "정규직", "계약직", "알바", "아르바이트"],
    "student": ["대학생", "학생", "재학생", "휴학생"],
    "unemployed": ["퇴사", "실직", "무직", "일 안 하고", "일을 안 하고"]
}


HOUSING_KEYWORDS = {
    "homeless": ["무주택", "주택 없음", "집 없음", "내 명의 집 없음", "자가 없음"],
    "renting": ["자취", "월세", "전세", "반전세", "원룸", "고시원", "임차"],
    "living_with_parents": ["부모님 집", "부모님과", "부모님이랑", "본가", "부모 집"],
    "homeowner": ["자가", "주택 소유", "내 집 있음", "집 있음"]
}


INCOME_KEYWORDS = {
    "low": ["저소득", "소득 낮", "소득이 낮", "기초생활수급", "수급자", "차상위", "소득 없음", "소득이 없어"],
    "middle": ["중위소득", "평균 소득"],
    "high": ["고소득", "소득 높", "소득이 높"]
}


INTEREST_KEYWORDS = {
    "housing": ["주거", "월세", "전세", "임대", "청년주택", "집", "보증금", "주택", "자취"],
    "employment": ["취업", "구직", "취준", "일자리", "면접", "교육", "훈련", "채용", "청년수당", "취업지원"]
}


def load_rules() -> Dict[str, Any]:
    if RULE_PATH.exists():
        try:
            with RULE_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_RULES
    return DEFAULT_RULES


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def extract_age(text: str) -> Optional[int]:
    patterns = [
        r"만\s*(\d{1,2})\s*(?:세|살)",
        r"(\d{1,2})\s*(?:세|살)",
        r"(\d{1,2})\s*대"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            age = int(match.group(1))

            # "20대"처럼 나온 경우는 정확 나이가 아니므로 unknown 처리한다.
            if "대" in match.group(0):
                return None

            if 0 < age < 100:
                return age

    return None


def extract_region(text: str) -> str:
    for normalized_region, keywords in REGION_KEYWORDS.items():
        if contains_any(text, keywords):
            return normalized_region
    return "unknown"


def extract_employment_status(text: str) -> str:
    # 우선순위: 구직/취준 > 재직 > 학생 > 실직
    # 예: "퇴사하고 구직 중"은 unemployed보다 job_seeking이 서비스상 더 유용하다.
    priority = ["job_seeking", "employed", "student", "unemployed"]

    for status in priority:
        if contains_any(text, EMPLOYMENT_KEYWORDS[status]):
            return status

    return "unknown"


def extract_housing_status(text: str) -> str:
    # 우선순위: 무주택 > 자취/임차 > 부모동거 > 자가
    # 예: "무주택이고 월세 자취"는 정책 필터상 homeless가 더 중요하다.
    priority = ["homeless", "renting", "living_with_parents", "homeowner"]

    for status in priority:
        if contains_any(text, HOUSING_KEYWORDS[status]):
            return status

    return "unknown"


def extract_income_level(text: str) -> str:
    for level, keywords in INCOME_KEYWORDS.items():
        if contains_any(text, keywords):
            return level
    return "unknown"


def extract_household_head_status(text: str) -> str:
    negative_patterns = ["세대주 아님", "세대주는 아님", "세대주 아니", "세대주가 아님", "세대주는 아니"]
    positive_patterns = ["세대주", "본인 세대주"]

    if contains_any(text, negative_patterns):
        return "no"

    if contains_any(text, positive_patterns):
        return "yes"

    return "unknown"


def extract_interest_tags(text: str, employment_status: str, housing_status: str) -> List[str]:
    tags: List[str] = []

    for tag, keywords in INTEREST_KEYWORDS.items():
        if contains_any(text, keywords):
            tags.append(tag)

    # 직접 관심사를 말하지 않아도 상태값으로 보조 추론한다.
    if employment_status in ["job_seeking", "unemployed"] and "employment" not in tags:
        tags.append("employment")

    if housing_status in ["homeless", "renting", "living_with_parents"] and "housing" not in tags:
        tags.append("housing")

    return tags


def build_unknown_fields(profile: Dict[str, Any]) -> List[str]:
    unknown_fields: List[str] = []

    if profile["age"] is None:
        unknown_fields.append("age")

    if profile["region"] == "unknown":
        unknown_fields.append("region")

    if profile["employment_status"] == "unknown":
        unknown_fields.append("employment_status")

    # 관심사가 주거인데 주거상태가 모르면 확인 필요
    if "housing" in profile["interest_tags"] and profile["housing_status"] == "unknown":
        unknown_fields.append("housing_status")

    # 소득은 대부분 정책 자격조건에서 필요하므로 기본 확인 필요로 둔다.
    if profile["income_level"] == "unknown":
        unknown_fields.append("income_level")

    # 주거 정책 관심이면 세대주 여부도 확인 필요
    if "housing" in profile["interest_tags"]:
        household_head_status = profile["condition_flags"].get("household_head_status", "unknown")
        if household_head_status == "unknown":
            unknown_fields.append("household_head_status")

    return list(dict.fromkeys(unknown_fields))


def build_reason_flags(profile: Dict[str, Any]) -> List[str]:
    flags: List[str] = []

    mapping = {
        "age": "age_missing",
        "region": "region_missing",
        "employment_status": "employment_status_missing",
        "housing_status": "housing_status_missing",
        "income_level": "income_missing",
        "household_head_status": "household_head_unknown"
    }

    for field in profile["unknown_fields"]:
        flags.append(mapping.get(field, f"{field}_missing"))

    return flags


def build_need_more_info(unknown_fields: List[str], rules: Dict[str, Any]) -> List[str]:
    labels = rules.get("unknown_field_labels", DEFAULT_RULES["unknown_field_labels"])
    return [labels.get(field, field) for field in unknown_fields]


def parse_profile(raw_text: str) -> Dict[str, Any]:
    rules = load_rules()
    text = raw_text.strip()

    age = extract_age(text)
    region = extract_region(text)
    employment_status = extract_employment_status(text)
    housing_status = extract_housing_status(text)
    income_level = extract_income_level(text)
    household_head_status = extract_household_head_status(text)
    interest_tags = extract_interest_tags(text, employment_status, housing_status)

    profile: Dict[str, Any] = {
        "schema_version": rules.get("schema_version", "c_profile_v1"),
        "raw_text": raw_text,
        "age": age,
        "region": region,
        "employment_status": employment_status,
        "housing_status": housing_status,
        "income_level": income_level,
        "interest_tags": interest_tags,
        "unknown_fields": [],
        "condition_flags": {
            "household_head_status": household_head_status
        },
        "result_status": "unknown",
        "reason_flags": [],
        "need_more_info": []
    }

    profile["unknown_fields"] = build_unknown_fields(profile)
    profile["reason_flags"] = build_reason_flags(profile)
    profile["need_more_info"] = build_need_more_info(profile["unknown_fields"], rules)

    # C 단독 단계에서는 실제 정책 row와 대조하지 않으므로 eligible/not eligible을 확정하지 않는다.
    if profile["unknown_fields"]:
        profile["result_status"] = "확인 필요"
    else:
        profile["result_status"] = "profile_ready"

    return profile


def parse_profile_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = payload.get("raw_text") or payload.get("question") or payload.get("query") or ""
    return parse_profile(raw_text)


if __name__ == "__main__":
    sample_questions = [
        "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
        "경기도 사는 25살 취준생인데 취업지원 정책 알려줘. 소득은 잘 모르겠어.",
        "부모님이랑 살고 있고 29세야. 서울 청년 주거 정책 받을 수 있어?"
    ]

    for question in sample_questions:
        print(json.dumps(parse_profile(question), ensure_ascii=False, indent=2))
        print("-" * 80)