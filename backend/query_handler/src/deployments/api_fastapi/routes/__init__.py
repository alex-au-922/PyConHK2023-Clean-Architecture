from .health_status import (
    router as health_status_router,
    lifespan as health_status_lifespan,
)
from .similar_products import (
    router as similar_products_router,
    lifespan as similar_products_lifespan,
)
from fastapi import APIRouter, FastAPI
from typing import AsyncIterator
from contextlib import asynccontextmanager, AsyncExitStack

router = APIRouter()

router.include_router(
    health_status_router,
    prefix="/health_status",
    tags=["health_status"],
)

router.include_router(
    similar_products_router,
    prefix="/similar_products",
    tags=["similar_products"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(health_status_lifespan(app))
            await stack.enter_async_context(similar_products_lifespan(app))
            yield
    finally:
        pass
