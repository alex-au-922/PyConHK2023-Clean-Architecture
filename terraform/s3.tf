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

  attach_policy = true
  policy = {
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = [
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
          ]
        },
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.data_bucket.arn}",
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Principal = {
          Service = [
            "lambda.amazonaws.com"
          ]
        },
        Action = [
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.data_bucket.arn}"
        ],
        Condition = {
          StringLike = {
            "aws:SourceArn" = [
              module.data_ingestion_handler_lambda.lambda_function_arn,
            ]
          }
        }
      },
      {
        Effect = "Allow",
        Principal = {
          Service = [
            "lambda.amazonaws.com"
          ]
        },
        Action = [
          "s3:GetObject",
        ],
        Resource = [
          "${aws_s3_bucket.data_bucket.arn}/*"
        ],
        Condition = {
          StringLike = {
            "aws:SourceArn" = [
              module.data_ingestion_handler_lambda.lambda_function_arn,
            ]
          }
        }
      }
    ]
  }
}
