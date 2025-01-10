resource "aws_s3_bucket" "manga_alert_frontend_bucket" {
  bucket        = "manga-alert-italia-frontend-${random_pet.this.id}"
  force_destroy = true
  tags = {
    Name = "Manga Alert Frontend Bucket"
  }
}

resource "aws_s3_bucket_website_configuration" "manga_alert_frontend_bucket_acl_webiste" {
  bucket = aws_s3_bucket.manga_alert_frontend_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Block public access entirely
resource "aws_s3_bucket_public_access_block" "manga_alert_frontend_bucket_acl_webiste_public_access" {
  bucket                  = aws_s3_bucket.manga_alert_frontend_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Policy
# Allow s3:GetObject only if the request comes from the CloudFront distribution.
resource "aws_s3_bucket_policy" "manga_alert_frontend_bucket_policy" {
  bucket = aws_s3_bucket.manga_alert_frontend_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid : "AllowOnlyCloudFrontOACRequests",
        Effect : "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.manga_alert_frontend_bucket.arn}/*",
        Condition = {
          StringEquals = {
            # CloudFront distribution ARN:
            "aws:SourceArn" : "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.manga_alert_italia_cdn.id}"
          }
        }
      }
    ]
  })
}
