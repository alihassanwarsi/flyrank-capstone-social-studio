# Build Log

## Project Setup
Started a fresh implementation using the current **Social Media Studio** brief.

## Phase 1 - Design
Created `docs/DESIGN.md` before feature implementation.

Key decisions:
- stored blog post is the source of truth
- Markdown or URL input
- Discord real publisher; X and LinkedIn mocks later
- deterministic constraints
- durable scheduling and idempotency later

## Phase 2 - Ingestion and Variant Generation

Added:
- PostgreSQL 16 with Docker Compose
- Psycopg connection
- raw SQL migration runner
- source post repository
- FastAPI ingestion API
- Markdown and URL ingestion
- URL extraction with `httpx` + BeautifulSoup
- `variants` table and repository
- platform constraint profiles and validator
- Gemini variant generator
- variant service and API endpoints
- automated tests

Personally verified:
- DB connectivity and persistence
- Markdown and URL ingestion
- three generated platform variants
- successful validation and persistence

Automated verification:
- stored content is used for generation
- three variants are saved
- invalid variant is blocked before persistence
- API success / 404 / 409 behavior

Latest test run: `5 passed, 1 warning`

Phase 2 status: Complete.
