output "repository_name" {
  description = "The name of the repository"
  value       = aws_ecr_repository.this.name
}

output "repository_url" {
  description = "The URL of the repository"
  value       = aws_ecr_repository.this.repository_url
}
