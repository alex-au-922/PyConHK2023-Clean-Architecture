from datetime import datetime
from typing import Optional, cast
from usecases import (
    FetchRawProductDetailsUseCase,
    UpsertEmbeddedProductDetailsUseCase,
    EmbedRawProductDetailsUseCase,
)

# from adapters.embed_raw_product_details.onnx import OnnxEmbedRawProductDetailsClient
from adapters.embed_raw_product_details.aws_sagemaker import (
    AWSSageMakerEmbedRawProductDetailsClient,
)
from adapters.fetch_raw_product_details.postgres import (
    PostgresFetchRawProductDetailsClient,
)
from adapters.upsert_embedded_product_details.postgres import (
    PostgresUpsertEmbeddedProductDetailsClient,
)
from adapters.upsert_embedded_product_details.opensearch import (
    OpenSearchUpsertEmbeddedProductDetailsClient,
)
from onnxruntime import InferenceSession
from transformers import AutoTokenizer
from .config import (
    OnnxEmbedConfig,
    AWSSageMakerEmbedConfig,
    PostgresConfig,
    OpenSearchConfig,
    ProjectConfig,
    AWSSQSConfig,
)
import boto3
import json
from aws_lambda_powertools.logging import Logger, utils as log_utils
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger(level=ProjectConfig.LOG_LEVEL)
log_utils.copy_config_to_registered_loggers(
    source_logger=logger,
    log_level=ProjectConfig.LOG_LEVEL,
)

embed_raw_product_details_client: Optional[EmbedRawProductDetailsUseCase] = None
fetch_raw_product_details_client: Optional[FetchRawProductDetailsUseCase] = None
postgres_upsert_embedded_product_details_client: Optional[
    UpsertEmbeddedProductDetailsUseCase
] = None
opensearch_upsert_embedded_product_details_client: Optional[
    UpsertEmbeddedProductDetailsUseCase
] = None
sqs_client = boto3.client("sqs")


def get_secrets_manager_secrets(secret_name: str) -> dict[str, str]:
    """Get secrets from AWS Secrets Manager"""

    secrets_manager_client = boto3.client("secretsmanager")
    response = secrets_manager_client.get_secret_value(SecretId=secret_name)
    result: dict[str, str] = json.loads(response["SecretString"])
    return result


def init_embed_raw_product_details_client() -> None:
    global embed_raw_product_details_client

    if embed_raw_product_details_client is not None:
        return

    # inference_session = InferenceSession(
    #     OnnxEmbedConfig.ONNX_MODEL_PATH, providers=["CPUExecutionProvider"]
    # )
    # tokenizer = AutoTokenizer.from_pretrained(OnnxEmbedConfig.TOKENIZER_PATH)
    # embed_raw_product_details_client = OnnxEmbedRawProductDetailsClient(
    #     inference_session=inference_session,
    #     tokenizer=tokenizer,
    # )

    embed_raw_product_details_client = AWSSageMakerEmbedRawProductDetailsClient(
        client_creator=lambda: boto3.client("sagemaker-runtime"),
        endpoint_name=AWSSageMakerEmbedConfig.AWS_SAGEMAKER_ENDPOINT_NAME,
        embed_batch_size=AWSSageMakerEmbedConfig.EMBED_BATCH_SIZE,
    )


def init_fetch_raw_product_details_client() -> None:
    global fetch_raw_product_details_client

    if fetch_raw_product_details_client is not None:
        return

    postgres_secrets = get_secrets_manager_secrets(
        secret_name=PostgresConfig.SECRETS_MANAGER_NAME
    )

    fetch_raw_product_details_client = PostgresFetchRawProductDetailsClient(
        host=postgres_secrets["host"],
        port=int(postgres_secrets["port"]),
        username=postgres_secrets["username"],
        password=postgres_secrets["password"],
        database=PostgresConfig.POSTGRES_DB,
        raw_product_table_name=PostgresConfig.RAW_PRODUCT_TABLE_NAME,
        fetch_batch_size=PostgresConfig.FETCH_BATCH_SIZE,
    )


def init_postgres_upsert_embedded_product_details_client() -> None:
    global postgres_upsert_embedded_product_details_client

    if postgres_upsert_embedded_product_details_client is not None:
        return

    postgres_secrets = get_secrets_manager_secrets(
        secret_name=PostgresConfig.SECRETS_MANAGER_NAME
    )

    postgres_upsert_embedded_product_details_client = (
        PostgresUpsertEmbeddedProductDetailsClient(
            host=postgres_secrets["host"],
            port=int(postgres_secrets["port"]),
            username=postgres_secrets["username"],
            password=postgres_secrets["password"],
            database=PostgresConfig.POSTGRES_DB,
            embedded_product_table_name=PostgresConfig.EMBEDDED_PRODUCT_TABLE_NAME,
            upsert_batch_size=PostgresConfig.UPSERT_BATCH_SIZE,
        )
    )


def init_opensearch_upsert_embedded_product_details_client() -> None:
    global opensearch_upsert_embedded_product_details_client

    if opensearch_upsert_embedded_product_details_client is not None:
        return

    opensearch_secrets = get_secrets_manager_secrets(
        secret_name=OpenSearchConfig.SECRETS_MANAGER_NAME
    )

    opensearch_upsert_embedded_product_details_client = (
        OpenSearchUpsertEmbeddedProductDetailsClient(
            opensearch_endpoint=opensearch_secrets["endpoint"],
            index_name=OpenSearchConfig.OPENSEARCH_INDEX_NAME,
            master_auth=(
                opensearch_secrets["username"],
                opensearch_secrets["password"],
            ),
            upsert_batch_size=OpenSearchConfig.UPSERT_BATCH_SIZE,
            timeout=OpenSearchConfig.TIMEOUT,
        )
    )


def pipeline_embed_product(product_id: str, product_modified_date: datetime) -> bool:
    """Pipeline for fetching, embeding, and upserting a single product details"""

    raw_product_details = cast(
        FetchRawProductDetailsUseCase, fetch_raw_product_details_client
    ).fetch(product_id)

    if raw_product_details is None:
        logger.error(f"Failed to fetch raw product details for product {product_id}!")
        return False

    if raw_product_details.modified_date > product_modified_date:
        logger.warning(f"Latest details for product {product_id} is not yet available!")
        return False

    embedded_product_details = cast(
        EmbedRawProductDetailsUseCase, embed_raw_product_details_client
    ).embed(raw_product_details=raw_product_details)

    if embedded_product_details is None:
        logger.error(f"Failed to embed raw product details for product {product_id}!")
        return False

    postgres_upsert_result = cast(
        UpsertEmbeddedProductDetailsUseCase,
        postgres_upsert_embedded_product_details_client,
    ).upsert(embedded_product_details=embedded_product_details)

    opensearch_upsert_result = cast(
        UpsertEmbeddedProductDetailsUseCase,
        opensearch_upsert_embedded_product_details_client,
    ).upsert(embedded_product_details=embedded_product_details)

    if not postgres_upsert_result or not opensearch_upsert_result:
        logger.error(
            f"Failed to upsert embedded product details for product {product_id}!"
        )
        return False

    logger.info(
        f"Successfully upserted embedded product details for product {product_id}!"
    )

    return True


def pipeline_embed_products(
    product_id_modified_date_pairs: list[tuple[str, datetime]]
) -> list[bool]:
    """Pipeline for fetching, embeding, and upserting a batch of product details"""

    successes: list[bool] = [True] * len(product_id_modified_date_pairs)

    product_ids: list[str]
    product_modified_dates: list[datetime]
    product_ids, product_modified_dates = zip(*product_id_modified_date_pairs)

    # Fetch raw product details

    raw_products_details = cast(
        FetchRawProductDetailsUseCase, fetch_raw_product_details_client
    ).fetch(product_ids)

    valid_raw_products_details = [
        raw_product_details
        for raw_product_details, modified_date in zip(
            raw_products_details, product_modified_dates
        )
        if (
            raw_product_details is not None
            and raw_product_details.modified_date <= modified_date
        )
    ]

    valid_raw_products_details_indices = [
        index
        for index, raw_product_details in enumerate(raw_products_details)
        if (
            raw_product_details is not None
            and raw_product_details.modified_date <= product_modified_dates[index]
        )
    ]

    invalid_raw_products_details_indices = [
        index
        for index, raw_product_details in enumerate(raw_products_details)
        if (
            raw_product_details is None
            or raw_product_details.modified_date > product_modified_dates[index]
        )
    ]

    for invalid_raw_products_details_index in invalid_raw_products_details_indices:
        successes[invalid_raw_products_details_index] = False

    # Embed raw product details

    embedded_raw_products_details = cast(
        EmbedRawProductDetailsUseCase, embed_raw_product_details_client
    ).embed(raw_product_details=valid_raw_products_details)

    valid_embedded_raw_products_details = [
        embedded_raw_product_details
        for embedded_raw_product_details, modified_date in zip(
            embedded_raw_products_details, product_modified_dates
        )
        if embedded_raw_product_details is not None
    ]

    valid_embedded_raw_products_details_indices = [
        index
        for index, embedded_raw_product_details in zip(
            valid_raw_products_details_indices, embedded_raw_products_details
        )
        if embedded_raw_product_details is not None
    ]

    invalid_embedded_raw_products_details_indices = [
        index
        for index, embedded_raw_product_details in enumerate(
            embedded_raw_products_details
        )
        if embedded_raw_product_details is None
    ]

    for (
        invalid_embedded_raw_products_details_index
    ) in invalid_embedded_raw_products_details_indices:
        successes[invalid_embedded_raw_products_details_index] = False

    # Upsert embedded product details to Postgres and OpenSearch

    postgres_upsert_results = cast(
        UpsertEmbeddedProductDetailsUseCase,
        postgres_upsert_embedded_product_details_client,
    ).upsert(embedded_product_details=valid_embedded_raw_products_details)

    opensearch_upsert_results = cast(
        UpsertEmbeddedProductDetailsUseCase,
        opensearch_upsert_embedded_product_details_client,
    ).upsert(embedded_product_details=valid_embedded_raw_products_details)

    overall_upsert_results = [
        postgres_upsert_result and opensearch_upsert_result
        for postgres_upsert_result, opensearch_upsert_result in zip(
            postgres_upsert_results, opensearch_upsert_results
        )
    ]

    upsert_invalid_embedded_products_details_indices = [
        index
        for index, overall_upsert_result in zip(
            valid_embedded_raw_products_details_indices, overall_upsert_results
        )
        if not overall_upsert_result
    ]

    for (
        upsert_invalid_embedded_products_details_index
    ) in upsert_invalid_embedded_products_details_indices:
        successes[upsert_invalid_embedded_products_details_index] = False

    # Clean up

    invalid_raw_products_ids = [
        product_ids[index] for index in invalid_raw_products_details_indices
    ]

    failed_embed_raw_products_ids = [
        product_ids[index] for index in invalid_embedded_raw_products_details_indices
    ]

    upsert_failed_products_ids = [
        product_ids[index] for index in upsert_invalid_embedded_products_details_indices
    ]

    if invalid_raw_products_ids:
        logger.error(
            f"Failed to fetch raw product details for products {invalid_raw_products_ids}!"
        )

    if failed_embed_raw_products_ids:
        logger.error(
            f"Failed to embed raw product details for products {failed_embed_raw_products_ids}!"
        )

    if upsert_failed_products_ids:
        logger.error(
            f"Failed to upsert embedded product details for products {upsert_failed_products_ids}!"
        )

    return successes


@logger.inject_lambda_context(log_event=ProjectConfig.LOG_SOURCE_EVENT)
@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context: LambdaContext) -> None:
    init_embed_raw_product_details_client()
    init_fetch_raw_product_details_client()
    init_postgres_upsert_embedded_product_details_client()
    init_opensearch_upsert_embedded_product_details_client()

    try:
        message_receipts = [
            event_record.receipt_handle for event_record in event.records
        ]

        product_id_modified_date_pairs = [
            (
                event_record.json_body["product_id"],
                datetime.strptime(
                    event_record.json_body["modified_date"], "%Y-%m-%d %H:%M:%S.%f"
                ),
            )
            for event_record in event.records
        ]

        if len(product_id_modified_date_pairs) == 1:
            product_id, product_modified_date = product_id_modified_date_pairs[0]

            success = pipeline_embed_product(
                product_id=product_id, product_modified_date=product_modified_date
            )

            if success:
                sqs_client.delete_message(
                    QueueUrl=AWSSQSConfig.SUBSCRIBED_QUEUE_URL,
                    ReceiptHandle=message_receipts[0],
                )
            else:
                raise Exception(f"Message {message_receipts[0]} failed to embed!")

        successes = pipeline_embed_products(
            product_id_modified_date_pairs=product_id_modified_date_pairs
        )

        message_receipts_map: dict[str, bool] = {}
        for message_receipt, success in zip(message_receipts, successes):
            if message_receipt not in message_receipts_map:
                message_receipts_map[message_receipt] = True
            message_receipts_map[message_receipt] = (
                message_receipts_map[message_receipt] and success
            )

        failed_message_receipts: list[str] = []
        for message_receipt, success in message_receipts_map.items():
            if success:
                sqs_client.delete_message(
                    QueueUrl=AWSSQSConfig.SUBSCRIBED_QUEUE_URL,
                    ReceiptHandle=message_receipt,
                )
            else:
                failed_message_receipts.append(message_receipt)

        if failed_message_receipts:
            raise Exception(
                f"Some messages failed to embed: {failed_message_receipts}!"
            )
    except Exception as e:
        logger.exception(e)
        raise e
