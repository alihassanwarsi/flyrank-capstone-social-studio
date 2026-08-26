# Capstone Evidence

## Phase 1 - Design
Evidence: `docs/DESIGN.md`

Status: Complete.

## Phase 2 - Ingestion and Variant Generation

Implemented:
- PostgreSQL persistence and raw SQL migrations
- Markdown ingestion
- URL fetching and text extraction
- stored source-of-truth workflow
- Discord, X-style, and LinkedIn-style Gemini variants
- deterministic constraint validation
- variant API endpoints

Verified:
- Markdown and URL sources can be stored and retrieved
- stored source content is used for generation
- three platform variants are generated and stored
- a rule-breaking variant is blocked before persistence

Status: Complete.

## Phase 3 - Human Review and Scheduling Gate

Implemented:
- variant statuses: `draft`, `approved`, `rejected`, `published`
- draft editing
- approve and reject workflow
- revalidation after human edits
- schedule slot persistence
- scheduling allowed only for approved variants
- future-time validation

Manually verified:
- draft variant can be edited
- draft variant can be approved
- approved variant cannot be rejected
- approved variant cannot be edited
- approved variant can be scheduled
- unapproved variant is refused with a clean 4xx response
- past schedule time is refused

Status: Phase 3 complete.
