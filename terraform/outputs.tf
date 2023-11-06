output "api_gateway_lambda_endpoint" {
  value = module.api_gateway_lambda.apigatewayv2_api_api_endpoint
}

output "api_gateway_ecs_endpoint" {
  value = module.api_gateway_ecs.apigatewayv2_api_api_endpoint
}