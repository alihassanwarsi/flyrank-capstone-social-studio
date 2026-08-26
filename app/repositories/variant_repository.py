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
                        status,
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
    def get_by_id(variant_id: int) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        source_post_id,
                        platform,
                        content,
                        status,
                        created_at,
                        updated_at
                    FROM variants
                    WHERE id = %s
                    """,
                    (variant_id,),
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
                        status,
                        created_at,
                        updated_at
                    FROM variants
                    WHERE source_post_id = %s
                    ORDER BY id
                    """,
                    (source_post_id,),
                )

                return cursor.fetchall()

    @staticmethod
    def update_content(
        *,
        variant_id: int,
        content: str,
    ) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE variants
                    SET
                        content = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING
                        id,
                        source_post_id,
                        platform,
                        content,
                        status,
                        created_at,
                        updated_at
                    """,
                    (
                        content,
                        variant_id,
                    ),
                )

                return cursor.fetchone()

    @staticmethod
    def update_status(
        *,
        variant_id: int,
        status: str,
    ) -> dict | None:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    UPDATE variants
                    SET
                        status = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING
                        id,
                        source_post_id,
                        platform,
                        content,
                        status,
                        created_at,
                        updated_at
                    """,
                    (
                        status,
                        variant_id,
                    ),
                )

                return cursor.fetchone()