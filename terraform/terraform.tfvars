timezone = "Asia/Hong_Kong"

vpc_config = {
  name       = "pyconhk2023"
  cidr_block = "10.0.0.0/16"
  private_subnets = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ],
  public_subnets = [
    "10.0.101.0/24",
    "10.0.102.0/24",
    "10.0.103.0/24",
  ]
}

rds_config = {
  main_username             = "alexau_pyconhk2023",
  main_user_password_length = 16,
  main_database             = "pyconhk2023",
  instance = {
    name  = "pyconhk2023-main"
    class = "db.t4g.micro"
  },
  engine = {
    name    = "postgres",
    version = "15",
  },
  multi_az = true
  allocated_storage = {
    initial = 10,
    max     = 100,
  },
  backup_retention_period = 7,
  parameters = [
    {
      name         = "client_encoding"
      value        = "utf8"
      apply_method = "immediate"
    },
    {
      name         = "rds.force_ssl"
      value        = "0"
      apply_method = "immediate"
    }
  ]
  performance_insights = {
    enabled          = true
    retention_period = 7
  }
  cloudwatch_logs_exports = ["postgresql"]
  windows = {
    maintenance = "Sat:10:00-Sat:12:00"
    backup      = "12:00-14:00"
  }
  monitoring_interval = 60
  skip_final_snapshot = true
  publicly_accessible = false
}

rds_table_config = {
  raw_products = {
    name = "raw_products"
  }
  embedded_products = {
    name = "embedded_products"
  }
}

opensearch_config = {
  version     = "OpenSearch_2.9"
  domain_name = "pyconhk2023"
  instance = {
    count = 1
    type  = "t3.small.search"
  }
  master_node = {
    count = 0
    type  = "t3.small.search"
  }
  main_username             = "alexau_pyconhk2023"
  main_user_password_length = 16
  ebs = {
    volume_type = "gp3"
    volume_size = 30
    throughput  = 125
  }
  publicly_accessible = false
}

opensearch_index_config = {
  index = {
    embedded_products = {
      name = "embedded_products"
    }
  }
  timeout = 30
}

bastion_host_config = {
  ami_filter = {
    name                = "al2023-ami-2023.2.20231016.0-kernel-6.1-arm64"
    virtualization_type = "hvm"
    owners              = ["amazon"]
  }
  name          = "pyconhk2023-bastion"
  instance_type = "t4g.nano"
  key_name      = "alexau_pyconhk2023_bastion"
}

ecr_config = {
  data_embedding_handler = {
    name = "pyconhk2023-data-embedding-handler"
  }
  query_handler = {
    name = "pyconhk2023-query-handler"
  }
}

s3_config = {
  embedding_model_bucket = {
    name          = "alexau-pyconhk2023-models"
    versioning    = false
    force_destroy = true

  }
  data_bucket = {
    name          = "alexau-pyconhk2023-data"
    versioning    = false
    force_destroy = true
  }
  frontend_bucket = {
    name                = "alexau-pyconhk2023-frontend"
    versioning          = true
    force_destroy       = true
    block_public_access = true
  }
}

cloudfront_config = {
  frontend = {
    name                = "pyconhk2023-frontend"
    aliases             = ["pyconhk2023.alexau.dev"]
    description         = "PyCon HK 2023 Frontend"
    price_class         = "PriceClass_All"
    default_ssl_cert    = true
    retain_on_delete    = false
    wait_for_deployment = false
    origin_access_control = {
      s3 = {
        origin_type      = "s3"
        signing_enabled  = true
        signing_protocol = "sigv4"
      }
    }
    logging_bucket = {
      name = "alexau-pyconhk2023-frontend-cloudfront-logs"
    }
    cache = {
      ttl = {
        min     = 0
        default = 600   # 10 minutes
        max     = 86400 # 1 day
      }
      viewer_protocol_policy = "redirect-to-https"
      allowed_methods        = ["GET", "HEAD", "OPTIONS"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true
      query_string           = true
    }
    restrictions = {
      whitelisted_locations = ["HK"]
    }
  }
}

lambda_config = {
  log_retention_days = 30
  data_ingestion_handler = {
    name                           = "pyconhk2023-data-ingestion-handler"
    description                    = "Data ingestion handler for PyCon HK 2023"
    memory_size                    = 128
    timeout                        = 60 # 1 minute
    reserved_concurrent_executions = -1
    runtime                        = "python3.10"
    source_path                    = "../backend/data_ingestion_handler/src/"
    package_type                   = "Zip"
    layer_path                     = "../backend/data_ingestion_handler/"
    layer_name                     = "pyconhk2023-data-ingestion-handler-layer"
    handler                        = "deployments.lambda.app.handler"
    function_url                   = true
    in_vpc                         = true
  }
  data_embedding_handler = {
    name                           = "pyconhk2023-data-embedding-handler"
    description                    = "Data Embedding handler for PyCon HK 2023"
    memory_size                    = 2048
    timeout                        = 5 * 60 # 5 minutes
    reserved_concurrent_executions = -1
    runtime                        = "python3.10"
    package_type                   = "Image"
    image_config_command           = ["deployments.lambda.app.handler"]
    function_url                   = false
    in_vpc                         = true
  }
  query_handler = {
    name                           = "pyconhk2023-query-handler"
    description                    = "Query handler for PyCon HK 2023"
    memory_size                    = 2048
    timeout                        = 5 * 60 # 5 minutes
    reserved_concurrent_executions = -1
    runtime                        = "python3.10"
    package_type                   = "Image"
    image_config_command           = ["deployments.lambda.app.handler"]
    function_url                   = false
    in_vpc                         = true
  }
}


sqs_config = {
  embedding_handler = {
    name                       = "pyconhk2023-embedding-handler-queue"
    delay_seconds              = 0
    message_retention_seconds  = 1209600 # 14 days
    receive_wait_time_seconds  = 0
    visibility_timeout_seconds = 5 * 60 # 5 minutes
    fifo_queue                 = false
    redrive_policy = {
      max_receive_count = 5
    }
  }
}

eventbridge_config = {
  data_ingestion_lambda_trigger = {
    name                = "pyconhk2023-data-ingestion-lambda-trigger"
    schedule_expression = "cron(0 * * * ? *)" # Every hour
  }
}

api_gateway_config = {
  name               = "pyconhk2023-api-gateway"
  log_retention_days = 30
  cors = {
    allow_origins = ["*"]
    allow_headers = ["*"]
    allow_methods = ["*"]
  }
  access_log_format = {
    "requestId" : "$context.requestId",
    "extendedRequestId" : "$context.extendedRequestId",
    "ip" : "$context.identity.sourceIp",
    "caller" : "$context.identity.caller",
    "user" : "$context.identity.user",
    "requestTime" : "$context.requestTime",
    "httpMethod" : "$context.httpMethod",
    "resourcePath" : "$context.resourcePath",
    "status" : "$context.status",
    "protocol" : "$context.protocol",
    "responseLength" : "$context.responseLength",
    "integrationError" : "$context.integrationErrorMessage"
  },

  routes = {
    query_handler = {
      method                 = "POST"
      path_parts             = ["api", "similar_products"]
      payload_format_version = "2.0"
      timeout                = 29
    }
  }
}

ecs_config = {
  query_handler = {
    name = "pyconhk2023-query-handler"
    log_group = {
      retention_days = 30
    }
    fargate_capacity_config = {
      normal_weight = 50
      spot_weight   = 50
    }
    container = {
      name                    = "pyconhk2023-ecs-query-handler"
      cpu                     = 1024
      memory                  = 2048
      port                    = 80
      filesystem_write_access = true
      health_check = {
        healthy_threshold   = 3
        unhealthy_threshold = 3
        interval            = 30
        matcher             = "200"
        path_parts          = ["api", "health_status"]
      }
      command = [
        "python",
        "-m",
        "uvicorn",
        "deployments.api_fastapi.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "80",
      ]
      autoscaling = {
        min = 1
        max = 2
      }
    }
  }
}

sagemaker_config = {
  embedding_model = {
    name = "pyconhk2023-embedding-model"
    deployment = {
      instance_type  = "m5.xlarge"
      instance_count = 1
      instance_variant = {
        weight = 1
        name   = "main"
      }
    }
    in_vpc = true
  }
}
