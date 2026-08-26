ALTER TABLE variants
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'draft'
CHECK (
    status IN (
        'draft',
        'approved',
        'rejected',
        'published'
    )
);