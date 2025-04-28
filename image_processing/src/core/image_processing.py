import numpy as np

from fastapi import UploadFile
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection

from ..infrastructure.file_storage_client import FileStorageClient
from .utils.constants import IMAGE_TO_PROCESS_COUNT, MAX_RANDOM_SEED
from .utils.enums import ReversabilityStatus
from .utils.sql_queries import (
    insert_into_original_image_table,
    insert_into_modified_image_table,
    insert_into_image_modification_params_table,
    insert_into_image_reversability_status_table
)
from .utils.image_utils import generate_shuffled_pixel_image
from .utils.file_utils import (
    construct_file_name_with_suffix, 
    construct_file_group_directory,
    get_file_extension
)

class ImageProcessingService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn

    async def upload_processed_files(self, image_file: UploadFile):
        image_bytes = image_file.file.read()
        image_group_directory = construct_file_group_directory(image_file.filename)
        
        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            original_upload_response = await self.file_storage_client.upload(
                image_file.filename,
                image_group_directory,
                image_bytes
            )
            original_upload_file_path = original_upload_response['file_save_path']
            query_original, params_original = insert_into_original_image_table(original_upload_file_path)
            cursor.execute(query_original, params_original)
            original_upload_id = cursor.fetchone().get('id')

            for iteration in range(1, IMAGE_TO_PROCESS_COUNT + 1):
                random_seed = np.random.default_rng().integers(0, MAX_RANDOM_SEED)

                file_bytes = generate_shuffled_pixel_image(
                    image_bytes, 
                    random_seed,
                    get_file_extension(image_file.filename)
                )

                modified_upload_response = await self.file_storage_client.upload(
                    construct_file_name_with_suffix(image_file.filename, iteration), 
                    image_group_directory, 
                    file_bytes
                )

                modified_upload_file_path = modified_upload_response['file_save_path']
                query_modified, params_modified = insert_into_modified_image_table(original_upload_id, modified_upload_file_path, iteration)
                cursor.execute(query_modified, params_modified)
                modified_image_variant_id = cursor.fetchone().get('id')

                query_modification, params_modification = insert_into_image_modification_params_table(modified_image_variant_id, int(random_seed))
                cursor.execute(query_modification, params_modification)

                query_reversability, params_reversability = insert_into_image_reversability_status_table(modified_image_variant_id, ReversabilityStatus.PENDING.value)
                cursor.execute(query_reversability, params_reversability)

            self.database_conn.commit()
            