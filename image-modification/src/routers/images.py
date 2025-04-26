from fastapi import APIRouter, UploadFile, Depends

from ..core.image_processing import ImageProcessingService
from ..dependencies.dependencies import get_image_service

router = APIRouter()

@router.post("/upload-image")
async def upload_image(
        image_file: UploadFile, 
        service: ImageProcessingService = Depends(get_image_service)
    ):
    await service.upload_processed_files(image_file)
    return {"message": f"Successfully uploaded {image_file.filename}"}