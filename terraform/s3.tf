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
