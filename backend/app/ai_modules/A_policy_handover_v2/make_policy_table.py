# make_policy_table.py
# A_policy_handover_v2
# 목적:
# 1) 최신 policy_master_YYYYMMDD.csv 자동 탐색
# 2) 원천 CSV를 D 전달용 17컬럼 schema로 변환
# 3) 최종 파일 policy_master_final.csv 생성
# 4) policy_metadata.json 생성

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_CSV = BASE_DIR / "policy_master_final.csv"
OUTPUT_META = BASE_DIR / "policy_metadata.json"

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


def parse_date(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None

    nums = re.sub(r"\D", "", str(value))

    if len(nums) >= 8:
        return f"{nums[:4]}-{nums[4:6]}-{nums[6:8]}"

    return None


def find_latest_source_csv() -> Path:
    """
    policy_master_YYYYMMDD.csv만 찾는다.
    policy_master_일자리_YYYYMMDD.csv, policy_master_주거_YYYYMMDD.csv, policy_master_final.csv는 제외한다.
    """
    pattern = re.compile(r"^policy_master_(\d{8})\.csv$")

    candidates = []

    for path in BASE_DIR.glob("policy_master_*.csv"):
        match = pattern.match(path.name)

        if match:
            candidates.append((match.group(1), path))

    if not candidates:
        raise FileNotFoundError(
            "원천 CSV를 찾지 못했습니다. 먼저 policy_data.py를 실행해서 "
            "policy_master_YYYYMMDD.csv를 생성하세요."
        )

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def normalize_category(row: pd.Series) -> str:
    raw_category = clean_text(row.get("_category")) or clean_text(row.get("lclsfNm")) or ""

    if "일자리" in raw_category or "취업" in raw_category:
        return "취업"

    if "주거" in raw_category:
        return "주거"

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


def main() -> None:
    input_path = find_latest_source_csv()

    print(f"입력 파일: {input_path.name}")

    df = pd.read_csv(input_path, dtype={"plcyNo": str})
    print(f"원본 행 수: {len(df)}")

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

    print(f"policy_id 중복 제거: {before_dedup}건 -> {len(out)}건")

    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    write_metadata()

    print("")
    print(f"저장 완료: {OUTPUT_CSV.name}")
    print(f"메타데이터 저장 완료: {OUTPUT_META.name}")
    print(f"최종 행 수: {len(out)}")

    print("")
    print("category 분포")
    print(out["category"].value_counts(dropna=False))

    print("")
    print("region_scope 분포")
    print(out["region_scope"].value_counts(dropna=False))

    print("")
    print("apply_status 분포")
    print(out["apply_status"].value_counts(dropna=False))

    print("")
    print("source_url null 개수")
    print(out["source_url"].isna().sum())

    print("")
    print("최종 컬럼")
    print(out.columns.tolist())


if __name__ == "__main__":
    main()