# FlyRank Social Studio

Backend capstone for the FlyRank Internship.

FlyRank Social Studio takes a stored blog article and turns it into validated, platform-specific social variants that later move through review, scheduling, and reliable publishing.

## Status

- Phase 1 — Design: complete
- Phase 2 — Ingestion and variant generation: complete
- Phase 3 — Human review workflow: next
- Phase 4 — Publisher adapters and idempotency: pending
- Phase 5 — Durable scheduling and hardening: pending

## Implemented

- PostgreSQL persistence with Docker Compose
- raw SQL migrations
- Markdown ingestion
- URL fetch and text extraction
- stored source-of-truth workflow
- Gemini variants for Discord, X-style, and LinkedIn-style
- deterministic constraint validation
- variant persistence and API endpoints
- automated Phase 2 tests

## Current API

```text
POST /posts
GET  /posts/{post_id}
POST /posts/{source_post_id}/variants
GET  /posts/{source_post_id}/variants
```

## Development

```powershell
docker compose up -d
python -m app.db.migrations
uvicorn app.main:app --reload
pytest -q
```

## Notes

- Real secrets belong only in `.env`.
- Real X, LinkedIn, and Instagram publishing are outside core scope.
- Image generation/resizing is not part of this implementation.
