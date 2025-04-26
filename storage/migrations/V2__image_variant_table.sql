CREATE TABLE originals (
  id           SERIAL PRIMARY KEY,
  file_path    TEXT     NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE image_variants (
  id                SERIAL PRIMARY KEY,
  original_id       INTEGER  NOT NULL REFERENCES originals(id) ON DELETE CASCADE,
  variant_index     SMALLINT NOT NULL CHECK (variant_index BETWEEN 1 AND 100),
  file_path         TEXT     NOT NULL,
  created_at        TIMESTAMPTZ DEFAULT now(),
  UNIQUE (original_id, variant_index)
);