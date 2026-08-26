# EVIDENCE

## 1. Ingestion and Source of Truth
Implemented Markdown and URL ingestion with PostgreSQL persistence. Generation reads stored source content.

Manual verification: Markdown and URL creation, retrieval, invalid source combinations, and clean URL failure handling.

Status: PASS

## 2. Variant Generation and Constraints
Implemented Gemini generation for Discord, X-style, and LinkedIn-style variants plus deterministic constraint validation.

Automated verification: invalid X-style content is blocked.

Status: PASS

## 3. Human Review
Implemented `draft`, `approved`, `rejected`, and `published`, plus draft editing with revalidation, approve, and reject.

Manual verification: edit succeeds, approval succeeds, invalid transitions are refused.

Status: PASS

## 4. Approved-Only Scheduling
Implemented durable schedule slots, future-time validation, and approved-only scheduling.

Automated verification: unapproved scheduling raises `ScheduleServiceError`.

Status: PASS

## 5. Publisher Architecture
Implemented one `SocialPublisher` contract with:
- `DiscordPublisher`
- `MockXPublisher`
- `MockLinkedInPublisher`

Adapter selection is configuration-driven.

Automated and manual verification: adapter swap works without changing business logic.

Status: PASS

## 6. Publishing
Manual verification:
- real Discord message published successfully
- X mock succeeded with preview
- LinkedIn mock succeeded with preview

Status: PASS

## 7. Publish Attempts and History
Implemented `publish_attempts` persistence and `GET /publish-history`.

Manual verification: Discord and mock publish records are visible.

Status: PASS

## 8. Duplicate Prevention
Implemented schedule idempotency keys and existing-success checks before publisher invocation.

Automated verification: publisher is not called when a successful attempt already exists.

Manual verification: publishing the same Discord schedule twice produced only one Discord message.

Status: PASS

## 9. Durable Worker and Recovery
Implemented PostgreSQL-backed polling, atomic claims with `FOR UPDATE SKIP LOCKED`, `processing_started_at`, and stale-processing recovery.

Manual verification:
- worker automatically processed due schedules
- worker was stopped
- a schedule became due while the worker was off
- restarting the worker immediately recovered and published the overdue job

Status: PASS

## 10. Final Automated Test Run

```text
9 passed
```

One Starlette TestClient deprecation warning was present and did not affect correctness.

Status: PASS
