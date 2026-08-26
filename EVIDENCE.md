# EVIDENCE

This document records concrete verification evidence for the FlyRank Social Studio capstone.

## 1. One-command startup and seed

### Seed

Command:

```powershell
python scripts/seed.py
```

Observed:

```text
Sample post created.
Post ID: 9
```

The seeded post was fetched successfully:

```text
GET /posts/9 HTTP/1.1" 200 OK
```

### One-command startup

Command:

```powershell
python scripts/run.py
```

Observed:

```text
Starting PostgreSQL...
Container flyrank-social-studio-postgres Running
Running migrations...
Skipping 001_create_source_posts.sql
Skipping 002_create_variants.sql
Skipping 003_add_variant_status.sql
Skipping 004_create_schedule_slots.sql
Skipping 005_add_publish_tracking.sql
Skipping 006_add_processing_lease.sql
Skipping 007_create_mock_posts.sql
Starting API and worker...
FlyRank Social Studio worker started.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: "GET /docs HTTP/1.1" 200 OK
INFO: "GET /openapi.json HTTP/1.1" 200 OK
```

Status: PASS

---

## 2. Source-of-truth ingestion

Implemented:
- pasted Markdown ingestion
- URL ingestion
- PostgreSQL persistence in `source_posts`
- variant generation reads stored post content rather than the live URL

Manual verification during development:
- Markdown creation returned `201`
- URL ingestion returned `201`
- stored post retrieval returned persisted content
- invalid source combinations were rejected
- URL-fetch failure returned a clean application error

Final smoke evidence:

```text
GET /posts/9 HTTP/1.1" 200 OK
```

Status: PASS

---

## 3. Constraint enforcement

Deterministic test:

```text
tests/test_final_requirements.py::test_bad_variant_is_blocked PASSED
```

Invalid X-style content is rejected through `VariantValidationError` before it can proceed.

Status: PASS

---

## 4. Human review and approved-only scheduling

Implemented states:

```text
draft
approved
rejected
published
```

Manual verification:
- draft edit succeeded
- approval succeeded
- invalid review transition was refused

Deterministic scheduling-gate test:

```text
tests/test_final_requirements.py::test_unapproved_variant_cannot_be_scheduled PASSED
```

Status: PASS

---

## 5. Publisher interface and adapters

One common `SocialPublisher` contract is implemented with:

- `DiscordPublisher`
- `MockXPublisher`
- `MockLinkedInPublisher`

Manual verification:
- real Discord message published successfully
- Mock X published a recorded preview
- Mock LinkedIn published a recorded preview

Status: PASS

---

## 6. Configuration-only adapter swap

Deterministic test:

```text
tests/test_final_requirements.py::test_adapter_swap_is_configuration_only PASSED
```

Changing the publisher environment configuration changes the selected adapter without changing business logic.

Status: PASS

---

## 7. Publish attempts and history

`publish_attempts` records:
- schedule slot
- adapter
- attempt number
- status
- external post ID
- external URL
- preview
- error
- timestamp

Endpoint:

```text
GET /publish-history
```

Manual verification:
- Discord, Mock X, and Mock LinkedIn attempts were visible through the history API

Status: PASS

---

## 8. Repeated publish after success

Deterministic test:

```text
tests/test_final_requirements.py::test_successful_publish_is_not_repeated PASSED
```

The test installs an existing successful attempt and asserts that the publisher must not be called again.

Manual verification:
- one Discord schedule was published successfully
- the same publish endpoint was called a second time
- the request returned successfully
- no second Discord message appeared

Status: PASS

---

## 9. Durable worker and restart recovery

Observed worker startup:

```text
FlyRank Social Studio worker started.
Processing schedule 2...
Schedule 2 published with status success.
Processing schedule 6...
Schedule 6 published with status success.
```

Separate recovery probe:
1. worker stopped
2. an X-style variant was approved and scheduled
3. its scheduled time passed while the worker was off
4. worker restarted
5. overdue schedule was immediately discovered and published successfully

Concurrency/recovery mechanisms:
- PostgreSQL-backed schedule persistence
- `FOR UPDATE SKIP LOCKED`
- `processing_started_at`
- stale processing lease recovery

Status: PASS

---

## 10. Mock adapter idempotency

Migration `007_create_mock_posts.sql` adds durable mock-post persistence with:

```text
UNIQUE(adapter_name, idempotency_key)
```

Both mock publishers use `create_or_get`, so retrying the same adapter/idempotency key returns the same logical mock post rather than creating another one.

Manual probe:

```text
PublishResult(success=True, external_post_id='mock-x:1', ...)
PublishResult(success=True, external_post_id='mock-x:1', ...)
Mock posts: 1
```

Automated test:

```text
tests/test_final_requirements.py::test_mock_publisher_reuses_idempotency_key PASSED
```

Status: PASS

---

## 11. Automated test suite

Final requirements tests include:

```text
test_bad_variant_is_blocked PASSED
test_unapproved_variant_cannot_be_scheduled PASSED
test_successful_publish_is_not_repeated PASSED
test_adapter_swap_is_configuration_only PASSED
test_mock_publisher_reuses_idempotency_key PASSED
```

Full suite:

```powershell
pytest -q
```

Observed:

```text
.......... [100%]
10 passed, 1 warning in 1.56s
```

The warning is a Starlette TestClient deprecation warning and does not represent a failed test.

Status: PASS

---

## 12. Secret-safety audit

Commands executed:

```powershell
git check-ignore .env
git ls-files .env
git grep -n "discord.com/api/webhooks"
git grep -n "AIza"
```

Observed:
- `git check-ignore .env` returned `.env`
- `git ls-files .env` returned no output
- the two `git grep` commands matched only the literal audit-command strings documented in `BUILDLOG.md` and `EVIDENCE.md`
- no actual Discord webhook URL was found in tracked files
- no actual Gemini API key matching the checked pattern was found in tracked files

Therefore:
- `.env` is ignored
- `.env` is not tracked
- tracked documentation contains only the security-check command text, not secrets

Status: PASS

---

## 13. Real Discord limitation

The real Discord adapter is suitable for proving a real free publish path and normal duplicate prevention after a successful attempt is recorded.

However, Discord webhooks do not provide the same database-backed idempotency guarantee as the local mock adapters for the exact crash window where Discord accepts a message but the worker dies before PostgreSQL records success.

For deterministic retry/idempotency proof, the project therefore uses the durable mock adapters, whose database uniqueness constraint guarantees one logical mock post per adapter/idempotency key.

This limitation is documented rather than hidden.
