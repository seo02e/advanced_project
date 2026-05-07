import logging

import pandas as pd

from app.infra.database import SessionLocal
from app.schemas.policy import PolicyAPI, PolicyCrawling

from app.repositories.policy_repository import (
    upsert_policy_rows,
    upsert_policy_chunks
)


from app.repositories.batch_repository import insert_batch_history
logger = logging.getLogger(__name__)


def save_policy_api_df(out: pd.DataFrame) -> int:

    db = SessionLocal()

    try:
        out_for_db = out.where(pd.notnull(out), None)

        policies = [
            PolicyAPI(**row)
            for row in out_for_db.to_dict(orient="records")
        ]

        saved_count = upsert_policy_rows(
            db=db,
            policies=policies
        )

        insert_batch_history(
            db=db,
            batch_name="youth_policy_api_batch",
            batch_yn="Y",
            batch_error=None
        )

        db.commit()

        logger.info(
            f"정책 API 데이터 DB 저장 완료: {saved_count}건"
        )

        return saved_count

    except Exception as e:

        db.rollback()

        logger.exception(
            f"정책 API 데이터 DB 저장 실패: {e}"
        )

        fail_db = SessionLocal()

        try:
            insert_batch_history(
                db=fail_db,
                batch_name="youth_policy_api_batch",
                batch_yn="N",
                batch_error=str(e)
            )

            fail_db.commit()

        except Exception:

            fail_db.rollback()

            logger.exception(
                "batch_history 실패 로그 저장 실패"
            )

        finally:
            fail_db.close()

        raise

    finally:
        db.close()
        
def save_policy_crawling(chunk_rows: list[dict]) -> int:
    db = SessionLocal()

    try:
        crawling_chunks = [
            PolicyCrawling(**row)
            for row in chunk_rows
        ]

        crawling_policies = [
            PolicyAPI(
                policy_id=chunk.policy_id or chunk.chunk_id,
                policy_name=chunk.policy_name,
                category="주거",
                subcategory=None,
                region_scope=None,
                age_min=None,
                age_max=None,
                employment_condition=None,
                housing_condition=None,
                income_condition_text=None,
                apply_start_date=None,
                apply_end_date=None,
                apply_status=None,
                source_org=chunk.issuing_org,
                source_url=chunk.source_url,
                summary=None,
                source_type="crawling",
                source_layer="B",
            )
            for chunk in crawling_chunks
            if chunk.policy_id
        ]

        saved_policy_count = upsert_policy_rows(
            db=db,
            policies=crawling_policies
        )

        db.flush()

        saved_chunk_count = upsert_policy_chunks(
            db=db,
            chunks=crawling_chunks
        )

        insert_batch_history(
            db=db,
            batch_name="youth_policy_crawling_batch",
            batch_yn="Y",
            batch_error=None
        )

        db.commit()

        logger.info(
            f"정책 크롤링 DB 저장 완료: policy={saved_policy_count}건, chunks={saved_chunk_count}건"
        )

        return saved_chunk_count

    except Exception as e:
        db.rollback()
        logger.exception(f"정책 크롤링 DB 저장 실패: {e}")
        
        fail_db = SessionLocal()

        try:
            insert_batch_history(
                db=fail_db,
                batch_name="youth_policy_crawling_batch",
                batch_yn="N",
                batch_error=str(e)
            )

            fail_db.commit()

        except Exception:
            fail_db.rollback()
            logger.exception("youth_policy_crawling_batch 실패 로그 저장 실패")

        finally:
            fail_db.close()

        raise

    finally:
        db.close()