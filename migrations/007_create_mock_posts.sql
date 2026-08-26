CREATE TABLE mock_posts (
    id BIGSERIAL PRIMARY KEY,

    adapter_name VARCHAR(50) NOT NULL,

    idempotency_key TEXT NOT NULL,

    content TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT mock_posts_adapter_key_unique
        UNIQUE (
            adapter_name,
            idempotency_key
        )
);