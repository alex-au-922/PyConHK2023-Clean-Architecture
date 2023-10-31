locals {
  labmda_default_policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
  ]
}

resource "aws_lambda_layer_version" "data_ingestion_handler_lambda_layer" {
  filename            = "${trimsuffix(var.lambda_config.data_ingestion_handler.layer_path, "/")}/${var.lambda_config.data_ingestion_handler.layer_name}.zip"
  layer_name          = var.lambda_config.data_ingestion_handler.layer_name
  source_code_hash    = filebase64sha256("${trimsuffix(var.lambda_config.data_ingestion_handler.layer_path, "/")}/${var.lambda_config.data_ingestion_handler.layer_name}.zip")
  compatible_runtimes = [var.lambda_config.data_ingestion_handler.runtime]
}

module "data_ingestion_handler_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.10.1"

  function_name              = var.lambda_config.data_ingestion_handler.name
  description                = var.lambda_config.data_ingestion_handler.description
  handler                    = var.lambda_config.data_ingestion_handler.handler
  runtime                    = var.lambda_config.data_ingestion_handler.runtime
  architectures              = ["x86_64"]
  publish                    = true
  create_lambda_function_url = var.lambda_config.data_ingestion_handler.function_url

  timeout                        = var.lambda_config.data_ingestion_handler.timeout
  memory_size                    = var.lambda_config.data_ingestion_handler.memory_size
  reserved_concurrent_executions = var.lambda_config.data_ingestion_handler.reserved_concurrent_executions

  package_type = var.lambda_config.data_ingestion_handler.package_type
  source_path  = var.lambda_config.data_ingestion_handler.source_path
  layers       = [aws_lambda_layer_version.data_ingestion_handler_lambda_layer.arn]

  environment_variables = {
    LOG_LEVEL                       = "INFO"
    LOG_SOURCE_EVENT                = true
    POSTGRES_SECRETS_MANAGER_NAME   = module.rds_credentials.secretsmanager_secret_name
    POSTGRES_DB                     = var.rds_config.main_database
    POSTGRES_RAW_PRODUCT_TABLE_NAME = var.rds_table_config.raw_products.name
    POSTGRES_UPSERT_BATCH_SIZE      = 5
    AWS_SQS_SUBSCRIBED_QUEUE_URL    = module.embedding_handler_queue.queue_url
    AWS_SQS_UPSERT_BATCH_SIZE       = 10
    AWS_S3_SAMPLE_DATA_BUCKET_NAME  = module.data_bucket.s3_bucket_id
    AWS_S3_SAMPLE_DATA_KEY          = "sampled_valid_images_dedup_tv_audio_camera_df.csv"
    TZ                              = "${var.timezone}"
  }

  create_role                       = true
  attach_cloudwatch_logs_policy     = false
  cloudwatch_logs_retention_in_days = var.lambda_config.log_retention_days

  attach_policies          = true
  number_of_policies       = length(local.labmda_default_policies)
  policies                 = local.labmda_default_policies
  attach_policy_statements = true
  policy_statements = {
    sqs = {
      effect    = "Allow",
      actions   = ["sqs:SendMessage", "sqs:GetQueueAttributes"],
      resources = [module.embedding_handler_queue.queue_arn]
    },
    s3 = {
      effect    = "Allow",
      actions   = ["s3:GetObject"],
      resources = ["${module.data_bucket.s3_bucket_arn}/*"]
    },
    secret_manager = {
      effect    = "Allow",
      actions   = ["secretsmanager:GetSecretValue"]
      resources = ["*"]
    },
  }

  allowed_triggers = {
    eventbridge = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.data_ingestion_lambda_trigger.arn
    }
  }

  vpc_subnet_ids         = var.lambda_config.data_ingestion_handler.in_vpc ? module.vpc.private_subnets : []
  vpc_security_group_ids = var.lambda_config.data_ingestion_handler.in_vpc ? [aws_security_group.lambda_security_group.id] : []
  attach_network_policy  = var.lambda_config.data_ingestion_handler.in_vpc
}

data "aws_ecr_repository" "data_embedding_handler_ecr" {
  name = var.lambda_config.data_embedding_handler.name
}

data "aws_ecr_image" "latest_data_embedding_handler_lambda_docker_image" {
  repository_name = data.aws_ecr_repository.data_embedding_handler_ecr.name
  most_recent     = true
}

module "data_embedding_handler_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.10.1"

  function_name              = var.lambda_config.data_embedding_handler.name
  description                = var.lambda_config.data_embedding_handler.description
  image_config_command       = var.lambda_config.data_embedding_handler.image_config_command
  runtime                    = var.lambda_config.data_embedding_handler.runtime
  publish                    = true
  create_lambda_function_url = var.lambda_config.data_embedding_handler.function_url

  timeout                        = var.lambda_config.data_embedding_handler.timeout
  memory_size                    = var.lambda_config.data_embedding_handler.memory_size
  reserved_concurrent_executions = var.lambda_config.data_embedding_handler.reserved_concurrent_executions

  create_package = false
  image_uri      = "${data.aws_ecr_repository.data_embedding_handler_ecr.repository_url}:${data.aws_ecr_image.latest_data_embedding_handler_lambda_docker_image.image_tags[0]}"
  package_type   = var.lambda_config.data_embedding_handler.package_type

  environment_variables = {
    LOG_LEVEL                            = "INFO"
    LOG_SOURCE_EVENT                     = true
    ONNX_MODEL_PATH                      = "model"
    TOKENIZER_PATH                       = "tokenizer"
    POSTGRES_SECRETS_MANAGER_NAME        = module.rds_credentials.secretsmanager_secret_name
    POSTGRES_DB                          = var.rds_config.main_database
    POSTGRES_RAW_PRODUCT_TABLE_NAME      = var.rds_table_config.raw_products.name
    POSTGRES_EMBEDDED_PRODUCT_TABLE_NAME = var.rds_table_config.embedded_products.name
    POSTGRES_FETCH_BATCH_SIZE            = 1000
    POSTGRES_UPSERT_BATCH_SIZE           = 5
    OPENSEARCH_SECRETS_MANAGER_NAME      = module.opensearch_credentials.secretsmanager_secret_name
    OPENSEARCH_INDEX_NAME                = var.opensearch_index_config.index.embedded_products.name
    OPENSEARCH_TIMEOUT                   = var.opensearch_index_config.timeout
    AWS_SQS_SUBSCRIBED_QUEUE_URL         = module.embedding_handler_queue.queue_url
    TZ                                   = "${var.timezone}"
  }


  create_role                       = true
  attach_cloudwatch_logs_policy     = false
  cloudwatch_logs_retention_in_days = var.lambda_config.log_retention_days

  attach_policies    = true
  number_of_policies = length(local.labmda_default_policies)
  policies           = local.labmda_default_policies

  attach_policy_statements = true
  policy_statements = {
    sqs_get = {
      effect = "Allow"
      actions = [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ]
      resources = [
        module.embedding_handler_queue.queue_arn
      ]
    },
    secret_manager = {
      effect    = "Allow",
      actions   = ["secretsmanager:GetSecretValue"]
      resources = ["*"]
    },
  }

  event_source_mapping = {
    sqs = {
      event_source_arn = module.embedding_handler_queue.queue_arn
    }
  }

  vpc_subnet_ids         = var.lambda_config.data_ingestion_handler.in_vpc ? module.vpc.private_subnets : []
  vpc_security_group_ids = var.lambda_config.data_ingestion_handler.in_vpc ? [aws_security_group.lambda_security_group.id] : []
  attach_network_policy  = var.lambda_config.data_ingestion_handler.in_vpc

  depends_on = [
    data.aws_ecr_image.latest_data_embedding_handler_lambda_docker_image,
  ]
}
