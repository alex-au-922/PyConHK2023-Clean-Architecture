output "secretsmanager_secret_arn" {
  description = "The ARN of the secret"
  value       = aws_secretsmanager_secret.this.arn
}

output "secretsmanager_secret_version_id" {
  description = "The ID of the secret version"
  value       = aws_secretsmanager_secret_version.this.id
}
