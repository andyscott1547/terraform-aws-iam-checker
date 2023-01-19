resource "aws_lambda_alias" "main" {
  name             = terraform.workspace
  description      = "Alias for ${aws_lambda_function.this.function_name}"
  function_name    = aws_lambda_function.this.arn
  function_version = "$LATEST"
}
