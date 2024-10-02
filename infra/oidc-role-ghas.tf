
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
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AWSOrganizationsFullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/AmazonRDSFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
  ]
  max_session_duration  = 3600
  force_detach_policies = false
}



