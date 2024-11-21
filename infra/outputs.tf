
# Output the Elastic IP
output "elastic_ip_address" {
  value = aws_eip.manga_alert_main_backend_ecs_eip.public_ip
}
