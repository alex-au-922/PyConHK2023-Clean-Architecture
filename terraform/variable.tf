variable "timezone" {
  description = "Timezone to use for the resources"
  type        = string
}

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

variable "rds_table_config" {
  description = "Config for the RDS Table"
  type = object({
    raw_products = object({
      name = string
    })
    embedded_products = object({
      name = string
    })
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

variable "opensearch_index_config" {
  description = "Config for the OpenSearch Index"
  type = object({
    index = object({
      embedded_products = object({
        name = string
      })
    })
    timeout = number
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

variable "ecr_config" {
  description = "Config for the ECR"
  type = object({
    data_embedding_handler = object({
      name = string
    })
    query_handler = object({
      name = string
    })
  })
}

variable "s3_config" {
  description = "Config for the S3"
  type = object({
    embedding_model_bucket = object({
      name          = string
      versioning    = bool
      force_destroy = bool
    })
    data_bucket = object({
      name          = string
      versioning    = bool
      force_destroy = bool
    })
    frontend_bucket = object({
      name                = string
      versioning          = bool
      force_destroy       = bool
      block_public_access = bool
    })
  })
}

variable "cloudfront_config" {
  description = "Config for the CloudFront"
  type = object({
    frontend = object({
      name                = string
      description         = string
      aliases             = list(string)
      price_class         = string
      default_ssl_cert    = bool
      retain_on_delete    = bool
      wait_for_deployment = bool
      origin_access_control = object({
        s3 = object({
          origin_type      = string
          signing_enabled  = bool
          signing_protocol = string
        })
      })
      logging_bucket = object({
        name = string
      })
      cache = object({
        allowed_methods        = list(string)
        cached_methods         = list(string)
        viewer_protocol_policy = string
        ttl = object({
          min     = number
          default = number
          max     = number
        })
        compress     = bool
        query_string = bool
      })
      restrictions = object({
        whitelisted_locations = list(string)
      })
    })
  })
}

variable "lambda_config" {
  description = "Config for the Lambda"
  type = object({
    log_retention_days = number
    data_ingestion_handler = object({
      name                           = string
      description                    = string
      memory_size                    = number
      timeout                        = number
      reserved_concurrent_executions = number
      runtime                        = string
      source_path                    = string
      package_type                   = string
      layer_path                     = string
      layer_name                     = string
      handler                        = string
      function_url                   = bool
      in_vpc                         = bool
    })
    data_embedding_handler = object({
      name                           = string
      description                    = string
      memory_size                    = number
      timeout                        = number
      reserved_concurrent_executions = number
      runtime                        = string
      package_type                   = string
      image_config_command           = list(string)
      function_url                   = bool
      in_vpc                         = bool
    })
    query_handler = object({
      name                           = string
      description                    = string
      memory_size                    = number
      timeout                        = number
      reserved_concurrent_executions = number
      runtime                        = string
      package_type                   = string
      image_config_command           = list(string)
      function_url                   = bool
      in_vpc                         = bool
    })
  })
}

variable "sqs_config" {
  description = "Config for the SQS"
  type = object({
    embedding_handler = object({
      name                       = string
      delay_seconds              = number
      message_retention_seconds  = number
      receive_wait_time_seconds  = number
      visibility_timeout_seconds = number
      fifo_queue                 = bool
      redrive_policy = object({
        max_receive_count = number
      })
    })
  })
}

variable "eventbridge_config" {
  description = "Config for the EventBridge"
  type = object({
    data_ingestion_lambda_trigger = object({
      name                = string
      schedule_expression = string
    })
  })
}

variable "api_gateway_config" {
  description = "Config for the API Gateway"
  type = object({
    lambda = object({
      name               = string
      description        = string
      log_retention_days = number
      access_log_format  = map(string),
      routes = object({
        query_handler = object({
          method                 = string
          path_parts             = list(string)
          payload_format_version = string
          timeout                = number
        })
      })
    })
    ecs = object({
      name               = string
      description        = string
      log_retention_days = number
      access_log_format  = map(string),
      routes = object({
        query_handler = object({
          method     = string
          path_parts = list(string)
        })
      })
    })
  })
}

variable "ecs_config" {
  description = "Config for the ECS"
  type = object({
    query_handler = object({
      name = string
      log_group = object({
        retention_days = number
      })
      fargate_capacity_config = object({
        normal_weight = number
        spot_weight   = number
      })
      container = object({
        name                    = string
        cpu                     = number
        memory                  = number
        port                    = number
        filesystem_write_access = bool
        health_check = object({
          healthy_threshold   = number
          unhealthy_threshold = number
          interval            = number
          matcher             = string
          path_parts          = list(string)
        })
        command = list(string)
        autoscaling = object({
          min = number
          max = number
        })
      })
    })
  })
}

variable "sagemaker_config" {
  description = "Config for the SageMaker"
  type = object({
    embedding_model = object({
      name = string
      deployment = object({
        instance_type  = string
        instance_count = number
        instance_variant = object({
          name   = string
          weight = number
        })
      })
      in_vpc = bool
    })
  })
}

variable "ssh_public_key" {
  description = "SSH Public Key, Provided by Pipeline"
  type        = string
}
