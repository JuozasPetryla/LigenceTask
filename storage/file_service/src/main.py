from fastapi import FastAPI

from .routers import files

app = FastAPI()

app.include_router(files.router)