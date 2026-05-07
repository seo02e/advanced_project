from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.policy import PolicyAPI


UPSERT_POLICY_API_SQL = text("""
    INSERT INTO youth_policy (
        policy_id,
        policy_name,
        category,
        subcategory,
        region_scope,
        age_min,
        age_max,
        employment_condition,
        housing_condition,
        income_condition_text,
        apply_start_date,
        apply_end_date,
        apply_status,
        source_org,
        source_url,
        summary,
        source_type,
        source_layer,
        created_at,
        updated_at
    )
    VALUES (
        :policy_id,
        :policy_name,
        :category,
        :subcategory,
        :region_scope,
        :age_min,
        :age_max,
        :employment_condition,
        :housing_condition,
        :income_condition_text,
        :apply_start_date,
        :apply_end_date,
        :apply_status,
        :source_org,
        :source_url,
        :summary,
        :source_type,
        'A',
        now(),
        now()
    )
    ON CONFLICT (policy_id)
    DO UPDATE SET
        policy_name = EXCLUDED.policy_name,
        category = EXCLUDED.category,
        subcategory = EXCLUDED.subcategory,
        region_scope = EXCLUDED.region_scope,
        age_min = EXCLUDED.age_min,
        age_max = EXCLUDED.age_max,
        employment_condition = EXCLUDED.employment_condition,
        housing_condition = EXCLUDED.housing_condition,
        income_condition_text = EXCLUDED.income_condition_text,
        apply_start_date = EXCLUDED.apply_start_date,
        apply_end_date = EXCLUDED.apply_end_date,
        apply_status = EXCLUDED.apply_status,
        source_org = EXCLUDED.source_org,
        source_url = EXCLUDED.source_url,
        summary = EXCLUDED.summary,
        source_type = EXCLUDED.source_type,
        source_layer = 'A',
        updated_at = now()
""")


def upsert_policy_rows(
    db: Session,
    policies: list[PolicyAPI]
) -> int:

    if not policies:
        return 0

    rows = [
        policy.model_dump()
        for policy in policies
    ]

    db.execute(UPSERT_POLICY_API_SQL, rows)

    return len(rows)