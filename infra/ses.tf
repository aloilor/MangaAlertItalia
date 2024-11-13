resource "aws_ses_email_identity" "email_identity" {
  email = "aloisi.lorenzo99@gmail.com"
}

resource "aws_ses_domain_identity" "manga_alert_ses_domain" {
  domain = "mangaalertitalia.it"
}

resource "aws_ses_domain_identity_verification" "ses_domain_verification" {
  domain     = aws_ses_domain_identity.manga_alert_ses_domain.domain
  depends_on = [aws_route53_record.ses_verification_record]
}

