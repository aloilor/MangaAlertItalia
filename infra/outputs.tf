output "manga_scraper_image_repository_url" {
  value = aws_ecr_repository.manga_scraper_image.repository_url
}

# Output the Elastic IP
output "elastic_ip_address" {
  value = aws_eip.manga_alert_main_backend_ecs_eip.public_ip
}
