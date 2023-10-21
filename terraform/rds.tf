locals {
  allowed_cidrs = split(",", var.allowed_cidrs_string)
}

resource "random_password" "db_master_password" {
  length           = var.rds_config.main_user_password_length
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# module "db" {
#   source = "terraform-aws-modules/rds-aurora/aws"

#   name           = var.rds_config.main_database
#   engine         = var.rds_config.engine.name
#   engine_version = var.rds_config.engine.version
#   instances = {
#     for v in var.rds_config.instance : v.name => {
#       identifier     = v.name
#       instance_class = v.class
#     }
#   }

#   vpc_id             = module.vpc.vpc_id
#   availability_zones = data.aws_availability_zones.available.names

#   #! Normally we would use the private subnets, but as I'm not in an enterprise environment,
#   #! I'm using the public subnets for simplicity.
#   subnets                = var.rds_config.publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets
#   create_db_subnet_group = true
#   security_group_rules = {
#     ct_access = {
#       description = "Postgres"
#       from_port   = 5432
#       to_port     = 5432
#       protocol    = "tcp"
#       cidr_blocks = local.allowed_cidrs
#     }
#     lambda_access = {
#       description = "Postgres"
#       from_port   = 5432
#       to_port     = 5432
#       protocol    = "tcp"
#       cidr_blocks = concat([module.vpc.vpc_cidr_block], module.vpc.vpc_secondary_cidr_blocks)
#     }
#   }

#   master_username = var.rds_config.main_username
#   master_password = random_password.db_master_password.result
#   database_name   = var.rds_config.main_database

#   skip_final_snapshot                   = var.rds_config.skip_final_snapshot
#   publicly_accessible                   = var.rds_config.publicly_accessible
#   performance_insights_enabled          = var.rds_config.performance_insights.enabled
#   performance_insights_retention_period = var.rds_config.performance_insights.retention_period
#   create_monitoring_role                = var.rds_config.monitoring_interval > 0
#   monitoring_interval                   = var.rds_config.monitoring_interval

#   storage_encrypted = true
#   apply_immediately = true

#   create_cloudwatch_log_group     = length(var.rds_config.cloudwatch_logs_exports) > 0
#   enabled_cloudwatch_logs_exports = var.rds_config.cloudwatch_logs_exports

#   preferred_backup_window      = var.rds_config.windows.backup
#   preferred_maintenance_window = var.rds_config.windows.maintenance
#   backup_retention_period      = var.rds_config.backup_retention_period

#   create_db_cluster_parameter_group     = length(var.rds_config.parameters) > 0
#   db_cluster_parameter_group_name       = "${var.rds_config.main_database}-db-cluster-parameter-group"
#   db_cluster_parameter_group_family     = "${var.rds_config.engine.name}${var.rds_config.engine.version}"
#   db_cluster_parameter_group_parameters = var.rds_config.parameters

#   manage_master_user_password = false
# }


resource "aws_security_group" "db_rds_security_group" {
  name        = "${var.rds_config.main_database}-rds-security-group"
  description = "Security group for RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Home access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = local.allowed_cidrs
  }

  ingress {
    description = "VPC access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = concat([module.vpc.vpc_cidr_block], module.vpc.vpc_secondary_cidr_blocks)
  }
}

resource "aws_db_subnet_group" "postgresql_subnet_group" {
  name       = "${var.rds_config.main_database}-db-subnet-group"
  subnet_ids = var.rds_config.publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets
}


module "db" {
  source = "terraform-aws-modules/rds/aws"

  multi_az = true


  identifier = var.rds_config.main_database

  engine               = var.rds_config.engine.name
  engine_version       = var.rds_config.engine.version
  family               = "${var.rds_config.engine.name}${var.rds_config.engine.version}"
  major_engine_version = var.rds_config.engine.version
  instance_class       = var.rds_config.instance.class

  allocated_storage     = var.rds_config.allocated_storage.initial
  max_allocated_storage = var.rds_config.allocated_storage.max


  db_name  = var.rds_config.main_database
  username = var.rds_config.main_username
  password = random_password.db_master_password.result
  port     = 5432

  skip_final_snapshot = var.rds_config.skip_final_snapshot

  storage_encrypted = true
  apply_immediately = true

  vpc_security_group_ids = [aws_security_group.db_rds_security_group.id]

  maintenance_window = var.rds_config.windows.maintenance
  backup_window      = var.rds_config.windows.backup

  performance_insights_enabled          = var.rds_config.performance_insights.enabled
  performance_insights_retention_period = var.rds_config.performance_insights.retention_period
  create_monitoring_role                = var.rds_config.monitoring_interval > 0
  monitoring_interval                   = var.rds_config.monitoring_interval
  monitoring_role_name                  = "${var.rds_config.main_database}-monitoring-role"
  monitoring_role_use_name_prefix       = true
  monitoring_role_description           = "Monitoring role for ${var.rds_config.main_database}"

  parameters = var.rds_config.parameters

  db_subnet_group_name = aws_db_subnet_group.postgresql_subnet_group.name
  # DB subnet group
  subnet_ids          = var.rds_config.publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets
  publicly_accessible = var.rds_config.publicly_accessible

  manage_master_user_password = random_password.db_master_password.result == ""
}
