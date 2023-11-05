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

uvloop.install()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s | %(levelname)s] (%(name)s) >> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        app.state.inference_session = InferenceSession(
            "./model", providers=["CPUExecutionProvider"]
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
        None, tokenized_text
    )[0]

    return JSONResponse(
        status_code=200,
        content={"result": text_embedding.tolist()},
    )
