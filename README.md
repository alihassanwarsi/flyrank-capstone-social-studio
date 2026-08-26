# FlyRank Social Studio

Backend capstone for the FlyRank Internship.

FlyRank Social Studio takes a stored blog article and turns it into validated, platform-specific social variants that move through human review, scheduling, and reliable publishing.

## Status

- Phase 1 — Design: complete
- Phase 2 — Ingestion and variant generation: complete
- Phase 3 — Human review workflow: complete
- Phase 4 — Publisher adapters and idempotency: next
- Phase 5 — Durable scheduling and hardening: pending

## Implemented

- PostgreSQL persistence with Docker Compose
- raw SQL migration system
- Markdown ingestion
- URL fetch and text extraction
- stored source-of-truth workflow
- Gemini variants for Discord, X-style, and LinkedIn-style
- deterministic platform constraint validation
- draft / approved / rejected / published review states
- variant editing with revalidation
- approve and reject endpoints
- schedule slot persistence
- scheduling allowed only for approved variants
- future-time validation

## Current API

```text
POST /posts
GET  /posts/{post_id}

POST /posts/{source_post_id}/variants
GET  /posts/{source_post_id}/variants

PATCH /variants/{variant_id}
POST  /variants/{variant_id}/approve
POST  /variants/{variant_id}/reject

POST  /variants/{variant_id}/schedule
```

## Development

```powershell
docker compose up -d
python -m app.db.migrations
uvicorn app.main:app --reload
```

## Notes

- Real secrets belong only in `.env`.
- Real X, LinkedIn, and Instagram publishing are outside core scope.
- Image generation/resizing is not part of this implementation.
