# BUILDLOG

## Phase 1 — Design
Defined ingestion, source-of-truth persistence, platform constraints, review states, publisher interface, data model, API surface, and non-goals.

## Phase 2 — Ingestion and Generation
Added PostgreSQL connection, raw SQL migrations, source post persistence, Markdown/URL ingestion, FastAPI endpoints, variant persistence, deterministic validation, and Gemini generation.

## Phase 3 — Review and Scheduling
Added variant statuses, editing with revalidation, approve/reject behavior, schedule slots, future-time validation, and approved-only scheduling.

## Phase 4 — Publishers and Idempotency
Added `SocialPublisher`, `PublishResult`, real Discord publishing, X/LinkedIn mocks, config-based registry, schedule idempotency keys, `publish_attempts`, publishing service, and manual publish endpoint.

Fixed a Psycopg `dict_row` bug by reading the aliased attempt-number value with `row["next_attempt"]`.

## Phase 5 — Durable Worker and Hardening
Added due-schedule processing, automatic polling worker, publish history endpoint, atomic claiming using `FOR UPDATE SKIP LOCKED`, `processing_started_at`, and stale-processing recovery.

Verified worker restart recovery by letting a schedule become due while the worker was stopped, then restarting it and observing successful processing.

Added deterministic tests for invalid variant blocking, unapproved scheduling refusal, duplicate publish prevention, and config-only adapter swapping.

Updated an older API test fixture after the required variant `status` field was introduced.

Final test result:

```text
9 passed
```

## Final Flow

```text
ingest
-> persist source
-> generate
-> validate
-> review
-> approve
-> schedule
-> durable worker
-> publish
-> record history
-> prevent repeated successful publish
```
