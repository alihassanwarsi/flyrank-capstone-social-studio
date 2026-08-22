from pathlib import Path

from app.db.database import get_connection


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def run_migrations():
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )

        for migration_file in migration_files:
            version = migration_file.name

            already_applied = conn.execute(
                """
                SELECT 1
                FROM schema_migrations
                WHERE version = %s
                """,
                (version,),
            ).fetchone()

            if already_applied:
                print(f"Skipping {version}")
                continue

            sql = migration_file.read_text(encoding="utf-8")

            conn.execute(sql)

            conn.execute(
                """
                INSERT INTO schema_migrations (version)
                VALUES (%s)
                """,
                (version,),
            )

            print(f"Applied {version}")


if __name__ == "__main__":
    run_migrations()