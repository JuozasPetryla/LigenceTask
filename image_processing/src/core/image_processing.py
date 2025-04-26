from fastapi import UploadFile

from .utils.constants import IMAGE_PROCESS_COUNT
from ..infra.file_storage_client import FileStorageClient

class ImageProcessingService:
    def __init__(self, file_storage_client: FileStorageClient):
        self.file_storage_client = file_storage_client

    @staticmethod
    def _construct_file_modified_name(file_name: str, suffix: str) -> str:
        file_name_array = file_name.split('.')
        return f"{''.join(file_name_array[:-1])}_{suffix}.{file_name_array[-1]}"

    def _generate_image_variant(self, image_file_contents: bytes, image_file_name: str, iteration: int):
        return self._construct_file_modified_name(image_file_name, iteration), image_file_contents

    async def upload_processed_files(self, image_file: UploadFile):
        contents = image_file.file.read()
        urls = []
        for i in range(0, IMAGE_PROCESS_COUNT):
            file_name_modified, file_bytes = self._generate_image_variant(
                contents, 
                image_file.filename, 
                i
            )
            url = await self.file_storage_client.upload(
                file_name_modified, 
                ''.join(image_file.filename.split('.')[:-1]), 
                file_bytes
            )
            urls.append(url)
        return urls
        

