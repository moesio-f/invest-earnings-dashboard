"""Entrypoint da API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import v1

app = FastAPI()
restricted = FastAPI()
restricted.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router, prefix="/v1")


@restricted.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "healthy", "available_versions": ["v1"]}


app.mount("/restricted", restricted)
