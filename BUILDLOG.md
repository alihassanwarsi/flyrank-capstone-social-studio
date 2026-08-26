# Build Log

## Project Setup

Started a fresh implementation using the current **Social Media Studio** capstone brief.

## Phase 1 - Design

Defined the source-of-truth workflow, platform constraints, review states, publisher interface, data model, API surface, and non-goals.

## Phase 2 - Ingestion and Variant Generation

Added:
- PostgreSQL with Docker Compose
- Psycopg and raw SQL migrations
- Markdown and URL ingestion
- URL extraction with `httpx` and BeautifulSoup
- source post and variant repositories
- Gemini generation
- deterministic platform constraint validation
- variant API endpoints

Personally verified the ingestion and generation flow.

Phase 2 status: Complete.

## Phase 3 - Human Review Workflow

Added:
- review status migration
- variant edit/status repository operations
- review service
- edit, approve, and reject endpoints
- schedule slots table
- schedule repository and service
- schedule API endpoint

Business rules:
- generated variants begin as `draft`
- only draft variants can be edited
- edited content is revalidated
- only draft variants can be approved or rejected
- only approved variants can be scheduled
- schedules must use a future timestamp

Personally verified the workflow through FastAPI Swagger.

Phase 3 status: Complete.
