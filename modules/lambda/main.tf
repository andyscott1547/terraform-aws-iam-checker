
resource "aws_lambda_function" "this" {
  //checkov:skip=CKV_AWS_272
  //checkov:skip=CKV_AWS_116
  //checkov:skip=CKV_AWS_173
  //checkov:skip=CKV_AWS_117
  //checkov:skip=CKV_SECRET_13
  function_name     = "${var.lambda_name}-${terraform.workspace}"
  s3_bucket         = data.aws_s3_object.this.bucket
  s3_key            = data.aws_s3_object.this.key
  s3_object_version = data.aws_s3_object.this.version_id

  handler                        = var.handler
  runtime                        = var.runtime
  role                           = aws_iam_role.this.arn
  memory_size                    = var.memory_size
  timeout                        = var.timeout
  reserved_concurrent_executions = var.reserved_concurrent_executions

  layers = [
    "arn:aws:lambda:eu-west-1:580247275435:layer:LambdaInsightsExtension:14"
  ]

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = merge(local.default_env_vars, var.additional_env_vars)
  }
}

resource "aws_cloudwatch_log_group" "this" {
  //checkov:skip=CKV_AWS_158
  name              = "/aws/lambda/${var.lambda_name}-${terraform.workspace}"
  retention_in_days = var.log_retention_in_days
}
