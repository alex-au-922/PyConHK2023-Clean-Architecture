# Reference: https://medium.com/geekculture/serve-your-react-app-with-aws-cloudfront-using-gitlab-and-terraform-322b2526943e

locals {
  s3_origin_id = "s3-${var.cloudfront_config.frontend.name}"
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = var.cloudfront_config.frontend.name
  description                       = var.cloudfront_config.frontend.description
  origin_access_control_origin_type = var.cloudfront_config.frontend.origin_access_control.s3.origin_type
  signing_behavior                  = var.cloudfront_config.frontend.origin_access_control.s3.signing_enabled ? "always" : "never"
  signing_protocol                  = var.cloudfront_config.frontend.origin_access_control.s3.signing_protocol
}

resource "aws_cloudfront_distribution" "frontend_distribution" {
  origin {
    domain_name              = module.frontend_bucket.s3_bucket_bucket_regional_domain_name
    origin_id                = local.s3_origin_id
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  logging_config {
    include_cookies = false
    bucket          = module.frontend_cloudfront_logging_bucket.s3_bucket_id
  }

  enabled         = true
  is_ipv6_enabled = true

  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = var.cloudfront_config.frontend.cache.allowed_methods
    cached_methods   = var.cloudfront_config.frontend.cache.cached_methods
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = var.cloudfront_config.frontend.cache.query_string

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = var.cloudfront_config.frontend.cache.viewer_protocol_policy
    min_ttl                = var.cloudfront_config.frontend.cache.ttl.min
    default_ttl            = var.cloudfront_config.frontend.cache.ttl.default
    max_ttl                = var.cloudfront_config.frontend.cache.ttl.max
    compress               = var.cloudfront_config.frontend.cache.compress
  }

  ordered_cache_behavior {
    path_pattern     = "/index.html"
    allowed_methods  = var.cloudfront_config.frontend.cache.allowed_methods
    cached_methods   = var.cloudfront_config.frontend.cache.cached_methods
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = var.cloudfront_config.frontend.cache.query_string

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = var.cloudfront_config.frontend.cache.viewer_protocol_policy
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = var.cloudfront_config.frontend.cache.compress
  }

  price_class = var.cloudfront_config.frontend.price_class

  viewer_certificate {
    cloudfront_default_certificate = var.cloudfront_config.frontend.default_ssl_cert
  }

  retain_on_delete = var.cloudfront_config.frontend.retain_on_delete

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = var.cloudfront_config.frontend.restrictions.whitelisted_locations
    }
  }

  depends_on = [
    module.frontend_bucket,
    module.frontend_cloudfront_logging_bucket,
    aws_cloudfront_origin_access_control.frontend
  ]
}
