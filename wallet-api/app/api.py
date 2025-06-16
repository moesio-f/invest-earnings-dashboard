"""Entrypoint da API."""

from fastapi import FastAPI

from . import v1

app = FastAPI()

app.include_router(v1.router)
