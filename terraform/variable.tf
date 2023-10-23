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

variable "opensearch_config" {
  description = "Config for the OpenSearch"
  type = object({
    version                   = string
    domain_name               = string
    main_username             = string
    main_user_password_length = number
    instance = object({
      type  = string
      count = number
    })
    master_node = object({
      type  = string
      count = number
    })
    ebs = object({
      volume_size = number
      throughput  = number
      volume_type = string
    })
    publicly_accessible = bool
  })
}

variable "allowed_cidrs_string" {
  description = "List of CIDRs to allow access to the resources, provided by Pipeline"
  type        = string
}

variable "bastion_host_config" {
  description = "Config for the Bastion Host"
  type = object({
    name          = string
    instance_type = string
    key_name      = string
    ami_filter = object({
      name                = string
      owners              = list(string)
      virtualization_type = string
    })
  })
}
