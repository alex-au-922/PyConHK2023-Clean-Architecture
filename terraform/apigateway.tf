resource "aws_cloudwatch_log_group" "api_gateway_lambda_logs" {
  name              = "/aws/api-gateway/${var.api_gateway_config.lambda.name}"
  retention_in_days = var.api_gateway_config.lambda.log_retention_days
}

module "api_gateway_lambda" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = var.api_gateway_config.lambda.name
  description   = var.api_gateway_config.lambda.description
  protocol_type = "HTTP"

  create_api_domain_name = false

  cors_configuration = {
    allow_headers = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_origins = ["*"]
  }

  # Access logs
  default_stage_access_log_destination_arn = aws_cloudwatch_log_group.api_gateway_lambda_logs.arn
  default_stage_access_log_format          = jsonencode(var.api_gateway_config.lambda.access_log_format)

  # Routes and integrations
  integrations = {
    "${var.api_gateway_config.lambda.routes.query_handler.method} ${format("/%s", join("/", var.api_gateway_config.lambda.routes.query_handler.path_parts))}" = {
      lambda_arn             = module.query_handler_lambda.lambda_function_arn
      payload_format_version = var.api_gateway_config.lambda.routes.query_handler.payload_format_version
      timeout_milliseconds   = var.api_gateway_config.lambda.routes.query_handler.timeout * 1000
    }
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_ecs_logs" {
  name              = "/aws/api-gateway/${var.api_gateway_config.ecs.name}"
  retention_in_days = var.api_gateway_config.ecs.log_retention_days
}


module "api_gateway_ecs" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = var.api_gateway_config.ecs.name
  description   = var.api_gateway_config.ecs.description
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_origins = ["*"]
  }

  create_api_domain_name = false

  # Access logs
  default_stage_access_log_destination_arn = aws_cloudwatch_log_group.api_gateway_ecs_logs.arn
  default_stage_access_log_format          = jsonencode(var.api_gateway_config.ecs.access_log_format)

  integrations = {
    "${var.api_gateway_config.ecs.routes.query_handler.method} ${format("/%s/", join("/", var.api_gateway_config.ecs.routes.query_handler.path_parts))}" = {
      connection_type    = "VPC_LINK"
      vpc_link           = "ecs"
      integration_uri    = aws_lb_listener.query_handler.arn
      integration_type   = "HTTP_PROXY"
      integration_method = "ANY"
    }
  }

  vpc_links = {
    ecs = {
      name               = "${var.api_gateway_config.ecs.name}-vpc-link"
      security_group_ids = [module.api_gateway_ecs_security_group.security_group_id]
      subnet_ids         = module.vpc.private_subnets
    }
  }
}

module "api_gateway_ecs_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${var.api_gateway_config.ecs.name}-sg"
  description = "API Gateway security group for ECS"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["http-80-tcp"]

  egress_rules = ["all-all"]
}
