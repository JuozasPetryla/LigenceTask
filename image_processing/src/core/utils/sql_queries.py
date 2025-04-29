def insert_into_original_image_table(file_path: str) -> tuple[str, tuple[str, ...]]:
    return "INSERT INTO originals (file_path) VALUES (%s) RETURNING id", (file_path,)

def insert_into_modified_image_table() -> str:
    return "INSERT INTO image_variants (original_id, file_path, variant_index) VALUES %s RETURNING id"

def insert_into_image_modification_params_table() -> str:
    return "INSERT INTO image_modification_params (variant_id, seed) VALUES %s"

def insert_into_image_reversability_status_table() -> str:
    return "INSERT INTO image_reversability_status (variant_id) VALUES %s"