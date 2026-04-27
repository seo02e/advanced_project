import pandas as pd

df = pd.read_csv("../A_policy_handover_v2/policy_master_final.csv", dtype={"policy_id": str})


def filter_policies(profile):
    result = df.copy()

    # 지역
    result = result[result["region_scope"].isin([profile["region"], "all"])]

    # 카테고리
    if "취업" in profile.get("interest_tags", []):
        result = result[result["category"] == "취업"]

    # 상태
    result = result[result["apply_status"].isin(["open", "always"])]

    # 나이
    age = profile.get("age")
    if age:
        result = result[
            (result["age_min"].isna() | (result["age_min"] <= age)) &
            (result["age_max"].isna() | (result["age_max"] >= age))
        ]

    return result.head(5)