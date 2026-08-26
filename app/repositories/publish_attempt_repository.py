from psycopg.rows import dict_row

from app.db.database import get_connection

class PublishAttemptRepository:
    @staticmethod
    def get_successful_by_slot(schedule_slot_id: int) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        schedule_slot_id,
                        adapter_name,
                        attempt_number,
                        status,
                        external_post_id,
                        external_url,
                        preview,
                        error_message,
                        created_at
                    FROM publish_attempts
                    WHERE
                        schedule_slot_id = %s
                        AND status = 'success'
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (schedule_slot_id,),
                )

                return cursor.fetchone()

    @staticmethod
    def create_started(*, schedule_slot_id: int, adapter_name: str) -> dict:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        COALESCE(MAX(attempt_number), 0) + 1
                        AS next_attempt
                    FROM publish_attempts
                    WHERE schedule_slot_id = %s
                    """,
                    (schedule_slot_id,),
                )

                row = cursor.fetchone()
                next_attempt = row["next_attempt"]

                cursor.execute(
                    """
                    INSERT INTO publish_attempts (
                        schedule_slot_id,
                        adapter_name,
                        attempt_number,
                        status
                    )
                    VALUES (%s, %s, %s, 'started')
                    RETURNING
                        id,
                        schedule_slot_id,
                        adapter_name,
                        attempt_number,
                        status,
                        created_at
                    """,
                    (
                        schedule_slot_id,
                        adapter_name,
                        next_attempt,
                    ),
                )

                return cursor.fetchone()

    @staticmethod
    def mark_success(
        *,
        attempt_id: int,
        external_post_id: str | None,
        external_url: str | None,
        preview: str | None,
    ) -> dict:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE publish_attempts
                    SET
                        status = 'success',
                        external_post_id = %s,
                        external_url = %s,
                        preview = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (
                        external_post_id,
                        external_url,
                        preview,
                        attempt_id,
                    ),
                )

                return cursor.fetchone()

    @staticmethod
    def mark_failed(*, attempt_id: int, error_message: str,) -> dict:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE publish_attempts
                    SET
                        status = 'failed',
                        error_message = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (
                        error_message,
                        attempt_id,
                    ),
                )

                return cursor.fetchone()