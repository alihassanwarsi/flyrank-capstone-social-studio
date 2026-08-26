# DESIGN

## Goal

FlyRank Social Studio converts a stored blog post into reviewed, scheduled social variants and publishes them through a common adapter interface.

The system is designed around correctness, persistence, explicit review, and observable publishing behavior.

## High-Level Flow

```text
URL or Markdown
      |
      v
source_posts
      |
      v
Gemini generation
      |
      v
platform validation
      |
      v
variants (draft)
      |
      +--> edit
      +--> reject
      |
      v
approved
      |
      v
schedule_slots
      |
      v
PostgreSQL-backed polling worker
      |
      v
SocialPublisher
      |
      +--> DiscordPublisher
      +--> MockXPublisher
      +--> MockLinkedInPublisher
      |
      v
publish_attempts
```

Mock publishers additionally persist their logical posts in:

```text
mock_posts
```

to provide deterministic idempotent retry behavior.

## Source of Truth

The original post is stored before social generation.

Accepted inputs:
- pasted Markdown
- URL

For URL ingestion, the application fetches and extracts the page text once, then stores it.

Later generation reads the stored database content instead of depending on the live URL.

## Platform Constraint Profiles

These are project-defined validation profiles, not official platform limits.

### Discord
- max length: 1000
- max hashtags: 3
- max emojis: 2
- excessive all-caps rejected

### X-style
- max length: 280
- max hashtags: 2
- max emojis: 1
- max exclamation marks: 1

### LinkedIn-style
- max length: 1300
- max hashtags: 3
- emojis: 0
- max exclamation marks: 1
- forbidden casual terms include `lol`, `omg`, and `bro`

Generated output must pass deterministic validation before it proceeds to review.

## Review State Model

Variant states:

```text
draft
approved
rejected
published
```

Rules:
- generated variants begin as `draft`
- only drafts can be edited
- edited content is revalidated
- only drafts can be approved
- only drafts can be rejected
- only approved variants can be scheduled
- successful publishing changes the variant to `published`

## Publisher Interface

All adapters implement the same conceptual contract:

```python
class SocialPublisher:
    def publish(
        self,
        *,
        content: str,
        idempotency_key: str,
    ) -> PublishResult:
        ...
```

`PublishResult` standardizes:
- success
- external post ID
- external URL
- preview

Implementations:
- real Discord publisher
- mock X publisher
- mock LinkedIn publisher

Publisher selection is configuration-driven through environment variables.

## Persistence Model

### `source_posts`
Stores:
- source type
- original URL when applicable
- title
- stored content
- creation timestamp

### `variants`
Stores:
- source post
- platform
- generated/edited content
- review status
- timestamps

One variant is stored per source post/platform.

### `schedule_slots`
Stores:
- variant
- scheduled time
- durable status
- unique idempotency key
- processing lease timestamp

### `publish_attempts`
Stores:
- schedule slot
- adapter name
- attempt number
- status
- external identifiers
- preview
- error
- timestamp

### `mock_posts`
Stores:
- mock adapter name
- idempotency key
- content
- timestamp

The database enforces:

```text
UNIQUE(adapter_name, idempotency_key)
```

This lets a mock publisher retry the same logical publish without creating a second mock post.

## Durable Scheduling

The final implementation does not rely on an in-memory scheduler.

PostgreSQL is the durable source for scheduled jobs.

The worker repeatedly:
1. finds due schedule rows
2. atomically claims them
3. marks them `processing`
4. invokes the publishing service
5. records success/failure
6. updates schedule and variant state

Because schedules persist in PostgreSQL, worker shutdown does not delete pending jobs.

On restart, overdue jobs are discovered again.

## Concurrency and Recovery

Due rows are claimed using:

```text
FOR UPDATE SKIP LOCKED
```

This prevents multiple workers from claiming the same due row in the same database transaction.

Claimed rows receive `processing_started_at`.

A `processing` row whose lease is stale becomes eligible for recovery, preventing a worker crash from leaving the job permanently stuck.

## Idempotency

### Application-level successful-attempt check

Before invoking a publisher, the publishing service checks whether the schedule already has a successful publish attempt.

If a success exists, it returns that result and does not call the publisher again.

### Mock adapter idempotency

The mock adapters persist logical posts in `mock_posts`.

For a given:

```text
adapter_name + idempotency_key
```

only one row can exist.

A retry therefore returns the same logical mock post.

This provides deterministic retry/crash acceptance behavior.

### Real Discord limitation

Discord is used as the real free publishing target.

The webhook proves a real external publish path, but Discord does not provide the same database-backed idempotency guarantee as the local mock adapters for the exact failure window where the external request succeeds and the process dies before local success is recorded.

This limitation is documented rather than hidden.

## API Surface

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

## Run and Seed Helpers

One-command startup:

```powershell
python scripts/run.py
```

Seed:

```powershell
python scripts/seed.py
```

## Explicit Non-Goals

- image generation
- analytics
- engagement tracking
- real X publishing
- real LinkedIn publishing
- real Instagram publishing
