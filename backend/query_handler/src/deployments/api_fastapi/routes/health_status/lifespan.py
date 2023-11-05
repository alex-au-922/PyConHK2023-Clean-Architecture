from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        pass
