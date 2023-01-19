resource "aws_lambda_permission" "schedule" {
  count         = var.cloudwatch_schedule != null ? 1 : 0
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule[0].arn
}

resource "aws_cloudwatch_event_rule" "schedule" {
  count               = var.cloudwatch_schedule != null ? 1 : 0
  name                = var.lambda_name
  schedule_expression = var.cloudwatch_schedule
}

resource "aws_cloudwatch_event_target" "schedule" {
  count     = var.cloudwatch_schedule != null ? 1 : 0
  rule      = aws_cloudwatch_event_rule.schedule[0].name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.this.arn
}