output "lambda_arn" {
  value = aws_lambda_function.lambda.invoke_arn
}

output "lambda_name" {
  value = aws_lambda_function.lambda.function_name
}

output "lambda_iam_role_name" {
  value = aws_iam_role.iam_role.name
}

output "lambda_iam_role_arn" {
  value = aws_iam_role.iam_role.arn
}

output "use_profile" {
  value = var.use_profile
}

output "days_count" {
  value = var.days_count
}

output "regions_arr" {
  value = var.regions_arr
}
