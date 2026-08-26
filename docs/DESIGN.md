# DESIGN

## Goal

FlyRank Social Studio converts a stored blog post into reviewed, scheduled social variants and publishes them through a common adapter interface.

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

## Source of Truth

The original post is stored before social generation. Accepted inputs are pasted Markdown or a URL. URL content is fetched and extracted once, then stored. Later generation reads the stored database content.

## Constraint Profiles

These are project-defined profiles, not official platform limits.

### Discord
- max length 1000
- max hashtags 3
- max emojis 2
- excessive all-caps rejected

### X-style
- max length 280
- max hashtags 2
- max emojis 1
- max exclamation marks 1

### LinkedIn-style
- max length 1300
- max hashtags 3
- emojis 0
- max exclamation marks 1
- forbidden casual terms include `lol`, `omg`, and `bro`

## Review States

```text
draft
approved
rejected
published
```

Only drafts can be edited/approved/rejected. Edited content is revalidated. Only approved variants can be scheduled. Successful publishing changes the variant to `published`.

## Publisher Interface

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

Implementations:
- real Discord publisher
- mock X publisher
- mock LinkedIn publisher

Publisher selection is configuration-driven.

## Persistence

### `source_posts`
Stores source type, original URL when relevant, title, stored content, and timestamp.

### `variants`
Stores source post, platform, content, review status, and timestamps.

### `schedule_slots`
Stores variant, scheduled time, status, idempotency key, and processing lease timestamp.

### `publish_attempts`
Stores schedule slot, adapter, attempt number, status, external identifiers, preview, error, and timestamp.

## Durable Scheduling

The final system does not rely on an in-memory scheduler. PostgreSQL is the durable source for jobs.

The worker repeatedly:
1. finds due rows
2. atomically claims them
3. marks them processing
4. invokes the publishing service
5. records success/failure
6. updates schedule and variant state

Pending jobs survive worker shutdown because they remain in PostgreSQL.

## Concurrency and Recovery

Due rows are claimed using:

```text
FOR UPDATE SKIP LOCKED
```

Claimed rows record `processing_started_at`. A stale processing row can later be reclaimed so a crash does not permanently strand the job.

## Idempotency

Each schedule slot has a unique idempotency key. Before publishing, the service checks whether that schedule already has a successful attempt. If so, it returns the existing success and does not call the publisher again.

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

## Non-Goals

- image generation
- analytics
- engagement tracking
- real X publishing
- real LinkedIn publishing
- real Instagram publishing
