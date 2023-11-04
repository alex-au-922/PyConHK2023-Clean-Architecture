resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/api-gateway/${var.api_gateway_config.name}"
  retention_in_days = var.api_gateway_config.log_retention_days
}

module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = var.api_gateway_config.name
  description   = "API Gateway for PyCon HK 2023"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = var.api_gateway_config.cors.allow_headers
    allow_methods = var.api_gateway_config.cors.allow_methods
    allow_origins = var.api_gateway_config.cors.allow_origins
  }

  # Access logs
  default_stage_access_log_destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
  default_stage_access_log_format          = jsonencode(var.api_gateway_config.access_log_format)

  # Routes and integrations
  integrations = {
    "${var.api_gateway_config.routes.query_handler.method} ${format("/%s", join("/", var.api_gateway_config.routes.query_handler.path_parts))}" = {
      lambda_arn             = module.query_handler_lambda.lambda_function_arn
      payload_format_version = var.api_gateway_config.routes.query_handler.payload_format_version
      timeout_milliseconds   = var.api_gateway_config.routes.query_handler.timeout * 1000
    }
  }
}
