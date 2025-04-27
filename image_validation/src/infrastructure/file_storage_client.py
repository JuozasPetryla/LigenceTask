from httpx import AsyncClient

class FileStorageClient:
    def __init__(self, base_url: str, client: AsyncClient):
        self.base_url = base_url
        self.client = client
        self.headers = { "Content-Type": "application/octet-stream" }

    async def download(self, file_path: str) -> bytes:
        resp = await self.client.get(
                f"{self.base_url}/download-file",
                params={ "file_path": file_path }
            )
        resp.raise_for_status()
        return resp