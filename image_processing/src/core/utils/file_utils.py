import os

def construct_file_name_with_suffix(file_name: str, suffix: str) -> str:
    file_name, extension = os.path.splitext(file_name)
    return f"{file_name}_{suffix}{extension}"

def construct_file_group_directory(file_name: str) -> str:
    return ''.join(file_name.split('.')[:-1])

def get_file_extension(file_name: str) -> str:
    return os.path.splitext(file_name)[1]