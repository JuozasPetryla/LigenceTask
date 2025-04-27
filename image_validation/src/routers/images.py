from fastapi import APIRouter, Depends

from ..core.image_validation import ImageValidationService
from ..dependencies.dependencies import get_image_validation_service

router = APIRouter()

@router.get("/poll-image")
async def upload_image(
        original_image_id: int,
        variant_index: int,
        service: ImageValidationService = Depends(get_image_validation_service)
    ):
    await service.retrieve_images_by_id(original_image_id, variant_index)
    return {"message": f"Successfully retrieved"}