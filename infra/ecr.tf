resource "aws_ecr_repository" "manga_scraper_image" {
  name                 = "manga-scraper-image-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_lifecycle_policy" "manga_scraper_repo_lifecycle_policy" {
  repository = aws_ecr_repository.manga_scraper_image.name

  policy = <<EOF
  {
  "rules":[
      {
        "rulePriority": 1,
        "description": "Keep last 10 images",
        "selection": {
          "tagStatus": "tagged",
          "tagPatternList": ["manga*"],
          "countType": "imageCountMoreThan",
          "countNumber": 10
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }
  EOF
}
