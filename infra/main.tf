terraform {
  backend "s3" {
    bucket         = "aloilor-terraform-remote-state"
    key            = "terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "aloilor-terraform-remote-state-lock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "eu-west-1"
}

# Provider for issuing ACM certificates
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}



resource "aws_s3_bucket" "s3-terraform-remote-state" {
  bucket        = "aloilor-terraform-remote-state"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "s3-terraform-remote-state-versioning" {
  bucket = aws_s3_bucket.s3-terraform-remote-state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "dynamodb-terraform-lock" {
  name         = "aloilor-terraform-remote-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "random_pet" "this" {}

data "aws_caller_identity" "current" {}
