CREATE TYPE REVERSABILITY_STATUS_TYPE AS ENUM ('pending', 'true', 'false');

CREATE TABLE image_reversability_status (
  id                    SERIAL PRIMARY KEY,
  variant_id            INTEGER NOT NULL REFERENCES image_variants(id) ON DELETE CASCADE,
  reversability_status  REVERSABILITY_STATUS_TYPE NOT NULL DEFAULT 'pending'
);