from httpx import AsyncClient

class FileStorageClient:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def download(self, file_path: str) -> bytes:
        resp = await self.client.get(
                f"{self.client.base_url}/download-file",
                params={ "file_path": file_path }
            )
        resp.raise_for_status()
        return resp.content