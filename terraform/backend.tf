terraform {
  backend "s3" {
    bucket = var.backend_s3_config.bucket
    key    = var.backend_s3_config.key
    region = data.aws_region.current.name
  }
}