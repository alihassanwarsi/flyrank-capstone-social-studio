from uuid import uuid4
from psycopg.rows import dict_row
from app.db.database import get_connection

class ScheduleRepository:
    
    @staticmethod
    def create(*, variant_id: int, scheduled_for) -> dict:
        idempotency_key = f"slot-{uuid4().hex}"

        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO schedule_slots (
                        variant_id,
                        scheduled_for,
                        idempotency_key
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        variant_id,
                        scheduled_for,
                        idempotency_key,
                        status,
                        created_at
                    """,
                    (variant_id, scheduled_for, idempotency_key)
                )
                return cursor.fetchone()

    @staticmethod
    def get_by_id(schedule_id: int) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        variant_id,
                        scheduled_for,
                        idempotency_key,
                        status,
                        created_at
                    FROM schedule_slots
                    WHERE id = %s
                    """,
                    (schedule_id,)
                )
                return cursor.fetchone()

    @staticmethod
    def get_by_variant(variant_id: int) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        variant_id,
                        scheduled_for,
                        idempotency_key,
                        status,
                        created_at
                    FROM schedule_slots
                    WHERE variant_id = %s
                    ORDER BY scheduled_for
                    """,
                    (variant_id,)
                )
                return cursor.fetchall()

    @staticmethod
    def update_status(*, schedule_id: int, status: str) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE schedule_slots
                    SET
                        status = %s,
                        processing_started_at = CASE
                            WHEN %s = 'processing'
                                THEN COALESCE(processing_started_at, NOW())
                            ELSE NULL
                        END
                    WHERE id = %s
                    RETURNING
                        id,
                        variant_id,
                        scheduled_for,
                        idempotency_key,
                        status,
                        created_at
                    """,
                    (status, status, schedule_id)
                )
                return cursor.fetchone()

    @staticmethod
    def get_due_schedules() -> list[dict]:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        variant_id,
                        scheduled_for,
                        idempotency_key,
                        status,
                        created_at
                    FROM schedule_slots
                    WHERE
                        scheduled_for <= NOW()
                        AND status IN ('scheduled', 'failed')
                    ORDER BY scheduled_for ASC
                    """
                )
                return cursor.fetchall()

    @staticmethod
    def claim_due_schedules(limit: int = 10) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    WITH due AS (
                        SELECT id
                        FROM schedule_slots
                        WHERE
                            scheduled_for <= NOW()
                            AND (
                                status IN ('scheduled', 'failed')
                                OR (
                                    status = 'processing'
                                    AND processing_started_at < NOW() - INTERVAL '1 minute'
                                )
                            )
                        ORDER BY scheduled_for ASC
                        FOR UPDATE SKIP LOCKED
                        LIMIT %s
                    )
                    UPDATE schedule_slots AS s
                    SET
                        status = 'processing',
                        processing_started_at = NOW()
                    FROM due
                    WHERE s.id = due.id
                    RETURNING
                        s.id,
                        s.variant_id,
                        s.scheduled_for,
                        s.idempotency_key,
                        s.status,
                        s.created_at
                    """,
                    (limit,)
                )
                return cursor.fetchall()