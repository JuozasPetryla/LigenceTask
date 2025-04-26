import base64

from httpx import AsyncClient

class FileStorageClient:
    def __init__(self, base_url: str, client: AsyncClient):
        self.base_url = base_url
        self.client = client
        self.headers = { "Content-Type": "application/octet-stream" }

    def _encode_file_name_headers(self, file_name_modified: str, file_name_original: str):
        b64_name_original = base64.b64encode(file_name_original.encode('utf-8')).decode('ascii')
        b64_name_modified = base64.b64encode(file_name_modified.encode('utf-8')).decode('ascii')
        self.headers["X-Filename-Original-B64"] = b64_name_original
        self.headers["X-Filename-Modified-B64"] = b64_name_modified

    async def upload(self, file_name_modified: str, file_name_original, file_bytes: bytes) -> str:
        self._encode_file_name_headers(file_name_modified, file_name_original)
        resp = await self.client.post(
                f"{self.base_url}/upload-files", 
                content=file_bytes,
                headers=self.headers
            )
        resp.raise_for_status()
        return resp.json()