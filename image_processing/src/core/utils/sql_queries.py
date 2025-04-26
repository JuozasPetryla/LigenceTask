def insert_into_original_image_table(file_path: str) -> tuple[str, tuple[str, ...]]:
    return "INSERT INTO originals (file_path) VALUES (%s) RETURNING id", (file_path,)

def insert_into_modified_image_table(original_id: int, file_path: str, variant_index: int) -> tuple[str, tuple[int, str, int]]:
    return "INSERT INTO image_variants (original_id, file_path, variant_index) VALUES (%s, %s, %s)", (original_id, file_path, variant_index,)