module "rds_credentials" {
  source      = "./modules/secretsmanager"
  name        = "rds_credentials"
  description = "RDS credentials"
  secret_string = jsonencode(
    {
      "username" : "${module.db.cluster_master_username}",
      "password" : "${module.db.cluster_master_password}",
      "engine" : "${var.rds_config.engine.name}",
      "host" : "${module.db.cluster_endpoint}",
      "port" : "${module.db.cluster_port}",
      "dbClusterIdentifier" : "${module.db.cluster_id}"
    }
  )
  recovery_window_in_days = 0
}
