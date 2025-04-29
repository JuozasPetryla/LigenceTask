from time import time
def write_file(
        file_save_path: str,
        file_bytes: bytes
    ) -> str:
    with open(file_save_path, 'wb') as f:
        f.write(file_bytes)
    
    return file_save_path

def read_file(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return file_bytes