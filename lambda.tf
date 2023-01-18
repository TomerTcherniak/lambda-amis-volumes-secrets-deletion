data "archive_file" "init" {
  type        = "zip"
  source_file = "./lambda-amis-volumes-secrets-deletion.py"
  output_path = "${path.module}/lambda-amis-volumes-secrets-deletion.zip"
}

resource "aws_lambda_function" "lambda" {
  filename                       = "${path.module}/lambda-amis-volumes-secrets-deletion.zip"
  function_name                  = "lambda-amis-volumes-secrets-deletion"
  description                    = "Function for sre visibility channel"
  role                           = aws_iam_role.iam_role.arn
  handler                        = "lambda-amis-volumes-secrets-deletion.lambda_handler"
  source_code_hash               = data.archive_file.init.output_base64sha256
  runtime                        = "python3.9"
  memory_size                    = var.memory_size
  timeout                        = var.timeout
  reserved_concurrent_executions = 1
  #kms_key_arn                    = aws_kms_key.kms_key.arn

  environment {
    variables = {
      region                    = var.region
      use_profile               = var.use_profile
      days_count                = var.days_count
      regions_arr               = "${var.regions_arr}"
      delete_flag               = var.delete_flag
    }
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.every_day.arn}"
}
