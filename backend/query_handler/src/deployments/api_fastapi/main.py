# from .utils.logging import setup_logger

# setup_logger()

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import uvloop
import logging
from .routes import router, lifespan
from .utils.api_response import ApiResponse, ApiResponseError

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s | %(levelname)s] (%(name)s) >> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

uvloop.install()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            ApiResponse(
                error=ApiResponseError(code="UNK", message=str(exc)),
            ),
        ),
    )
