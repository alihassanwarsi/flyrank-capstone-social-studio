CREATE TABLE source_posts (
    id BIGSERIAL PRIMARY KEY,

    source_type VARCHAR(20) NOT NULL
        CHECK (source_type IN ('markdown', 'url')),

    source_url TEXT,

    title TEXT,

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT source_posts_source_check
        CHECK (
            (source_type = 'markdown' AND source_url IS NULL)
            OR
            (source_type = 'url' AND source_url IS NOT NULL)
        )
);