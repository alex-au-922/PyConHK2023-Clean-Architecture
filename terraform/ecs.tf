data "aws_ecr_repository" "query_handler_ecr_ecs" {
  name = "${var.ecs_config.query_handler.name}-api-server"
}

data "aws_ecr_image" "latest_query_handler_ecs_docker_image" {
  repository_name = data.aws_ecr_repository.query_handler_ecr_ecs.name
  most_recent     = true
}

resource "aws_security_group" "query_handler" {
  name        = "${var.ecs_config.query_handler.name}-sg"
  description = "Allow TCP inbound traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "TCP from VPC"
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

resource "aws_lb" "query_handler" {
  name               = "${var.ecs_config.query_handler.name}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.query_handler.id]
  subnets            = module.vpc.public_subnets
  idle_timeout       = 300
}

resource "aws_lb_listener" "query_handler" {
  load_balancer_arn = aws_lb.query_handler.arn
  protocol          = "HTTP"
  port              = var.ecs_config.query_handler.container.port
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.query_handler.arn
  }
}

resource "aws_lb_target_group" "query_handler" {
  name        = "${var.ecs_config.query_handler.name}-lb"
  port        = var.ecs_config.query_handler.container.port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = module.vpc.vpc_id
  health_check {
    enabled             = true
    healthy_threshold   = var.ecs_config.query_handler.container.health_check.healthy_threshold
    unhealthy_threshold = var.ecs_config.query_handler.container.health_check.unhealthy_threshold
    interval            = var.ecs_config.query_handler.container.health_check.interval
    protocol            = "HTTP"
    matcher             = var.ecs_config.query_handler.container.health_check.matcher
    path                = format("/%s", join("/", var.ecs_config.query_handler.container.health_check.path_parts))
  }
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

          environment = [
            {
              name  = "LOG_LEVEL",
              value = "INFO"
            },
            {
              name  = "ONNX_MODEL_PATH",
              value = "model"
            },
            {
              name  = "TOKENIZER_PATH",
              value = "tokenizer"
            },
            {
              name  = "POSTGRES_SECRETS_MANAGER_NAME",
              value = module.rds_credentials.secretsmanager_secret_name
            },
            {
              name  = "POSTGRES_DB",
              value = var.rds_config.main_database
            },
            {
              name  = "POSTGRES_RAW_PRODUCT_TABLE_NAME",
              value = var.rds_table_config.raw_products.name
            },
            {
              name  = "POSTGRES_EMBEDDED_PRODUCT_TABLE_NAME",
              value = var.rds_table_config.embedded_products.name
            },
            {
              name  = "POSTGRES_FETCH_BATCH_SIZE",
              value = "1000"
            },
            {
              name  = "POSTGRES_UPSERT_BATCH_SIZE",
              value = "5"
            },
            {
              name  = "OPENSEARCH_SECRETS_MANAGER_NAME",
              value = module.opensearch_credentials.secretsmanager_secret_name
            },
            {
              name  = "OPENSEARCH_INDEX_NAME",
              value = var.opensearch_index_config.index.embedded_products.name
            },
            {
              name  = "OPENSEARCH_TIMEOUT",
              value = var.opensearch_index_config.timeout
            },
            {
              name  = "AWS_SQS_SUBSCRIBED_QUEUE_URL",
              value = module.embedding_handler_queue.queue_url
            },
            {
              name  = "SEARCH_DEFAULT_LIMIT",
              value = "10"
            },
            {
              name  = "SEARCH_DEFAULT_THRESHOLD",
              value = "0.3"
            },
            {
              name  = "TRANSFORMERS_CACHE",
              value = "/tmp"
            },
            {
              name  = "TZ",
              value = "${var.timezone}"
            }
          ]

          # Example image used requires access to write to root filesystem
          readonly_root_filesystem = !var.ecs_config.query_handler.container.filesystem_write_access

          enable_cloudwatch_logging = true
          memory_reservation        = 100
        }
      }

      load_balancer = {
        service = {
          target_group_arn = aws_lb_target_group.query_handler.arn
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
