import numpy as np

from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection

from PIL import Image
from io import BytesIO

from .utils.sql_queries import select_image_variant_metadata_by_id
from ..infrastructure.file_storage_client import FileStorageClient

class ImageValidationService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn
    
    async def retrieve_images_by_id(self, original_image_id: int, variant_index: int):
        query_select, params_select = select_image_variant_metadata_by_id(original_image_id, variant_index)

        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query_select, params_select)
            result = cursor.fetchone()

            original_file_bytes = await self.file_storage_client.download(result.get('original_file_path'))
            modified_file_bytes = await self.file_storage_client.download(result.get('variant_file_path'))


            unshuffled_image_bytes = self.unshuffle_random_subset(modified_file_bytes, result.get('modification_seed'))

            comparison_result = self.compare_image_bytes_plain(
                original_file_bytes,
                unshuffled_image_bytes
            )

            print(comparison_result)



    def compare_image_bytes_plain(self, bytes1: bytes, bytes2: bytes):
        img1 = Image.open(BytesIO(bytes1)); img1.load()
        img2 = Image.open(BytesIO(bytes2)); img2.load()
        
        if img1.size != img2.size or img1.mode != img2.mode:
            raise ValueError("Images differ in size or mode")
        
        pixels1 = list(img1.getdata())
        pixels2 = list(img2.getdata())
        
        total = len(pixels1)
        diff_count = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 != p2)
        
        return {
            "total_pixels": total,
            "num_different": diff_count,
            "percent_diff": diff_count / total * 100
        }


    def unshuffle_random_subset(
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
        flat_shuffled = arr.reshape(N, C)

        rng = np.random.default_rng(seed)
        k = int(rng.integers(min_pixels, N + 1))
        perm = rng.permutation(N)                  
        pick = perm[:k]
        perm_k = rng.permutation(k)

        inv_perm_k = np.empty_like(perm_k)
        inv_perm_k[perm_k] = np.arange(k)

        orig_flat = flat_shuffled.copy()
        orig_flat[pick] = flat_shuffled[pick][inv_perm_k]

        orig_arr = orig_flat.reshape(H, W, C)
        orig_img = Image.fromarray(orig_arr)
        with BytesIO() as out_buf:
            orig_img.save(out_buf, format="PNG")
            return out_buf.getvalue()
