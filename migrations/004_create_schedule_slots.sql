CREATE TABLE schedule_slots (
    id BIGSERIAL PRIMARY KEY,

    variant_id BIGINT NOT NULL
        REFERENCES variants(id)
        ON DELETE CASCADE,

    scheduled_for TIMESTAMPTZ NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'scheduled'
        CHECK (
            status IN (
                'scheduled',
                'processing',
                'completed',
                'failed'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT schedule_slots_variant_time_unique
        UNIQUE (variant_id, scheduled_for)
);