# policy_data.py
# A_policy_handover_v2
# 목적:
# 1) 온통청년 API에서 일자리 + 주거 정책을 모두 수집
# 2) 수도권 중심 정책만 정리
# 3) 원천 CSV를 policy_master_YYYYMMDD.csv로 저장
# 4) API 키는 코드에 직접 쓰지 않고 환경변수 YOUTH_API_KEY로 받음

from __future__ import annotations

import os
import time
import re
import json

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

import logging
logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"

OUTPUT_CSV = BASE_DIR / "data/policy_master_final.csv"
OUTPUT_META = BASE_DIR / "data/policy_metadata.json"


URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

# 온통청년 API의 대분류명 기준
# D 최종 schema에서는 make_policy_table.py에서 일자리 -> 취업, 주거 -> 주거로 변환한다.
CATEGORIES = ["일자리", "주거"]

# 서울 + 인천 + 경기 행정구역 코드
METRO_ZIP_CODES = [
    # 서울
    "11110", "11140", "11170", "11200", "11215", "11230", "11260", "11290",
    "11305", "11320", "11350", "11380", "11410", "11440", "11470", "11500",
    "11530", "11545", "11560", "11590", "11620", "11650", "11680", "11710",
    "11740",

    # 경기
    "41111", "41113", "41115", "41117", "41131", "41133", "41135", "41150",
    "41171", "41173", "41192", "41194", "41196", "41210", "41220", "41250",
    "41271", "41273", "41281", "41285", "41287", "41290", "41310", "41360",
    "41370", "41390", "41410", "41430", "41450", "41461", "41463", "41465",
    "41480", "41500", "41550", "41570", "41591", "41593", "41595", "41597",
    "41610", "41630", "41650", "41670", "41800", "41820", "41830",
]

ZIP_PARAM = ",".join(METRO_ZIP_CODES)

METRO_PREFIXES = ["11", "41"]

METRO_KEYWORDS = [
    "서울", "경기",
    "강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
    "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
    "송파", "양천", "영등포", "용산", "은평", "종로", "중구", "중랑",
    "수원", "성남", "고양", "용인", "부천", "안양", "안산", "화성", "평택",
    "의정부", "시흥", "김포", "광명", "광주", "군포", "하남", "오산",
    "이천", "안성", "의왕", "양주", "구리", "포천", "여주", "동두천",
    "과천", "파주", "남양주",
]

FINAL_COLUMNS = [
    "policy_id",
    "policy_name",
    "category",
    "subcategory",
    "region_scope",
    "age_min",
    "age_max",
    "employment_condition",
    "housing_condition",
    "income_condition_text",
    "apply_start_date",
    "apply_end_date",
    "apply_status",
    "source_org",
    "source_url",
    "summary",
    "source_type",
]


def get_api_key() -> str:

    api_key = os.getenv("YOUTH_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "YOUTH_API_KEY가 설정되어 있지 않습니다.\n"
            ".env파일에서 YOUTH_API_KEY 값을 확인해주세요.\n"
        )

    return api_key


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text

def clean_text(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None

    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[\r\n\t]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if text.lower() in ["nan", "none", "null", ""]:
        return None

    return text


def fetch_page(api_key: str, category: str, page: int, page_size: int = 100) -> List[Dict[str, Any]]:
    params = {
        "apiKeyNm": api_key,
        "pageNum": page,
        "pageSize": page_size,
        "pageType": "1",
        "rtnType": "json",
        "lclsfNm": category,
    }

    # 일자리는 수도권 zipCd로 직접 제한한다.
    # 주거는 API 필터가 누락될 가능성이 있어 전체 수집 후 수도권 키워드/zip 필터를 한 번 더 적용한다.
    if category == "일자리":
        params["zipCd"] = ZIP_PARAM

    response = requests.get(URL, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    policies = data.get("result", {}).get("youthPolicyList", [])

    if not isinstance(policies, list):
        return []

    return policies


def fetch_category(api_key: str, category: str, page_size: int = 100) -> List[Dict[str, Any]]:
    all_rows: List[Dict[str, Any]] = []
    page = 1

    while True:
        try:
            rows = fetch_page(
                api_key=api_key,
                category=category,
                page=page,
                page_size=page_size,
            )
        except Exception as e:
            print(f"[{category}] {page}페이지 수집 오류: {type(e).__name__}: {e}")
            break

        if not rows:
            break

        for row in rows:
            row["_category"] = category

        all_rows.extend(rows)

        print(f"[{category}] {page}페이지 -> {len(rows)}건 / 누적 {len(all_rows)}건")

        if len(rows) < page_size:
            break

        page += 1
        time.sleep(0.3)

    print(f"[{category}] 수집 완료: 총 {len(all_rows)}건")
    return all_rows


def has_metro_zip(row: pd.Series) -> bool:
    zip_value = clean_value(row.get("zipCd", ""))

    if not zip_value:
        return False

    for code in zip_value.split(","):
        code = code.strip()

        if any(code.startswith(prefix) for prefix in METRO_PREFIXES):
            return True

    return False


def has_metro_keyword(row: pd.Series) -> bool:
    text_cols = [
        "plcyNm",
        "plcyExplnCn",
        "operInstCdNm",
        "sprvsnInstCdNm",
        "rgtrInstCdNm",
        "rgtrHghrkInstCdNm",
        "plcyKywdNm",
    ]

    combined = " ".join(clean_value(row.get(col, "")) for col in text_cols)
    logger.info(f"combined : {combined}")
    return any(keyword in combined for keyword in METRO_KEYWORDS)


def is_metro_policy(row: pd.Series) -> bool:
    return has_metro_zip(row) or has_metro_keyword(row)

def normalize_category(row: pd.Series) -> str:
    raw_category = clean_text(row.get("_category")) or clean_text(row.get("lclsfNm")) or ""

    if "일자리" in raw_category or "취업" in raw_category:
        return "취업"

    if "주거" in raw_category:
        return "주거"

    return "unknown"

def parse_date(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None

    nums = re.sub(r"\D", "", str(value))

    if len(nums) >= 8:
        return f"{nums[:4]}-{nums[4:6]}-{nums[6:8]}"

    return None

def pick_subcategory(name: Optional[str], desc: Optional[str], category: str) -> str:
    text = f"{name or ''} {desc or ''}"

    if "월세" in text:
        return "월세지원"

    if "전세" in text:
        return "전세지원"

    if "임대" in text or "주택" in text or "주거" in text:
        return "주거지원"

    if "창업" in text:
        return "창업지원"

    if "자격증" in text:
        return "자격증지원"

    if "면접" in text:
        return "면접지원"

    if "교육" in text or "훈련" in text:
        return "교육훈련"

    if "취업" in text or "채용" in text or "일자리" in text:
        return "취업지원"

    if category == "주거":
        return "주거지원"

    if category == "취업":
        return "취업지원"

    return "unknown"

def normalize_region(row: pd.Series) -> str:
    text_parts = [
        clean_text(row.get("rgtrHghrkInstCdNm")),
        clean_text(row.get("rgtrInstCdNm")),
        clean_text(row.get("sprvsnInstCdNm")),
        clean_text(row.get("operInstCdNm")),
        clean_text(row.get("plcyNm")),
        clean_text(row.get("plcyExplnCn")),
        clean_text(row.get("plcyKywdNm")),
    ]

    text = " ".join(part for part in text_parts if part)

    nationwide_orgs = [
        "고용노동부",
        "국토교통부",
        "중소벤처기업부",
        "교육부",
        "국가보훈부",
        "농림축산식품부",
        "정부산하기관",
        "정부산하기관및위원회",
        "한국토지주택공사",
    ]

    if "전국" in text or "전국단위" in text:
        return "all"

    if any(org in text for org in nationwide_orgs):
        return "all"

    seoul_keywords = [
        "서울", "강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천",
        "노원", "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동",
        "성북", "송파", "양천", "영등포", "용산", "은평", "종로", "중랑",
    ]

    gyeonggi_keywords = [
        "경기", "수원", "성남", "고양", "용인", "부천", "안양", "안산",
        "화성", "평택", "의정부", "시흥", "김포", "광명", "광주", "군포",
        "하남", "오산", "이천", "안성", "의왕", "양주", "구리", "포천",
        "여주", "동두천", "과천", "파주", "남양주",
    ]



    if any(keyword in text for keyword in seoul_keywords):
        return "서울"

    if any(keyword in text for keyword in gyeonggi_keywords):
        return "경기"

    return "기타"

def normalize_status(start_date: Optional[str], end_date: Optional[str]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    if not start_date and not end_date:
        return "always"

    if end_date and end_date < today:
        return "closed"

    if start_date and start_date > today:
        return "unknown"

    return "open"

def safe_int(value: Any) -> Optional[int]:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        return int(float(text))
    except ValueError:
        return None

def pick_employment_condition(name: Optional[str], desc: Optional[str]) -> str:
    text = f"{name or ''} {desc or ''}"

    if any(keyword in text for keyword in ["재직", "근로", "직장인", "중소기업 재직", "근무"]):
        return "employed"

    if any(keyword in text for keyword in ["구직", "취준", "취업준비", "미취업", "실업", "구직자"]):
        return "job_seeking"

    if any(keyword in text for keyword in ["대학생", "재학생", "학생"]):
        return "student"

    if any(keyword in text for keyword in ["누구나", "제한 없음", "제한없음", "전체", "무관"]):
        return "all"

    return "unknown"


def pick_housing_condition(name: Optional[str], desc: Optional[str]) -> str:
    text = f"{name or ''} {desc or ''}"

    if "무주택" in text:
        return "homeless"

    if any(keyword in text for keyword in ["월세", "전세", "임차", "임대", "자취"]):
        return "renting"

    if "부모" in text:
        return "living_with_parents"

    if "세대주" in text:
        return "household_head"

    if any(keyword in text for keyword in ["누구나", "제한 없음", "제한없음", "전체", "무관"]):
        return "all"

    return "unknown"


def pick_source_url(row: pd.Series) -> Optional[str]:
    for col in ["aplyUrlAddr", "refUrlAddr1", "refUrlAddr2", "plcyUrlAddr"]:
        value = clean_text(row.get(col))

        if value:
            return value

    return None


def make_summary(name: Optional[str], desc: Optional[str], row: pd.Series) -> Optional[str]:
    candidates = [
        desc,
        clean_text(row.get("plcySprtCn")),
        clean_text(row.get("plcyKywdNm")),
        name,
    ]

    text = " ".join(candidate for candidate in candidates if candidate)

    if not text:
        return None

    return text[:300]

def build_policy_row(row: pd.Series) -> dict:
    name = clean_text(row.get("plcyNm"))
    desc = clean_text(row.get("plcyExplnCn"))

    category = normalize_category(row)

    source_org = (
        clean_text(row.get("operInstCdNm"))
        or clean_text(row.get("sprvsnInstCdNm"))
        or clean_text(row.get("rgtrInstCdNm"))
        or "정보없음"
    )

    start_date = parse_date(row.get("bizPrdBgngYmd"))
    end_date = parse_date(row.get("bizPrdEndYmd"))

    return {
        "policy_id": clean_text(row.get("plcyNo")) or "",
        "policy_name": name,
        "category": category,
        "subcategory": pick_subcategory(name, desc, category),
        "region_scope": normalize_region(row),
        "age_min": safe_int(row.get("sprtTrgtMinAge")),
        "age_max": safe_int(row.get("sprtTrgtMaxAge")),
        "employment_condition": pick_employment_condition(name, desc),
        "housing_condition": pick_housing_condition(name, desc),
        "income_condition_text": clean_text(row.get("earnCndSeCdNm")) or clean_text(row.get("earnEtcCn")),
        "apply_start_date": start_date,
        "apply_end_date": end_date,
        "apply_status": normalize_status(start_date, end_date),
        "source_org": source_org,
        "source_url": pick_source_url(row),
        "summary": make_summary(name, desc, row),
        "source_type": "api",
    }

def write_metadata() -> None:
    metadata = {
        "schema_version": "a_policy_final_v2",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "final_columns": FINAL_COLUMNS,
        "value_standards": {
            "category": ["취업", "주거", "unknown"],
            "region_scope": ["서울", "경기", "all", "기타"],
            "apply_status": ["open", "closed", "always", "unknown"],
            "employment_condition": ["employed", "job_seeking", "student", "all", "unknown"],
            "housing_condition": ["homeless", "living_with_parents", "renting", "household_head", "all", "unknown"],
        },
        "notes": [
            "A_policy_handover_v2 기준 최종 D 전달용 schema입니다.",
            "원천 카테고리 일자리는 취업으로 정규화합니다.",
            "원천 카테고리 주거는 주거로 정규화합니다.",
            "최종 파일명은 policy_master_final.csv로 고정합니다.",
        ],
    }

    OUTPUT_META.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def policy_from_api():
    api_key = get_api_key()
    logger.info(f"api_key : {api_key}")
    
    logger.info("온통청년 정책 데이터 수집 시작")
    logger.info("수집 범위: 일자리 + 주거")
    logger.info("대상 지역: 서울 + 경기 중심")
    logger.info("API 키: 환경변수 YOUTH_API_KEY 사용")
    
    all_rows: List[Dict[str, Any]] = []

    for category in CATEGORIES:
        logger.info("=" * 80)
        logger.info(f"{category} 수집 시작")
        logger.info("=" * 80)

        rows = fetch_category(api_key=api_key, category=category)
        all_rows.extend(rows)

    if not all_rows:
        logger.info("수집된 데이터가 없습니다.")
        return
    
    df = pd.DataFrame(all_rows)
    logger.info(f"원본 수집 건수: {len(df)}")

    if "_category" not in df.columns:
        raise ValueError("수집 데이터에 _category 컬럼이 없습니다.")

    # 주거 정책은 전체 수집 후 수도권 필터를 적용한다.
    job_df = df[df["_category"] == "일자리"].copy()
    housing_df = df[df["_category"] == "주거"].copy()

    if len(housing_df) > 0:
        before_housing = len(housing_df)
        housing_df = housing_df[housing_df.apply(is_metro_policy, axis=1)].copy()
        logger.info(f"주거 수도권 필터: {before_housing}건 -> {len(housing_df)}건")

    df = pd.concat([job_df, housing_df], ignore_index=True)
    logger.info(f"수도권 필터 후 통합 건수: {len(df)}")

    before_dedup = len(df)

    if "plcyNo" in df.columns:
        df = df.drop_duplicates(subset=["plcyNo"]).copy()

    logger.info(f"중복 제거: {before_dedup}건 -> {len(df)}건")

    logger.info(f"최종 건수: {len(df)}")
    logger.info("카테고리 분포")
    logger.info(df["_category"].value_counts(dropna=False))
    
    if "_category" in df.columns:
        df = df[df["_category"].isin(["일자리", "주거"])].copy()
        print(f"일자리/주거 필터 후: {len(df)}")

    rows = [build_policy_row(row) for _, row in df.iterrows()]

    out = pd.DataFrame(rows)

    # 최종 컬럼 고정
    out = out[FINAL_COLUMNS]

    # 기본 품질 정리
    out = out[out["policy_id"].notna() & (out["policy_id"].astype(str).str.strip() != "")]
    out = out[out["policy_name"].notna() & (out["policy_name"].astype(str).str.strip() != "")]

    before_dedup = len(out)
    out = out.drop_duplicates(subset=["policy_id"]).copy()

    logger.info(f"policy_id 중복 제거: {before_dedup}건 -> {len(out)}건")
    
    ###### DB 관련 작업 추가 필요
    # logger.info(f"out : {out}")
    
    DATA_DIR.mkdir(exist_ok=True)

    # 파일 저장
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    write_metadata()
    
    # DB 저장

    logger.info(f"저장 완료: {OUTPUT_CSV.name}")
    logger.info(f"메타데이터 저장 완료: {OUTPUT_META.name}")
    logger.info(f"최종 행 수: {len(out)}")

    logger.info("category 분포")
    logger.info(out["category"].value_counts(dropna=False))

    logger.info("region_scope 분포")
    logger.info(out["region_scope"].value_counts(dropna=False))

    logger.info("apply_status 분포")
    logger.info(out["apply_status"].value_counts(dropna=False))

    logger.info("source_url null 개수")
    logger.info(out["source_url"].isna().sum())

    logger.info("최종 컬럼")
    logger.info(out.columns.tolist())
