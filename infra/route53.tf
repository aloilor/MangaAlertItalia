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
