import os

def get_file_extension(file_name: str) -> str:
    return os.path.splitext(file_name)[1]

def get_file_name_from_path(file_path: str) -> str:
        return file_path.split('/')[-1]