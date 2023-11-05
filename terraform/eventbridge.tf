resource "aws_cloudwatch_event_rule" "data_ingestion_lambda_trigger" {
  name                = var.eventbridge_config.data_ingestion_lambda_trigger.name
  schedule_expression = var.eventbridge_config.data_ingestion_lambda_trigger.schedule_expression
}

resource "aws_cloudwatch_event_target" "data_ingestion_lambda" {
  rule      = aws_cloudwatch_event_rule.data_ingestion_lambda_trigger.name
  target_id = "SendToLambda"
  arn       = module.data_ingestion_handler_lambda.lambda_function_arn
}
