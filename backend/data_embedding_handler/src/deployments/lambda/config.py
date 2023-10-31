import os


class ProjectConfig:
    LOG_LEVEL: bool = str(os.environ.get("LOG_LEVEL"))
    LOG_SOURCE_EVENT: bool = str(os.environ.get("LOG_SOURCE_EVENT")) == "true"


class OnnxEmbedConfig:
    ONNX_MODEL_PATH = str(os.environ.get("ONNX_MODEL_PATH"))
    TOKENIZER_PATH = str(os.environ.get("TOKENIZER_PATH"))


class AWSSageMakerEmbedConfig:
    AWS_SAGEMAKER_ENDPOINT_NAME = str(os.environ.get("AWS_SAGEMAKER_ENDPOINT_NAME"))
    TOKENIZER_PATH = str(os.environ.get("TOKENIZER_PATH"))
    EMBED_BATCH_SIZE = int(os.environ.get("AWS_SAGEMAKER_EMBED_BATCH_SIZE", 5))


class PostgresConfig:
    POSTGRES_HOST = str(os.environ.get("POSTGRES_HOST"))
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_USER = str(os.environ.get("POSTGRES_USER"))
    POSTGRES_PASSWORD = str(os.environ.get("POSTGRES_PASSWORD"))
    POSTGRES_DB = str(os.environ.get("POSTGRES_DB"))
    SECRETS_MANAGER_NAME = str(os.environ.get("POSTGRES_SECRETS_MANAGER_NAME"))
    RAW_PRODUCT_TABLE_NAME = str(os.environ.get("POSTGRES_RAW_PRODUCT_TABLE_NAME"))
    EMBEDDED_PRODUCT_TABLE_NAME = str(
        os.environ.get("POSTGRES_EMBEDDED_PRODUCT_TABLE_NAME")
    )
    FETCH_BATCH_SIZE = int(os.environ.get("POSTGRES_FETCH_BATCH_SIZE", 1000))
    UPSERT_BATCH_SIZE = int(os.environ.get("POSTGRES_UPSERT_BATCH_SIZE", 1000))


class OpenSearchConfig:
    OPENSEARCH_ENDPOINT = str(os.environ.get("OPENSEARCH_ENDPOINT"))
    OPENSEARCH_INDEX_NAME = str(os.environ.get("OPENSEARCH_INDEX_NAME"))
    OPENSEARCH_USERNAME = str(os.environ.get("OPENSEARCH_USERNAME"))
    OPENSEARCH_PASSWORD = str(os.environ.get("OPENSEARCH_PASSWORD"))
    SECRETS_MANAGER_NAME = str(os.environ.get("OPENSEARCH_SECRETS_MANAGER_NAME"))
    UPSERT_BATCH_SIZE = int(os.environ.get("OPENSEARCH_UPSERT_BATCH_SIZE", 1000))
    _TIMEOUT = os.environ.get("OPENSEARCH_TIMEOUT")
    if _TIMEOUT is None:
        TIMEOUT = None
    else:
        TIMEOUT = int(_TIMEOUT)


class AWSSQSConfig:
    SUBSCRIBED_QUEUE_URL = str(os.environ.get("AWS_SQS_SUBSCRIBED_QUEUE_URL"))
