data "aws_caller_identity" "current" {
}

resource "aws_ecr_repository" "this" {
  name                 = var.name
  image_tag_mutability = var.image_mutable ? "MUTABLE" : "IMMUTABLE"
  force_delete         = var.force_delete
  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

}

resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last ${var.keep_images} images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = "imageCountMoreThan",
          countNumber   = var.keep_images
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

data "aws_iam_policy_document" "this" {
  statement {
    sid    = "Full Access from account"
    effect = "Allow"

    principals {
      type = "AWS"
      identifiers = [
        data.aws_caller_identity.current.account_id,
        var.caller_identity_arn,
      ]
    }

    actions = [
      "ecr:*"
    ]
  }
  statement {
    sid    = "Allow Lambda to pull images"
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "ecs-tasks.amazonaws.com",
        "ecs.amazonaws.com",
        "ec2.amazonaws.com",
      ]
    }

    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:DescribeRepositories",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
    ]
  }
}

resource "aws_ecr_repository_policy" "this" {
  repository = aws_ecr_repository.this.name
  policy     = data.aws_iam_policy_document.this.json
}
