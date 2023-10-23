module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = var.vpc_config.name
  cidr = var.vpc_config.cidr_block

  azs             = data.aws_availability_zones.available.names
  private_subnets = var.vpc_config.private_subnets
  public_subnets  = var.vpc_config.public_subnets
}

data "aws_ami" "ami" {
  most_recent = true

  filter {
    name   = "name"
    values = [var.bastion_host_config.ami_filter.name]
  }

  filter {
    name   = "virtualization-type"
    values = [var.bastion_host_config.ami_filter.virtualization_type]
  }

  owners = var.bastion_host_config.ami_filter.owners
}

resource "aws_ami_copy" "encrypted_ami" {
  name              = "encrypted-${var.bastion_host_config.ami_filter.name}"
  description       = "An encrypted root ami based off ${data.aws_ami.ami.id}"
  source_ami_id     = data.aws_ami.ami.id
  source_ami_region = data.aws_region.current.name
  encrypted         = true
}

resource "aws_security_group" "bastion_host_security_group" {
  name        = "${var.bastion_host_config.name}-security-group"
  description = "Security group for Bastion Host"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow SSH access from Home"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = local.allowed_cidrs
  }

  ingress {
    description = "Allow SSH access from VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = concat([module.vpc.vpc_cidr_block], module.vpc.vpc_secondary_cidr_blocks)
  }
}

resource "aws_key_pair" "bastion_host_key_pair" {
  key_name   = var.bastion_host_config.key_name
  public_key = tls_private_key.rsa.public_key_openssh

  provisioner "local-exec" {
    command = "echo '${tls_private_key.rsa.private_key_pem}' > ./terraform/${var.bastion_host_config.key_name}.pem"
  }
}

resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_instance" "bastion_host" {
  ami                         = aws_ami_copy.encrypted_ami.id
  instance_type               = var.bastion_host_config.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.bastion_host_security_group.id,
    module.vpc.default_security_group_id,
  ]

  key_name  = aws_key_pair.bastion_host_key_pair.key_name
  subnet_id = module.vpc.public_subnets[0]

}
