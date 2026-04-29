# rag_pipeline_final.py
# Youth-Sync D Layer - Day4 Final Pipeline
# 목적:
# 입력 자연어 질문
# → C profile parser
# → A/B 정책 메타데이터 필터링
# → B 주거 chunk BM25 검색
# → 정책별 eligibility_result 생성
# → answer_blocks / answer_text 생성
# → Day4용 JSON 응답 반환

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from llm_answer_generator import generate_llm_answer
except ImportError:
    from .llm_answer_generator import generate_llm_answer
    

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent


try:
    from retriever_final import retrieve_relevant_chunks_bm25
except ImportError:
    from .retriever_final import retrieve_relevant_chunks_bm25


POLICY_CANDIDATE_PATHS = [
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_final.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_v2.csv",
    PROJECT_ROOT / "A_policy_handover_v2" / "policy_master_v1.csv",
    PROJECT_ROOT / "policy_master_final.csv",
]

B_POLICY_CANDIDATE_PATHS = [
    PROJECT_ROOT / "B_chunks_output_handover" / "housing_policy_master_from_b.csv",
]

CHUNK_CANDIDATE_PATHS = [
    PROJECT_ROOT / "B_chunks_output_handover" / "housing_chunks_final.jsonl",
    PROJECT_ROOT / "B_chunks_handover_v1" / "housing_chunks_final.jsonl",
    CURRENT_DIR / "housing_chunks_final.jsonl",
]


HOUSING_INTENT_KEYWORDS = [
    "주거", "월세", "전세", "임대", "청년주택", "집", "보증금", "주택", "자취"
]

EMPLOYMENT_INTENT_KEYWORDS = [
    "취업", "구직", "취준", "일자리", "면접", "교육", "훈련", "채용", "청년수당", "창업"
]


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

    return clean_value(value)


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

def get_condition_flags(profile: Dict[str, Any]) -> Dict[str, Any]:
    flags = profile.get("condition_flags", {})

    if isinstance(flags, dict):
        return flags

    return {}


def get_profile_primary_interest(profile: Dict[str, Any]) -> str:
    flags = get_condition_flags(profile)
    value = clean_value(flags.get("primary_interest", ""))

    if value in ["housing", "employment", "startup", "life", "unknown"]:
        return value

    return "unknown"


def get_profile_employment_detail(profile: Dict[str, Any]) -> str:
    flags = get_condition_flags(profile)
    value = clean_value(flags.get("employment_detail", ""))

    if value:
        return value

    return "unknown"


def get_profile_rent_burden_signal(profile: Dict[str, Any]) -> bool:
    flags = get_condition_flags(profile)
    return bool(flags.get("rent_burden_signal", False))


def get_profile_home_ownership_status(profile: Dict[str, Any]) -> str:
    flags = get_condition_flags(profile)
    value = clean_value(flags.get("home_ownership_status", ""))

    if value:
        return value

    return "unknown"


def get_profile_policy_intent_strength(profile: Dict[str, Any]) -> str:
    flags = get_condition_flags(profile)
    value = clean_value(flags.get("policy_intent_strength", ""))

    if value in ["direct", "indirect", "unclear"]:
        return value

    return "unclear"

def should_block_broad_recommendation(profile: Dict[str, Any]) -> bool:
    """
    관심분야가 불명확한 질문에서 넓은 정책 추천을 막는다.

    예:
    - "서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나"
      → 직장인이라는 상태값은 있지만, 취업/주거/창업 중 무엇을 원하는지 불명확
      → 추천 정책을 바로 보여주지 않고 관심분야 확인 필요
    """
    primary_interest = detect_primary_interest(profile)
    intent_strength = get_profile_policy_intent_strength(profile)

    if primary_interest == "unknown":
        return True

    if primary_interest == "unknown" and intent_strength in ["indirect", "unclear"]:
        return True

    return False


def get_profile_specific_region(profile: Dict[str, Any]) -> str:
    flags = get_condition_flags(profile)
    value = clean_value(flags.get("specific_region", ""))

    if value:
        return value

    return "unknown"


def detect_primary_interest(profile: Dict[str, Any]) -> str:
    """
    관심분야 판단.

    우선순위:
    1) profile LLM enhancer가 명확히 판단한 primary_interest
    2) profile LLM enhancer가 unknown이라고 명시한 경우에는 raw_text fallback 금지
    3) LLM 보완이 없을 때만 interest_tags / raw_text keyword fallback
    """
    flags = get_condition_flags(profile)

    llm_primary_interest = clean_value(flags.get("primary_interest", ""))
    profile_llm_status = clean_value(
        profile.get("profile_llm_enhancement", {}).get("status", "")
    )

    # 1. LLM이 명확히 판단한 경우 우선 사용
    if llm_primary_interest in ["housing", "employment", "startup", "life"]:
        return llm_primary_interest

    # 2. LLM enhancer가 실행됐고 primary_interest=unknown이면 그대로 unknown 유지
    # 예:
    # "서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나"
    # 여기서 '직장인'은 상태값이지, 취업정책 관심사라고 단정하면 안 됨.
    if profile_llm_status == "enhanced_openai_responses_api" and llm_primary_interest == "unknown":
        return "unknown"

    interest_tags = profile.get("interest_tags", []) or []
    raw_text = clean_value(profile.get("raw_text", ""))

    housing_keywords = [
        "주거", "월세", "전세", "임대", "주택", "자취", "보증금",
        "무주택", "집", "방", "주거비"
    ]

    employment_keywords = [
        "취업", "구직", "일자리", "재직", "중소기업",
        "퇴사", "실직", "면접", "자격증", "교육", "훈련"
    ]

    startup_keywords = [
        "창업", "사업", "초기창업", "스타트업"
    ]

    if "housing" in interest_tags:
        return "housing"

    if "employment" in interest_tags:
        return "employment"

    if "startup" in interest_tags:
        return "startup"

    if any(keyword in raw_text for keyword in housing_keywords):
        return "housing"

    if any(keyword in raw_text for keyword in startup_keywords):
        return "startup"

    if any(keyword in raw_text for keyword in employment_keywords):
        return "employment"

    return "unknown"

def get_allowed_categories_by_profile(profile: Dict[str, Any]) -> List[str]:
    primary_interest = detect_primary_interest(profile)

    if primary_interest == "housing":
        return ["주거"]

    if primary_interest == "employment":
        return ["취업"]

    return []


def should_ask_interest_first(profile: Dict[str, Any]) -> bool:
    primary_interest = detect_primary_interest(profile)
    interest_tags = profile.get("interest_tags", [])

    return primary_interest == "unknown" and not interest_tags


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


def find_b_policy_csv_path() -> Optional[Path]:
    for path in B_POLICY_CANDIDATE_PATHS:
        if path.exists():
            return path

    return None


def find_chunk_jsonl_path() -> Optional[Path]:
    for path in CHUNK_CANDIDATE_PATHS:
        if path.exists():
            return path

    return None


def read_policy_master() -> List[Dict[str, Any]]:
    csv_path = find_policy_csv_path()
    policies: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {k: clean_value(v) for k, v in row.items()}
            normalized["source_layer"] = "A"
            policies.append(normalized)

    return policies


def read_b_housing_policy_master() -> List[Dict[str, Any]]:
    csv_path = find_b_policy_csv_path()

    if csv_path is None:
        return []

    policies: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {k: clean_value(v) for k, v in row.items()}
            normalized["source_layer"] = "B"
            policies.append(normalized)

    return policies


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


def get_policy_category(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("category", ""))


def get_policy_name(policy: Dict[str, Any]) -> str:
    return clean_value(policy.get("policy_name", "")) or clean_value(policy.get("name", ""))


def get_display_policy_name(policy_name: Any) -> str:
    text = clean_value(policy_name)

    if "|" in text:
        return text.split("|")[0].strip()

    return text


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

    return apply_status != "closed"


def is_employment_match(profile: Dict[str, Any], policy: Dict[str, Any]) -> bool:
    # Day4 기준:
    # 주거 질문에서는 취업상태를 하드 필터로 쓰지 않는다.
    # 예: "퇴사한 28세 자취생 월세 부담"은 주거 정책 후보로 남겨야 한다.
    if detect_primary_interest(profile) == "housing":
        return True

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

    if "무주택" in policy_condition and user_status == "homeowner":
        return False

    return True


def filter_policies(profile: Dict[str, Any], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if should_block_broad_recommendation(profile):
        return []
    
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

def is_startup_policy(policy: Dict[str, Any]) -> bool:
    text = " ".join(
        [
            clean_value(policy.get("policy_name", "")),
            clean_value(policy.get("subcategory", "")),
            clean_value(policy.get("summary", "")),
        ]
    )

    return "창업" in text

def calculate_policy_match_score(profile: Dict[str, Any], policy: Dict[str, Any]) -> float:
    """
    A/B 공통 정책 후보 랭킹 점수.
    profile_llm_enhancer가 만든 condition_flags를 실제 랭킹에 반영한다.
    """
    score = 0.0

    raw_text = clean_value(profile.get("raw_text", ""))
    user_region = clean_value(profile.get("region", "unknown"))
    specific_region = get_profile_specific_region(profile)
    employment_status = clean_value(profile.get("employment_status", "unknown"))

    primary_interest = detect_primary_interest(profile)
    employment_detail = get_profile_employment_detail(profile)
    rent_burden_signal = get_profile_rent_burden_signal(profile)
    home_ownership_status = get_profile_home_ownership_status(profile)
    policy_intent_strength = get_profile_policy_intent_strength(profile)

    policy_name = clean_value(policy.get("policy_name", ""))
    policy_category = get_policy_category(policy)
    policy_region = get_policy_region(policy)
    apply_status = get_policy_apply_status(policy)
    employment_condition = clean_value(policy.get("employment_condition", "unknown"))
    housing_condition = clean_value(policy.get("housing_condition", "unknown"))
    source_url = get_policy_source_url(policy)
    source_layer = clean_value(policy.get("source_layer", "unknown"))
    subcategory = clean_value(policy.get("subcategory", ""))
    summary = clean_value(policy.get("summary", ""))

    combined_text = " ".join(
        [
            policy_name,
            subcategory,
            summary,
            employment_condition,
            housing_condition,
        ]
    )

    # 0. 질문 의도가 불명확하면 과추천 방지
    if policy_intent_strength in ["unclear", "indirect"] and primary_interest == "unknown":
        score -= 10.0

    # 1. 관심 분야 점수
    if primary_interest == "housing":
        if policy_category == "주거":
            score += 4.0
        elif policy_category == "취업":
            score -= 3.0

    elif primary_interest == "employment":
        if policy_category == "취업":
            score += 4.0
        elif policy_category == "주거":
            score -= 3.0

    elif primary_interest == "startup":
        if is_startup_policy(policy):
            score += 4.0
        elif policy_category == "취업":
            score += 1.0

    # 2. 지역 점수
    # specific_region은 LLM이 문장에서 세부 지역을 감지한 값.
    # top-level region이 unknown이어도 specific_region이 있으면 보조로 쓴다.
    effective_region = user_region

    if effective_region == "unknown" and specific_region in ["서울", "경기"]:
        effective_region = specific_region

    if effective_region == "unknown":
        if policy_region == "all":
            score += 1.0
        elif policy_region in ["서울", "경기"]:
            score += 0.3
        elif policy_region == "기타":
            score -= 1.0
    else:
        if policy_region == effective_region:
            score += 3.0
        elif policy_region == "all":
            score += 2.0
        elif policy_region == "기타":
            score -= 2.0
        else:
            score -= 4.0

    # 3. 신청 상태 점수
    if apply_status in ["open", "always"]:
        score += 2.0
    elif apply_status == "unknown":
        score += 0.3
    elif apply_status == "closed":
        score -= 5.0

    # 4. 연령 점수
    age = profile.get("age")
    age_min = to_int_or_none(policy.get("age_min"))
    age_max = to_int_or_none(policy.get("age_max"))

    if age is not None:
        if age_min is not None and age < age_min:
            score -= 10.0
        elif age_max is not None and age > age_max:
            score -= 10.0
        else:
            score += 1.5

    # 5. 취업상태 + employment_detail 점수
    if primary_interest == "employment":
        if employment_detail == "sme_employee":
            if any(keyword in combined_text for keyword in ["중소기업", "기업", "재직", "근로", "직장", "근무"]):
                score += 4.0

            if employment_condition in ["employed", "all", "unknown"]:
                score += 2.0

            if employment_condition in ["job_seeking", "student"]:
                score -= 2.0

        elif employment_detail in ["employed", "unknown"] and employment_status == "employed":
            if employment_condition in ["employed", "all", "unknown"]:
                score += 2.0

            if any(keyword in combined_text for keyword in ["재직", "근로", "직장", "근무"]):
                score += 2.0

        elif employment_detail == "resigned_this_year":
            if any(keyword in combined_text for keyword in ["구직", "미취업", "실업", "취업준비", "재취업"]):
                score += 3.0

            if employment_condition in ["job_seeking", "all", "unknown"]:
                score += 2.0

            if employment_condition == "employed":
                score -= 2.0

        elif employment_status in ["job_seeking", "unemployed"]:
            if employment_condition in ["job_seeking", "all", "unknown"]:
                score += 2.0

            if employment_condition == "employed":
                score -= 2.0

    # 6. 창업 정책 패널티
    # 사용자가 창업을 직접 말하지 않았는데 취업 질문이면 창업 정책이 상단을 덮지 않게 낮춘다.
    if primary_interest == "employment":
        user_asked_startup = "창업" in raw_text or employment_detail == "startup"

        if is_startup_policy(policy) and not user_asked_startup:
            score -= 4.0

    # 7. 주거 관련 세부 feature 반영
    if primary_interest == "housing":
        if rent_burden_signal:
            if any(keyword in combined_text for keyword in ["월세", "임대료", "주거급여", "주거비"]):
                score += 3.0

        if any(keyword in raw_text for keyword in ["월세", "월세가", "월세 지원"]):
            if any(keyword in combined_text for keyword in ["월세", "임대료", "주거급여", "주거비"]):
                score += 2.5

        if any(keyword in raw_text for keyword in ["전세", "보증금"]):
            if any(keyword in combined_text for keyword in ["전세", "보증금", "임차보증금"]):
                score += 2.5

        if home_ownership_status == "homeless":
            if housing_condition in ["homeless", "all", "unknown"]:
                score += 2.0

            if "무주택" in combined_text:
                score += 1.5

        elif home_ownership_status == "homeowner":
            if housing_condition == "homeless" or "무주택" in combined_text:
                score -= 8.0

    # 8. source_url 있는 정책 우선
    if source_url:
        score += 0.5
    else:
        score -= 0.5

    # 9. B 원문 근거 보정
    # 주거 질문에서 B는 원문 chunk 근거가 있으므로 약간 가점.
    if primary_interest == "housing" and source_layer == "B":
        score += 0.8

    return round(score, 4)


def rank_policies_for_profile(profile: Dict[str, Any], policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []

    for policy in policies:
        item = dict(policy)
        item["policy_match_score"] = calculate_policy_match_score(profile, item)
        ranked.append(item)

    ranked.sort(
        key=lambda p: (
            float(p.get("policy_match_score", 0.0)),
            1 if get_policy_apply_status(p) in ["open", "always"] else 0,
            1 if get_policy_source_url(p) else 0,
        ),
        reverse=True,
    )

    return ranked

def build_short_reason(profile: Dict[str, Any], policy: Dict[str, Any]) -> str:
    reasons: List[str] = []

    age = profile.get("age")
    region = profile.get("region")
    category = get_policy_category(policy)
    apply_status = get_policy_apply_status(policy)

    if age is not None:
        reasons.append("연령 조건 후보에 포함됩니다")

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


def evaluate_policy_eligibility(profile: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    status = "maybe"
    reasons: List[str] = []
    missing_requirements: List[str] = []

    age = profile.get("age")
    region = clean_value(profile.get("region", "unknown"))
    employment_status = clean_value(profile.get("employment_status", "unknown"))
    housing_status = clean_value(profile.get("housing_status", "unknown"))
    income_level = clean_value(profile.get("income_level", "unknown"))
    household_head_status = profile.get("condition_flags", {}).get("household_head_status", "unknown")

    policy_name = get_policy_name(policy)
    policy_region = get_policy_region(policy)
    policy_category = get_policy_category(policy)
    apply_status = get_policy_apply_status(policy)

    age_min = to_int_or_none(policy.get("age_min"))
    age_max = to_int_or_none(policy.get("age_max"))
    employment_condition = clean_value(policy.get("employment_condition", ""))
    housing_condition = clean_value(policy.get("housing_condition", ""))
    summary = clean_value(policy.get("summary", ""))

    evidence_text = " ".join(
        [
            policy_name,
            policy_category,
            employment_condition,
            housing_condition,
            summary,
        ]
    )

    if apply_status == "closed":
        return {
            "eligibility_status": "not eligible",
            "eligibility_reasons": ["신청 상태가 마감으로 표시되어 후보에서 제외됩니다."],
            "missing_requirements": [],
        }

    if apply_status in ["unknown", ""]:
        missing_requirements.append("신청 가능 상태")
    else:
        reasons.append("신청 상태가 마감은 아닙니다.")

    if age is None:
        missing_requirements.append("나이")
    else:
        if age_min is not None and age < age_min:
            return {
                "eligibility_status": "not eligible",
                "eligibility_reasons": [f"나이 {age}세가 최소 연령 {age_min}세보다 낮습니다."],
                "missing_requirements": [],
            }

        if age_max is not None and age > age_max:
            return {
                "eligibility_status": "not eligible",
                "eligibility_reasons": [f"나이 {age}세가 최대 연령 {age_max}세보다 높습니다."],
                "missing_requirements": [],
            }

        if age_min is not None or age_max is not None:
            reasons.append("연령 조건 범위 안에 있습니다.")
        else:
            reasons.append("정책 데이터에 명확한 연령 제한이 없거나 추가 확인이 필요합니다.")

    if region == "unknown":
        missing_requirements.append("지역")
    else:
        if policy_region not in ["all", "전국", "unknown", ""] and region != policy_region:
            return {
                "eligibility_status": "not eligible",
                "eligibility_reasons": [f"사용자 지역({region})과 정책 지역({policy_region})이 일치하지 않습니다."],
                "missing_requirements": [],
            }

        reasons.append("지역 조건에서 제외되지는 않습니다.")

    if "무주택" in evidence_text:
        if housing_status == "homeowner":
            return {
                "eligibility_status": "not eligible",
                "eligibility_reasons": ["정책에 무주택 요건이 있으나 사용자는 주택 보유자로 파악됩니다."],
                "missing_requirements": [],
            }

        if housing_status in ["unknown", "renting", "living_with_parents"]:
            missing_requirements.append("무주택 여부")
        else:
            reasons.append("무주택 요건과 충돌하지 않습니다.")

    if "세대주" in evidence_text and household_head_status == "unknown":
        missing_requirements.append("세대주 여부")

    income_keywords = ["소득", "중위소득", "자산", "도시근로자", "수급자", "차상위"]

    if any(keyword in evidence_text for keyword in income_keywords):
        if income_level == "unknown":
            missing_requirements.append("소득수준")
        else:
            reasons.append("소득 정보가 입력되어 추가 대조가 가능합니다.")

    if employment_status == "unknown":
        if any(keyword in evidence_text for keyword in ["취업준비생", "구직", "미취업", "재직", "근로"]):
            missing_requirements.append("취업상태")
    else:
        reasons.append("취업상태 정보가 입력되어 있습니다.")

    missing_requirements = list(dict.fromkeys(missing_requirements))
    reasons = list(dict.fromkeys(reasons))

    if missing_requirements:
        status = "확인 필요"
    else:
        status = "maybe"

    return {
        "eligibility_status": status,
        "eligibility_reasons": reasons,
        "missing_requirements": missing_requirements,
    }


def build_need_more_info(profile: Dict[str, Any]) -> List[str]:
    need_more_info = list(profile.get("need_more_info", []))
    interest_tags = profile.get("interest_tags", [])

    if "housing" in interest_tags:
        if "무주택 여부" not in need_more_info and profile.get("housing_status") in ["renting", "living_with_parents", "unknown"]:
            need_more_info.append("무주택 여부")

        household_head_status = profile.get("condition_flags", {}).get("household_head_status", "unknown")

        if household_head_status == "unknown" and "세대주 여부" not in need_more_info:
            need_more_info.append("세대주 여부")

    return list(dict.fromkeys(need_more_info))


def build_recommended_policies(profile: Dict[str, Any], matched_policies: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    recommended: List[Dict[str, Any]] = []

    for policy in matched_policies[:limit]:
        raw_policy_name = get_policy_name(policy)
        eligibility_result = evaluate_policy_eligibility(profile, policy)

        recommended.append(
            {
                "policy_id": clean_value(policy.get("policy_id", "")),
                "policy_name": get_display_policy_name(raw_policy_name),
                "raw_policy_name": raw_policy_name,
                "source_layer": clean_value(policy.get("source_layer", "unknown")),
                "short_reason": build_short_reason(profile, policy),
                "support_type": clean_value(policy.get("subcategory", "")) or get_policy_category(policy),
                "apply_status": get_policy_apply_status(policy),
                "source_url": get_policy_source_url(policy),
                "summary": get_policy_summary(policy),
                "policy_match_score": policy.get("policy_match_score", 0.0),
                "eligibility_result": eligibility_result,
                "eligibility_status": eligibility_result["eligibility_status"],
                "missing_requirements": eligibility_result["missing_requirements"],
            }
        )

    return recommended


def retrieve_relevant_chunks(
    profile: Dict[str, Any],
    limit: int = 3,
    candidate_policy_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    primary_interest = detect_primary_interest(profile)

    if primary_interest != "housing":
        return []

    chunks = read_housing_chunks()

    if not chunks:
        return []

    return retrieve_relevant_chunks_bm25(
        profile=profile,
        chunks=chunks,
        limit=limit,
        candidate_policy_ids=candidate_policy_ids,
    )


def build_citations(recommended_policies: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    citations: List[Dict[str, str]] = []

    for policy in recommended_policies:
        source_url = clean_value(policy.get("source_url", ""))

        if source_url:
            citations.append(
                {
                    "policy_name": clean_value(policy.get("policy_name", "")),
                    "source_url": source_url,
                }
            )

    return citations


def build_chunk_citations(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    citations: List[Dict[str, str]] = []

    for chunk in retrieved_chunks:
        source_url = clean_value(chunk.get("source_url", ""))

        if source_url:
            citations.append(
                {
                    "policy_name": clean_value(chunk.get("policy_name", "")),
                    "section_title": clean_value(chunk.get("section_title", "")),
                    "source_url": source_url,
                }
            )

    return citations


def find_best_chunk_for_policy(policy: Dict[str, Any], retrieved_chunks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    policy_id = clean_value(policy.get("policy_id", ""))

    for chunk in retrieved_chunks:
        if clean_value(chunk.get("policy_id", "")) == policy_id:
            return chunk

    return None


def summarize_chunk_text(text: str, max_length: int = 160) -> str:
    cleaned = clean_value(text)

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[:max_length].rstrip() + "..."


def build_answer_blocks(
    profile: Dict[str, Any],
    recommended_policies: List[Dict[str, Any]],
    retrieved_chunks: List[Dict[str, Any]],
    need_more_info: List[str],
) -> Dict[str, Any]:
    primary_interest = detect_primary_interest(profile)

    if not recommended_policies:
        if primary_interest == "unknown":
            return {
                "summary": "관심 분야가 명확하지 않아 정책 후보를 넓게 추천하지 않았습니다.",
                "recommended": [],
                "need_more_info": need_more_info,
                "sources": [],
                "next_action": "주거, 취업, 창업, 생활지원 중 어떤 분야의 정책을 보고 싶은지 먼저 선택해 주세요.",
            }

        return {
            "summary": "현재 입력 조건으로는 조건에 맞는 정책 후보를 찾지 못했습니다.",
            "recommended": [],
            "need_more_info": need_more_info,
            "sources": [],
            "next_action": "지역, 나이, 소득수준 등 확인 필요 정보를 보완하면 후보를 다시 좁힐 수 있습니다.",
        }

    recommended_blocks: List[Dict[str, Any]] = []

    for policy in recommended_policies:
        best_chunk = find_best_chunk_for_policy(policy, retrieved_chunks)
        eligibility_result = policy.get("eligibility_result", {})

        if best_chunk:
            evidence = {
                "section_title": clean_value(best_chunk.get("section_title", "")),
                "chunk_text": summarize_chunk_text(clean_value(best_chunk.get("chunk_text", ""))),
                "source_url": clean_value(best_chunk.get("source_url", "")),
                "retrieval_method": clean_value(best_chunk.get("retrieval_method", "")),
                "bm25_score": best_chunk.get("bm25_score"),
                "dense_status": clean_value(best_chunk.get("dense_status", "")),
            }
        else:
            evidence = {
                "section_title": "",
                "chunk_text": "",
                "source_url": clean_value(policy.get("source_url", "")),
                "retrieval_method": "metadata_only",
                "bm25_score": None,
                "dense_status": "not_applicable",
            }

        recommended_blocks.append(
            {
                "policy_name": clean_value(policy.get("policy_name", "")),
                "source_layer": clean_value(policy.get("source_layer", "")),
                "support_type": clean_value(policy.get("support_type", "")),
                "eligibility_status": clean_value(policy.get("eligibility_status", "")),
                "recommend_reason": clean_value(policy.get("short_reason", "")),
                "eligibility_reasons": eligibility_result.get("eligibility_reasons", []),
                "missing_requirements": eligibility_result.get("missing_requirements", []),
                "apply_status": clean_value(policy.get("apply_status", "")),
                "source_url": clean_value(policy.get("source_url", "")),
                "evidence": evidence,
            }
        )

    sources = []

    for chunk in retrieved_chunks:
        sources.append(
            {
                "policy_name": clean_value(chunk.get("policy_name", "")),
                "section_title": clean_value(chunk.get("section_title", "")),
                "source_url": clean_value(chunk.get("source_url", "")),
                "retrieval_method": clean_value(chunk.get("retrieval_method", "")),
                "bm25_score": chunk.get("bm25_score"),
                "dense_status": clean_value(chunk.get("dense_status", "")),
            }
        )

    return {
        "summary": "입력 조건을 기준으로 정책 후보를 찾았지만, 최종 자격 확정을 위해 추가 확인이 필요합니다.",
        "recommended": recommended_blocks,
        "need_more_info": need_more_info,
        "sources": sources,
        "next_action": "추가 확인 항목을 입력하면 eligible / maybe / 확인 필요 / not eligible 범위를 더 좁힐 수 있습니다.",
    }


def build_answer_text(answer_blocks: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append(answer_blocks.get("summary", ""))

    recommended = answer_blocks.get("recommended", [])

    if recommended:
        lines.append("")
        lines.append("[추천 정책 후보]")

        for idx, item in enumerate(recommended, start=1):
            policy_name = item.get("policy_name", "")
            eligibility_status = item.get("eligibility_status", "")
            recommend_reason = item.get("recommend_reason", "")
            missing = item.get("missing_requirements", [])
            source_url = item.get("source_url", "")

            lines.append(f"{idx}. {policy_name}")
            lines.append(f"- 자격 판단: {eligibility_status}")
            lines.append(f"- 추천 이유: {recommend_reason}")

            if missing:
                lines.append(f"- 추가 확인 필요: {', '.join(missing)}")

            if source_url:
                lines.append(f"- 출처: {source_url}")

    need_more_info = answer_blocks.get("need_more_info", [])

    if need_more_info:
        lines.append("")
        lines.append("[추가로 확인하면 좋은 정보]")
        lines.append(", ".join(need_more_info))

    next_action = answer_blocks.get("next_action", "")

    if next_action:
        lines.append("")
        lines.append("[다음 행동]")
        lines.append(next_action)

    return "\n".join(line for line in lines if line is not None)


def generate_answer(profile: Dict[str, Any]) -> Dict[str, Any]:
    a_policies = read_policy_master()
    b_policies = read_b_housing_policy_master()

    primary_interest = detect_primary_interest(profile)
    block_broad_recommendation = should_block_broad_recommendation(profile)
    
    if primary_interest == "housing":
        policies = a_policies + b_policies
    else:
        policies = a_policies

    if should_ask_interest_first(profile):
        matched_policies: List[Dict[str, Any]] = []
        recommended_policies: List[Dict[str, Any]] = []
    else:
        matched_policies = filter_policies(profile, policies)
        matched_policies = rank_policies_for_profile(profile, matched_policies)
        recommended_policies = build_recommended_policies(profile, matched_policies, limit=5)
        
    if block_broad_recommendation:
        if block_broad_recommendation:
            recommended_policies = []
            recommended_policies_a = []
            recommended_policies_b = []

    candidate_policy_ids = [
        clean_value(policy.get("policy_id", ""))
        for policy in recommended_policies
    ]

    retrieved_chunks = retrieve_relevant_chunks(
        profile,
        limit=3,
        candidate_policy_ids=candidate_policy_ids,
    )
    
    if block_broad_recommendation:
        retrieved_chunks = []

    need_more_info = build_need_more_info(profile)
    if block_broad_recommendation and "관심분야" not in need_more_info:
        need_more_info.append("관심분야")

    recommended_policies_a = [
        policy for policy in recommended_policies
        if clean_value(policy.get("source_layer", "")) == "A"
    ]

    recommended_policies_b = [
        policy for policy in recommended_policies
        if clean_value(policy.get("source_layer", "")) == "B"
    ]

    policy_citations = build_citations(recommended_policies)
    chunk_citations = build_chunk_citations(retrieved_chunks)
    citations = policy_citations + chunk_citations

    answer_blocks = build_answer_blocks(
        profile=profile,
        recommended_policies=recommended_policies,
        retrieved_chunks=retrieved_chunks,
        need_more_info=need_more_info,
    )

    answer_text = build_answer_text(answer_blocks)
    
    llm_answer_result = {
        "answer_text": answer_text,
        "llm_generation_status": "not_attempted_before_final_answer_build",
        "llm_model_name": "",
        "llm_context": {},
    }    
    if recommended_policies:
        if any(policy.get("eligibility_status") == "확인 필요" for policy in recommended_policies):
            result_status = "확인 필요"
        elif any(policy.get("eligibility_status") == "maybe" for policy in recommended_policies):
            result_status = "maybe"
        else:
            result_status = "추천 가능 후보"

        if primary_interest == "housing":
            why_recommended = "사용자의 나이, 지역, 주거상태를 기준으로 A 정책 테이블과 B 주거 정책 데이터를 함께 조회했습니다."
        else:
            why_recommended = "사용자의 나이, 지역, 관심 분야를 기준으로 A 정책 테이블에서 후보 정책을 추렸습니다."

        next_action = answer_blocks.get("next_action", "")
    else:
        result_status = "확인 필요"

        if primary_interest == "housing":
            why_recommended = "주거 관심 질문으로 분류했지만, 현재 A 정책 테이블과 B 주거 정책 데이터에서 조건에 맞는 후보를 찾지 못했습니다."
            next_action = "지역, 나이, 소득수준, 세대주 여부, 무주택 여부를 보완하면 더 정확하게 조회할 수 있습니다."

        elif primary_interest == "employment":
            why_recommended = "현재 입력 조건으로는 추천 후보가 비어 있습니다. 지역, 나이, 관심 분야 또는 신청 상태 조건을 다시 확인해야 합니다."
            next_action = "지역, 나이, 취업상태, 소득수준을 보완하면 더 정확하게 조회할 수 있습니다."

        else:
            why_recommended = "관심 분야가 명확하지 않아 정책 후보를 넓게 추천하지 않았습니다."
            next_action = "주거, 취업, 창업, 생활지원 중 어떤 분야의 정책을 보고 싶은지 먼저 선택해 주세요."

    llm_context_answer = {
        "result_status": result_status,
        "profile_used": profile,
        "recommended_policies": recommended_policies,
        "recommended_policies_a": recommended_policies_a,
        "recommended_policies_b": recommended_policies_b,
        "retrieved_chunks": retrieved_chunks,
        "answer_blocks": answer_blocks,
        "answer_text": answer_text,
        "llm_answer_generation": llm_answer_result,
        "why_recommended": why_recommended,
        "need_more_info": need_more_info,
        "caution_notes": [
            "현재 결과는 A 정책 메타데이터와 B 주거 정책 데이터 기준 1차 후보입니다.",
            "최종 자격은 소득, 세대주 여부, 세부 공고문 조건 확인이 필요합니다.",
            "Dense retrieval은 sentence-transformers 기반으로 연결되어 있으며, 주거 정책 검색은 BM25 + Dense hybrid 결과를 사용합니다.",
            "source_url이 없는 정책은 citations에 포함하지 않았습니다.",
        ],
        "citations": citations,
        "next_action": next_action,
    }

    llm_answer_result = generate_llm_answer(llm_context_answer)
    answer_text = llm_answer_result.get("answer_text", answer_text)

    answer = {
        "schema_version": "d_answer_day4_final_v1",
        "result_status": result_status,
        "profile_used": profile,
        "recommended_policies": recommended_policies,
        "recommended_policies_a": recommended_policies_a,
        "recommended_policies_b": recommended_policies_b,
        "retrieved_chunks": retrieved_chunks,
        "answer_blocks": answer_blocks,
        "answer_text": answer_text,
        "why_recommended": why_recommended,
        "need_more_info": need_more_info,
        "caution_notes": [
            "현재 결과는 A 정책 메타데이터와 B 주거 정책 데이터 기준 1차 후보입니다.",
            "최종 자격은 소득, 세대주 여부, 세부 공고문 조건 확인이 필요합니다.",
            "Dense retrieval은 Day4 기준 미구현이며 BM25 baseline 결과를 우선 사용합니다.",
            "source_url이 없는 정책은 citations에 포함하지 않았습니다.",
        ],
        "citations": citations,
        "next_action": next_action,
        "debug": {
            "pipeline_file": "D_retrieval/rag_pipeline.py",
            "retriever_file": "D_retrieval/retriever_final.py",
            "policy_count_total": len(policies),
            "policy_count_a": len(a_policies),
            "policy_count_b": len(b_policies),
            "policy_count_matched": len(matched_policies),
            "primary_interest": primary_interest,
            "allowed_categories": get_allowed_categories_by_profile(profile),
            "policy_csv_path": str(find_policy_csv_path()),
            "b_policy_csv_path": str(find_b_policy_csv_path()) if find_b_policy_csv_path() else "",
            "chunk_file_path": str(find_chunk_jsonl_path()) if find_chunk_jsonl_path() else "",
            "chunk_count_retrieved": len(retrieved_chunks),
            "retrieval_method": retrieved_chunks[0].get("retrieval_method", "none") if retrieved_chunks else "none",
            "dense_status": retrieved_chunks[0].get("dense_status", "not_applicable") if retrieved_chunks else "not_applicable",
            "dense_model_name": retrieved_chunks[0].get("dense_model_name", "") if retrieved_chunks else "",
            "retriever_file": "D_retrieval/retriever_final.py",
            "answer_generation": "template_grounded_answer_blocks",
            "llm_generation_status": llm_answer_result.get("llm_generation_status", ""),
            "llm_model_name": llm_answer_result.get("llm_model_name", ""),
            "profile_llm_status": profile.get("profile_llm_enhancement", {}).get("status", ""),
            "profile_llm_model": profile.get("profile_llm_enhancement", {}).get("model", ""),
            "profile_condition_flags": profile.get("condition_flags", {}),
            "profile_intent_strength": get_profile_policy_intent_strength(profile),
        },
    }

    return answer


def run_pipeline(profile: Dict[str, Any]) -> Dict[str, Any]:
    return generate_answer(profile)


def answer_question(raw_text: str, profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if profile is None:
        import sys

        c_profile_dir = PROJECT_ROOT / "C_profile"

        if str(c_profile_dir) not in sys.path:
            sys.path.append(str(c_profile_dir))

        from profile_parser_final import parse_profile

        profile = parse_profile(raw_text)

        try:
            from profile_llm_enhancer import enhance_profile_with_llm

            profile = enhance_profile_with_llm(raw_text, profile)

        except Exception as e:
            profile["profile_llm_enhancement"] = {
                "status": f"profile_llm_enhancer_import_or_runtime_error_{type(e).__name__}",
                "model": "",
                "changed_fields": [],
                "evidence": {},
                "confidence": None,
                "notes": [str(e)],
                "raw_patch": {},
            }

    return generate_answer(profile)


if __name__ == "__main__":
    sample_questions = [
        "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
        "경기도 거주 25세 중소기업 재직자인데 취업 지원 정책이 있을까?",
        "서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나",
        "올해 퇴사한 28세 자취생인데 월세가 부담돼",
        "무주택인데 세대주는 아니야. 주거 지원이 가능해?",
    ]

    for question in sample_questions:
        print("=" * 100)
        print(f"QUESTION: {question}")
        print("=" * 100)
        result = answer_question(question)
        print(json.dumps(result, ensure_ascii=False, indent=2))