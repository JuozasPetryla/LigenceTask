def insert_into_original_image_table(file_path: str) -> tuple[str, tuple[str, ...]]:
    return "INSERT INTO originals (file_path) VALUES (%s) RETURNING id", (file_path,)

def insert_into_modified_image_table(original_id: int, file_path: str, variant_index: int) -> tuple[str, tuple[int, str, int]]:
    return "INSERT INTO image_variants (original_id, file_path, variant_index) VALUES (%s, %s, %s) RETURNING id", (original_id, file_path, variant_index,)

def insert_into_image_modification_params_table(variant_id: int, seed: int) -> tuple[str, tuple[int, int]]:
    return "INSERT INTO image_modification_params (variant_id, seed) VALUES (%s, %s)", (variant_id, seed,)

def insert_into_image_reversability_status_table(variant_id: int, reversability_status: str) -> tuple[str, tuple[int, str]]:
    return "INSERT INTO image_reversability_status (variant_id, reversability_status) VALUES (%s, %s)", (variant_id, reversability_status,)