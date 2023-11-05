from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncIterator
from contextlib import asynccontextmanager
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
import uvloop

uvloop.install()


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
    return JSONResponse(
        status_code=200,
        content={"message": "Hello World"},
    )