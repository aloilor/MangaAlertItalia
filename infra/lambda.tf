resource "aws_lambda_layer_version" "ssl_renew_certs_layer" {
  filename   = "${path.module}/src-lambda/ssl-renew-certificates/layer_content.zip"
  layer_name = "certbot-dns-route53-layer"

  compatible_runtimes = ["python3.11"]
  source_code_hash    = filebase64sha256("${path.module}/src-lambda/ssl-renew-certificates/layer_content.zip")

}

data "archive_file" "lambda_ssl_renew_certs_zip" {
  type        = "zip"
  source_file = "${path.module}/src-lambda/ssl-renew-certificates/main.py"
  output_path = "${path.module}/src-lambda/ssl-renew-certificates/lambda_ssl_renew_certs_payload.zip"
}

resource "aws_lambda_function" "lambda_ssl_renew_certs" {
  filename      = "${path.module}/src-lambda/ssl-renew-certificates/lambda_ssl_renew_certs_payload.zip"
  function_name = "ssl-renew-certificates"
  handler       = "main.lambda_handler"
  role          = aws_iam_role.ssl_renew_certs_lambda_role.arn

  source_code_hash = data.archive_file.lambda_ssl_renew_certs_zip.output_base64sha256
  runtime          = "python3.11"
  layers           = [aws_lambda_layer_version.ssl_renew_certs_layer.arn]
  timeout          = 90
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ssl_renew_certs_lambda_role" {
  name               = "ssl-renew-certificates-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "ssl_renew_certs_lambda_policy_doc" {
  statement {
    effect = "Allow"
    actions = ["secretsmanager:GetSecretValue",
      "secretsmanager:PutSecretValue"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = ["route53:ListHostedZones",
      "route53:GetChange",
      "route53:ChangeResourceRecordSets"
    ]
    resources = ["arn:aws:route53:::hostedzone/Z09963622FQGDU6DVL521"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "ssl_renew_certs_lambda_policy" {
  name        = "ssl-renew-certificates-lambda-policy"
  description = "IAM Role Policy managing permissions for ssl/renew-certificates lambda, such as SecretsManager and Route53"
  policy      = data.aws_iam_policy_document.ssl_renew_certs_lambda_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "ssl_renew_certs_lambda_role_policy_attach" {
  role       = aws_iam_role.ssl_renew_certs_lambda_role.name
  policy_arn = aws_iam_policy.ssl_renew_certs_lambda_policy.arn
}


