from httpx import AsyncClient
from fastapi import Depends

from ..infra.file_storage_client import FileStorageClient
from ..core.image_processing import ImageProcessingService

async def get_storage_client() -> FileStorageClient:
    async with AsyncClient() as client:
        yield FileStorageClient(base_url="http://localhost:9000", client=client)

async def get_image_service(
    storage: FileStorageClient = Depends(get_storage_client)
) -> ImageProcessingService:
    return ImageProcessingService(storage)