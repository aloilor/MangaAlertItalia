# Create the Origin Access Control for CloudFront
resource "aws_cloudfront_origin_access_control" "manga_alert_oac_s3" {
  name                              = "mangaalertitalia-s3-oac"
  description                       = "OAC for Manga Alert Italia S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}


# Update your existing aws_cloudfront_distribution to use OAC:
resource "aws_cloudfront_distribution" "manga_alert_italia_cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Distribution for Manga Alert Italia app"
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.manga_alert_frontend_bucket.bucket_regional_domain_name
    origin_id                = "s3-mangaalertitalia"
    origin_access_control_id = aws_cloudfront_origin_access_control.manga_alert_oac_s3.id
  }


  restrictions {
    geo_restriction {
      restriction_type = "none"
      locations        = []
    }
  }


  viewer_certificate {
    cloudfront_default_certificate = true
  }

  default_cache_behavior {
    allowed_methods  = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-mangaalertitalia"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_100"
}
