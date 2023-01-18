resource "aws_iam_role" "iam_role" {
  name               = "lambda-amis-volumes-secrets-deletion-${var.region}-iam-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_policy.json
}

resource "aws_iam_role_policy" "logging_policy" {
  name   = "logging"
  role   = aws_iam_role.iam_role.id
  policy = data.aws_iam_policy_document.logging_policy_document.json
}

resource "aws_iam_role_policy" "ec2_describe_policy" {
  name   = "ec2_describe"
  role   = aws_iam_role.iam_role.id
  policy = data.aws_iam_policy_document.ec2_policy_document.json
}

resource "aws_iam_role_policy" "ec2_ami_launch_config_policy" {
  name   = "ec2_ami_launch_config"
  role   = aws_iam_role.iam_role.id
  policy = data.aws_iam_policy_document.ec2_describe_policy_ami.json
}

resource "aws_iam_role_policy_attachment" "basic_lambda_exec_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.iam_role.name
}
