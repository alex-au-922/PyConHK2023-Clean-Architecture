data "aws_ecr_repository" "embedding_model" {
  name = var.sagemaker_config.embedding_model.name
}

data "aws_ecr_image" "latest_embedding_model_docker_image" {
  repository_name = data.aws_ecr_repository.embedding_model.name
  most_recent     = true
}

resource "aws_iam_role" "embedding_model" {
  name               = "${var.sagemaker_config.embedding_model.name}-sagemaker-role"
  assume_role_policy = data.aws_iam_policy_document.sagemaker_assume_role.json
}

data "aws_iam_policy_document" "sagemaker_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "embedding_model_policy" {
  statement {
    effect  = "Allow"
    actions = ["sagemaker:*"]

    resources = ["*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:*",
      "logs:*",
      "ecr:*",
      "ec2:*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "embedding_model_policy" {
  name   = "${var.sagemaker_config.embedding_model.name}-sagemaker-policy"
  policy = data.aws_iam_policy_document.embedding_model_policy.json
}

resource "aws_security_group" "embedding_model" {
  name        = "${var.sagemaker_config.embedding_model.name}-sagemaker-security-group"
  description = "Security group for SageMaker Embedding Model"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "VPC access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = concat([module.vpc.vpc_cidr_block], module.vpc.vpc_secondary_cidr_blocks)
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

resource "aws_iam_role_policy_attachment" "sagemaker" {
  role       = aws_iam_role.embedding_model.name
  policy_arn = aws_iam_policy.embedding_model_policy.arn
}

resource "aws_sagemaker_model" "embedding_model" {
  name               = "${var.sagemaker_config.embedding_model.name}-${substr(uuid(), 0, 3)}"
  execution_role_arn = aws_iam_role.embedding_model.arn

  primary_container {
    image = "${data.aws_ecr_repository.embedding_model.repository_url}:${data.aws_ecr_image.latest_embedding_model_docker_image.image_tags[0]}"
    environment = {
      LOG_LEVEL  = "INFO"
      LOG_FORMAT = "[%(asctime)s | %(levelname)s] (%(module)s | %(funcName)s | %(lineno)d) >> %(message)s"
    }
  }

  vpc_config {
    security_group_ids = [aws_security_group.embedding_model.id]
    subnets            = module.vpc.private_subnets
  }
}

resource "aws_sagemaker_endpoint_configuration" "embedding_model" {
  name = "${var.sagemaker_config.embedding_model.name}-sagemaker-endpoint-config"

  production_variants {
    variant_name           = var.sagemaker_config.embedding_model.deployment.instance_variant.name
    model_name             = aws_sagemaker_model.embedding_model.name
    initial_instance_count = var.sagemaker_config.embedding_model.deployment.instance_count
    instance_type          = var.sagemaker_config.embedding_model.deployment.instance_type
    initial_variant_weight = var.sagemaker_config.embedding_model.deployment.instance_variant.weight
  }
}

resource "aws_sagemaker_endpoint" "embedding_model" {
  name                 = "${var.sagemaker_config.embedding_model.name}-sagemaker-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.embedding_model.name
}
