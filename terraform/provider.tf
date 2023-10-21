locals {
  tags = {
    developer = "alexau"
    contact   = "alexuau922@gmail.com"
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
  default_tags {
    tags = local.tags
  }
}
