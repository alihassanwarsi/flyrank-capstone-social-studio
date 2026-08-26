# BUILDLOG

This build log documents how FlyRank Social Studio was developed, where AI assistance was used, what went wrong during implementation, and what was changed before submission.

## Project Context

The internship capstone requirements changed after work had already started on an earlier version of the project.

The earlier direction included image processing and a fake social-platform server. The final project was restarted around the current **Social Media Studio** brief, which focuses on:

- blog/Markdown ingestion
- platform-specific social variants
- deterministic constraints
- human review
- durable scheduling
- one real free publisher
- two mock publishers
- idempotency and publish history

This reset was the main reason the project was rebuilt in a fresh repository.

---

## Phase 1 — Design

Before implementation, the project was reduced to one clear flow:

```text
ingest source
-> store source of truth
-> generate variants
-> validate
-> human review
-> approve
-> schedule
-> publish
-> record attempts
```

Design decisions included:

- PostgreSQL as durable persistence
- FastAPI for the API
- Gemini for text generation
- Discord as the real free publishing target
- X and LinkedIn as mock adapters
- explicit review states
- project-defined validation profiles
- adapter selection through configuration

### AI assistance

AI was used to:
- break the capstone brief into phases
- propose the repository/service/API boundaries
- identify which requirements should be implemented first
- explain unfamiliar concepts such as idempotency, durable workers, and publisher interfaces

### Human decisions

The final choices were made based on the project constraints:
- Discord instead of restricted social platforms
- PostgreSQL-backed jobs instead of relying only on an in-memory scheduler
- mock X and LinkedIn publishers
- raw SQL migrations to stay consistent with the rest of the project

---

## Phase 2 — Source Ingestion and Variant Generation

Implemented:

- PostgreSQL connection
- migration runner
- `source_posts`
- Markdown ingestion
- URL fetching with `httpx`
- HTML extraction using BeautifulSoup
- post service and API
- `variants`
- platform constraint profiles
- deterministic validator
- Gemini generation
- variant API

A key rule was that generation must read from the stored post, not refetch a live URL.

### Problems encountered

#### Gemini model availability

The initial Gemini model returned an API error because it was no longer available for the current account configuration.

The configured model was changed to a working Gemini model and generation was verified manually.

#### Old tests after schema evolution

Later, an older API test failed because the response schema had gained a required `status` field.

The application behavior was correct; the fake test fixture was outdated.

The fixture was updated to include:

```text
status = draft
```

After the update, the full suite passed.

---

## Phase 3 — Human Review and Scheduling Gate

Implemented:

- `draft`
- `approved`
- `rejected`
- `published`
- draft editing
- revalidation after edits
- approve/reject endpoints
- schedule slots
- approved-only scheduling
- future-time validation

Manual verification included:
- editing a draft
- approving it
- refusing an invalid review transition
- refusing to schedule an unapproved variant

### AI assistance

AI was mainly used to:
- translate brief language into state-transition rules
- suggest clean service boundaries
- help debug validation and API errors

The final behavior was verified manually through Swagger rather than accepted from generated code alone.

---

## Phase 4 — Publisher Architecture

Implemented:

- `SocialPublisher`
- `PublishResult`
- `DiscordPublisher`
- `MockXPublisher`
- `MockLinkedInPublisher`
- environment-controlled registry
- schedule idempotency keys
- `publish_attempts`
- publishing service
- manual publish endpoint

### Real Discord publishing

Discord was chosen because it is a safe, user-owned, free target.

A webhook configuration issue initially caused a `401` response.

The webhook was rotated/configured correctly and a real Discord message was then successfully posted.

No real webhook URL is stored in Git.

### Bug: Psycopg `dict_row`

A publishing attempt initially returned an internal server error.

The cause was this assumption:

```python
cursor.fetchone()[0]
```

The cursor used `dict_row`, so the result was a dictionary rather than a positional tuple.

The fix was to alias the SQL value and read:

```python
row["next_attempt"]
```

This was verified by successfully publishing afterward.

### Duplicate prevention

The same schedule was published twice through the API.

The second request returned the existing success and did not create a second Discord message.

---

## Phase 5 — Durable Worker and Recovery

A PostgreSQL-backed polling worker was implemented instead of an in-memory-only scheduler.

The worker:

```text
checks due schedules
-> claims rows
-> marks processing
-> publishes
-> records result
```

Implemented:

- due schedule lookup
- automatic worker loop
- durable PostgreSQL schedule persistence
- publish-history endpoint
- `FOR UPDATE SKIP LOCKED`
- `processing_started_at`
- stale processing recovery

### Worker restart verification

The worker was stopped.

A new X-style variant was:
- approved
- scheduled for the near future

The scheduled time passed while the worker was still off.

When the worker restarted, it immediately found the overdue persisted row and successfully published it through the mock adapter.

This verified that schedules were not dependent on worker process memory.

---

## Reliability Hardening

### Mock publisher idempotency

The strict retry requirement exposed an important distinction:

A real Discord webhook can prove real publishing, but it does not provide a native idempotency-key guarantee for the tiny failure window where:

```text
Discord accepts message
-> process dies
-> database success is not recorded
```

Rather than falsely claiming this external API behavior was solved, deterministic crash-safe retry behavior was implemented for the mock adapters.

Added:

```text
mock_posts
```

with a unique constraint on:

```text
(adapter_name, idempotency_key)
```

The mock publishers now use a `create_or_get` repository method.

Manual proof:

```text
first result  -> mock-x:1
second result -> mock-x:1
database rows -> 1
```

This gives the project a deterministic adapter for retry/idempotency acceptance testing while keeping Discord as the required real publish target.

---

## Submission Helpers

Added:

### `scripts/run.py`

One command:

```powershell
python scripts/run.py
```

starts:
- PostgreSQL
- migrations
- FastAPI
- worker

Verified output included successful application startup and `GET /docs` returning `200`.

### `scripts/seed.py`

Command:

```powershell
python scripts/seed.py
```

created a sample source post.

Observed:

```text
Sample post created.
Post ID: 9
```

The seeded post was fetched successfully through the API.

---

## Testing

Final deterministic requirement tests cover:

- bad variant blocking
- refusing unapproved scheduling
- avoiding repeat publishing after success
- configuration-only adapter swapping
- mock publisher idempotency

Final local suite:

```text
10 passed
```

One Starlette TestClient deprecation warning remains, but it does not fail the suite.

---

## Secret and Repository Checks

Before submission the following were checked:

```powershell
git check-ignore .env
git ls-files .env
git grep -n "discord.com/api/webhooks"
git grep -n "AIza"
```

Results confirmed:

- `.env` is ignored
- `.env` is not tracked
- no Discord webhook URL is present in tracked files
- no Gemini API key matching the checked pattern is present in tracked files

---

## Where AI Helped

AI assistance was useful for:

- decomposing the changed brief
- explaining architecture choices
- generating initial implementation drafts
- debugging stack traces
- designing deterministic acceptance tests
- documenting the final system

AI-generated suggestions were not treated as automatically correct.

Examples where implementation had to be corrected or refined:

- outdated test fixtures after the schema changed
- Psycopg `dict_row` access bug
- the initial Gemini model configuration
- the original assumption that repeated-success checks alone were enough to describe strict crash safety
- the original scheduler design was changed to a PostgreSQL-backed worker
- the mock adapters were later strengthened with database-backed idempotency

The final behavior was verified using actual API calls, worker runs, database checks, and pytest.

---

## Final System

```text
URL / Markdown
-> PostgreSQL source of truth
-> Gemini variants
-> deterministic validation
-> human review
-> approved-only scheduling
-> durable PostgreSQL worker
-> Discord real / X mock / LinkedIn mock
-> publish attempts
-> history
-> retry and duplicate protection
```

The final project intentionally stays smaller than a production social-media platform and focuses on the capstone's correctness, durability, and reliability requirements.
