import json
import boto3
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator
from adapters.embed_raw_query_details.onnx import OnnxEmbedRawQueryDetailsClient
from adapters.fetch_raw_product_details.postgres import (
    PostgresFetchRawProductDetailsClient,
)
from adapters.query_similar_product_details.opensearch import (
    OpenSearchQuerySimilarProductDetailsClient,
)
from ...config import (
    PostgresConfig,
    OpenSearchConfig,
    OnnxEmbedConfig,
    SearchSimilarProductsConfig,
)
from onnxruntime import InferenceSession
from transformers import AutoTokenizer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        inference_session = InferenceSession(
            OnnxEmbedConfig.ONNX_MODEL_PATH, providers=["CPUExecutionProvider"]
        )
        tokenizer = AutoTokenizer.from_pretrained(OnnxEmbedConfig.TOKENIZER_PATH)

        app.state.embed_raw_query_details_client = OnnxEmbedRawQueryDetailsClient(
            inference_session=inference_session,
            tokenizer=tokenizer,
        )

        secrets_manager_client = boto3.client("secretsmanager")
        postgres_secrets = secrets_manager_client.get_secret_value(
            SecretId=PostgresConfig.SECRETS_MANAGER_NAME
        )
        postgres_secrets_dict = json.loads(postgres_secrets["SecretString"])

        app.state.fetch_raw_product_details_client = (
            PostgresFetchRawProductDetailsClient(
                host=postgres_secrets_dict["host"],
                port=int(postgres_secrets_dict["port"]),
                username=postgres_secrets_dict["username"],
                password=postgres_secrets_dict["password"],
                database=PostgresConfig.POSTGRES_DB,
                raw_product_table_name=PostgresConfig.RAW_PRODUCT_TABLE_NAME,
                fetch_batch_size=PostgresConfig.FETCH_BATCH_SIZE,
            )
        )

        opensearch_secrets = secrets_manager_client.get_secret_value(
            SecretId=OpenSearchConfig.SECRETS_MANAGER_NAME
        )
        opensearch_secrets_dict = json.loads(opensearch_secrets["SecretString"])

        app.state.query_similar_product_details_client = (
            OpenSearchQuerySimilarProductDetailsClient(
                opensearch_endpoint=opensearch_secrets_dict["endpoint"],
                index_name=OpenSearchConfig.OPENSEARCH_INDEX_NAME,
                master_auth=(
                    opensearch_secrets_dict["username"],
                    opensearch_secrets_dict["password"],
                ),
                default_threshold=SearchSimilarProductsConfig.DEFAULT_THRESHOLD,
                default_top_k=SearchSimilarProductsConfig.DEFAULT_LIMIT,
                fetch_batch_size=PostgresConfig.FETCH_BATCH_SIZE,
                timeout=OpenSearchConfig.TIMEOUT,
            )
        )

        yield

    finally:
        app.state.embed_raw_query_details_client.close()
        app.state.fetch_raw_product_details_client.close()
        app.state.query_similar_product_details_client.close()
