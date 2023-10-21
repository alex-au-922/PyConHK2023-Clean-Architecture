locals {
  tags = {
    developer = var.developer_config.developer
    contact   = var.developer_config.contact
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = data.aws_region.current
  assume_role {
    role_arn = var.aws_assume_role_arn
  }
  default_tags {
    tags = local.tags
  }
}
