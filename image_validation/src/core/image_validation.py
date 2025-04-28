from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as PGConnection

from ..infrastructure.file_storage_client import FileStorageClient
from .utils.enums import ReversabilityStatus
from .utils.sql_queries import (
    select_image_variant_metadata_by_id, 
    update_image_reversability_status_table
)
from .utils.image_utils import (
    generate_unshuffled_pixel_image,
    compare_image_reversability_by_pixel
)
from .utils.file_utils import (
    get_file_extension,
    get_file_name_from_path
)
from .utils.mapping_utils import map_string_to_bool

class ImageVerifierService:
    def __init__(self, file_storage_client: FileStorageClient, database_conn: PGConnection):
        self.file_storage_client = file_storage_client
        self.database_conn = database_conn
    
    async def verify_image_variant(self, original_image_id: int, variant_index: int) -> bool:
        with self.database_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query_select, params_select = select_image_variant_metadata_by_id(original_image_id, variant_index)
            cursor.execute(query_select, params_select)
            result = cursor.fetchone()

            original_image_path = result.get('original_file_path')
            modified_image_path = result.get('variant_file_path')
            modified_image_id = result.get('variant_id')
            image_modification_seed = result.get('modification_seed')

            original_file_bytes = await self.file_storage_client.download(original_image_path)
            modified_file_bytes = await self.file_storage_client.download(modified_image_path)

            unshuffled_image_bytes = generate_unshuffled_pixel_image(
                modified_file_bytes, 
                image_modification_seed,
                get_file_extension(modified_image_path)
            )

            comparison_result = compare_image_reversability_by_pixel(
                original_file_bytes,
                unshuffled_image_bytes
            )

            reversability_status = ReversabilityStatus.TRUE.value if comparison_result else ReversabilityStatus.FALSE.value

            query_status, params_status = update_image_reversability_status_table(reversability_status, modified_image_id)
            cursor.execute(query_status, params_status)
        self.database_conn.commit()

        return get_file_name_from_path(original_image_path), map_string_to_bool(reversability_status)


