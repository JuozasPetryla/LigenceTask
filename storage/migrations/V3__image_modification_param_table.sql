CREATE TABLE image_modification_params (
  id                SERIAL PRIMARY KEY,
  variant_id        INTEGER  NOT NULL REFERENCES image_variants(id) ON DELETE CASCADE,
  seed              INTEGER  NOT NULL
);