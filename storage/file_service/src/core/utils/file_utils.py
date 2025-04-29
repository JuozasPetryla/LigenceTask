import base64
import os

from .constants import FILE_STORAGE_MAIN_DIR

def create_save_dir_and_path(
    x_filename_original_b64: str, 
    x_filename_modified_b64: str, 
) -> str:
    file_name_original = base64.b64decode(x_filename_original_b64).decode("utf-8")
    file_name_modified = base64.b64decode(x_filename_modified_b64).decode("utf-8")

    file_save_dir  = os.path.join(FILE_STORAGE_MAIN_DIR, file_name_original)
    file_save_path = os.path.join(file_save_dir, file_name_modified)

    os.makedirs(file_save_dir, exist_ok=True)

    return file_save_path