data "aws_iam_policy_document" "lambda_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "logging_policy_document" {
  statement {
    effect = "Allow"
    sid    = "CreateLogStream"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:FilterLogEvents"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "ec2_policy_document" {
  statement {
    effect = "Allow"
    sid    = "CreateLogStream"
    actions = [
      "ec2:describe*",      
      "ec2:DeregisterImage*",
      "ec2:DeleteVolume",
      "ec2:DeleteSnapshot",
      "secretsmanager:DeleteSecret",
      "secretsmanager:ListSecrets"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "ec2_describe_policy_ami" {
  statement {
    effect = "Allow"
    sid    = "CreateLogStream"
    actions = [
      "ec2:DeregisterImage*",
      "ec2:DeleteSnapshot*",
      "ec2:DeleteVolume*",
      "autoscaling:DescribeLaunchConfiguration*"
    ]
    resources = ["*"]
  }
}
