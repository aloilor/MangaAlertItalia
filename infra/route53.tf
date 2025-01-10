resource "aws_route53_zone" "manga_alert_hosted_zone" {
  name = "mangaalertitalia.it"
}

resource "aws_route53_record" "ses_verification_record" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "_amazonses.mangaalertitalia.it"
  type    = "TXT"
  ttl     = 300
  records = [aws_ses_domain_identity.manga_alert_ses_domain.verification_token]
}

resource "aws_ses_domain_dkim" "ses_dkim" {
  domain = aws_ses_domain_identity.manga_alert_ses_domain.domain
}

resource "aws_route53_record" "ses_dkim_record" {
  count   = 3
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "${aws_ses_domain_dkim.ses_dkim.dkim_tokens[count.index]}._domainkey.mangaalertitalia.it"
  type    = "CNAME"
  ttl     = 300
  records = ["${aws_ses_domain_dkim.ses_dkim.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "spf_record" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "mangaalertitalia.it"
  type    = "TXT"
  ttl     = 300
  records = ["v=spf1 include:amazonses.com -all"]
}

resource "aws_route53_record" "dmarc_record" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "_dmarc.mangaalertitalia.it"
  type    = "TXT"
  ttl     = 300
  records = ["v=DMARC1; p=none; rua=mailto:postmaster@mangaalertitalia.it"]
}

resource "aws_route53_record" "api_record" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "api.mangaalertitalia.it"
  type    = "A"
  ttl     = 300
  records = [aws_eip.manga_alert_main_backend_ecs_eip.public_ip]
}


# ACM SSL Certificates for Cloudfront
resource "aws_acm_certificate" "manga_alert_cert" {
  domain_name       = "mangaalertitalia.it"
  validation_method = "DNS"

  subject_alternative_names = ["www.mangaalertitalia.it"]

  provider = aws.us_east_1
}

# DNS validation record
resource "aws_route53_record" "manga_alert_cert_validation" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id

  for_each = {
    for dvo in aws_acm_certificate.manga_alert_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 600
  type            = each.value.type

}

resource "aws_acm_certificate_validation" "manga_alert_cert_validation_complete" {
  certificate_arn         = aws_acm_certificate.manga_alert_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.manga_alert_cert_validation : record.fqdn]


  provider = aws.us_east_1
}

# CDN Alias record
resource "aws_route53_record" "manga_alert_cf_alias" {
  zone_id = aws_route53_zone.manga_alert_hosted_zone.zone_id
  name    = "mangaalertitalia.it"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.manga_alert_italia_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.manga_alert_italia_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}


