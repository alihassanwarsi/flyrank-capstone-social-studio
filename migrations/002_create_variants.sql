CREATE TABLE variants (
    id BIGSERIAL PRIMARY KEY,

    source_post_id BIGINT NOT NULL
        REFERENCES source_posts(id)
        ON DELETE CASCADE,

    platform VARCHAR(20) NOT NULL
        CHECK (platform IN ('discord', 'x', 'linkedin')),

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT variants_source_platform_unique
        UNIQUE (source_post_id, platform)
);