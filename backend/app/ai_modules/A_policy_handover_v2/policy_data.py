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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent

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


def load_env_file() -> None:
    """
    python-dotenv 없이 .env 파일을 간단히 읽는다.
    우선순위:
    1) 이미 설정된 환경변수
    2) A_policy_handover_v2/.env
    """
    env_path = BASE_DIR / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def get_api_key() -> str:
    load_env_file()

    api_key = os.getenv("YOUTH_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "YOUTH_API_KEY가 설정되어 있지 않습니다.\n"
            "CMD에서 아래처럼 설정하세요.\n"
            "set YOUTH_API_KEY=본인_청년정책_API_KEY"
        )

    return api_key


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

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

    return any(keyword in combined for keyword in METRO_KEYWORDS)


def is_metro_policy(row: pd.Series) -> bool:
    return has_metro_zip(row) or has_metro_keyword(row)


def save_category_files(df: pd.DataFrame, today: str) -> None:
    for category in CATEGORIES:
        sub = df[df["_category"] == category].copy()
        output_path = BASE_DIR / f"policy_master_{category}_{today}.csv"
        sub.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {output_path.name} ({len(sub)}건)")


def main() -> None:
    api_key = get_api_key()

    print("온통청년 정책 데이터 수집 시작")
    print("수집 범위: 일자리 + 주거")
    print("대상 지역: 서울 + 경기 중심")
    print("API 키: 환경변수 YOUTH_API_KEY 사용")
    print("")

    all_rows: List[Dict[str, Any]] = []

    for category in CATEGORIES:
        print("=" * 80)
        print(f"{category} 수집 시작")
        print("=" * 80)

        rows = fetch_category(api_key=api_key, category=category)
        all_rows.extend(rows)
        print("")

    if not all_rows:
        print("수집된 데이터가 없습니다.")
        return

    df = pd.DataFrame(all_rows)
    print(f"원본 수집 건수: {len(df)}")

    if "_category" not in df.columns:
        raise ValueError("수집 데이터에 _category 컬럼이 없습니다.")

    # 주거 정책은 전체 수집 후 수도권 필터를 적용한다.
    job_df = df[df["_category"] == "일자리"].copy()
    housing_df = df[df["_category"] == "주거"].copy()

    if len(housing_df) > 0:
        before_housing = len(housing_df)
        housing_df = housing_df[housing_df.apply(is_metro_policy, axis=1)].copy()
        print(f"주거 수도권 필터: {before_housing}건 -> {len(housing_df)}건")

    df = pd.concat([job_df, housing_df], ignore_index=True)
    print(f"수도권 필터 후 통합 건수: {len(df)}")

    before_dedup = len(df)

    if "plcyNo" in df.columns:
        df = df.drop_duplicates(subset=["plcyNo"]).copy()

    print(f"중복 제거: {before_dedup}건 -> {len(df)}건")

    today = datetime.now().strftime("%Y%m%d")

    save_category_files(df, today)

    output_path = BASE_DIR / f"policy_master_{today}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("")
    print(f"통합 저장 완료: {output_path.name}")
    print(f"최종 건수: {len(df)}")
    print("")
    print("카테고리 분포")
    print(df["_category"].value_counts(dropna=False))


if __name__ == "__main__":
    main()