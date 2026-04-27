import os
import requests
import pandas as pd
import time
from datetime import datetime

URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
API_KEY = "2bbe939c-244e-48be-bc27-b658929481c0"

METRO_ZIP_CODES = [
    "11110", "11140", "11170", "11200", "11215",
    "11230", "11260", "11290", "11305", "11320",
    "11350", "11380", "11410", "11440", "11470",
    "11500", "11530", "11545", "11560", "11590",
    "11620", "11650", "11680", "11710", "11740",
    "28110", "28140", "28177", "28185", "28200",
    "28237", "28245", "28260", "28710", "28720",
    "41111", "41113", "41115", "41117",
    "41131", "41133", "41135",
    "41150",
    "41171", "41173",
    "41192", "41194", "41196",
    "41210",
    "41220",
    "41250",
    "41271", "41273",
    "41281", "41285", "41287",
    "41290",
    "41310",
    "41360",
    "41370",
    "41390",
    "41410",
    "41430",
    "41450",
    "41461", "41463", "41465",
    "41480",
    "41500",
    "41550",
    "41570",
    "41591", "41593", "41595", "41597",
    "41610",
    "41630",
    "41650",
    "41670",
    "41800",
    "41820",
    "41830",
]

ZIP_PARAM = ",".join(METRO_ZIP_CODES)
CATEGORIES = ["일자리", "주거"]


def fetch_page(api_key, category, page, page_size=100):
    params = {
        "apiKeyNm": api_key,
        "pageNum": page,
        "pageSize": page_size,
        "pageType": "1",
        "rtnType": "json",
        "lclsfNm": category,
        "zipCd": ZIP_PARAM,
    }
    resp = requests.get(URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    policies = data.get("result", {}).get("youthPolicyList", [])
    return policies


def fetch_category(api_key, category, page_size=100):
    all_rows = []
    page = 1

    while True:
        try:
            rows = fetch_page(api_key, category, page, page_size)
        except Exception as e:
            print(f"\n  오류 [{category}] 페이지 {page}: {e}")
            break

        if not rows:
            break

        for row in rows:
            row["_category"] = category

        all_rows.extend(rows)
        print(f"  [{category}] {page}페이지 -> {len(rows)}건 (누적 {len(all_rows)}건)")

        if len(rows) < page_size:
            break

        page += 1
        time.sleep(0.3)

    print(f"  [{category}] 완료 - 총 {len(all_rows)}건")
    return all_rows


def main():
    if not API_KEY:
        raise ValueError("YOUTH_API_KEY 환경변수가 비어 있습니다.")

    print("온통청년 정책 데이터 수집 시작")
    print("지역: 서울 + 인천 + 경기")
    print("카테고리: 일자리, 주거\n")

    all_policies = []

    for category in CATEGORIES:
        print(f">> {category} 수집 중...")
        rows = fetch_category(API_KEY, category)
        all_policies.extend(rows)
        print("")

    if not all_policies:
        print("수집된 데이터가 없습니다.")
        return

    df = pd.DataFrame(all_policies)

    before = len(df)
    if "plcyNo" in df.columns:
        df = df.drop_duplicates(subset=["plcyNo"])
    after = len(df)
    if before != after:
        print(f"중복 제거: {before}건 -> {after}건")

    today = datetime.now().strftime("%Y%m%d")

    for category in CATEGORIES:
        sub = df[df["_category"] == category].drop(columns=["_category"])
        fname = f"policy_master_{category}_{today}.csv"
        sub.to_csv(fname, index=False, encoding="utf-8-sig")
        print(f"저장 완료: {fname} ({len(sub)}건)")

    fname_all = f"policy_master_{today}.csv"
    df.to_csv(fname_all, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {fname_all} ({len(df)}건, 통합)")


if __name__ == "__main__":
    main()