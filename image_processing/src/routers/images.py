from fastapi import APIRouter, UploadFile, Depends, status
from pydantic import BaseModel

from ..core.image_processing import ImageProcessingService
from ..core.utils.constants import IMAGE_TO_PROCESS_COUNT
from ..dependencies.dependencies import get_image_service

router = APIRouter()

class UploadImageResponse(BaseModel):
    file_name: str
    variants_created: int

@router.post(
    "/upload-image",
    response_model=UploadImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image and generate shuffled variants",
)
async def upload_image(
    image_file: UploadFile,
    service: ImageProcessingService = Depends(get_image_service),
) -> UploadImageResponse:
    await service.upload_processed_files(image_file)
    return UploadImageResponse(
        file_name=image_file.filename,
        variants_created=IMAGE_TO_PROCESS_COUNT,
    )