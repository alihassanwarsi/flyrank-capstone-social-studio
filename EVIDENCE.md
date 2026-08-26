# Capstone Evidence

## Phase 1 - Design
Status: Complete.

## Phase 2 - Ingestion and Variant Generation
Implemented and verified:
- Markdown and URL ingestion
- PostgreSQL source-of-truth persistence
- Gemini generation for Discord, X-style, and LinkedIn-style variants
- deterministic platform constraint validation
- invalid variants blocked before persistence
- variant API endpoints

Status: Complete.

## Phase 3 - Human Review and Scheduling Gate
Implemented and verified:
- variant statuses: `draft`, `approved`, `rejected`, `published`
- draft editing with revalidation
- approve and reject workflow
- only approved variants can be scheduled
- past schedule times are rejected

Status: Complete.

## Phase 4 - Publisher Adapters and Idempotency

Implemented:
- common `SocialPublisher` interface
- shared `PublishResult`
- real `DiscordPublisher`
- `MockXPublisher`
- `MockLinkedInPublisher`
- configuration-based publisher registry
- stable schedule idempotency keys
- `publish_attempts` persistence
- publishing service
- manual publish API endpoint

Manually verified:
- real Discord message publishing
- mock X publishing
- mock LinkedIn publishing
- configuration-based adapter swap
- publish attempt recording
- repeated successful schedule publish returns the existing success
- repeated successful Discord publish does not create a duplicate message

Status: Phase 4 complete.
