from datetime import datetime
import json
from typing import Optional, cast
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
import boto3
import logging
from aws_lambda_powertools.logging import Logger, correlation_paths, utils as log_utils
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.api_gateway import Response

from entities import RawQueryDetails
from usecases import (
    EmbedRawQueryDetailsUseCase,
    FetchRawProductDetailsUseCase,
    QuerySimilarProductDetailsUseCase,
)
from adapters.embed_raw_query_details.onnx import OnnxEmbedRawQueryDetailsClient
from adapters.fetch_raw_product_details.postgres import (
    PostgresFetchRawProductDetailsClient,
)
from adapters.query_similar_product_details.opensearch import (
    OpenSearchQuerySimilarProductDetailsClient,
)
from .config import (
    PostgresConfig,
    OpenSearchConfig,
    OnnxEmbedConfig,
    SearchSimilarProductsConfig,
    ProjectConfig,
)

logger = Logger(level=ProjectConfig.LOG_LEVEL)
log_utils.copy_config_to_registered_loggers(
    source_logger=logger,
    log_level=ProjectConfig.LOG_LEVEL,
)
tracer = Tracer(service="query_handler")
app = APIGatewayHttpResolver()

embed_raw_query_details_client: Optional[EmbedRawQueryDetailsUseCase] = None
fetch_raw_product_details_client: Optional[FetchRawProductDetailsUseCase] = None
query_similar_product_details_client: Optional[QuerySimilarProductDetailsUseCase] = None


def get_secrets_manager_secrets(secret_name: str) -> dict[str, str]:
    """Get secrets from AWS Secrets Manager"""

    secrets_manager_client = boto3.client("secretsmanager")
    response = secrets_manager_client.get_secret_value(SecretId=secret_name)
    result: dict[str, str] = json.loads(response["SecretString"])
    return result


def init_embed_raw_query_details_client() -> None:
    global embed_raw_query_details_client
    if embed_raw_query_details_client is not None:
        return
    inference_session = InferenceSession(
        OnnxEmbedConfig.ONNX_MODEL_PATH, providers=["CPUExecutionProvider"]
    )
    tokenizer = AutoTokenizer.from_pretrained(OnnxEmbedConfig.TOKENIZER_PATH)
    embed_raw_query_details_client = OnnxEmbedRawQueryDetailsClient(
        inference_session=inference_session,
        tokenizer=tokenizer,
    )


def init_fetch_raw_product_details_client() -> None:
    global fetch_raw_product_details_client
    if fetch_raw_product_details_client is not None:
        return
    postgres_secrets = get_secrets_manager_secrets(
        secret_name=PostgresConfig.SECRETS_MANAGER_NAME
    )
    fetch_raw_product_details_client = PostgresFetchRawProductDetailsClient(
        host=postgres_secrets["readerHost"],
        port=int(postgres_secrets["readerPort"]),
        username=postgres_secrets["username"],
        password=postgres_secrets["password"],
        database=PostgresConfig.POSTGRES_DB,
        raw_product_table_name=PostgresConfig.RAW_PRODUCT_TABLE_NAME,
        fetch_batch_size=PostgresConfig.FETCH_BATCH_SIZE,
    )


def init_query_similar_product_details_client() -> None:
    global query_similar_product_details_client
    if query_similar_product_details_client is not None:
        return
    opensearch_secrets = get_secrets_manager_secrets(
        secret_name=OpenSearchConfig.SECRETS_MANAGER_NAME
    )
    query_similar_product_details_client = OpenSearchQuerySimilarProductDetailsClient(
        opensearch_endpoint=opensearch_secrets["endpoint"],
        index_name=OpenSearchConfig.OPENSEARCH_INDEX_NAME,
        master_auth=(
            opensearch_secrets["username"],
            opensearch_secrets["password"],
        ),
        default_threshold=SearchSimilarProductsConfig.DEFAULT_THRESHOLD,
        default_top_k=SearchSimilarProductsConfig.DEFAULT_LIMIT,
        fetch_batch_size=PostgresConfig.FETCH_BATCH_SIZE,
        timeout=OpenSearchConfig.TIMEOUT,
    )


@app.post("/api/similar_products")
def similar_products() -> Response:
    """Pipeline for querying similar products"""

    INTERNAL_SERVER_ERROR_CODE = 500
    CLIENT_ERROR_CODE = 400
    SUCCESS_CODE = 201

    try:
        query_body: dict = app.current_event.json_body

        logger.info(f"{query_body=}")

        raw_query_details = RawQueryDetails(
            query=query_body["query"], created_date=datetime.now()
        )

        logger.info(f"{raw_query_details=}")

        embedded_query_details = cast(
            EmbedRawQueryDetailsUseCase, embed_raw_query_details_client
        ).embed(raw_query_details)

        logger.info(f"{embedded_query_details=}")

        if embedded_query_details is None:
            return Response(
                status_code=INTERNAL_SERVER_ERROR_CODE,
                content_type="application/json",
                body={
                    "message": "Query Embedding failed",
                    "error": {
                        "message": "Query Embedding failed",
                        "code": "QUERY_EMBEDDING_FAILED",
                    },
                },
            )

        similar_products_tuples = cast(
            QuerySimilarProductDetailsUseCase, query_similar_product_details_client
        ).query(
            embedded_query_details, query_body.get("threshold"), query_body.get("limit")
        )

        logger.info(f"{similar_products_tuples=}")

        if similar_products_tuples is None:
            return Response(
                status_code=INTERNAL_SERVER_ERROR_CODE,
                content_type="application/json",
                body={
                    "message": "Query Similar Products failed",
                    "error": {
                        "message": "Query Similar Products failed",
                        "code": "QUERY_SIMILAR_PRODUCTS_FAILED",
                    },
                },
            )

        similar_product_ids: list[str]
        similar_product_scores: list[float]
        similar_product_ids, similar_product_scores = zip(*similar_products_tuples)

        similar_product_details = cast(
            FetchRawProductDetailsUseCase, fetch_raw_product_details_client
        ).fetch(similar_product_ids)

        logger.info(f"{similar_product_details=}")

        valid_similar_product_details = [
            similar_product_detail
            for similar_product_detail in similar_product_details
            if similar_product_detail is not None
        ]

        valid_similar_product_scores = [
            similar_product_score
            for similar_product_score in similar_product_scores
            if similar_product_score is not None
        ]

        return Response(
            status_code=SUCCESS_CODE,
            content_type="application/json",
            body={
                "message": "Query Similar Products successful",
                "data": {
                    "similar_products": [
                        {
                            "product_id": product.product_id,
                            "name": product.name,
                            "main_category": product.main_category,
                            "sub_category": product.sub_category,
                            "image_url": product.image_url,
                            "ratings": product.ratings,
                            "discount_price": product.discount_price,
                            "actual_price": product.actual_price,
                            "modified_date": datetime.strftime(
                                product.modified_date, "%Y-%m-%d %H:%M:%S"
                            ),
                            "created_date": datetime.strftime(
                                product.created_date, "%Y-%m-%d %H:%M:%S"
                            ),
                            "score": min(1, max(-1, score)),
                        }
                        for product, score in zip(
                            valid_similar_product_details, valid_similar_product_scores
                        )
                    ],
                    "query": query_body["query"],
                    "created_date": datetime.now(),
                    "modified_date": datetime.now(),
                },
            },
        )
    except ValueError as e:
        return Response(
            status_code=CLIENT_ERROR_CODE,
            content_type="application/json",
            body={
                "message": "Invalid request body",
                "error": {
                    "message": str(e),
                    "code": "INVALID_REQUEST_BODY",
                },
            },
        )
    except Exception as e:
        return Response(
            status_code=INTERNAL_SERVER_ERROR_CODE,
            content_type="application/json",
            body={
                "message": "Internal server error",
                "error": {
                    "message": str(e),
                    "code": "UNK",
                },
            },
        )


@logger.inject_lambda_context(
    log_event=ProjectConfig.LOG_SOURCE_EVENT,
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP,
)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    init_embed_raw_query_details_client()
    logger.info(f"{embed_raw_query_details_client=}")
    init_fetch_raw_product_details_client()
    logger.info(f"{fetch_raw_product_details_client=}")
    init_query_similar_product_details_client()
    logger.info(f"{query_similar_product_details_client=}")

    return app.resolve(event, context)
