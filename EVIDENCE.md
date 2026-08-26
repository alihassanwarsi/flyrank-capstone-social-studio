# Capstone Evidence

## Phase 1 - Design
Evidence: `docs/DESIGN.md`

Verified design coverage:
- platform constraint profiles
- `SocialPublisher` interface
- core data model
- API surface
- explicit non-goals

Status: Complete.

## Phase 2 - Ingestion and Variant Generation

Implemented:
- PostgreSQL persistence and raw SQL migrations
- Markdown ingestion
- URL fetching and text extraction
- stored source-of-truth workflow
- `variants` table and repository
- Discord, X-style, and LinkedIn-style Gemini generation
- deterministic constraint validation
- variant API endpoints

Verified manually:
- Markdown source can be stored and retrieved unchanged
- URL content can be fetched, cleaned, stored, and retrieved
- Gemini generated three platform variants from a stored source post
- generated variants passed validation and were stored

Verified automatically:
- stored source content is used during generation
- three platform variants are saved
- a rule-breaking X variant is blocked before any variant is saved
- generation endpoint returns `201`
- missing source post returns `404`
- duplicate generation returns `409`

Latest result: `5 passed, 1 warning`

Status: Phase 2 complete.
