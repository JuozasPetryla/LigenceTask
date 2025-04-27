import os
import psycopg2

from httpx import AsyncClient
from typing import AsyncGenerator
from fastapi import Depends
from starlette.concurrency import run_in_threadpool
from psycopg2.extensions import connection as PGConnection

from ..infrastructure.file_storage_client import FileStorageClient
from ..core.image_validation import ImageValidationService

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")
FILE_STORAGE_URL = os.getenv("FILE_STORAGE_URL", "http://localhost:5000")

async def get_file_storage_client() -> AsyncGenerator[FileStorageClient, None]:
    async with AsyncClient() as client:
        yield FileStorageClient(base_url=FILE_STORAGE_URL, client=client)

async def get_database_conn() -> AsyncGenerator[PGConnection, None]:
    conn = await run_in_threadpool(psycopg2.connect, DATABASE_URL)
    try:
        yield conn
    finally:
        await run_in_threadpool(conn.close)

async def get_image_validation_service(
    storage: FileStorageClient = Depends(get_file_storage_client),
    database_conn: PGConnection = Depends(get_database_conn)
) -> ImageValidationService:
    return ImageValidationService(storage, database_conn)