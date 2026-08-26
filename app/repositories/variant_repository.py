from psycopg.rows import dict_row

from app.db.database import get_connection


class VariantRepository:
    @staticmethod
    def create(
        *,
        source_post_id: int,
        platform: str,
        content: str,
    ) -> dict:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO variants (
                        source_post_id,
                        platform,
                        content
                    )
                    VALUES (%s, %s, %s)
                    RETURNING
                        id,
                        source_post_id,
                        platform,
                        content,
                        created_at,
                        updated_at
                    """,
                    (
                        source_post_id,
                        platform,
                        content,
                    ),
                )

                return cursor.fetchone()

    @staticmethod
    def get_by_source_post(source_post_id: int) -> list[dict]:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        source_post_id,
                        platform,
                        content,
                        created_at,
                        updated_at
                    FROM variants
                    WHERE source_post_id = %s
                    ORDER BY id
                    """,
                    (source_post_id,),
                )

                return cursor.fetchall()