resource "aws_cloudwatch_event_rule" "every_day" {
    name = "every-day"
    description = "triggers every day"
    schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "monitor_lambda_amis_autoscaling_to_be_deleted_every_day" {
    rule = "${aws_cloudwatch_event_rule.every_day.name}"
    target_id = "lambda-amis-volumes-secrets-deletion"
    arn = "${aws_lambda_function.lambda.arn}"
}
