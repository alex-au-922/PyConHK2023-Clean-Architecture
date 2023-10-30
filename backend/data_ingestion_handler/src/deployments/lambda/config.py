import os


class ProjectConfig:
    LOG_LEVEL: bool = str(os.environ.get("LOG_LEVEL"))
    LOG_SOURCE_EVENT: bool = str(os.environ.get("LOG_SOURCE_EVENT")) == "true"


class PostgresConfig:
    POSTGRES_HOST = str(os.environ.get("POSTGRES_HOST"))
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT"))
    POSTGRES_USER = str(os.environ.get("POSTGRES_USER"))
    POSTGRES_PASSWORD = str(os.environ.get("POSTGRES_PASSWORD"))
    POSTGRES_DB = str(os.environ.get("POSTGRES_DB"))
    SECRETS_MANAGER_NAME = str(os.environ.get("POSTGRES_SECRETS_MANAGER_NAME"))
    RAW_PRODUCT_TABLE_NAME = str(os.environ.get("POSTGRES_RAW_PRODUCT_TABLE_NAME"))
    UPSERT_BATCH_SIZE = int(os.environ.get("POSTGRES_UPSERT_BATCH_SIZE"))


class AWSSQSConfig:
    SUBSCRIBED_QUEUE_URL = str(os.environ.get("AWS_SQS_SUBSCRIBED_QUEUE_URL"))
    UPSERT_BATCH_SIZE = int(os.environ.get("AWS_SQS_UPSERT_BATCH_SIZE"))


class AWSS3Config:
    SAMPLE_DATA_BUCKET_NAME = str(os.environ.get("AWS_S3_SAMPLE_DATA_BUCKET_NAME"))
    SAMPLE_DATA_KEY = str(os.environ.get("AWS_S3_SAMPLE_DATA_KEY"))
