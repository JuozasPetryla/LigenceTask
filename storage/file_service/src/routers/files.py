from fastapi import APIRouter, Request, Response, Header
from pydantic import BaseModel

from ..core.files import write_file, read_file
from ..core.utils.file_utils import create_save_dir_and_path
from starlette.concurrency import run_in_threadpool

router = APIRouter()

class UploadFileResponse(BaseModel):
    message: str
    file_save_path: str

@router.post(
    "/upload-file",
    response_model=UploadFileResponse,
)
async def upload_file(
    request: Request,
    x_filename_original_b64: str = Header(..., alias="X-Filename-Original-B64"),
    x_filename_modified_b64: str = Header(..., alias="X-Filename-Modified-B64")
):
    file_save_path = create_save_dir_and_path(
        x_filename_original_b64,
        x_filename_modified_b64
    )

    file_bytes: bytes = await request.body()
    await run_in_threadpool(
        write_file,
        file_save_path,
        file_bytes
    )

    return UploadFileResponse(
        message="Successfully uploaded file",
        file_save_path=file_save_path
    )

@router.get("/download-file")
async def download_file(
    file_path: str
):
    file_bytes = read_file(file_path)

    return Response(
        content=file_bytes,
        media_type="application/octet-stream"
    )