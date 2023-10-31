from datetime import datetime
from typing import Optional, cast
from entities import RawProductDetails
from usecases import UpsertRawProductDetailsUseCase
from adapters.upsert_raw_product_details.aws_sqs import (
    AWSSQSUpsertRawProductDetailsClient,
)
from adapters.upsert_raw_product_details.postgres import (
    PostgresUpsertRawProductDetailsClient,
)
from .config import PostgresConfig, ProjectConfig, AWSSQSConfig, AWSS3Config
import boto3
import json
from aws_lambda_powertools.logging import Logger, utils as log_utils
from aws_lambda_powertools.utilities.typing import LambdaContext
import csv
import re

logger = Logger(level=ProjectConfig.LOG_LEVEL)
log_utils.copy_config_to_registered_loggers(
    source_logger=logger,
    log_level=ProjectConfig.LOG_LEVEL,
)

postgres_upsert_raw_product_details_client: Optional[
    UpsertRawProductDetailsUseCase
] = None
sqs_upsert_raw_product_details_client: Optional[UpsertRawProductDetailsUseCase] = None
s3_client = boto3.client("s3")


def get_secrets_manager_secrets(secret_name: str) -> dict[str, str]:
    """Get secrets from AWS Secrets Manager"""

    secrets_manager_client = boto3.client("secretsmanager")
    response = secrets_manager_client.get_secret_value(SecretId=secret_name)
    result: dict[str, str] = json.loads(response["SecretString"])
    return result


def init_postgres_upsert_raw_product_details_client() -> None:
    global postgres_upsert_raw_product_details_client

    if postgres_upsert_raw_product_details_client is not None:
        return

    postgres_secrets = get_secrets_manager_secrets(
        secret_name=PostgresConfig.SECRETS_MANAGER_NAME
    )

    connection_string = f"postgresql://{postgres_secrets['username']}:{postgres_secrets['password']}@{postgres_secrets['host']}:{postgres_secrets['port']}/{PostgresConfig.POSTGRES_DB}"

    postgres_upsert_raw_product_details_client = PostgresUpsertRawProductDetailsClient(
        connection_string=connection_string,
        raw_product_table_name=PostgresConfig.RAW_PRODUCT_TABLE_NAME,
        upsert_batch_size=PostgresConfig.UPSERT_BATCH_SIZE,
    )


def init_sqs_upsert_raw_product_details_client() -> None:
    global sqs_upsert_raw_product_details_client

    if sqs_upsert_raw_product_details_client is not None:
        return

    sqs_upsert_raw_product_details_client = AWSSQSUpsertRawProductDetailsClient(
        client_creator=lambda: boto3.client("sqs"),
        queue_url=AWSSQSConfig.SUBSCRIBED_QUEUE_URL,
        upsert_batch_size=AWSSQSConfig.UPSERT_BATCH_SIZE,
    )


def pipeline_upsert_raw_product(raw_product_details: RawProductDetails) -> bool:
    """Pipeline for upserting a single raw product details"""

    postgres_upsert_result = cast(
        UpsertRawProductDetailsUseCase, postgres_upsert_raw_product_details_client
    ).upsert(raw_product_details=raw_product_details)

    sqs_upsert_result = cast(
        UpsertRawProductDetailsUseCase, sqs_upsert_raw_product_details_client
    ).upsert(raw_product_details=raw_product_details)

    overall_upsert_result = postgres_upsert_result and sqs_upsert_result

    if not overall_upsert_result:
        logger.error(
            f"Failed to upsert raw product details for product {raw_product_details.product_id}!"
        )

    return overall_upsert_result


def pipeline_upsert_raw_products(
    raw_product_details: list[RawProductDetails],
) -> list[bool]:
    """Pipeline for upserting a batch of product details"""

    postgres_upsert_results = cast(
        UpsertRawProductDetailsUseCase, postgres_upsert_raw_product_details_client
    ).upsert(raw_product_details=raw_product_details)

    sqs_upsert_results = cast(
        UpsertRawProductDetailsUseCase, sqs_upsert_raw_product_details_client
    ).upsert(raw_product_details=raw_product_details)

    overall_upsert_results = [
        postgres_upsert_result and sqs_upsert_result
        for postgres_upsert_result, sqs_upsert_result in zip(
            postgres_upsert_results, sqs_upsert_results
        )
    ]

    failed_product_ids = [
        raw_product_detail.product_id
        for raw_product_detail, overall_upsert_result in zip(
            raw_product_details, overall_upsert_results
        )
        if not overall_upsert_result
    ]

    if failed_product_ids:
        logger.error(
            f"Failed to upsert raw product details for products {','.join(failed_product_ids)}!"
        )

    return overall_upsert_results


@logger.inject_lambda_context(log_event=ProjectConfig.LOG_SOURCE_EVENT)
def handler(event: dict, context: LambdaContext) -> dict:
    init_postgres_upsert_raw_product_details_client()
    init_sqs_upsert_raw_product_details_client()

    lambda_invoke_time = datetime.now()

    try:
        response = s3_client.get_object(
            Bucket=AWSS3Config.SAMPLE_DATA_BUCKET_NAME,
            Key=AWSS3Config.SAMPLE_DATA_KEY,
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception(
                f"Found error status code {response['ResponseMetadata']['HTTPStatusCode']}!"
            )

        raw_product_details: list[RawProductDetails] = []

        logger.info(
            f"Reading raw product details from {AWSS3Config.SAMPLE_DATA_KEY}..."
        )

        INDIAN_RUPEE_TO_HKD_EXCHANGE_RATE = 0.094

        for index, row in enumerate(
            csv.DictReader(response["Body"].read().decode("utf-8").splitlines()),
            start=1,
        ):
            raw_product_details.append(
                RawProductDetails(
                    product_id=str(index).zfill(10),
                    name=row["name"],
                    main_category=row["main_category"],
                    sub_category=row["sub_category"],
                    image_url=row["image"],
                    ratings=float(row["ratings"]),
                    discount_price=float(
                        re.sub(
                            r"\D+",
                            "",
                            row["discount_price"] or row["actual_price"] or "0",
                        )
                    )
                    * INDIAN_RUPEE_TO_HKD_EXCHANGE_RATE,
                    actual_price=float(
                        re.sub(
                            r"\D+",
                            "",
                            row["actual_price"] or row["discount_price"] or "0",
                        )
                    )
                    * INDIAN_RUPEE_TO_HKD_EXCHANGE_RATE,
                    modified_date=lambda_invoke_time,
                    created_date=datetime.now(),
                )
            )

        logger.info(f"Found {len(raw_product_details)} raw product details!")

        upsert_results = pipeline_upsert_raw_products(raw_product_details)

        if not all(upsert_results):
            raise Exception("Error upserting raw product details!")

    except Exception as e:
        logger.exception(e)
        raise e
