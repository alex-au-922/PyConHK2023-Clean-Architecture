variable "backend_s3_config" {
    description = "Config for the backend s3 bucket for storing terraform states"
    type = object({
      bucket = string
      key = string
    })
}

variable "developer_config" {
    description = "Provide by CI/CD Pipeline"
    type = object({
      developer = string
      contact = string
    })
}

variable "aws_assume_role_arn" {
    description = "Provide by CI/CD Pipeline"
    type = string
}