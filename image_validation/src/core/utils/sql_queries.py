def select_image_variant_metadata_by_id(original_image_id: int, variant_index: int) -> tuple[str, tuple[str, ...]]:
    return """
        SELECT 
            original.file_path AS original_file_path,
            variant.file_path AS variant_file_path,
            modification_params.seed AS modification_seed
        FROM originals original
        JOIN image_variants variant ON original.id = variant.original_id
        JOIN image_modification_params modification_params ON variant.id = modification_params.variant_id
        WHERE 
            original.id = %s AND
            variant.variant_index = %s
        """, (original_image_id, variant_index)