resource "aws_cloudwatch_metric_alarm" "lambda_timeouts" {
  count               = var.alarms_enabled ? 1 : 0
  alarm_name          = "${var.lambda_name}-${terraform.workspace}-Timeouts"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.timeout_alarm_evaluation_periods
  threshold           = var.timeout_alarm_threshold
  period              = var.timeout_alarm_period
  unit                = "Count"

  namespace   = "TEST"
  metric_name = "Timeouts"
  statistic   = "Maximum"
  dimensions = {
    Environment = terraform.workspace
    Service     = "/aws/lambda/${var.lambda_name}"
  }
  lifecycle {
    ignore_changes = [alarm_actions]
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = var.alarms_enabled ? 1 : 0
  alarm_name          = "${var.lambda_name}-${terraform.workspace}-Errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.errors_alarm_evaluation_periods
  threshold           = var.errors_alarm_threshold
  period              = var.errors_alarm_period
  unit                = "Count"
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  statistic           = "Maximum"
  dimensions = {
    FunctionName = var.lambda_name
  }
  lifecycle {
    ignore_changes = [alarm_actions]
  }
}