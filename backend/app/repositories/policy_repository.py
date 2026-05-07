from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.policy import PolicyAPI, PolicyCrawling


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
        :source_layer,
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
        source_layer = EXCLUDED.source_layer,
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

UPSERT_POLICY_CHUNKS_SQL = text("""
    INSERT INTO policy_chunks (
        chunk_id,
        policy_id,
        policy_name,
        issuing_org,
        source_doc_name,
        source_url,
        section_title,
        chunk_text,
        chunk_order,
        has_table,
        doc_type,
        created_from,
        source_layer,
        created_at,
        updated_at
    )
    VALUES (
        :chunk_id,
        :policy_id,
        :policy_name,
        :issuing_org,
        :source_doc_name,
        :source_url,
        :section_title,
        :chunk_text,
        :chunk_order,
        :has_table,
        :doc_type,
        :created_from,
        :source_layer,
        now(),
        now()
    )
    ON CONFLICT (chunk_id)
    DO UPDATE SET
        policy_id = EXCLUDED.policy_id,
        policy_name = EXCLUDED.policy_name,
        issuing_org = EXCLUDED.issuing_org,
        source_doc_name = EXCLUDED.source_doc_name,
        source_url = EXCLUDED.source_url,
        section_title = EXCLUDED.section_title,
        chunk_text = EXCLUDED.chunk_text,
        chunk_order = EXCLUDED.chunk_order,
        has_table = EXCLUDED.has_table,
        doc_type = EXCLUDED.doc_type,
        created_from = EXCLUDED.created_from,
        source_layer = EXCLUDED.source_layer,
        updated_at = now()
""")

def upsert_policy_chunks(
    db: Session,
    chunks: list[PolicyCrawling]
) -> int:
    if not chunks:
        return 0

    rows = [
        chunk.model_dump()
        for chunk in chunks
    ]

    db.execute(UPSERT_POLICY_CHUNKS_SQL, rows)

    return len(rows)