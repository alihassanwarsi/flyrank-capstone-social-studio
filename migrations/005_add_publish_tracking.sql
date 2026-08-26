ALTER TABLE schedule_slots
ADD COLUMN idempotency_key TEXT;

UPDATE schedule_slots
SET idempotency_key = 'slot-' || id
WHERE idempotency_key IS NULL;

ALTER TABLE schedule_slots
ALTER COLUMN idempotency_key SET NOT NULL;

ALTER TABLE schedule_slots
ADD CONSTRAINT schedule_slots_idempotency_key_unique
UNIQUE (idempotency_key);


CREATE TABLE publish_attempts (
    id BIGSERIAL PRIMARY KEY,

    schedule_slot_id BIGINT NOT NULL
        REFERENCES schedule_slots(id)
        ON DELETE CASCADE,

    adapter_name VARCHAR(50) NOT NULL,

    attempt_number INTEGER NOT NULL,

    status VARCHAR(20) NOT NULL
        CHECK (
            status IN (
                'started',
                'success',
                'failed'
            )
        ),

    external_post_id TEXT,
    external_url TEXT,
    preview TEXT,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT publish_attempt_number_unique
        UNIQUE (schedule_slot_id, attempt_number)
);