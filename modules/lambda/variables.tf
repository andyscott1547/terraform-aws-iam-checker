variable "s3_bucket" {
  type        = string
  description = "The S3 bucket to pull the lambda zip from."
}

variable "code_zip" {
  type        = string
  description = "The lambda package zip"
}

variable "handler" {
  type        = string
  default     = "lambda_function.lambda_handler"
  description = "filename.function called by Lambda"
}

variable "runtime" {
  type        = string
  default     = "python3.9"
  description = "The lambda runtime, defaults to `python3.9`"
}

variable "memory_size" {
  type        = number
  default     = 128
  description = "Memory size required for the lambda"
}

variable "timeout" {
  type        = number
  default     = 3
  description = "Timeout for the lambda"
}

variable "reserved_concurrent_executions" {
  type        = number
  default     = null
  description = "Reserved concurrency for the lambda"
}

variable "managed_policies" {
  type        = list(string)
  default     = []
  description = "List of aws managed Iam policies to be attached to lambda"
}

variable "custom_policy" {
  description = "custom policy"
  type        = string
  default     = ""
}

variable "additional_env_vars" {
  type        = map(string)
  default     = {}
  description = "A map of key value pairs for environment variables."
}

variable "region" {
  type        = string
  default     = "eu-west-1"
  description = "The AWS region to deploy into. Defaults to `eu-west-1`"
}

variable "log_retention_in_days" {
  type        = number
  description = "Number of days we want to retain logs for"
  default     = 365
}

variable "s3_key" {
  type        = string
  default     = null
  description = "Lambda Package stored as S3 Object"
}

variable "timeout_alarm_threshold" {
  type        = number
  default     = 1
  description = "The threshold at which the alarm triggers for timeouts"
}

variable "timeout_alarm_evaluation_periods" {
  type        = number
  default     = 2
  description = "The evaluation period for which the alarm triggers for timeouts"
}

variable "timeout_alarm_period" {
  type        = number
  default     = 60
  description = "The period for which the alarm triggers for timeouts"
}

variable "errors_alarm_threshold" {
  type        = number
  default     = 1
  description = "The threshold at which the alarm triggers for errors"
}

variable "errors_alarm_evaluation_periods" {
  type        = number
  default     = 2
  description = "The evaluation period for which the alarm triggers for errors"
}

variable "errors_alarm_period" {
  type        = number
  default     = 60
  description = "The period for which the alarm triggers for errors"
}

variable "alarms_enabled" {
  type        = bool
  default     = false
  description = "Do we want to enable alarms?"
}

variable "lambda_name" {
  type        = string
  description = "What is the name of the lambda function"
}

variable "cloudwatch_schedule" {
  type        = string
  description = "Do we want to run the Lambda on a schedule, what frequency etc"
  default     = null
}