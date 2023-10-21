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
  instance = [
    {
      name  = "pyconhk2023-main"
      class = "db.t4g.medium"
    }
  ],
  engine = {
    name    = "aurora-postgresql",
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
  publicly_accessible = true
}
