resource "random_password" "opensearch_master_password" {
  length           = var.rds_config.main_user_password_length
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_security_group" "opensearch_security_group" {
  name        = "${var.opensearch_config.domain_name}-security-group"
  description = "Security group for Opensearch"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Allow access from Home"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = local.allowed_cidrs
  }

  ingress {
    description = "Allow access from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = concat([module.vpc.vpc_cidr_block], module.vpc.vpc_secondary_cidr_blocks)
  }
}


data "aws_iam_policy_document" "opensearch_access_policies" {
  statement {
    effect = "Allow"

    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["es:*"]
    resources = ["arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/*"]
  }
}

data "aws_iam_policy_document" "opensearch_logs" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["es.amazonaws.com"]
    }

    actions = [
      "logs:PutLogEvents",
      "logs:PutLogEventsBatch",
      "logs:CreateLogStream",
    ]

    resources = ["arn:aws:logs:*"]
  }
}


resource "aws_opensearch_domain" "opensearch" {

  domain_name    = var.opensearch_config.domain_name
  engine_version = var.opensearch_config.version


  cluster_config {
    instance_type  = var.opensearch_config.instance.type
    instance_count = var.opensearch_config.instance.count

    zone_awareness_enabled = var.opensearch_config.instance.count > 1
    zone_awareness_config {
      availability_zone_count = length(data.aws_availability_zones.available.names)
    }

    dedicated_master_count   = var.opensearch_config.master_node.count
    dedicated_master_enabled = var.opensearch_config.master_node.count > 0
    dedicated_master_type    = var.opensearch_config.master_node.type
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.opensearch_config.main_username
      master_user_password = random_password.opensearch_master_password.result
    }
  }

  ebs_options {
    ebs_enabled = var.opensearch_config.ebs.volume_size > 0
    volume_size = var.opensearch_config.ebs.volume_size
    throughput  = var.opensearch_config.ebs.throughput
    volume_type = var.opensearch_config.ebs.volume_type
  }

  vpc_options {
    subnet_ids = slice(var.opensearch_config.publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets, 0, min(
      var.opensearch_config.instance.count,
      length(data.aws_availability_zones.available.names)
    ))
    security_group_ids = [aws_security_group.opensearch_security_group.id]
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-0-2019-07"
  }

  access_policies = data.aws_iam_policy_document.opensearch_access_policies.json
}
