import os

from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection
from fastapi import UploadFile

from .utils.constants import IMAGE_PROCESS_COUNT
from .utils.sql_queries import \
    insert_into_original_image_table, \
    insert_into_modified_image_table
from ..infrastructure.file_storage_client import FileStorageClient

FILE_STORAGE_MAIN_DIR = os.getenv("FILE_STORAGE_MAIN_DIR")

class ImageProcessingService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn

    @staticmethod
    def _construct_file_modified_name(file_name: str, suffix: str) -> str:
        file_name_array = file_name.split('.')
        return f"{''.join(file_name_array[:-1])}_{suffix}.{file_name_array[-1]}"

    def _generate_image_variant(self, image_file_contents: bytes, image_file_name: str, iteration: int):
        return self._construct_file_modified_name(image_file_name, iteration), image_file_contents

    async def upload_processed_files(self, image_file: UploadFile):
        contents = image_file.file.read()
        image_group_dir = ''.join(image_file.filename.split('.')[:-1])

        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            original_upload_response = await self.file_storage_client.upload(
                self._construct_file_modified_name(image_file.filename, "original"),
                image_group_dir,
                contents
            )
            original_upload_file_path = original_upload_response['file_save_path']
            query_original, param_original = insert_into_original_image_table(original_upload_file_path)
            cursor.execute(query_original, param_original)
            original_upload_id = cursor.fetchone().get('id')
            print(original_upload_id)

            for i in range(0, IMAGE_PROCESS_COUNT):
                file_name_modified, file_bytes = self._generate_image_variant(
                    contents, 
                    image_file.filename, 
                    i + 1
                )
                modified_upload_response = await self.file_storage_client.upload(
                    file_name_modified, 
                    image_group_dir, 
                    file_bytes
                )
                modified_upload_file_path = modified_upload_response['file_save_path']
                query_modified, param_modified = insert_into_modified_image_table(original_upload_id, modified_upload_file_path, i + 1)
                cursor.execute(query_modified, param_modified)
            self.database_conn.commit()
        

