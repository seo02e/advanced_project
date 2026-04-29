# test_filter.py
# A_policy_handover_v2
# 목적:
# policy_master_final.csv가 D에서 바로 필터 가능한지 확인

from __future__ import annotations

import pandas as pd


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


df = pd.read_csv("policy_master_final.csv", dtype={"policy_id": str})

df["age_min"] = pd.to_numeric(df["age_min"], errors="coerce")
df["age_max"] = pd.to_numeric(df["age_max"], errors="coerce")


def validate_schema() -> None:
    missing = [col for col in FINAL_COLUMNS if col not in df.columns]
    extra = [col for col in df.columns if col not in FINAL_COLUMNS]

    print("=== schema 검증 ===")
    print("행 수:", len(df))
    print("컬럼 수:", len(df.columns))
    print("누락 컬럼:", missing)
    print("추가 컬럼:", extra)

    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")


def filter_policies(
    region_scope=None,
    age=None,
    category=None,
    apply_statuses=None,
):
    result = df.copy()

    if region_scope:
        result = result[result["region_scope"].isin([region_scope, "all"])]

    if category:
        result = result[result["category"] == category]

    if apply_statuses:
        result = result[result["apply_status"].isin(apply_statuses)]

    if age is not None:
        result = result[
            (result["age_min"].isna() | (result["age_min"] <= age))
            & (result["age_max"].isna() | (result["age_max"] >= age))
        ]

    return result


def print_distribution() -> None:
    print("")
    print("=== category 분포 ===")
    print(df["category"].value_counts(dropna=False))

    print("")
    print("=== region_scope 분포 ===")
    print(df["region_scope"].value_counts(dropna=False))

    print("")
    print("=== apply_status 분포 ===")
    print(df["apply_status"].value_counts(dropna=False))


def run_tests() -> None:
    tests = [
        {
            "name": "경기 25세 취업 open/always",
            "kwargs": {
                "region_scope": "경기",
                "age": 25,
                "category": "취업",
                "apply_statuses": ["open", "always"],
            },
        },
        {
            "name": "서울 27세 주거 open/always",
            "kwargs": {
                "region_scope": "서울",
                "age": 27,
                "category": "주거",
                "apply_statuses": ["open", "always"],
            },
        },
        {
            "name": "인천 25세 주거 open/always",
            "kwargs": {
                "region_scope": "인천",
                "age": 25,
                "category": "주거",
                "apply_statuses": ["open", "always"],
            },
        },
        {
            "name": "서울 31세 전체 open/always",
            "kwargs": {
                "region_scope": "서울",
                "age": 31,
                "apply_statuses": ["open", "always"],
            },
        },
    ]

    for test in tests:
        print("")
        print("=" * 80)
        print(test["name"])
        print("=" * 80)

        out = filter_policies(**test["kwargs"])

        print("결과 개수:", len(out))

        if len(out) > 0:
            print(
                out[
                    [
                        "policy_id",
                        "policy_name",
                        "category",
                        "subcategory",
                        "region_scope",
                        "apply_status",
                        "source_org",
                    ]
                ]
                .head(10)
                .to_string(index=False)
            )


if __name__ == "__main__":
    validate_schema()
    print_distribution()
    run_tests()