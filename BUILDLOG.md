# Build Log

This file records development decisions, AI assistance, corrections, and personally verified work.

## Project Setup

Started a fresh implementation using the current **Social Media Studio** capstone brief.

The older Multi-Platform Social Campaign Publisher implementation is not being used as the final submission architecture.

## Phase 1 - Design

Created `docs/DESIGN.md` before implementing application features.

The design follows the current brief and defines:

- stored blog posts as the source of truth
- platform-specific variants
- constraint profiles
- review statuses: `draft`, `approved`, `rejected`, `published`
- one common `SocialPublisher` interface
- one real publishing target: Discord
- two mock publishers: X-style and LinkedIn-style
- durable scheduling
- idempotent publishing
- visible publish history

AI assistance:
- Helped organize the capstone brief into a concrete backend architecture and development plan.

Personally verified:
- The design matches the current Social Media Studio brief.
- Image generation is excluded from the new core scope.
- Real publishing is limited to a safe, owned free target.

## Phase 2 - Persistence Foundation

Added PostgreSQL persistence for stored source posts.

Implemented:

- PostgreSQL 16 with Docker Compose
- Psycopg database connection
- versioned raw SQL migration runner
- `source_posts` table
- `SourcePostRepository.create()`
- `SourcePostRepository.get_by_id()`

Personally verified:

- PostgreSQL container starts successfully
- Python connects to the database
- migration creates `source_posts`
- a Markdown post can be stored and read back unchanged