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

# 정책 API 데이터 업서트 (중복 시 업데이트)
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

# 정책 크롤링 데이터 업서트 (중복 시 업데이트)
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

SELECT_POLICY_ROWS_SQL = text("""
    SELECT
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
        source_layer
    FROM youth_policy
    WHERE source_layer = :source_layer
    ORDER BY id
""")

#   정책 API 데이터 조회 (RAG용) - source_layer 조건으로 조회
def select_policy_rows_for_retrieval(
    db: Session,
    source_layer: str,
) -> list[dict]:

    rows = db.execute(
        SELECT_POLICY_ROWS_SQL,
        {"source_layer": source_layer}
    ).mappings().all()

    return [dict(row) for row in rows]


SELECT_POLICY_CHUNKS_SQL = text("""
    SELECT
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
        source_layer
    FROM policy_chunks
    ORDER BY policy_id, chunk_order
""")


#   정책 크롤링 데이터 조회 (RAG용) - source_layer 조건 없이 전체 조회
def select_policy_chunks_for_retrieval(
    db: Session,
) -> list[dict]:

    rows = db.execute(SELECT_POLICY_CHUNKS_SQL).mappings().all()

    return [dict(row) for row in rows]