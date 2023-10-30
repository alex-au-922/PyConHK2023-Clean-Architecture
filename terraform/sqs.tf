module "embedding_handler_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "4.0.1"

  name                       = var.sqs_config.embedding_handler.name
  visibility_timeout_seconds = var.sqs_config.embedding_handler.visibility_timeout_seconds
  delay_seconds              = var.sqs_config.embedding_handler.delay_seconds
  message_retention_seconds  = var.sqs_config.embedding_handler.message_retention_seconds
  receive_wait_time_seconds  = var.sqs_config.embedding_handler.receive_wait_time_seconds
  fifo_queue                 = var.sqs_config.embedding_handler.fifo_queue

  create_dlq = true
  redrive_policy = {
    maxReceiveCount = var.sqs_config.embedding_handler.redrive_policy.max_receive_count
  }

  create_queue_policy = true
  queue_policy_statements = {
    sns = {
      sid     = "DataIngestionLambdaPublish"
      effect  = "Allow"
      actions = ["SQS:SendMessage"]

      principals = [
        {
          type        = "Service"
          identifiers = ["lambda.amazonaws.com"]
        }
      ]

      conditions = [
        {
          test     = "ArnEquals"
          variable = "aws:SourceArn"
          values   = [module.data_ingestion_handler_lambda.lambda_function_arn]
        }
      ]
    }
    # lambda = {
    #   sid     = "DataEmbeddingLambdaConsume"
    #   effect  = "Allow"
    #   actions = ["SQS:ReceiveMessage", "SQS:DeleteMessage", "SQS:GetQueueAttributes"]
    #   principals = [
    #     {
    #       type        = "Service"
    #       identifiers = ["lambda.amazonaws.com"]
    #     }
    #   ]
    #   conditions = [
    #     {
    #       test     = "ArnEquals"
    #       variable = "aws:SourceArn"
    #       values   = [module.data_embedding_handler_lambda.lambda_function_arn]
    #     }
    #   ]
    # }
  }
}
