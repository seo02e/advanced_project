# rag_pipeline.py
# Youth-Sync D Layer
# 목적: C profile parser 결과를 받아 A policy_master_final.csv를 필터링하고
#      Day4용 answer schema JSON을 생성한다.

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent


POLICY_CANDIDATE_PATHS = [
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_final.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_v2.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_v1.csv",
    PROJECT_ROOT / "policy_master_final.csv",
]

CHUNK_CANDIDATE_PATHS = [
    PROJECT_ROOT / "B_chunks_handover_v1" / "housing_chunks_final.jsonl",
    CURRENT_DIR / "housing_chunks_final.jsonl",
]

INTEREST_TO_CATEGORY = {
    "housing": "주거",
    "employment": "취업"
}

HOUSING_INTENT_KEYWORDS = [
    "주거", "월세", "전세", "임대", "청년주택", "집", "보증금", "주택", "자취"
]

EMPLOYMENT_INTENT_KEYWORDS = [
    "취업", "구직", "취준", "일자리", "면접", "교육", "훈련", "채용", "청년수당", "창업"
]


def detect_primary_interest(profile: Dict[str, Any]) -> str:
    """
    질문의 핵심 관심사를 하나로 정한다.
    Day4 기준에서는 주거/취업이 섞일 때 원문 키워드를 우선한다.
    """
    raw_text = clean_value(profile.get("raw_text", ""))

    has_housing = any(keyword in raw_text for keyword in HOUSING_INTENT_KEYWORDS)
    has_employment = any(keyword in raw_text for keyword in EMPLOYMENT_INTENT_KEYWORDS)

    if has_housing and not has_employment:
        return "housing"

    if has_employment and not has_housing:
        return "employment"

    # 둘 다 있으면 질문에서 더 뒤에 나온 키워드를 핵심 관심사로 본다.
    housing_positions = [raw_text.rfind(keyword) for keyword in HOUSING_INTENT_KEYWORDS if keyword in raw_text]
    employment_positions = [raw_text.rfind(keyword) for keyword in EMPLOYMENT_INTENT_KEYWORDS if keyword in raw_text]

    last_housing = max(housing_positions) if housing_positions else -1
    last_employment = max(employment_positions) if employment_positions else -1

    if last_housing > last_employment:
        return "housing"

    if last_employment > last_housing:
        return "employment"

    interest_tags = profile.get("interest_tags", [])

    if "housing" in interest_tags:
        return "housing"

    if "employment" in interest_tags:
        return "employment"

    return "unknown"


def get_allowed_categories_by_profile(profile: Dict[str, Any]) -> List[str]:
    primary_interest = detect_primary_interest(profile)

    if primary_interest == "housing":
        return ["주거"]

    if primary_interest == "employment":
        return ["취업"]

    return []

def find_policy_csv_path() -> Path:
    for path in POLICY_CANDIDATE_PATHS:
        if path.exists():
            return path

    searched = "\n".join(str(p) for p in POLICY_CANDIDATE_PATHS)
    raise FileNotFoundError(
        "policy_master_final.csv를 찾지 못했습니다.\n"
        "확인한 경로:\n"
        f"{searched}"
    )


def read_policy_master() -> List[Dict[str, Any]]:
    csv_path = find_policy_csv_path()

    policies: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {k: clean_value(v) for k, v in row.items()}
            policies.append(normalized)

    return policies

def find_chunk_jsonl_path() -> Optional[Path]:
    for path in CHUNK_CANDIDATE_PATHS:
        if path.exists():
            return path
    return None


def read_housing_chunks() -> List[Dict[str, Any]]:
    chunk_path = find_chunk_jsonl_path()

    if chunk_path is None:
        return []

    chunks: List[Dict[str, Any]] = []

    with chunk_path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue

            chunks.append(item)

    return chunks

def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def to_int_or_none(value: Any) -> Optional[int]:
    text = clean_value(value)

    if text == "":
        return None

    try:
        return int(float(text))
    except ValueError:
        return None


def normalize_apply_status(value: str) -> str:
    text = clean_value(value).lower()

    if text in ["open", "신청중", "접수중"]:
        return "open"

    if text in ["always", "상시", "상시접수"]:
        return "always"

    if text in ["closed", "마감", "종료"]:
        return "closed"

    if text in ["unknown", ""]:
        return "unknown"

    return text


def normalize_region(value: str) -> str:
    text = clean_value(value)

    if text in ["all", "전국", "전체", "공통"]:
        return "all"

    if "서울" in text:
        return "서울"

    if "경기" in text:
        return "경기"

    if "인천" in text:
        return "인천"

    return text if text else "unknown"


def get_policy_category(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("category", ""))


def get_policy_name(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("policy_name", "")) or clean_value(policy.get("name", ""))


def get_policy_summary(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("summary", ""))


def get_policy_source_url(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("source_url", ""))


def get_policy_apply_status(policy: Dict[str, Any]) -> str:
    return normalize_apply_status(policy.get("apply_status", ""))


def get_policy_region(policy: Dict[str, Any]) -> str:
    return normalize_region(policy.get("region_scope", ""))


def is_age_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    user_age = profile.get("age")

    if user_age is None:
        return True

    age_min = to_int_or_none(policy.get("age_min"))
    age_max = to_int_or_none(policy.get("age_max"))

    if age_min is not None and user_age < age_min:
        return False

    if age_max is not None and user_age > age_max:
        return False

    return True


def is_region_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    user_region = clean_value(profile.get("region", "unknown"))
    policy_region = get_policy_region(policy)

    if user_region == "unknown":
        return True

    if policy_region in ["all", "전국", "unknown", ""]:
        return True

    return user_region == policy_region


def is_category_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    policy_category = get_policy_category(policy)
    allowed_categories = get_allowed_categories_by_profile(profile)

    if not allowed_categories:
        return True

    return policy_category in allowed_categories



def is_apply_status_match(policy: Dict[str, Any]) -> bool:
    apply_status = get_policy_apply_status(policy)

    # Day4 기준: 마감 정책만 제외한다.
    # unknown은 버리지 않고 확인 필요 후보로 둔다.
    return apply_status != "closed"


def is_employment_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    user_status = clean_value(profile.get("employment_status", "unknown"))
    policy_condition = clean_value(policy.get("employment_condition", "")).lower()

    if policy_condition in ["", "all", "전체", "제한없음", "무관", "unknown"]:
        return True

    if user_status == "unknown":
        return True

    if user_status == "job_seeking":
        return any(keyword in policy_condition for keyword in ["job_seeking", "구직", "취준", "미취업", "취업"])

    if user_status == "employed":
        return any(keyword in policy_condition for keyword in ["employed", "재직", "근로", "직장", "취업자"])

    if user_status == "student":
        return any(keyword in policy_condition for keyword in ["student", "학생", "대학생", "재학생"])

    if user_status == "unemployed":
        return any(keyword in policy_condition for keyword in ["unemployed", "무직", "실직", "미취업", "구직"])

    return True


def is_housing_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    user_status = clean_value(profile.get("housing_status", "unknown"))
    policy_condition = clean_value(policy.get("housing_condition", ""))

    if policy_condition in ["", "all", "전체", "제한없음", "무관", "unknown"]:
        return True

    # 자가 보유자가 무주택 조건 정책에 들어가는 것은 하드하게 제외한다.
    if "무주택" in policy_condition and user_status == "homeowner":
        return False

    # renting/living_with_parents는 실제 무주택 여부를 확정할 수 없으므로 일단 후보로 둔다.
    # 세부 판단은 need_more_info에서 확인하게 한다.
    return True


def filter_policies(profile: Dict[str, Any], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    matched: List[Dict[str, Any]] = []

    for policy in policies:
        if not is_apply_status_match(policy):
            continue

        if not is_category_match(profile, policy):
            continue

        if not is_region_match(profile, policy):
            continue

        if not is_age_match(profile, policy):
            continue

        if not is_employment_match(profile, policy):
            continue

        if not is_housing_match(profile, policy):
            continue

        matched.append(policy)

    return matched


def build_short_reason(profile: Dict[str, Any], policy: Dict[str, Any]) -> str:
    reasons: List[str] = []

    age = profile.get("age")
    region = profile.get("region")
    category = get_policy_category(policy)
    apply_status = get_policy_apply_status(policy)

    if age is not None:
        reasons.append(f"연령 조건 후보에 포함됩니다")

    if region and region != "unknown":
        reasons.append(f"{region} 지역 또는 전국 대상 후보입니다")

    if category:
        reasons.append(f"관심 분야와 정책 유형({category})이 일치합니다")

    if apply_status in ["open", "always"]:
        reasons.append("신청 가능 상태 후보입니다")
    elif apply_status == "unknown":
        reasons.append("신청 상태는 추가 확인이 필요합니다")

    if not reasons:
        return "사용자 조건과 일부 기본 조건이 일치하는 후보입니다."

    return ", ".join(reasons) + "."


def build_need_more_info(profile: Dict[str, Any]) -> List[str]:
    need_more_info = list(profile.get("need_more_info", []))

    # 주거 정책 관심이면 실제 자격에 자주 필요한 항목을 보강한다.
    interest_tags = profile.get("interest_tags", [])

    if "housing" in interest_tags:
        if "무주택 여부" not in need_more_info and profile.get("housing_status") in ["renting", "living_with_parents", "unknown"]:
            need_more_info.append("무주택 여부")

        if "세대주 여부" not in need_more_info:
            need_more_info.append("세대주 여부")

    return list(dict.fromkeys(need_more_info))


def build_recommended_policies(profile: Dict[str, Any], matched_policies: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    recommended: List[Dict[str, Any]] = []

    for policy in matched_policies[:limit]:
        recommended.append(
            {
                "policy_id": clean_value(policy.get("policy_id", "")),
                "policy_name": get_policy_name(policy),
                "short_reason": build_short_reason(profile, policy),
                "support_type": clean_value(policy.get("subcategory", "")) or get_policy_category(policy),
                "apply_status": get_policy_apply_status(policy),
                "source_url": get_policy_source_url(policy),
                "summary": get_policy_summary(policy)
            }
        )

    return recommended


def build_citations(recommended_policies: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    citations: List[Dict[str, str]] = []

    for policy in recommended_policies:
        source_url = clean_value(policy.get("source_url", ""))

        if source_url:
            citations.append(
                {
                    "policy_name": clean_value(policy.get("policy_name", "")),
                    "source_url": source_url
                }
            )

    return citations

def score_chunk_by_query(raw_text: str, chunk: Dict[str, Any]) -> int:
    chunk_text = clean_value(chunk.get("chunk_text", ""))
    section_title = clean_value(chunk.get("section_title", ""))
    policy_name = clean_value(chunk.get("policy_name", ""))

    target = f"{policy_name} {section_title} {chunk_text}"

    keywords: List[str] = []

    if any(word in raw_text for word in ["월세", "주거", "자취", "전세", "임대", "무주택", "세대주"]):
        keywords.extend(["월세", "주거", "자취", "전세", "임대", "무주택", "세대주", "지원 대상", "신청 자격"])

    if any(word in raw_text for word in ["소득", "중위소득"]):
        keywords.extend(["소득", "중위소득", "소득 기준"])

    if any(word in raw_text for word in ["부모", "부모님", "본가"]):
        keywords.extend(["부모", "부모님", "본가", "가구"])

    score = 0

    for keyword in keywords:
        if keyword and keyword in target:
            score += 1

    return score


def retrieve_relevant_chunks(profile: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    primary_interest = detect_primary_interest(profile)

    if primary_interest != "housing":
        return []

    chunks = read_housing_chunks()

    if not chunks:
        return []

    raw_text = clean_value(profile.get("raw_text", ""))

    scored = []

    for chunk in chunks:
        score = score_chunk_by_query(raw_text, chunk)

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [chunk for score, chunk in scored[:limit]]


def build_chunk_citations(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    citations: List[Dict[str, str]] = []

    for chunk in retrieved_chunks:
        source_url = clean_value(chunk.get("source_url", ""))

        if source_url:
            citations.append(
                {
                    "policy_name": clean_value(chunk.get("policy_name", "")),
                    "section_title": clean_value(chunk.get("section_title", "")),
                    "source_url": source_url
                }
            )

    return citations

def generate_answer(profile: Dict[str, Any]) -> Dict[str, Any]:
    policies = read_policy_master()
    matched_policies = filter_policies(profile, policies)
    recommended_policies = build_recommended_policies(profile, matched_policies, limit=5)
    retrieved_chunks = retrieve_relevant_chunks(profile, limit=3)

    need_more_info = build_need_more_info(profile)
    policy_citations = build_citations(recommended_policies)
    chunk_citations = build_chunk_citations(retrieved_chunks)
    citations = policy_citations + chunk_citations

    if recommended_policies:
        result_status = "확인 필요" if need_more_info else "추천 가능 후보"
        why_recommended = "사용자의 나이, 지역, 관심 분야를 기준으로 A 정책 테이블에서 후보 정책을 추렸습니다."
        next_action = "추가 확인 항목을 입력하면 더 정확하게 가능 여부를 좁힐 수 있습니다."
    else:
        result_status = "확인 필요"

        primary_interest = detect_primary_interest(profile)

        if primary_interest == "housing":
            why_recommended = "주거 관심 질문으로 분류했지만, 현재 A 정책 테이블에서 조건에 맞는 주거 정책 후보를 찾지 못했습니다."
            next_action = "현재 A 정책 테이블에 주거 정책 후보가 부족합니다. 주거 정책 데이터가 병합되면 다시 조회하세요."

        elif primary_interest == "employment":
            why_recommended = "현재 입력 조건으로는 추천 후보가 비어 있습니다. 지역, 나이, 관심 분야 또는 신청 상태 조건을 다시 확인해야 합니다."
            next_action = "지역, 나이, 취업상태, 소득수준을 보완하면 더 정확하게 조회할 수 있습니다."

        else:
            why_recommended = "현재 입력 조건으로는 추천 후보가 비어 있습니다. 지역, 나이, 관심 분야 또는 신청 상태 조건을 다시 확인해야 합니다."
            next_action = "지역, 나이, 관심 분야를 보완해서 다시 조회하세요."

    answer = {
        "result_status": result_status,
        "profile_used": profile,
        "recommended_policies": recommended_policies,
        "retrieved_chunks": retrieved_chunks,
        "why_recommended": why_recommended,
        "need_more_info": need_more_info,
        "caution_notes": [
            "현재 결과는 A 정책 메타데이터 기준 1차 후보입니다.",
            "최종 자격은 소득, 세대주 여부, 세부 공고문 조건 확인이 필요합니다.",
            "source_url이 없는 정책은 citations에 포함하지 않았습니다."
        ],
        "citations": citations,
        "next_action": next_action,
        "debug": {
            "policy_count_total": len(policies),
            "policy_count_matched": len(matched_policies),
            "primary_interest": detect_primary_interest(profile),
            "allowed_categories": get_allowed_categories_by_profile(profile),
            "policy_csv_path": str(find_policy_csv_path()),
            "chunk_file_path": str(find_chunk_jsonl_path()) if find_chunk_jsonl_path() else "",
            "chunk_count_retrieved": len(retrieved_chunks)
        }
    }

    return answer


def run_pipeline(profile: Dict[str, Any]) -> Dict[str, Any]:
    return generate_answer(profile)


def answer_question(raw_text: str, profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if profile is None:
        # 필요할 때만 C parser를 불러온다.
        import sys

        c_profile_dir = PROJECT_ROOT / "C_profile"
        if str(c_profile_dir) not in sys.path:
            sys.path.append(str(c_profile_dir))

        from profile_parser_final import parse_profile

        profile = parse_profile(raw_text)

    return generate_answer(profile)


if __name__ == "__main__":
    sample_profile = {
        "schema_version": "c_profile_v1",
        "raw_text": "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
        "age": 27,
        "region": "서울",
        "employment_status": "job_seeking",
        "housing_status": "homeless",
        "income_level": "unknown",
        "interest_tags": ["housing", "employment"],
        "unknown_fields": ["income_level", "household_head_status"],
        "condition_flags": {
            "household_head_status": "unknown"
        },
        "result_status": "확인 필요",
        "reason_flags": ["income_missing", "household_head_unknown"],
        "need_more_info": ["소득수준", "세대주 여부"]
    }

    print(json.dumps(generate_answer(sample_profile), ensure_ascii=False, indent=2))