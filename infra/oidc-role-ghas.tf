
resource "aws_iam_openid_connect_provider" "oidc_github_actions" {
  client_id_list = [
    "sts.amazonaws.com",
  ]
  thumbprint_list = [
    "d89e3bd43d5d909b47a18977aa9d5ce36cee184c",
  ]
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions_role" {
  name = "github-actions-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = aws_iam_openid_connect_provider.oidc_github_actions.arn,
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com",
          },
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:aloilor/iac-cicd-aws:*",
              "repo:aloilor/manga-scrape-italy:*"
            ]
          }
        },
      },
    ],
  })
  managed_policy_arns   = [aws_iam_policy.ghas_admin_policy.arn]
  max_session_duration  = 3600
  force_detach_policies = false
}

# Custom policy for (almost) admin access
resource "aws_iam_policy" "ghas_admin_policy" {
  name        = "github-actions-combined-policy"
  description = "Combined policy with access to commonly used AWS services for GitHub Actions."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [

      # Amazon EC2, ECS and ECR access
      {
        Effect = "Allow",
        Action = [
          "ec2:*",
          "ecs:*",
          "ecr:*",
        ],
        Resource = "*"
      },

      # Amazon S3 access
      {
        Effect = "Allow",
        Action = [
          "s3:*",
        ],
        Resource = "*"
      },

      # Amazon RDS access
      {
        Effect = "Allow",
        Action = [
          "rds:*",
        ],
        Resource = "*"
      },

      # Amazon DynamoDB access
      {
        Effect = "Allow",
        Action = [
          "dynamodb:*",
        ],
        Resource = "*"
      },

      # AWS Lambda access
      {
        Effect = "Allow",
        Action = [
          "lambda:*",
        ],
        Resource = "*"
      },

      # Amazon CloudWatch access
      {
        Effect = "Allow",
        Action = [
          "cloudwatch:*",
          "logs:*",
          "events:*",
        ],
        Resource = "*"
      },

      # AWS IAM access (limited to necessary actions)
      {
        Effect = "Allow",
        Action = [
          "iam:*"
        ],
        Resource = "*"
      },

      # Amazon SES access
      {
        Effect = "Allow",
        Action = [
          "ses:*",
        ],
        Resource = "*"
      },

      # AWS Organizations access
      {
        Effect = "Allow",
        Action = [
          "organizations:*",
        ],
        Resource = "*"
      },

      # AWS Route53 access
      {
        Effect = "Allow",
        Action = [
          "route53:*",
        ],
        Resource = "*"
      },

      # AWS Cloudfront access
      {
        Effect = "Allow",
        Action = [
          "cloudfront:*",
        ],
        Resource = "*"
      },


    ]
  })
}


