import base64, os

from .utils.constants import FILE_SAVE_DIRECTORY

def _decode_file_name_headers(
        x_filename_original_b64: str, 
        x_filename_modified_b64: str
    ) -> tuple[str, str]:
    file_name_original = base64.b64decode(x_filename_original_b64).decode("utf-8")
    file_name_modified = base64.b64decode(x_filename_modified_b64).decode("utf-8")

    return file_name_original, file_name_modified

def write_file(
        x_filename_original_b64: str, 
        x_filename_modified_b64: str, 
        file_bytes: bytes
    ):
    file_name_original, file_name_modified = _decode_file_name_headers(x_filename_original_b64, x_filename_modified_b64)

    file_save_dir  = os.path.join(FILE_SAVE_DIRECTORY, file_name_original)
    file_save_path = os.path.join(file_save_dir, file_name_modified)

    os.makedirs(file_save_dir, exist_ok=True)

    with open(file_save_path, 'wb') as f:
        f.write(file_bytes)