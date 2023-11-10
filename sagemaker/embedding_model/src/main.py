from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncIterator
from contextlib import asynccontextmanager
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
import uvloop
import logging
import asyncio
import numpy.typing as npt
import numpy as np
from config import LogConfig

uvloop.install()

logging.basicConfig(
    level=LogConfig.LOG_LEVEL,
    format=LogConfig.FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.getLogger("uvicorn.access").handlers = logging.root.handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        app.state.inference_session = InferenceSession(
            "./model", providers=["CUDAExecutionProvider"]
        )
        app.state.tokenizer = AutoTokenizer.from_pretrained("./tokenizer")
        yield
    finally:
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def ping(request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"message": "pong"},
    )


@app.post("/invocations")
def invocations(request: Request) -> JSONResponse:
    request_body: dict = asyncio.run(request.json())
    logging.info(request_body)

    text = request_body["text"]

    tokenized_text = app.state.tokenizer(
        [text], return_tensors="np", padding=True, truncation=True
    )
    text_embedding: npt.NDArray[np.float_] = app.state.inference_session.run(
        ["output"], dict(tokenized_text)
    )[0][0]

    return JSONResponse(
        status_code=200,
        content={"result": text_embedding.tolist()},
    )
