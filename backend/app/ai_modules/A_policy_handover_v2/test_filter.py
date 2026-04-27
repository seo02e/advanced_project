import pandas as pd

df = pd.read_csv("policy_master_final.csv", dtype={"policy_id": str})


def filter_policies(region_scope=None, age=None, category=None, apply_statuses=None):
    result = df.copy()

    if region_scope:
        result = result[result["region_scope"].isin([region_scope, "all"])]

    if category:
        result = result[result["category"] == category]

    if apply_statuses:
        result = result[result["apply_status"].isin(apply_statuses)]

    if age is not None:
        result = result[
            (result["age_min"].isna() | (result["age_min"] <= age)) &
            (result["age_max"].isna() | (result["age_max"] >= age))
        ]

    return result


tests = [
    {
        "name": "경기 25세 취업 open/always",
        "kwargs": {"region_scope": "경기", "age": 25, "category": "취업", "apply_statuses": ["open", "always"]}
    },
    {
        "name": "서울 26세 open/always",
        "kwargs": {"region_scope": "서울", "age": 26, "apply_statuses": ["open", "always"]}
    },
    {
        "name": "서울 27세 주거 open/always",
        "kwargs": {"region_scope": "서울", "age": 27, "category": "주거", "apply_statuses": ["open", "always"]}
    }
]

for t in tests:
    print(f"\n=== {t['name']} ===")
    out = filter_policies(**t["kwargs"])
    print("결과 개수:", len(out))
    if len(out) > 0:
        print(out[["policy_id", "policy_name", "category", "region_scope", "apply_status"]].head(5).to_string(index=False))