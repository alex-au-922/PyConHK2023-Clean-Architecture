module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = var.vpc_config.name
  cidr = var.vpc_config.cidr_block

  azs             = data.aws_availability_zones.available.names
  private_subnets = var.vpc_config.private_subnets
  public_subnets  = var.vpc_config.public_subnets
}
