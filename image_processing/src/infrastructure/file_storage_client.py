import base64

from httpx import AsyncClient

class FileStorageClient:
    def __init__(self, client: AsyncClient):
        self.client = client

    def _encode_file_name_headers(self, file_name_modified: str, file_name_original: str):
        b64_name_original = base64.b64encode(file_name_original.encode('utf-8')).decode('ascii')
        b64_name_modified = base64.b64encode(file_name_modified.encode('utf-8')).decode('ascii')
        self.client.headers["X-Filename-Original-B64"] = b64_name_original
        self.client.headers["X-Filename-Modified-B64"] = b64_name_modified

    async def upload(self, file_name_modified: str, file_name_original, file_bytes: bytes) -> str:
        self._encode_file_name_headers(file_name_modified, file_name_original)
        resp = await self.client.post(
                f"{self.client.base_url}/upload-file", 
                content=file_bytes
            )
        resp.raise_for_status()
        return resp.json()