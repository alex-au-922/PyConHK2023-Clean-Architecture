variable "developer_config" {
  description = "Provide by CI/CD Pipeline"
  type = object({
    developer = string
    contact   = string
  })
}

variable "vpc_config" {
  description = "Config for the VPC"
  type = object({
    name            = string
    cidr            = string
    private_subnets = list(string)
    public_subnets  = list(string)
  })
}
