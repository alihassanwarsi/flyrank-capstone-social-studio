from psycopg.rows import dict_row

from app.db.database import get_connection


class SourcePostRepository:
    @staticmethod
    def create(
        *,
        source_type: str,
        content: str,
        title: str | None = None,
        source_url: str | None = None,
    ) -> dict:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO source_posts (
                        source_type,
                        source_url,
                        title,
                        content
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING
                        id,
                        source_type,
                        source_url,
                        title,
                        content,
                        created_at
                    """,
                    (
                        source_type,
                        source_url,
                        title,
                        content,
                    ),
                )

                return cursor.fetchone()

    @staticmethod
    def get_by_id(post_id: int) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        source_type,
                        source_url,
                        title,
                        content,
                        created_at
                    FROM source_posts
                    WHERE id = %s
                    """,
                    (post_id,),
                )

                return cursor.fetchone()