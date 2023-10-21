locals {
  allowed_cidrs = [var.allowed_cidr]
}

resource "random_password" "db_master_password" {
  length           = var.rds_config.main_user_password_length
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}


module "db" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name           = var.rds_config.main_database
  engine         = var.rds_config.engine.name
  engine_version = var.rds_config.engine.version
  instance_class = var.rds_config.instance_class
  instances = {
    for v in var.rds_config.instance : v.name => {
      instance_class = v.class
    }
  }

  vpc_id             = data.aws_vpc.vpc.id
  availability_zones = data.aws_availability_zones.available.names

  #! Normally we would use the private subnets, but as I'm not in an enterprise environment,
  #! I'm using the public subnets for simplicity.
  subnets                = var.rds_config.publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets
  create_db_subnet_group = true
  security_group_rules = {
    ct_access = {
      description = "Postgres"
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = local.allowed_cidrs
    }
    lambda_access = {
      description = "Postgres"
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [data.aws_vpc.vpc.cidr_block]
    }
  }

  master_username = var.rds_config.main_username
  master_password = random_password.db_master_password.result
  database_name   = var.rds_config.main_database

  skip_final_snapshot                   = var.rds_config.skip_final_snapshot
  publicly_accessible                   = var.rds_config.publicly_accessible
  performance_insights_enabled          = var.rds_config.performance_insights.enabled
  performance_insights_retention_period = var.rds_config.performance_insights.retention_period
  create_monitoring_role                = var.rds_config.monitoring_interval > 0
  monitoring_interval                   = var.rds_config.monitoring_interval

  storage_encrypted = true
  apply_immediately = true

  create_cloudwatch_log_group     = length(var.rds_config.cloudwatch_logs_exports) > 0
  enabled_cloudwatch_logs_exports = var.rds_config.cloudwatch_logs_exports

  preferred_backup_window      = var.rds_config.windows.backup
  preferred_maintenance_window = var.rds_config.windows.maintenance
  backup_retention_period      = var.rds_config.backup_retention_period

  create_db_cluster_parameter_group     = length(var.rds_config.parameters) > 0
  db_cluster_parameter_group_name       = "${var.rds_config.main_database}-db-cluster-parameter-group"
  db_cluster_parameter_group_family     = "${var.rds_config.engine.name}${var.rds_config.engine.version}"
  db_cluster_parameter_group_parameters = var.rds_config.parameters

  manage_master_user_password = false
}
