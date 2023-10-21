variable "vpc_config" {
  description = "Config for the VPC"
  type = object({
    name            = string
    cidr_block      = string
    private_subnets = list(string)
    public_subnets  = list(string)
  })
}

variable "rds_config" {
  description = "Config for the RDS"
  type = object({
    main_username             = string
    main_user_password_length = number
    main_database             = string
    instance = object({
      name  = string
      class = string
    })
    engine = object({
      name    = string
      version = string
    })
    multi_az = bool
    allocated_storage = object({
      initial = number
      max     = number
    })
    backup_retention_period = number
    parameters = list(object({
      name         = string
      value        = string
      apply_method = string
    }))
    performance_insights = object({
      enabled          = bool
      retention_period = number
    })
    cloudwatch_logs_exports = list(string)
    windows = object({
      maintenance = string
      backup      = string
    })
    monitoring_interval = number
    skip_final_snapshot = bool
    publicly_accessible = bool
  })
}

variable "allowed_cidrs_string" {
  description = "List of CIDRs to allow access to the resources, provided by Pipeline"
  type        = string
}
