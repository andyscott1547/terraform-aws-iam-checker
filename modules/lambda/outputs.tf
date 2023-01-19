# /modules/lambda/outputs.tf

output "lambda_arn" {
  value = aws_lambda_function.this.arn
}

output "lambda_name" {
  value = aws_lambda_function.this.function_name
}

output "lambda_invoke_arn" {
  value = aws_lambda_function.this.invoke_arn
}

output "role_arn" {
  value = aws_iam_role.this.arn
}

output "role_name" {
  value = aws_iam_role.this.name
}