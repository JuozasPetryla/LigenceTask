from fastapi import APIRouter, Request, Response, Header

from ..core.files import write_file, read_file

router = APIRouter()

@router.post("/upload-file")
async def upload_image(
        request: Request,
        x_filename_original_b64: str = Header(..., alias="X-Filename-Original-B64"),
        x_filename_modified_b64: str = Header(..., alias="X-Filename-Modified-B64")
    ):
    file_bytes: bytes = await request.body()

    file_save_path = write_file(
        x_filename_original_b64, 
        x_filename_modified_b64, 
        file_bytes
    )

    return {"message": f"Successfully uploaded files", "file_save_path": file_save_path}

@router.get("/download-file")
async def download_image(
        file_path: str
    ):
    file_bytes = read_file(file_path)
    
    return Response(
        content=file_bytes,
        media_type="application/octet-stream"
    ) 