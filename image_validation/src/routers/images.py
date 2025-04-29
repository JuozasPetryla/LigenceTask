from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..core.image_validation import ImageVerifierService
from ..dependencies.dependencies import get_image_verifier_service

router = APIRouter()

class VerificationResult(BaseModel):
    original_image_id: int
    variant_index: int
    file_name: str
    is_reversible: bool

@router.get(
    "/images/{original_image_id}/variants/{variant_index}/verify",
    response_model=VerificationResult,
    summary="Verify whether a shuffled variant can be reversed",
)
async def verify_image_variant(
    original_image_id: int,
    variant_index: int,
    service: ImageVerifierService = Depends(get_image_verifier_service),
) -> VerificationResult:
    file_name, is_reversible = await service.verify_image_variant(original_image_id, variant_index)
    return VerificationResult(
        original_image_id=original_image_id,
        variant_index=variant_index,
        file_name=file_name,
        is_reversible=is_reversible,
    )