import numpy as np
import asyncio

from fastapi import UploadFile
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.extensions import connection as PGConnection
from starlette.concurrency import run_in_threadpool

from ..infrastructure.file_storage_client import FileStorageClient
from .utils.constants import IMAGE_TO_PROCESS_COUNT, MAX_RANDOM_SEED, MAX_ASYNC_WORKERS
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
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection, max_workers: int = MAX_ASYNC_WORKERS):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn
        self.variants_info = []
        self.semaphore = asyncio.Semaphore(max_workers)

    async def upload_processed_files(self, image_file: UploadFile):
        image_bytes = await image_file.read()
        image_group_directory = construct_file_group_directory(image_file.filename)
        image_file_extension = get_file_extension(image_file.filename)

        original_upload_response = await self.file_storage_client.upload(
            image_file.filename,
            image_group_directory,
            image_bytes,
        )
        original_file_path = original_upload_response.get('file_save_path')

        original_record = self._insert_original(original_file_path)
        original_id = original_record.get('id')
        tasks = []
        for iteration in range(1, IMAGE_TO_PROCESS_COUNT + 1):
            tasks.append(
                asyncio.create_task(
                    self._process_image_variant(
                        iteration, 
                        image_file.filename,
                        image_file_extension,
                        image_bytes,
                        image_group_directory
                    )
                )
            )
        await asyncio.gather(*tasks)

        await run_in_threadpool(
            self._insert_variant,
            original_id
        )
    
    async def _process_image_variant(
        self, iteration, original_name, ext, image_bytes, group_dir
    ):
        async with self.semaphore:
            seed = np.random.default_rng().integers(0, MAX_RANDOM_SEED)
            modified_name = construct_file_name_with_suffix(original_name, iteration)

            shuffled: bytes = await run_in_threadpool(
                generate_shuffled_pixel_image,
                image_bytes, seed, ext
            )

            upload_resp = await self.file_storage_client.upload(
                modified_name, group_dir, shuffled
            )

            self.variants_info.append({
                "file_path": upload_resp["file_save_path"],
                "iteration": iteration,
                "seed": seed,
            })
    
    def _insert_original(self, file_path: str):
        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query, params = insert_into_original_image_table(file_path)
            cursor.execute(query, params)
            return cursor.fetchone()

    def _insert_variant(
        self,
        original_id: int
    ):
        variant_values = [
            (original_id, variant_info['file_path'], variant_info['iteration'],)
            for variant_info in self.variants_info
        ]

        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            execute_values(cursor, insert_into_modified_image_table(), variant_values)
            variant_ids = [row["id"] for row in cursor.fetchall()]

            param_values = [
                (variant_id, int(info["seed"]),)
                for variant_id, info in zip(variant_ids, self.variants_info)
            ]

            status_values = [
                (variant_id,)
                for variant_id in variant_ids
            ]

            execute_values(cursor, insert_into_image_modification_params_table(), param_values)
            execute_values(cursor, insert_into_image_reversability_status_table(), status_values)
        self.database_conn.commit()