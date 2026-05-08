from sqlalchemy import text
from sqlalchemy.orm import Session


INSERT_BATCH_HISTORY_SQL = text("""
    INSERT INTO batch_history (
        batch_name,
        batch_yn,
        batch_error
    )
    VALUES (
        :batch_name,
        :batch_yn,
        :batch_error
    )
""")


def insert_batch_history(
    db: Session,
    batch_name: str,
    batch_yn: str,
    batch_error: str | None = None
):

    db.execute(
        INSERT_BATCH_HISTORY_SQL,
        {
            "batch_name": batch_name,
            "batch_yn": batch_yn,
            "batch_error": batch_error
        }
    )