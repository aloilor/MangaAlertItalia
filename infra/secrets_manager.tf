resource "aws_secretsmanager_secret" "ssl_certificates_secret" {
  name        = "ssl/api.mangaalertitalia.it"
  description = "Secret containing the SSL certificates created through Let's Encrypt"
}
