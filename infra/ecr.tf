
## MANGA SCRAPER REGISTRY
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
        "description": "Keep last 3 images",
        "selection": {
          "tagStatus": "tagged",
          "tagPatternList": ["manga*"],
          "countType": "imageCountMoreThan",
          "countNumber": 3
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }
  EOF
}


## EMAIL NOTIFIER REGISTRY
resource "aws_ecr_repository" "email_notifier_image" {
  name                 = "email-notifier-image-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}


resource "aws_ecr_lifecycle_policy" "email_notifier_repo_lifecycle_policy" {
  repository = aws_ecr_repository.email_notifier_image.name

  policy = <<EOF
  {
  "rules":[
      {
        "rulePriority": 1,
        "description": "Keep last 3 images",
        "selection": {
          "tagStatus": "tagged",
          "tagPatternList": ["email*"],
          "countType": "imageCountMoreThan",
          "countNumber": 3
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }
  EOF
}
