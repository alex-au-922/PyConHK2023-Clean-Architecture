# module "rds_credentials" {
#   source      = "./modules/secretsmanager"
#   name        = "rds_credentials"
#   description = "RDS credentials"
#   secret_string = jsonencode(
#     {
#       "username" : "${module.db.db_instance_username}",
#       "password" : "${random_password.db_master_password.result}",
#       "engine" : "${var.rds_config.engine.name}",
#       "host" : "${module.db.db_instance_address}",
#       "port" : "${module.db.db_instance_port}",
#       "dbInstanceIdentifier" : "${module.db.db_instance_identifier}"
#     }
#   )
#   recovery_window_in_days = 0
# }
