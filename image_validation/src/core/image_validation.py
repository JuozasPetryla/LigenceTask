from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection

from .utils.sql_queries import select_image_variant_paths_by_id
from ..infrastructure.file_storage_client import FileStorageClient

class ImageValidationService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn
    
    async def retrieve_images_by_id(self, original_image_id: int, variant_index: int):
        query_select, params_select = select_image_variant_paths_by_id(original_image_id, variant_index)

        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query_select, params_select)
            result = cursor.fetchone()

            original_file_bytes = await self.file_storage_client.download(result.get('original_file_path'))
            modified_file_bytes = await self.file_storage_client.download(result.get('modified_file_path'))

