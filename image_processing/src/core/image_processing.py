import numpy as np

from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection
from fastapi import UploadFile
from PIL import Image
from io import BytesIO

from .utils.constants import IMAGE_PROCESS_COUNT
from .utils.sql_queries import \
    insert_into_original_image_table, \
    insert_into_modified_image_table, \
    insert_into_image_modification_params_table
from ..infrastructure.file_storage_client import FileStorageClient

class ImageProcessingService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn

    @staticmethod
    def _construct_file_modified_name(file_name: str, suffix: str) -> str:
        file_name_array = file_name.split('.')
        return f"{''.join(file_name_array[:-1])}_{suffix}.{file_name_array[-1]}"

    def _generate_image_variant(self, image_file_contents: bytes, image_file_name: str, iteration: int, random_seed: int):
        return self._construct_file_modified_name(image_file_name, iteration), self.shuffle_random_subset(image_file_contents, random_seed)

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
            query_original, params_original = insert_into_original_image_table(original_upload_file_path)
            cursor.execute(query_original, params_original)
            original_upload_id = cursor.fetchone().get('id')

            for i in range(0, IMAGE_PROCESS_COUNT):
                random_seed = np.random.default_rng().integers(0, 10000)
                file_name_modified, file_bytes = self._generate_image_variant(
                    contents, 
                    image_file.filename, 
                    i + 1,
                    random_seed
                )
                modified_upload_response = await self.file_storage_client.upload(
                    file_name_modified, 
                    image_group_dir, 
                    file_bytes
                )
                modified_upload_file_path = modified_upload_response['file_save_path']
                query_modified, params_modified = insert_into_modified_image_table(original_upload_id, modified_upload_file_path, i + 1)
                cursor.execute(query_modified, params_modified)
                modified_image_variant_id = cursor.fetchone().get('id')

                query_modification, params_modification = insert_into_image_modification_params_table(modified_image_variant_id, int(random_seed))
                cursor.execute(query_modification, params_modification)

            self.database_conn.commit()

    def shuffle_random_subset(
        self,
        img_bytes: bytes,
        seed: int,
        min_pixels: int = 100,
    ) -> bytes:
        with BytesIO(img_bytes) as buf:
            img = Image.open(buf)
            img.load()
        arr = np.array(img)
        H, W, C = arr.shape
        N = H * W
        flat = arr.reshape(N, C)

        rng = np.random.default_rng(seed)
        k = int(rng.integers(min_pixels, N+1))

        perm = rng.permutation(N)
        pick = perm[:k]

        out_flat = flat.copy()
        out_flat[pick] = flat[pick][rng.permutation(k)]

        out_arr = out_flat.reshape(H, W, C)
        out_img = Image.fromarray(out_arr)
        with BytesIO() as out_buf:
            out_img.save(out_buf, format="PNG")
            return out_buf.getvalue()
            