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
  parameters = [{
    name         = "client_encoding"
    value        = "utf8"
    apply_method = "immediate"
  }]
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
    name          = "pyconhk2023-data-embedding-handler"
    image_mutable = false
    force_delete  = true
    scan_on_push  = true
    keep_images   = 5
  }
  query_handler = {
    name          = "pyconhk2023-query-handler"
    image_mutable = false
    force_delete  = true
    scan_on_push  = true
    keep_images   = 5
  }
}

s3_config = {
  model_bucket = {
    name          = "alexau-pyconhk2023-models"
    versioning    = false
    force_destroy = true

  }
  data_bucket = {
    name          = "alexau-pyconhk2023-data"
    versioning    = false
    force_destroy = true
  }
}

lambda_config = {
  log_retention_days = 30
  data_ingestion_handler = {
    name         = "pyconhk2023-data-ingestion-handler"
    description  = "Data ingestion handler for PyCon HK 2023"
    memory_size  = 128
    timeout      = 60
    runtime      = "python3.10"
    source_path  = "backend/data_ingestion_handler/src"
    package_type = "Zip"
    layer_name   = "pyconhk2023-data-ingestion-handler-layer"
    handler      = "app.handler"
    function_url = false
    in_vpc       = true
  }
  data_embedding_handler = {
    name                 = "pyconhk2023-data-embedding-handler"
    description          = "Data ingestion handler for PyCon HK 2023"
    memory_size          = 128
    timeout              = 60
    runtime              = "python3.10"
    package_type         = "Image"
    image_config_command = ["app.handler"]
    function_url         = false
    in_vpc               = true
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
