module "data_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = var.s3_config.data_bucket.name
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  force_destroy = var.s3_config.data_bucket.force_destroy

  versioning = {
    enabled = var.s3_config.data_bucket.versioning
  }
}

data "aws_iam_policy_document" "frontend_bucket_access_policy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${module.frontend_bucket.s3_bucket_arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.frontend_distribution.arn]
    }
  }
}

module "frontend_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket                   = var.s3_config.frontend_bucket.name
  acl                      = var.s3_config.frontend_bucket.block_public_access ? "private" : "public-read"
  control_object_ownership = true
  object_ownership         = "ObjectWriter"
  force_destroy            = var.s3_config.frontend_bucket.force_destroy

  versioning = {
    enabled = var.s3_config.frontend_bucket.versioning
  }
}

resource "aws_s3_bucket_policy" "frontend_bucket_access_policy" {
  bucket = module.frontend_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.frontend_bucket_access_policy.json
}

data "aws_iam_policy_document" "frontend_bucket_access_policy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${module.frontend_bucket.s3_bucket_arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.frontend_distribution.arn]
    }
  }
}

module "frontend_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket                   = var.s3_config.frontend_bucket.name
  acl                      = var.s3_config.frontend_bucket.block_public_access ? "private" : "public-read"
  control_object_ownership = true
  object_ownership         = "ObjectWriter"
  force_destroy            = var.s3_config.frontend_bucket.force_destroy

  versioning = {
    enabled = var.s3_config.frontend_bucket.versioning
  }
}

resource "aws_s3_bucket_policy" "frontend_bucket_access_policy" {
  bucket = module.frontend_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.frontend_bucket_access_policy.json
}
