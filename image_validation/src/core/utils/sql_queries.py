def select_image_variant_paths_by_id(original_image_id: int, variant_index: int) -> tuple[str, tuple[str, ...]]:
    return """
        SELECT 
            original.file_path AS original_file_path,
            modified.file_path AS modified_file_path
        FROM originals original
        JOIN image_variants modified ON original.id = modified.original_id
        WHERE 
            original.id = %s AND
            modified.variant_index = %s 
        """, (original_image_id, variant_index)