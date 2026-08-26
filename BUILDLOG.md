# Build Log

## Project Setup
Started a fresh implementation using the current **Social Media Studio** capstone brief.

## Phase 1 - Design
Defined the source-of-truth workflow, constraints, review flow, publisher interface, data model, API surface, and non-goals.

## Phase 2 - Ingestion and Variant Generation
Built PostgreSQL persistence, Markdown/URL ingestion, Gemini generation, validation, persistence, and API endpoints.

Phase 2 status: Complete.

## Phase 3 - Human Review Workflow
Added review statuses, edit/approve/reject behavior, schedule slots, and the approved-only scheduling gate.

Phase 3 status: Complete.

## Phase 4 - Publisher Adapters and Idempotency

Added:
- `SocialPublisher` base interface
- `PublishResult`
- real Discord webhook publisher
- mock X publisher
- mock LinkedIn publisher
- environment-configured publisher registry
- schedule idempotency keys
- `publish_attempts` table and repository
- publishing service
- manual publish endpoint

Reliability behavior:
- publish attempts are persisted
- existing successful attempts are checked before publishing again
- repeated successful schedule calls do not call the publisher again

Personally verified:
- real Discord publishing
- mock X publishing
- mock LinkedIn publishing
- adapter swapping through configuration
- no duplicate Discord message on a repeated successful schedule publish

Fixed during development:
- publish attempt numbering with Psycopg `dict_row` now reads the aliased value using `row["next_attempt"]`

Phase 4 status: Complete.
