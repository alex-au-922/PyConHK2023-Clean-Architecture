module "rds_credentials" {
  source      = "./modules/secretsmanager"
  name        = "${var.rds_config.main_database}_rds_credentials"
  description = "RDS credentials"
  secret_string = jsonencode(
    {
      "username" : "${module.db.db_instance_username}",
      "password" : "${random_password.db_master_password.result}",
      "engine" : "${var.rds_config.engine.name}",
      "host" : "${module.db.db_instance_address}",
      "port" : "${module.db.db_instance_port}",
      "readerHost" : "${module.db_replica.db_instance_address}",
      "readerPort" : "${module.db_replica.db_instance_port}",
    }
  )
  recovery_window_in_days = 0
}

module "opensearch_credentials" {
  source      = "./modules/secretsmanager"
  name        = "${var.opensearch_config.domain_name}_opensearch_credentials"
  description = "Opensearch credentials"
  secret_string = jsonencode(
    {
      "domain_name" : "${aws_opensearch_domain.opensearch.domain_name}",
      "endpoint" : "https://${aws_opensearch_domain.opensearch.endpoint}",
      "username" : "${var.opensearch_config.main_username}",
      "password" : "${random_password.opensearch_master_password.result}"
    }
  )
  recovery_window_in_days = 0
}
