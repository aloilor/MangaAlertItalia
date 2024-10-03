# Manga Alert Italy documentation

## Directory Structure
```
manga-scrape-italy-main/
│
├── .github/                                    
│   └── workflows/
│       ├── scraper-build-pipeline.yml          # CI/CD pipeline configuration for scraper build.
│       └── terraform-cicd-pipeline.yml         # CI/CD pipeline for Terraform infrastructure.
│
│
├── docs/                                       # Documentation related to development and application usage.
│   ├── docs-dev.md                             # General developer documentation.
│   └── manga_scraper/
│       └── docs-manga-scraper.md               # Developer documentation for the manga scraper.
│
│
├── infra/                                      # Infrastructure as Code files for deployment.
│   ├── .terraform.lock.hcl                     # Lock file for Terraform dependencies.
│   ├── ecr.tf                                  # Terraform configuration for ECR.
│   ├── ecs.tf                                  # Terraform configuration for ECS.
│   ├── eventbridge.tf                          # Terraform configuration for EventBridge.
│   ├── main.tf                                 # Main Terraform configuration file.
│   ├── oidc-role-ghas.tf                       # Role for GitHub Actions OIDC.
│   ├── organizations.tf                        # Terraform configuration for AWS Organizations.
│   ├── outputs.tf                              # Terraform outputs.
│   ├── rds.tf                                  # Terraform configuration for RDS.
│   ├── variables.tf                            # Variable definitions for Terraform.
│   └── vpc.tf                                  # Terraform configuration for VPC.
│
│
├── src/                                        # Source code for the project.
│   └── backend/
│       ├── Dockerfile.email_alerter            # Dockerfile for the email alerter service.
│       ├── Dockerfile.manga_scraper            # Dockerfile for the manga scraper service.
│       ├── aws_utils/                          # AWS utility scripts.
│       │   ├── db_connector.py                 # Utility for database connections.
│       │   └── secrets_manager.py              # Utility for managing AWS Secrets Manager.
│       └── manga_scraper/                      # Manga scraper application.
│           ├── main.py                         # Entry point for the manga scraping process.
│           ├── manga_scraper_app.py            # Orchestrates the scraping and notification process.
│           ├── requirements.txt                # Dependencies for the scraper application.
│           ├── models/                 
│           │   └── manga_release.py            # Defines the model for scraped manga release data.
│           ├── scrapers/                       # Scrapers for specific manga publishers.
│           │   ├── planet_manga_scraper.py     # Scraper for Planet Manga publisher.
│           │   ├── publisher_scraper.py        # Base class for publisher scrapers.
│           │   └── star_comics_scraper.py      # Scraper for Star Comics publisher.
│           └── utils/                          # Utility functions for the scraper.
│               ├── file_handler.py             # Handles file operations like saving responses.
│               └── logging_config.py           # Configures logging for the application.
│
│
└── tests/                                      # Test suite for validating functionality.
    ├── conftest.py                             # Configuration for test cases.
    ├── requirements.txt                        # Dependencies for running tests (imports mainly).
    ├── test_aws_utils.py                       # Tests for AWS utility scripts.
    └── test_manga_scraper.py                   # Tests for manga scraper functionality.
```

## High-level description
