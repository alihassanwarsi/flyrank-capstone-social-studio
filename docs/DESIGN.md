# FlyRank Social Studio — Design

## 1. Problem

FlyRank Social Studio turns one stored blog post into platform-specific social variants.

A user can ingest a blog post as pasted Markdown or a URL, generate platform-specific variants, validate every variant against platform constraints, review/edit/approve/reject each variant, schedule only approved variants, publish through one common `SocialPublisher` interface, and keep visible publish history without duplicate posts.

The main backend goals are constraint enforcement, review safety, adapter architecture, idempotency, and durable scheduling.

## 2. Core Pipeline

```text
Blog post: URL or Markdown
        |
        v
Ingest + store source post
        |
        v
Generate platform variants
        |
        v
Constraint validation
        |
        v
draft
   |-------------|
   v             v
approved       rejected
   |
   v
Schedule slot
   |
   v
Durable scheduler / worker
   |
   v
SocialPublisher
   |-----------------------------|
   v              v              v
Discord       Mock X       Mock LinkedIn
(real)        (database)    (database)
   |
   v
Publish history
```

All variant generation must read from the stored source post. The stored post is the single source of truth.

## 3. Target Platforms

Initial targets:

- Discord — real free publishing target
- X-style — mock adapter
- LinkedIn-style — mock adapter

The application depends on the common publisher interface, not on platform-specific implementations.

## 4. Constraint Profiles

These are project-defined rules used to make validation deterministic and testable. They are not claims about official platform limits.

### Discord

- Maximum length: 1000 characters
- Maximum hashtags: 3
- Maximum emojis: 2
- Tone: conversational and clear
- Excessive all-caps text is rejected

### X-style

- Maximum length: 280 characters
- Maximum hashtags: 2
- Maximum emojis: 1
- Tone: short and direct
- More than one exclamation mark is rejected

### LinkedIn-style

- Maximum length: 1300 characters
- Maximum hashtags: 3
- Emojis: not allowed
- Tone: professional
- More than one exclamation mark is rejected

Constraint validation runs before a variant can enter the review workflow. A rule-breaking variant is rejected with a clear validation error.

## 5. Review Workflow

Variant statuses:

```text
draft
  |
  +--> approved
  |
  +--> rejected

approved
  |
  +--> published
```

Rules:

- Newly generated variants start as `draft`.
- A draft can be edited.
- A draft can be approved or rejected.
- Only an `approved` variant can be scheduled.
- Scheduling a draft or rejected variant returns a clean 4xx response.
- The same variant and schedule slot must not publish twice.

## 6. Data Model

### source_posts

Stores the single source of truth.

Fields:

- `id`
- `source_type` — `markdown` or `url`
- `source_url` — nullable
- `title`
- `content`
- `created_at`

### variants

Stores one platform-specific version of a source post.

Fields:

- `id`
- `source_post_id`
- `platform`
- `content`
- `status` — `draft`, `approved`, `rejected`, `published`
- `created_at`
- `updated_at`

Constraints:

- foreign key to `source_posts`
- unique `(source_post_id, platform)`

### schedule_slots

Stores one scheduled publishing slot for a variant.

Fields:

- `id`
- `variant_id`
- `scheduled_for`
- `idempotency_key`
- `status`
- `created_at`

Constraints:

- foreign key to `variants`
- unique `idempotency_key`

### publish_attempts

Stores visible publish history.

Fields:

- `id`
- `schedule_slot_id`
- `adapter_name`
- `attempt_number`
- `result`
- `external_post_id` — nullable
- `external_url` — nullable
- `error_message` — nullable
- `created_at`

Every publish attempt is recorded.

## 7. SocialPublisher Interface

Business logic publishes through one common contract.

Conceptual signature:

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

```text
SocialPublisher
├── DiscordPublisher
├── MockXPublisher
└── MockLinkedInPublisher
```

Changing the configured adapter must not require business-logic changes.

## 8. API Surface

Initial API design:

```text
POST   /posts
GET    /posts/{post_id}

POST   /posts/{post_id}/variants
GET    /posts/{post_id}/variants

PATCH  /variants/{variant_id}
POST   /variants/{variant_id}/approve
POST   /variants/{variant_id}/reject

POST   /variants/{variant_id}/schedule

GET    /publish-history
```

## 9. Layered Architecture

```text
FastAPI routers
      |
      v
Pydantic boundary validation
      |
      v
Services / business logic
      |
      +------> variant generator + constraint validator
      |
      +------> scheduling / publishing logic
      |
      v
Repositories
      |
      v
PostgreSQL
```

Publishing:

```text
Publishing service
      |
      v
SocialPublisher interface
      |
      +--> DiscordPublisher
      +--> MockXPublisher
      +--> MockLinkedInPublisher
```

Layer responsibilities:

- API layer: HTTP only
- schemas: request/response validation
- services: workflow and business rules
- repositories: parameterized SQL and persistence
- publishers: platform-specific publishing details
- scheduler: durable background execution

## 10. Persistence

PostgreSQL runs locally through Docker.

Python connects using Psycopg.

Database changes are versioned as raw SQL migrations.

Tests use a separate PostgreSQL test database so test cleanup never touches development data.

## 11. Scheduling and Idempotency

APScheduler will use persistent storage rather than an in-memory-only job store.

Every scheduled publish gets a stable idempotency key for the variant and schedule slot.

Before publishing, the system checks whether the slot already has a successful publish. Retries must therefore produce one successful external post, not duplicates.

Worker restart behavior will be tested explicitly.

## 12. Secrets

Secrets are read from environment variables.

Examples:

- database credentials
- Gemini API key
- Discord webhook URL

Real secrets live only in `.env`.

The repository ships `.env.example` once environment-backed features are introduced.

Secrets must never be committed or logged.

## 13. Testing Strategy

Core deterministic tests will cover:

- source post persistence
- generation reading from stored content
- constraint profile acceptance/rejection
- invalid variant blocked before review
- approve/reject/edit workflow
- unapproved scheduling returns 4xx
- adapter swap without business-logic change
- duplicate publish prevention
- durable restart behavior
- publish history recording

AI calls will be mocked in automated tests.

## 14. Explicit Non-Goal

Image generation and image resizing are not part of the core implementation.

The project also does not publish to real X, LinkedIn, or Instagram accounts and does not implement analytics or engagement tracking.

## 15. Phase Gates

### Phase 1
Design document complete.

### Phase 2
One stored post produces different valid platform variants, and a rule-breaking variant is blocked.

### Phase 3
An unapproved variant cannot be scheduled; an approved one can.

### Phase 4
A real Discord message publishes successfully, both mock adapters work, and repeated publishing produces exactly one post.

### Phase 5
Scheduled jobs survive worker restart without duplicates, publish history is visible, required tests pass, and documentation is complete.
