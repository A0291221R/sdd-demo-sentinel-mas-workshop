variable "environment" {
  type = string
}

variable "aws_region" {
  description = "AWS region for dashboard widgets."
  type        = string
}

variable "alb_arn_suffix" {
  description = "ARN suffix of the ALB (aws_lb.this.arn_suffix)."
  type        = string
}

variable "api_tg_arn_suffix" {
  description = "ARN suffix of the API blue target group."
  type        = string
}

variable "alarm_sns_arn" {
  description = "Optional SNS topic ARN for alarm notifications. Leave empty to skip."
  type        = string
  default     = ""
}

variable "cluster_name" {
  description = "ECS cluster name for dashboard widgets."
  type        = string
}

variable "api_service_name" {
  description = "ECS api service name for dashboard widgets."
  type        = string
}

variable "central_service_name" {
  description = "ECS central service name for dashboard widgets."
  type        = string
}

variable "sqs_queue_name" {
  description = "SQS queue name for dashboard widgets."
  type        = string
}
