import pandas as pd
import re
from datetime import datetime

INPUT_PATH = "policy_master_20260421.csv"
OUTPUT_CSV = "policy_master_final.csv"
OUTPUT_META = "policy_metadata.json"


def clean_text(x):
    if pd.isna(x):
        return None
    x = str(x)
    x = re.sub(r"<[^>]+>", " ", x)
    x = re.sub(r"[\r\n\t]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x if x else None


def parse_date(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    nums = re.sub(r"\D", "", str(x))
    if len(nums) >= 8:
        return f"{nums[:4]}-{nums[4:6]}-{nums[6:8]}"
    return None


def normalize_region(row):
    text_parts = [
        clean_text(row.get("rgtrHghrkInstCdNm")),
        clean_text(row.get("rgtrInstCdNm")),
        clean_text(row.get("sprvsnInstCdNm")),
        clean_text(row.get("operInstCdNm")),
        clean_text(row.get("plcyExplnCn")),
        clean_text(row.get("plcyKywdNm")),
    ]
    text = " ".join([t for t in text_parts if t])

    nationwide_orgs = [
        "고용노동부", "중소벤처기업부", "교육부", "국가보훈부",
        "농림축산식품부", "정부산하기관", "정부산하기관및위원회"
    ]

    if "전국" in text or "전국단위" in text:
        return "all"
    if any(org in text for org in nationwide_orgs):
        return "all"
    if "서울" in text:
        return "서울"
    if "경기" in text:
        return "경기"
    return "기타"


def normalize_category(raw):
    text = clean_text(raw) or ""
    if "일자리" in text or "취업" in text:
        return "취업"
    if "주거" in text:
        return "주거"
    return "unknown"


def normalize_status(start_date, end_date):
    if not start_date and not end_date:
        return "always"
    today = datetime.now().strftime("%Y-%m-%d")
    if end_date and end_date < today:
        return "closed"
    if start_date and start_date > today:
        return "unknown"
    return "open"


def pick_subcategory(name, desc):
    text = f"{clean_text(name) or ''} {clean_text(desc) or ''}"
    if "월세" in text:
        return "월세지원"
    if "전세" in text:
        return "전세지원"
    if "창업" in text:
        return "창업지원"
    if "취업" in text or "채용" in text:
        return "취업지원"
    if "주거" in text:
        return "주거지원"
    return "unknown"


def pick_employment_condition(name, desc):
    text = f"{clean_text(name) or ''} {clean_text(desc) or ''}"
    if any(k in text for k in ["재직", "근로", "직장인"]):
        return "employed"
    if any(k in text for k in ["구직", "취준", "미취업", "실업"]):
        return "job_seeking"
    if any(k in text for k in ["누구나", "제한 없음", "전체"]):
        return "all"
    return "unknown"


def pick_housing_condition(name, desc):
    text = f"{clean_text(name) or ''} {clean_text(desc) or ''}"
    if "무주택" in text:
        return "homeless"
    if "부모" in text:
        return "living_with_parents"
    if any(k in text for k in ["자취", "월세", "전세"]):
        return "renting"
    if "세대주" in text:
        return "household_head"
    return "unknown"


def make_summary(desc):
    text = clean_text(desc)
    if not text:
        return None
    return text[:120]


df = pd.read_csv(INPUT_PATH, dtype={"plcyNo": str})

rows = []
for _, row in df.iterrows():
    name = clean_text(row.get("plcyNm"))
    desc = clean_text(row.get("plcyExplnCn"))
    source_org = clean_text(row.get("operInstCdNm")) or clean_text(row.get("sprvsnInstCdNm")) or "정보없음"

    start_date = parse_date(row.get("bizPrdBgngYmd"))
    end_date = parse_date(row.get("bizPrdEndYmd"))
    category_raw = row.get("_category") if pd.notna(row.get("_category")) else row.get("lclsfNm")

    source_url = None
    if pd.notna(row.get("aplyUrlAddr")) and str(row.get("aplyUrlAddr")).strip():
        source_url = str(row.get("aplyUrlAddr")).strip()
    elif pd.notna(row.get("refUrlAddr1")) and str(row.get("refUrlAddr1")).strip():
        source_url = str(row.get("refUrlAddr1")).strip()

    rows.append({
        "policy_id": str(row.get("plcyNo", "")),
        "policy_name": name,
        "category": normalize_category(category_raw),
        "subcategory": pick_subcategory(name, desc),
        "region_scope": normalize_region(row),
        "age_min": row.get("sprtTrgtMinAge") if pd.notna(row.get("sprtTrgtMinAge")) else None,
        "age_max": row.get("sprtTrgtMaxAge") if pd.notna(row.get("sprtTrgtMaxAge")) else None,
        "employment_condition": pick_employment_condition(name, desc),
        "housing_condition": pick_housing_condition(name, desc),
        "income_condition_text": clean_text(row.get("earnCndSeCdNm")) or clean_text(row.get("earnEtcCn")),
        "apply_start_date": start_date,
        "apply_end_date": end_date,
        "apply_status": normalize_status(start_date, end_date),
        "source_org": source_org,
        "source_url": source_url,
        "summary": make_summary(desc),
        "source_type": "api"
    })

out = pd.DataFrame(rows)
out = out.drop_duplicates(subset=["policy_id"])
out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("저장 완료:", OUTPUT_CSV)
print("행 수:", len(out))
print("\ncategory 분포")
print(out["category"].value_counts(dropna=False))
print("\napply_status 분포")
print(out["apply_status"].value_counts(dropna=False))
print("\nregion_scope 분포")
print(out["region_scope"].value_counts(dropna=False))