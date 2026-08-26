# FlyRank Social Studio

Backend capstone for the FlyRank Internship.

FlyRank Social Studio ingests a blog post, stores the original source of truth, generates platform-specific social variants, validates them, sends them through human review, schedules approved variants, and publishes them through one real adapter and two mock adapters.

## Status

- Phase 1 — Design: complete
- Phase 2 — Ingestion and generation: complete
- Phase 3 — Human review and scheduling gate: complete
- Phase 4 — Publisher adapters and idempotent publishing: complete
- Phase 5 — Durable worker, recovery, publish history, and hardening: complete

## Architecture

```text
Markdown / URL
      |
      v
SourcePost in PostgreSQL
      |
      v
Gemini variant generation
      |
      v
Deterministic validation
      |
      v
draft -> edit / approve / reject
      |
      v
approved variant
      |
      v
schedule_slots
      |
      v
durable polling worker
      |
      v
SocialPublisher
   /      |       \
Discord   X       LinkedIn
 real    mock       mock
      |
      v
publish_attempts / publish history
```

## Core Features

- Markdown and URL ingestion
- PostgreSQL source-of-truth persistence
- Gemini generation for Discord, X-style, and LinkedIn-style variants
- deterministic platform constraints
- bad variants blocked before review
- human edit, approve, and reject workflow
- only approved variants can be scheduled
- durable PostgreSQL-backed scheduling
- automatic background worker
- worker restart recovery
- atomic due-job claiming with `FOR UPDATE SKIP LOCKED`
- stale processing lease recovery
- real Discord publishing
- mock X and LinkedIn publishing
- configuration-based adapter swapping
- publish attempt persistence
- duplicate prevention for repeated successful schedule publishes
- publish history API

## API

```text
POST /posts
GET  /posts/{post_id}

POST /posts/{source_post_id}/variants
GET  /posts/{source_post_id}/variants

PATCH /variants/{variant_id}
POST  /variants/{variant_id}/approve
POST  /variants/{variant_id}/reject

POST /variants/{variant_id}/schedule

POST /schedules/{schedule_id}/publish
GET  /publish-history
```

## Local Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Fill in PostgreSQL, Gemini, publisher-adapter, and Discord webhook values. Never commit `.env`.

### 4. Start PostgreSQL

```powershell
docker compose up -d
docker compose ps
```

### 5. Run migrations

```powershell
python -m app.db.migrations
```

### 6. Start the API

```powershell
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the worker

In a second activated terminal:

```powershell
python -m app.worker
```

## End-to-End Flow

1. Create a post with Markdown or a URL.
2. Generate variants.
3. Review/edit them.
4. Approve a variant.
5. Schedule it for a future timestamp.
6. Keep the worker running.
7. At the scheduled time, the worker automatically publishes the slot.
8. Inspect `GET /publish-history`.

## Reliability

Schedules live in PostgreSQL, so worker shutdown does not erase them. On restart, overdue rows are discovered again.

Workers claim due rows atomically using PostgreSQL row locking with `SKIP LOCKED`. Claimed jobs record `processing_started_at`; stale processing rows can later be recovered.

Each schedule slot has an idempotency key. Before publishing, the service checks for an existing successful attempt. If one exists, it returns that success instead of invoking the publisher again.

## Tests

Run:

```powershell
pytest -q
```

Final verified result:

```text
9 passed
```

Automated coverage includes invalid variant blocking, unapproved scheduling refusal, duplicate publish prevention, and configuration-only adapter swapping.

## Manually Verified

- Markdown and URL ingestion
- real Discord publishing
- mock X publishing
- mock LinkedIn publishing
- configuration-based adapter swap
- automatic scheduled publishing
- worker-off / schedule-due / worker-restart recovery
- repeated successful Discord publish does not create a second message
- publish history visibility

## Security

- `.env` is ignored by Git.
- Real API keys and webhook URLs must never be committed.
- `.env.example` contains placeholders only.

## Out of Scope

- real X publishing
- real LinkedIn publishing
- real Instagram publishing
- image generation
- analytics and engagement tracking
