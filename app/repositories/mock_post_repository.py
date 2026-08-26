from psycopg.rows import dict_row

from app.db.database import get_connection


class MockPostRepository:
    @staticmethod
    def create_or_get(
        *,
        adapter_name: str,
        idempotency_key: str,
        content: str,
    ) -> dict:
        with get_connection() as conn:
            with conn.cursor(
                row_factory=dict_row
            ) as cursor:
                cursor.execute(
                    """
                    INSERT INTO mock_posts (
                        adapter_name,
                        idempotency_key,
                        content
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (
                        adapter_name,
                        idempotency_key
                    )
                    DO NOTHING
                    RETURNING
                        id,
                        adapter_name,
                        idempotency_key,
                        content,
                        created_at
                    """,
                    (
                        adapter_name,
                        idempotency_key,
                        content,
                    ),
                )

                created = cursor.fetchone()

                if created is not None:
                    return created

                cursor.execute(
                    """
                    SELECT
                        id,
                        adapter_name,
                        idempotency_key,
                        content,
                        created_at
                    FROM mock_posts
                    WHERE
                        adapter_name = %s
                        AND idempotency_key = %s
                    """,
                    (
                        adapter_name,
                        idempotency_key,
                    ),
                )

                existing = cursor.fetchone()

                if existing is None:
                    raise RuntimeError(
                        "Mock post could not be recovered."
                    )

                if existing["content"] != content:
                    raise RuntimeError(
                        "Idempotency key was reused "
                        "with different content."
                    )

                return existing