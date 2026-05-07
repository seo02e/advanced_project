import logging

import pandas as pd

from app.infra.database import SessionLocal
from app.schemas.policy import PolicyAPI

from app.repositories.policy_repository import (
    upsert_policy_rows
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