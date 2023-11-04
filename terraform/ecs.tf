data "aws_ecr_repository" "query_handler_ecr_ecs" {
  name = "${var.ecs_config.query_handler.name}-api-server"
}

data "aws_ecr_image" "latest_query_handler_ecs_docker_image" {
  repository_name = data.aws_ecr_repository.query_handler_ecr_ecs.name
  most_recent     = true
}

resource "aws_security_group" "query_handler" {
  name        = "${var.ecs_config.query_handler.name}-sg"
  description = "Allow TCP traffic on ${var.ecs_config.query_handler.container.port} from VPC"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow TCP traffic on ${var.ecs_config.query_handler.container.port} from VPC"
    from_port   = var.ecs_config.query_handler.container.port
    to_port     = var.ecs_config.query_handler.container.port
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

module "query_handler_alb" {
  source = "terraform-aws-modules/alb/aws"

  name = "${var.ecs_config.query_handler.name}-alb"

  load_balancer_type = "application"

  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.query_handler.id]

  access_logs = {
    bucket = "${var.ecs_config.query_handler.name}-alb"
  }

  target_groups = [
    {
      name_prefix      = "query-handler-"
      backend_protocol = "HTTP"
      backend_port     = var.ecs_config.query_handler.container.port
      target_type      = "instance"
    }
  ]

  #   http_tcp_listeners = [
  #     {
  #       port               = var.ecs_config.query_handler.container.port
  #       protocol           = "HTTP"
  #       target_group_index = 0
  #     }
  #   ]
}

module "query_handler" {
  source = "terraform-aws-modules/ecs/aws"

  cluster_name = var.ecs_config.query_handler.name

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = var.ecs_config.query_handler.log_group.retention_days
      }
    }
  }

  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = var.ecs_config.query_handler.fargate_capacity_config.normal_weight
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = var.ecs_config.query_handler.fargate_capacity_config.spot_weight
      }
    }
  }

  services = {
    query_handler = {
      cpu                      = var.ecs_config.query_handler.container.cpu
      memory                   = var.ecs_config.query_handler.container.memory
      autoscaling_min_capacity = var.ecs_config.query_handler.container.autoscaling.min
      autoscaling_max_capacity = var.ecs_config.query_handler.container.autoscaling.max

      # Container definition(s)
      container_definitions = {

        (var.ecs_config.query_handler.container.name) = {
          cpu       = var.ecs_config.query_handler.container.cpu
          memory    = var.ecs_config.query_handler.container.memory
          essential = true
          image     = "${data.aws_ecr_repository.query_handler_ecr_ecs.repository_url}:${data.aws_ecr_image.latest_query_handler_ecs_docker_image.image_tags[0]}"
          port_mappings = [
            {
              name          = "http"
              containerPort = var.ecs_config.query_handler.container.port
              protocol      = "tcp"
            }
          ]

          environment = {
            LOG_LEVEL                            = "INFO"
            ONNX_MODEL_PATH                      = "model"
            TOKENIZER_PATH                       = "tokenizer"
            POSTGRES_SECRETS_MANAGER_NAME        = module.rds_credentials.secretsmanager_secret_name
            POSTGRES_DB                          = var.rds_config.main_database
            POSTGRES_RAW_PRODUCT_TABLE_NAME      = var.rds_table_config.raw_products.name
            POSTGRES_EMBEDDED_PRODUCT_TABLE_NAME = var.rds_table_config.embedded_products.name
            POSTGRES_FETCH_BATCH_SIZE            = 1000
            POSTGRES_UPSERT_BATCH_SIZE           = 5
            OPENSEARCH_SECRETS_MANAGER_NAME      = module.opensearch_credentials.secretsmanager_secret_name
            OPENSEARCH_INDEX_NAME                = var.opensearch_index_config.index.embedded_products.name
            OPENSEARCH_TIMEOUT                   = var.opensearch_index_config.timeout
            AWS_SQS_SUBSCRIBED_QUEUE_URL         = module.embedding_handler_queue.queue_url
            SEARCH_DEFAULT_LIMIT                 = 10
            SEARCH_DEFAULT_THRESHOLD             = 0.3
            TRANSFORMERS_CACHE                   = "/tmp"
            TZ                                   = "${var.timezone}"
          }

          # Example image used requires access to write to root filesystem
          readonly_root_filesystem = !var.ecs_config.query_handler.container.filesystem_write_access

          enable_cloudwatch_logging = true
          memory_reservation        = 100
        }
      }

      load_balancer = {
        service = {
          target_group_arn = module.query_handler_alb.target_group_arns[0]
          container_name   = var.ecs_config.query_handler.container.name
          container_port   = var.ecs_config.query_handler.container.port
        }
      }

      subnet_ids = module.vpc.private_subnets
      security_group_rules = {
        alb_ingress = {
          type        = "ingress"
          from_port   = var.ecs_config.query_handler.container.port
          to_port     = var.ecs_config.query_handler.container.port
          protocol    = "tcp"
          cidr_blocks = [module.vpc.vpc_cidr_block]
        }
        egress_all = {
          type        = "egress"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
        }
      }
    }
  }
}
